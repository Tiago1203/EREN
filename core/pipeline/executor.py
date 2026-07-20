"""Pipeline Executor for EREN OS Cognitive Capability Pipeline.

Internal executor that runs stages according to policies.
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.pipeline.context import PipelineContext
from core.pipeline.policy import PipelinePolicy, StopOnFailurePolicy
from core.pipeline.stage import PipelineStage
from core.pipeline.types import PipelineResult, PipelineState, StageState

if TYPE_CHECKING:
    from core.pipeline.pipeline import CognitivePipeline


class PipelineExecutor:
    """Executes pipeline stages according to policies.

    Responsible for:
    - Traversing stages
    - Controlling errors
    - Applying policies
    - Supporting cancellation
    - Supporting pause/resume
    - Collecting metrics
    """

    def __init__(
        self,
        pipeline: CognitivePipeline,
        policy: PipelinePolicy | None = None,
    ):
        """Initialize the executor.

        Args:
            pipeline: The pipeline to execute.
            policy: Execution policy to apply.
        """
        self._pipeline = pipeline
        self._policy = policy or StopOnFailurePolicy()
        self._is_cancelled = False
        self._is_paused = False
        self._pause_event = threading.Event()
        self._lock = threading.RLock()

    @property
    def is_cancelled(self) -> bool:
        """Check if execution is cancelled."""
        with self._lock:
            return self._is_cancelled

    @property
    def is_paused(self) -> bool:
        """Check if execution is paused."""
        with self._lock:
            return self._is_paused

    def request_cancellation(self) -> None:
        """Request cancellation of execution."""
        with self._lock:
            self._is_cancelled = True
            self._pause_event.set()  # Unblock any wait

    def pause(self) -> None:
        """Pause execution."""
        with self._lock:
            if not self._is_paused:
                self._is_paused = True
                self._pause_event.clear()

    def resume(self) -> None:
        """Resume execution."""
        with self._lock:
            if self._is_paused:
                self._is_paused = False
                self._pause_event.set()

    def execute(
        self,
        context: PipelineContext,
    ) -> PipelineResult:
        """Execute the pipeline.

        Args:
            context: Pipeline context with intent and shared data.

        Returns:
            PipelineResult with execution outcome.

        Raises:
            PipelineExecutionError: If execution fails.
        """
        start_time = time.time()
        stage_results: list = []
        failed_stage: str | None = None
        errors: list[str] = []

        try:
            # Mark context as started
            context.start()

            # Execute stages
            for stage in self._pipeline.stages:
                # Check cancellation
                if self._is_cancelled or context.is_cancellation_requested():
                    return self._create_result(
                        context,
                        PipelineState.CANCELLED,
                        start_time,
                        stage_results,
                        failed_stage,
                        ["Cancelled"],
                    )

                # Handle pause
                self._wait_if_paused()

                # Update current stage
                context.current_stage = stage.name
                context.current_stage_index += 1

                # Execute stage
                try:
                    result = self._execute_stage(stage, context)
                    stage_results.append(result)
                    context.add_stage_result(stage.name, result)

                    # Check if stage failed
                    if not result.is_success:
                        if stage.is_required:
                            # Apply policy
                            should_stop = self._policy.should_stop_on_failure(
                                stage,
                                result,
                                context,
                            )

                            if should_stop:
                                failed_stage = stage.name
                                errors.append(
                                    f"Stage '{stage.name}' failed and policy requires stop"
                                )
                                return self._create_result(
                                    context,
                                    PipelineState.FAILED,
                                    start_time,
                                    stage_results,
                                    failed_stage,
                                    errors,
                                )
                        else:
                            # Optional stage failed, continue
                            pass

                except Exception as e:
                    # Stage threw exception
                    from core.pipeline.types import StageResult
                    result = StageResult(
                        stage_name=stage.name,
                        stage_type=stage.stage_type,
                        status=StageState.FAILED,
                        errors=[str(e)],
                    )
                    stage_results.append(result)
                    failed_stage = stage.name

                    # Check policy
                    if stage.is_required:
                        should_stop = self._policy.should_stop_on_failure(
                            stage,
                            result,
                            context,
                        )
                        if should_stop:
                            errors.append(f"Stage '{stage.name}' raised exception")
                            return self._create_result(
                                context,
                                PipelineState.FAILED,
                                start_time,
                                stage_results,
                                failed_stage,
                                errors,
                            )
                    errors.append(str(e))

            # Pipeline completed
            return self._create_result(
                context,
                PipelineState.COMPLETED,
                start_time,
                stage_results,
                None,
                errors if errors else None,
            )

        except Exception as e:
            # Unexpected error
            return self._create_result(
                context,
                PipelineState.FAILED,
                start_time,
                stage_results,
                failed_stage,
                [str(e)],
            )

        finally:
            context.finish()

    def _execute_stage(
        self,
        stage: PipelineStage,
        context: PipelineContext,
    ) -> StageResult:
        """Execute a single stage.

        Args:
            stage: Stage to execute.
            context: Pipeline context.

        Returns:
            StageResult from execution.
        """
        # Execute with retry support
        result = stage.execute_with_retry(context)

        # Check if should skip optional failed stages
        if not result.is_success and not stage.is_required:
            result.status = StageState.SKIPPED

        return result

    def _wait_if_paused(self) -> None:
        """Wait if execution is paused."""
        with self._lock:
            if self._is_paused:
                self._pause_event.wait()

    def _create_result(
        self,
        context: PipelineContext,
        status: PipelineState,
        start_time: float,
        stage_results: list,
        failed_stage: str | None,
        errors: list[str] | None,
    ) -> PipelineResult:
        """Create a pipeline result.

        Args:
            context: Pipeline context.
            status: Final status.
            start_time: Start timestamp.
            stage_results: List of stage results.
            failed_stage: Name of failed stage.
            errors: List of errors.

        Returns:
            PipelineResult instance.
        """
        duration_ms = int((time.time() - start_time) * 1000)

        completed_stages = [
            r.stage_name for r in stage_results if r.is_success
        ]

        return PipelineResult(
            pipeline_id=context.pipeline_id,
            pipeline_name=context.pipeline_name,
            status=status,
            started_at=datetime.fromtimestamp(start_time, tz=UTC),
            finished_at=datetime.now(UTC),
            duration_ms=duration_ms,
            completed_stages=completed_stages,
            failed_stage=failed_stage,
            stage_results=stage_results,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            errors=errors or [],
            metadata=context.metadata,
        )


class SyncPipelineExecutor(PipelineExecutor):
    """Synchronous pipeline executor.

    Provides synchronous execution for pipelines that don't need async.
    """

    def execute(
        self,
        context: PipelineContext,
    ) -> PipelineResult:
        """Execute pipeline synchronously.

        Args:
            context: Pipeline context.

        Returns:
            PipelineResult.
        """
        return super().execute(context)
