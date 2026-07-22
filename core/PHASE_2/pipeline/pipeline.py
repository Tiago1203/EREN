"""Cognitive Pipeline for EREN OS Cognitive Capability Pipeline.

Main pipeline engine that orchestrates stage execution.
"""

from __future__ import annotations

import threading
import uuid
from typing import TYPE_CHECKING, Any

from core.PHASE_2.pipeline.context import PipelineContext
from core.PHASE_2.pipeline.exceptions import (
    DuplicateStageError,
    EmptyPipelineError,
    PipelineStateError,
)
from core.PHASE_2.pipeline.executor import PipelineExecutor
from core.PHASE_2.pipeline.policy import PipelinePolicy, StopOnFailurePolicy
from core.PHASE_2.pipeline.stage import PipelineStage
from core.PHASE_2.pipeline.types import (
    PipelineConfig,
    PipelineResult,
    PipelineState,
    StageMetadata,
)
from core.PHASE_2.pipeline.validator import PipelineValidator

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.events import PipelineEventPublisher
    from core.PHASE_2.pipeline.metrics import PipelineMetrics
    from core.PHASE_2.pipeline.trace import PipelineTrace


class CognitivePipeline:
    """Main cognitive pipeline engine.

    Responsible for:
    - Executing stages in order
    - Maintaining state
    - Publishing events
    - Recording metrics
    - Recording traces

    Features:
    - Thread-safe execution
    - State machine
    - Cancellation support
    - Pause/resume
    - Multiple execution policies
    """

    def __init__(
        self,
        name: str,
        pipeline_id: str | None = None,
        stages: list[PipelineStage] | None = None,
        policy: PipelinePolicy | None = None,
        config: PipelineConfig | None = None,
    ):
        """Initialize the pipeline.

        Args:
            name: Pipeline name.
            pipeline_id: Optional pipeline ID.
            stages: Optional list of initial stages.
            policy: Execution policy.
            config: Pipeline configuration.
        """
        self._name = name
        self._pipeline_id = pipeline_id or f"pipeline_{uuid.uuid4().hex[:16]}"
        self._stages: list[PipelineStage] = []
        self._policy = policy or StopOnFailurePolicy()
        self._config = config or PipelineConfig(
            pipeline_name=name,
            pipeline_id=self._pipeline_id,
        )

        # State
        self._state = PipelineState.CREATED
        self._lock = threading.RLock()

        # Observability
        self._event_publisher: PipelineEventPublisher | None = None
        self._metrics: PipelineMetrics | None = None
        self._trace: PipelineTrace | None = None

        # Statistics
        self._execution_count = 0
        self._failure_count = 0
        self._total_duration_ms = 0

        # Validator
        self._validator = PipelineValidator()

        # Add initial stages
        if stages:
            for stage in stages:
                self.add_stage(stage)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def pipeline_id(self) -> str:
        """Get pipeline ID."""
        return self._pipeline_id

    @property
    def name(self) -> str:
        """Get pipeline name."""
        return self._name

    @property
    def stages(self) -> list[PipelineStage]:
        """Get pipeline stages."""
        with self._lock:
            return list(self._stages)

    @property
    def state(self) -> PipelineState:
        """Get current state."""
        with self._lock:
            return self._state

    @property
    def policy(self) -> PipelinePolicy:
        """Get execution policy."""
        return self._policy

    @property
    def config(self) -> PipelineConfig:
        """Get pipeline configuration."""
        return self._config

    @property
    def is_running(self) -> bool:
        """Check if pipeline is running."""
        with self._lock:
            return self._state == PipelineState.RUNNING

    @property
    def stage_count(self) -> int:
        """Get number of stages."""
        with self._lock:
            return len(self._stages)

    @property
    def metadata(self) -> list[StageMetadata]:
        """Get metadata for all stages."""
        return [stage.metadata for stage in self._stages]

    @property
    def execution_count(self) -> int:
        """Get total execution count."""
        return self._execution_count

    @property
    def failure_count(self) -> int:
        """Get failure count."""
        return self._failure_count

    @property
    def average_duration_ms(self) -> float:
        """Get average execution duration."""
        if self._execution_count == 0:
            return 0.0
        return self._total_duration_ms / self._execution_count

    # =========================================================================
    # Observability
    # =========================================================================

    def set_event_publisher(self, publisher: PipelineEventPublisher) -> None:
        """Set the event publisher.

        Args:
            publisher: Event publisher instance.
        """
        self._event_publisher = publisher

    def set_metrics(self, metrics: PipelineMetrics) -> None:
        """Set the metrics collector.

        Args:
            metrics: Metrics collector instance.
        """
        self._metrics = metrics

    def set_trace(self, trace: PipelineTrace) -> None:
        """Set the trace collector.

        Args:
            trace: Trace collector instance.
        """
        self._trace = trace

    # =========================================================================
    # Stage Management
    # =========================================================================

    def add_stage(self, stage: PipelineStage) -> CognitivePipeline:
        """Add a stage to the pipeline.

        Args:
            stage: Stage to add.

        Returns:
            Self for chaining.

        Raises:
            DuplicateStageError: If stage name already exists.
        """
        with self._lock:
            # Check for duplicate
            if any(s.name == stage.name for s in self._stages):
                raise DuplicateStageError(stage.name)

            self._stages.append(stage)
            return self

    def remove_stage(self, stage_name: str) -> bool:
        """Remove a stage by name.

        Args:
            stage_name: Name of stage to remove.

        Returns:
            True if removed.
        """
        with self._lock:
            for i, stage in enumerate(self._stages):
                if stage.name == stage_name:
                    self._stages.pop(i)
                    return True
            return False

    def insert_stage(
        self,
        index: int,
        stage: PipelineStage,
    ) -> CognitivePipeline:
        """Insert a stage at a specific position.

        Args:
            index: Position to insert.
            stage: Stage to insert.

        Returns:
            Self for chaining.
        """
        with self._lock:
            if index < 0 or index > len(self._stages):
                index = len(self._stages)
            self._stages.insert(index, stage)
            return self

    def get_stage(self, stage_name: str) -> PipelineStage | None:
        """Get a stage by name.

        Args:
            stage_name: Stage name.

        Returns:
            Stage or None.
        """
        with self._lock:
            for stage in self._stages:
                if stage.name == stage_name:
                    return stage
            return None

    def clear_stages(self) -> CognitivePipeline:
        """Remove all stages.

        Returns:
            Self for chaining.
        """
        with self._lock:
            self._stages.clear()
            return self

    # =========================================================================
    # Execution
    # =========================================================================

    def validate(self) -> bool:
        """Validate the pipeline configuration.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If validation fails.
        """
        # Check for empty pipeline
        if not self._stages:
            raise EmptyPipelineError()

        # Run validator
        return self._validator.validate(self)

    def prepare(self) -> CognitivePipeline:
        """Prepare pipeline for execution.

        Returns:
            Self for chaining.

        Raises:
            PipelineValidationError: If validation fails.
        """
        with self._lock:
            if self._state != PipelineState.CREATED:
                raise PipelineStateError(
                    f"Cannot prepare from state: {self._state.value}",
                    self._state.value,
                    "prepare",
                )

            # Validate
            self.validate()

            # Reset stages
            for stage in self._stages:
                stage.reset()

            # Transition to READY
            self._state = PipelineState.READY
            return self

    def execute(
        self,
        intent: dict | None = None,
        session_id: str = "",
        correlation_id: str = "",
        **kwargs: Any,
    ) -> PipelineResult:
        """Execute the pipeline.

        Args:
            intent: Intent data.
            session_id: Session ID.
            correlation_id: Correlation ID.
            **kwargs: Additional context data.

        Returns:
            PipelineResult with execution outcome.

        Raises:
            PipelineStateError: If not in valid state.
            PipelineValidationError: If validation fails.
        """
        with self._lock:
            # Check state
            if self._state not in (PipelineState.READY, PipelineState.CREATED):
                raise PipelineStateError(
                    f"Cannot execute from state: {self._state.value}",
                    self._state.value,
                    "execute",
                )

            # Transition to RUNNING
            self._state = PipelineState.RUNNING

        # Create context
        context = PipelineContext(
            pipeline_id=self._pipeline_id,
            pipeline_name=self._name,
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:16]}",
            session_id=session_id,
            intent_type=kwargs.get("intent_type", ""),
            intent_data=kwargs.get("intent_data", intent or {}),
            runtime_id=kwargs.get("runtime_id", ""),
            user_id=kwargs.get("user_id", ""),
            hospital_id=kwargs.get("hospital_id", ""),
            metadata=kwargs,
        )

        # Publish event
        self._publish_event("PipelineStarted", context)

        # Create executor and run
        executor = PipelineExecutor(self, self._policy)
        result = executor.execute(context)

        # Update statistics
        with self._lock:
            self._execution_count += 1
            self._total_duration_ms += result.duration_ms

            if not result.is_success:
                self._failure_count += 1

            # Transition state
            self._state = result.status

        # Record metrics
        self._record_metrics(result)

        # Publish completion event
        self._publish_event("PipelineCompleted", context, result)

        return result

    def cancel(self, reason: str = "") -> bool:
        """Cancel pipeline execution.

        Args:
            reason: Cancellation reason.

        Returns:
            True if cancelled.
        """
        with self._lock:
            if not PipelineState.can_cancel(self._state):
                return False

            self._state = PipelineState.CANCELLED
            return True

    def pause(self) -> bool:
        """Pause pipeline execution.

        Returns:
            True if paused.
        """
        with self._lock:
            if not PipelineState.can_pause(self._state):
                return False

            self._state = PipelineState.PAUSED
            return True

    def resume(self) -> bool:
        """Resume pipeline execution.

        Returns:
            True if resumed.
        """
        with self._lock:
            if not PipelineState.can_resume(self._state):
                return False

            self._state = PipelineState.RUNNING
            return True

    # =========================================================================
    # Observability
    # =========================================================================

    def _publish_event(self, event_type: str, context: PipelineContext, result: PipelineResult | None = None) -> None:
        """Publish an event.

        Args:
            event_type: Type of event.
            context: Pipeline context.
            result: Optional result.
        """
        if self._event_publisher:
            self._event_publisher.publish(event_type, self, context, result)

    def _record_metrics(self, result: PipelineResult) -> None:
        """Record execution metrics.

        Args:
            result: Pipeline result.
        """
        if self._metrics:
            self._metrics.record_pipeline_execution(result)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def reset(self) -> None:
        """Reset pipeline to initial state."""
        with self._lock:
            self._state = PipelineState.CREATED
            for stage in self._stages:
                stage.reset()

    def to_dict(self) -> dict:
        """Convert pipeline to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "pipeline_id": self._pipeline_id,
            "name": self._name,
            "state": self._state.value,
            "stage_count": len(self._stages),
            "stages": [s.to_dict() for s in self._stages],
            "execution_count": self._execution_count,
            "failure_count": self._failure_count,
            "average_duration_ms": self.average_duration_ms,
            "config": self._config.to_dict(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CognitivePipeline("
            f"name={self._name!r}, "
            f"stages={len(self._stages)}, "
            f"state={self._state.value})"
        )
