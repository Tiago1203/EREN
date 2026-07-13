"""Engine result definitions for orchestration.

Standard result format for all cognitive engines.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Result Status
# =============================================================================


class ResultStatus(str, Enum):
    """Status of an engine result."""

    SUCCESS = "success"  # Successfully completed
    PARTIAL = "partial"  # Partially completed
    FAILED = "failed"  # Failed
    SKIPPED = "skipped"  # Skipped
    PENDING = "pending"  # Not yet executed


# =============================================================================
# Result Type
# =============================================================================


class ResultType(str, Enum):
    """Types of engine results."""

    # Cognitive results
    HYPOTHESIS = "hypothesis"  # Reasoning result
    DECISION = "decision"  # Decision result
    KNOWLEDGE = "knowledge"  # Knowledge result
    MEMORY = "memory"  # Memory result

    # Action results
    ACTION = "action"  # Action result
    TOOL_RESULT = "tool_result"  # Tool execution result
    WORKFLOW = "workflow"  # Workflow result

    # Meta results
    PLAN = "plan"  # Planning result
    CONTEXT = "context"  # Context update
    EVENT = "event"  # Event data


# =============================================================================
# Engine Result
# =============================================================================


@dataclass(frozen=True)
class EngineResult:
    """Standard result from a cognitive engine.

    All engines return results in this format for
    consistent orchestration.
    """

    result_id: str
    engine_id: str
    engine_type: str
    status: ResultStatus
    result_type: ResultType
    data: dict = field(default_factory=dict)
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)
    execution_time_ms: int = 0
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())

    @property
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.status == ResultStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return self.status == ResultStatus.FAILED

    @property
    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0

    def merge(self, other: EngineResult) -> EngineResult:
        """Merge two results.

        Args:
            other: Another result to merge.

        Returns:
            Merged result.
        """
        from dataclasses import replace

        return replace(
            self,
            data={**self.data, **other.data},
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            metadata={**self.metadata, **other.metadata},
        )


# =============================================================================
# Result Factory
# =============================================================================


class ResultFactory:
    """Factory for creating engine results."""

    @staticmethod
    def success(
        result_id: str,
        engine_id: str,
        engine_type: str,
        result_type: ResultType,
        data: dict | None = None,
        **kwargs: Any,
    ) -> EngineResult:
        """Create a success result.

        Args:
            result_id: Unique result ID.
            engine_id: Engine ID.
            engine_type: Engine type.
            result_type: Result type.
            data: Result data.
            **kwargs: Additional metadata.

        Returns:
            Success result.
        """
        return EngineResult(
            result_id=result_id,
            engine_id=engine_id,
            engine_type=engine_type,
            status=ResultStatus.SUCCESS,
            result_type=result_type,
            data=data or {},
            metadata=kwargs,
        )

    @staticmethod
    def failure(
        result_id: str,
        engine_id: str,
        engine_type: str,
        error: str,
        result_type: ResultType = ResultType.ACTION,
    ) -> EngineResult:
        """Create a failure result.

        Args:
            result_id: Unique result ID.
            engine_id: Engine ID.
            engine_type: Engine type.
            error: Error message.
            result_type: Result type.

        Returns:
            Failure result.
        """
        return EngineResult(
            result_id=result_id,
            engine_id=engine_id,
            engine_type=engine_type,
            status=ResultStatus.FAILED,
            result_type=result_type,
            errors=(error,),
        )

    @staticmethod
    def partial(
        result_id: str,
        engine_id: str,
        engine_type: str,
        result_type: ResultType,
        data: dict | None = None,
        warnings: tuple[str, ...] = (),
    ) -> EngineResult:
        """Create a partial success result.

        Args:
            result_id: Unique result ID.
            engine_id: Engine ID.
            engine_type: Engine type.
            result_type: Result type.
            data: Result data.
            warnings: Warnings.

        Returns:
            Partial success result.
        """
        return EngineResult(
            result_id=result_id,
            engine_id=engine_id,
            engine_type=engine_type,
            status=ResultStatus.PARTIAL,
            result_type=result_type,
            data=data or {},
            warnings=warnings,
        )

    @staticmethod
    def skipped(
        result_id: str,
        engine_id: str,
        engine_type: str,
        reason: str,
        result_type: ResultType = ResultType.ACTION,
    ) -> EngineResult:
        """Create a skipped result.

        Args:
            result_id: Unique result ID.
            engine_id: Engine ID.
            engine_type: Engine type.
            reason: Skip reason.
            result_type: Result type.

        Returns:
            Skipped result.
        """
        return EngineResult(
            result_id=result_id,
            engine_id=engine_id,
            engine_type=engine_type,
            status=ResultStatus.SKIPPED,
            result_type=result_type,
            metadata={"skip_reason": reason},
        )
