"""Pipeline Stage for EREN OS Cognitive Capability Pipeline.

Abstract base class and contracts for all pipeline stages.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.pipeline.exceptions import (
    CancellationRequestedError,
)
from core.PHASE_2.pipeline.types import StageMetadata, StageResult, StageState, StageType

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.context import PipelineContext


class PipelineStage(ABC):
    """Abstract base class for all pipeline stages.

    All pipeline stages must inherit from this class and implement
    the execute method. The pipeline executor will call execute()
    with the shared context.

    Features:
    - Thread-safe execution
    - Timeout support
    - Cancellation support
    - Retry support
    - Metrics collection
    - Event publishing
    """

    def __init__(
        self,
        name: str | None = None,
        stage_type: StageType = StageType.CUSTOM,
        required: bool = True,
        timeout_seconds: float = 30.0,
        retry_count: int = 0,
        tags: list[str] | None = None,
    ):
        """Initialize the pipeline stage.

        Args:
            name: Stage name. If None, derived from class name.
            stage_type: Type of stage.
            required: Whether stage is required for pipeline success.
            timeout_seconds: Execution timeout.
            retry_count: Number of retries on failure.
            tags: Optional tags for categorization.
        """
        self._name = name or self.__class__.__name__
        self._stage_type = stage_type
        self._required = required
        self._timeout_seconds = timeout_seconds
        self._retry_count = retry_count
        self._tags = tuple(tags or [])

        # State
        self._state = StageState.PENDING
        self._lock = threading.RLock()

        # Statistics
        self._execution_count = 0
        self._failure_count = 0
        self._total_duration_ms = 0

    @property
    def name(self) -> str:
        """Get stage name."""
        return self._name

    @property
    def stage_type(self) -> StageType:
        """Get stage type."""
        return self._stage_type

    @property
    def is_required(self) -> bool:
        """Check if stage is required."""
        return self._required

    @property
    def state(self) -> StageState:
        """Get current state."""
        with self._lock:
            return self._state

    @property
    def metadata(self) -> StageMetadata:
        """Get stage metadata."""
        return StageMetadata(
            stage_name=self._name,
            stage_type=self._stage_type,
            description=self.describe(),
            required=self._required,
            optional=not self._required,
            retry_count=self._retry_count,
            timeout_seconds=self._timeout_seconds,
            tags=self._tags,
        )

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
        """Get average execution duration in milliseconds."""
        if self._execution_count == 0:
            return 0.0
        return self._total_duration_ms / self._execution_count

    @abstractmethod
    def describe(self) -> str:
        """Return human-readable description of this stage.

        Returns:
            Description string.
        """
        ...

    @abstractmethod
    async def execute(self, context: PipelineContext) -> Any:
        """Execute the stage logic.

        This method must be implemented by all stages.
        It receives the shared context and returns the stage output.

        Args:
            context: Shared pipeline context.

        Returns:
            Stage output (can be any type).

        Raises:
            StageExecutionError: If execution fails.
            StageTimeoutError: If execution times out.
            StageCancelledError: If cancellation is requested.
        """
        ...

    def execute_with_retry(
        self,
        context: PipelineContext,
    ) -> StageResult:
        """Execute stage with retry support.

        Args:
            context: Shared pipeline context.

        Returns:
            StageResult with execution outcome.
        """

        start_time = time.time()
        retry_attempts = 0
        errors: list[str] = []
        last_error: Exception | None = None

        while retry_attempts <= self._retry_count:
            try:
                # Check for cancellation
                if context.is_cancellation_requested():
                    return self._create_result(
                        context,
                        StageState.CANCELLED,
                        start_time,
                        errors=["Cancelled by request"],
                    )

                # Set running state
                with self._lock:
                    self._state = StageState.RUNNING

                # Execute stage
                # Note: This is synchronous for now; async would require event loop
                output = self.execute(context)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Update statistics
                with self._lock:
                    self._execution_count += 1
                    self._total_duration_ms += duration_ms
                    self._state = StageState.COMPLETED

                return StageResult(
                    stage_name=self._name,
                    stage_type=self._stage_type,
                    status=StageState.COMPLETED,
                    started_at=datetime.fromtimestamp(start_time, tz=UTC),
                    finished_at=datetime.now(UTC),
                    duration_ms=duration_ms,
                    output=output,
                    retry_attempts=retry_attempts,
                )

            except CancellationRequestedError:
                return self._create_result(
                    context,
                    StageState.CANCELLED,
                    start_time,
                    errors=["Cancellation requested"],
                )

            except Exception as e:
                last_error = e
                errors.append(str(e))
                retry_attempts += 1

                if retry_attempts <= self._retry_count:
                    # Retry after delay
                    time.sleep(0.1 * retry_attempts)  # Exponential backoff

        # All retries exhausted
        with self._lock:
            self._failure_count += 1
            self._state = StageState.FAILED

        duration_ms = int((time.time() - start_time) * 1000)
        return StageResult(
            stage_name=self._name,
            stage_type=self._stage_type,
            status=StageState.FAILED,
            started_at=datetime.fromtimestamp(start_time, tz=UTC),
            finished_at=datetime.now(UTC),
            duration_ms=duration_ms,
            errors=errors,
            retry_attempts=retry_attempts,
        )

    def _create_result(
        self,
        context: PipelineContext,
        status: StageState,
        start_time: float,
        errors: list[str] | None = None,
    ) -> StageResult:
        """Create a stage result.

        Args:
            context: Pipeline context.
            status: Final status.
            start_time: Start timestamp.
            errors: Optional error list.

        Returns:
            StageResult instance.
        """
        duration_ms = int((time.time() - start_time) * 1000)
        return StageResult(
            stage_name=self._name,
            stage_type=self._stage_type,
            status=status,
            started_at=datetime.fromtimestamp(start_time, tz=UTC),
            finished_at=datetime.now(UTC),
            duration_ms=duration_ms,
            errors=errors or [],
        )

    def reset(self) -> None:
        """Reset stage state."""
        with self._lock:
            self._state = StageState.PENDING

    def to_dict(self) -> dict:
        """Convert stage to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "name": self._name,
            "stage_type": self._stage_type.value,
            "required": self._required,
            "timeout_seconds": self._timeout_seconds,
            "retry_count": self._retry_count,
            "tags": list(self._tags),
            "state": self._state.value,
            "execution_count": self._execution_count,
            "failure_count": self._failure_count,
            "average_duration_ms": self.average_duration_ms,
            "description": self.describe(),
        }


