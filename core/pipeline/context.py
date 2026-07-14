"""Pipeline Context for EREN OS Cognitive Capability Pipeline.

Provides the shared context that flows through all pipeline stages.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class PipelineContext:
    """Shared context passed through pipeline stages.

    This context flows through all stages of the pipeline, carrying:
    - The original intent
    - Session and runtime information
    - Shared data between stages
    - Stage results
    - Metadata

    Thread-safe for concurrent access.
    """

    # Core identifiers
    pipeline_id: str = ""
    pipeline_name: str = ""
    correlation_id: str = ""
    session_id: str = ""

    # Intent information
    intent_type: str = ""
    intent_data: dict = field(default_factory=dict)

    # Runtime information
    runtime_id: str = ""
    runtime_version: str = ""

    # Session information
    user_id: str = ""
    hospital_id: str = ""
    tenant_id: str = ""

    # Shared data (key-value store for stage communication)
    shared_data: dict = field(default_factory=dict)

    # Stage results (stage_name -> StageResult)
    stage_results: dict = field(default_factory=dict)

    # Current stage
    current_stage: str = ""
    current_stage_index: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None

    # Execution state
    is_cancelled: bool = False
    is_paused: bool = False
    cancellation_reason: str = ""

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock if not provided."""
        if self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # Shared Data Operations
    # =========================================================================

    def set(self, key: str, value: Any) -> None:
        """Set a value in the shared context.

        Args:
            key: The key to set.
            value: The value to store.
        """
        with self._lock:
            self.shared_data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the shared context.

        Args:
            key: The key to retrieve.
            default: Default value if key not found.

        Returns:
            The stored value or default.
        """
        with self._lock:
            return self.shared_data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a key exists in shared context.

        Args:
            key: The key to check.

        Returns:
            True if key exists.
        """
        with self._lock:
            return key in self.shared_data

    def delete(self, key: str) -> bool:
        """Delete a key from shared context.

        Args:
            key: The key to delete.

        Returns:
            True if key was deleted.
        """
        with self._lock:
            if key in self.shared_data:
                del self.shared_data[key]
                return True
            return False

    def get_stage_result(self, stage_name: str) -> dict | None:
        """Get the result of a specific stage.

        Args:
            stage_name: Name of the stage.

        Returns:
            Stage result dict or None.
        """
        with self._lock:
            result = self.stage_results.get(stage_name)
            return result.to_dict() if result else None

    def add_stage_result(self, stage_name: str, result: StageResult) -> None:
        """Add a stage result to the context.

        Args:
            stage_name: Name of the stage.
            result: The stage result.
        """
        with self._lock:
            self.stage_results[stage_name] = result

    def get_all_stage_results(self) -> list[dict]:
        """Get all stage results.

        Returns:
            List of stage result dicts.
        """
        with self._lock:
            return [r.to_dict() for r in self.stage_results.values()]

    def get_successful_stages(self) -> list[str]:
        """Get names of all successful stages.

        Returns:
            List of stage names.
        """
        with self._lock:
            return [
                name for name, result in self.stage_results.items()
                if result.is_success
            ]

    # =========================================================================
    # Execution Control
    # =========================================================================

    def start(self) -> None:
        """Mark the pipeline context as started."""
        with self._lock:
            self.started_at = datetime.now(UTC)

    def finish(self) -> None:
        """Mark the pipeline context as finished."""
        with self._lock:
            self.finished_at = datetime.now(UTC)

    def request_cancellation(self, reason: str = "") -> None:
        """Request pipeline cancellation.

        Args:
            reason: Reason for cancellation.
        """
        with self._lock:
            self.is_cancelled = True
            self.cancellation_reason = reason

    def pause(self) -> None:
        """Mark the context as paused."""
        with self._lock:
            self.is_paused = True

    def resume(self) -> None:
        """Mark the context as resumed."""
        with self._lock:
            self.is_paused = False

    def is_cancellation_requested(self) -> bool:
        """Check if cancellation was requested.

        Returns:
            True if cancellation was requested.
        """
        with self._lock:
            return self.is_cancelled

    def is_paused_state(self) -> bool:
        """Check if context is paused.

        Returns:
            True if paused.
        """
        with self._lock:
            return self.is_paused

    # =========================================================================
    # Metadata Operations
    # =========================================================================

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        with self._lock:
            self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata.

        Args:
            key: Metadata key.
            default: Default value.

        Returns:
            Metadata value or default.
        """
        with self._lock:
            return self.metadata.get(key, default)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_duration_ms(self) -> int:
        """Calculate pipeline duration in milliseconds.

        Returns:
            Duration in ms, or 0 if not started/finished.
        """
        with self._lock:
            if not self.started_at:
                return 0
            end = self.finished_at or datetime.now(UTC)
            return int((end - self.started_at).total_seconds() * 1000)

    def get_stage_count(self) -> int:
        """Get total number of stages executed.

        Returns:
            Number of stages.
        """
        with self._lock:
            return len(self.stage_results)

    def get_success_rate(self) -> float:
        """Calculate success rate of executed stages.

        Returns:
            Success rate as percentage (0-100).
        """
        with self._lock:
            if not self.stage_results:
                return 0.0
            successful = sum(1 for r in self.stage_results.values() if r.is_success)
            return successful / len(self.stage_results) * 100

    def to_dict(self) -> dict:
        """Convert context to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "pipeline_id": self.pipeline_id,
                "pipeline_name": self.pipeline_name,
                "correlation_id": self.correlation_id,
                "session_id": self.session_id,
                "intent_type": self.intent_type,
                "intent_data": self.intent_data,
                "runtime_id": self.runtime_id,
                "runtime_version": self.runtime_version,
                "user_id": self.user_id,
                "hospital_id": self.hospital_id,
                "tenant_id": self.tenant_id,
                "shared_data": dict(self.shared_data),
                "stage_results": self.get_all_stage_results(),
                "current_stage": self.current_stage,
                "current_stage_index": self.current_stage_index,
                "created_at": self.created_at.isoformat(),
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "is_cancelled": self.is_cancelled,
                "is_paused": self.is_paused,
                "cancellation_reason": self.cancellation_reason,
                "metadata": dict(self.metadata),
                "duration_ms": self.get_duration_ms(),
                "stage_count": len(self.stage_results),
                "success_rate": self.get_success_rate(),
            }

    def copy(self) -> PipelineContext:
        """Create a deep copy of the context.

        Returns:
            New PipelineContext with copied data.
        """
        with self._lock:
            new_context = PipelineContext(
                pipeline_id=self.pipeline_id,
                pipeline_name=self.pipeline_name,
                correlation_id=self.correlation_id,
                session_id=self.session_id,
                intent_type=self.intent_type,
                intent_data=dict(self.intent_data),
                runtime_id=self.runtime_id,
                runtime_version=self.runtime_version,
                user_id=self.user_id,
                hospital_id=self.hospital_id,
                tenant_id=self.tenant_id,
                shared_data=dict(self.shared_data),
                stage_results=dict(self.stage_results),
                current_stage=self.current_stage,
                current_stage_index=self.current_stage_index,
                started_at=self.started_at,
                finished_at=self.finished_at,
                is_cancelled=self.is_cancelled,
                is_paused=self.is_paused,
                cancellation_reason=self.cancellation_reason,
                metadata=dict(self.metadata),
            )
            return new_context