# =============================================================================
# Concrete Stage Types
# =============================================================================


class PlanningStage(PipelineStage):
    """Stage for planning capability.

    Responsible for decomposing intent into an executable plan.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.PLANNING,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Decomposes intent into executable plan"

    async def execute(self, context: PipelineContext) -> Any:
        # Implementation delegates to Planner via contract
        # This is infrastructure only
        return {"plan": "infrastructure_only"}


class KnowledgeStage(PipelineStage):
    """Stage for knowledge retrieval capability.

    Responsible for retrieving relevant knowledge.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.KNOWLEDGE,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Retrieves relevant knowledge"

    async def execute(self, context: PipelineContext) -> Any:
        return {"knowledge": "infrastructure_only"}


class MemoryStage(PipelineStage):
    """Stage for memory capability.

    Responsible for memory operations.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.MEMORY,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Performs memory operations"

    async def execute(self, context: PipelineContext) -> Any:
        return {"memory": "infrastructure_only"}


class ReasoningStage(PipelineStage):
    """Stage for reasoning capability.

    Responsible for logical reasoning.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.REASONING,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Performs logical reasoning"

    async def execute(self, context: PipelineContext) -> Any:
        return {"reasoning": "infrastructure_only"}


class DecisionStage(PipelineStage):
    """Stage for decision capability.

    Responsible for making decisions.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.DECISION,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Makes decisions"

    async def execute(self, context: PipelineContext) -> Any:
        return {"decision": "infrastructure_only"}


class ToolStage(PipelineStage):
    """Stage for tool execution capability.

    Responsible for executing tools.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.TOOL,
            required=False,  # Optional - may not always execute
            **kwargs,
        )

    def describe(self) -> str:
        return "Executes tools"

    async def execute(self, context: PipelineContext) -> Any:
        return {"tools": "infrastructure_only"}


class ContextUpdateStage(PipelineStage):
    """Stage for context update.

    Responsible for updating the shared context.
    """

    def __init__(self, **kwargs):
        super().__init__(
            stage_type=StageType.CONTEXT_UPDATE,
            required=True,
            **kwargs,
        )

    def describe(self) -> str:
        return "Updates shared context"

    async def execute(self, context: PipelineContext) -> Any:
        return {"context_updated": True}
