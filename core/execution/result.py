"""Execution Result for EREN OS Cognitive Execution Coordinator.

Represents the result of a complete cognitive execution cycle.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.execution.types import ExecutionState

if TYPE_CHECKING:
    pass


@dataclass
class ExecutionResult:
    """Result of a complete cognitive execution cycle.

    Contains all information about the execution including:
    - Execution identity
    - Session information
    - Timing information
    - Routing result
    - Pipeline result
    - Context updates
    - Errors and warnings
    - Events and traces
    """

    # Identity
    execution_id: str = ""
    session_id: str = ""

    # Status
    status: ExecutionState = ExecutionState.CREATED
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    duration_ms: int = 0

    # Sub-results
    routing_result: dict | None = None
    pipeline_result: dict | None = None
    lifecycle_result: dict | None = None
    context_updates: dict = field(default_factory=dict)

    # Timing breakdown
    session_creation_time_ms: int = 0
    routing_time_ms: int = 0
    pipeline_time_ms: int = 0
    context_update_time_ms: int = 0
    session_completion_time_ms: int = 0

    # Selected pipeline
    selected_pipeline: str = ""
    policy_used: str = ""

    # Errors and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Events and trace
    events: list[dict] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        if self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        with self._lock:
            return self.status == ExecutionState.COMPLETED

    @property
    def is_failure(self) -> bool:
        """Check if execution failed."""
        with self._lock:
            return self.status == ExecutionState.FAILED

    @property
    def was_cancelled(self) -> bool:
        """Check if execution was cancelled."""
        with self._lock:
            return self.status == ExecutionState.CANCELLED

    @property
    def total_cycle_time_ms(self) -> int:
        """Get total cycle time in milliseconds."""
        with self._lock:
            return (
                self.session_creation_time_ms +
                self.routing_time_ms +
                self.pipeline_time_ms +
                self.context_update_time_ms +
                self.session_completion_time_ms
            )

    @property
    def has_errors(self) -> bool:
        """Check if execution has errors."""
        with self._lock:
            return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if execution has warnings."""
        with self._lock:
            return len(self.warnings) > 0

    # =========================================================================
    # State Management
    # =========================================================================

    def set_status(self, status: ExecutionState) -> None:
        """Set execution status.

        Args:
            status: New status.
        """
        with self._lock:
            self.status = status

    def complete(self) -> None:
        """Mark execution as completed."""
        with self._lock:
            self.finished_at = datetime.now(timezone.utc)
            if self.started_at:
                self.duration_ms = int(
                    (self.finished_at - self.started_at).total_seconds() * 1000
                )
            self.status = ExecutionState.COMPLETED

    def fail(self, error: str | None = None) -> None:
        """Mark execution as failed.

        Args:
            error: Optional error message.
        """
        with self._lock:
            self.finished_at = datetime.now(timezone.utc)
            if self.started_at:
                self.duration_ms = int(
                    (self.finished_at - self.started_at).total_seconds() * 1000
                )
            if error:
                self.errors.append(error)
            self.status = ExecutionState.FAILED

    def cancel(self) -> None:
        """Mark execution as cancelled."""
        with self._lock:
            self.finished_at = datetime.now(timezone.utc)
            if self.started_at:
                self.duration_ms = int(
                    (self.finished_at - self.started_at).total_seconds() * 1000
                )
            self.status = ExecutionState.CANCELLED

    # =========================================================================
    # Sub-results
    # =========================================================================

    def set_routing_result(self, result: dict) -> None:
        """Set routing result.

        Args:
            result: Routing result dict.
        """
        with self._lock:
            self.routing_result = result
            if result:
                self.routing_time_ms = result.get("duration_ms", 0)
                if "selected_pipeline" in result:
                    self.selected_pipeline = result["selected_pipeline"]
                if "policy_used" in result:
                    self.policy_used = result["policy_used"]

    def set_pipeline_result(self, result: dict) -> None:
        """Set pipeline result.

        Args:
            result: Pipeline result dict.
        """
        with self._lock:
            self.pipeline_result = result
            if result:
                self.pipeline_time_ms = result.get("duration_ms", 0)

    def set_lifecycle_result(self, result: dict) -> None:
        """Set lifecycle result.

        Args:
            result: Lifecycle result dict.
        """
        with self._lock:
            self.lifecycle_result = result

    def add_context_update(self, key: str, value: Any) -> None:
        """Add a context update.

        Args:
            key: Update key.
            value: Update value.
        """
        with self._lock:
            self.context_updates[key] = value

    # =========================================================================
    # Errors and Warnings
    # =========================================================================

    def add_error(self, error: str) -> None:
        """Add an error.

        Args:
            error: Error message.
        """
        with self._lock:
            self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning.

        Args:
            warning: Warning message.
        """
        with self._lock:
            self.warnings.append(warning)

    # =========================================================================
    # Events and Trace
    # =========================================================================

    def add_event(self, event_type: str, data: dict | None = None) -> None:
        """Add an event.

        Args:
            event_type: Event type.
            data: Event data.
        """
        with self._lock:
            self.events.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "data": data or {},
            })

    def add_trace_entry(self, operation: str, details: dict | None = None) -> None:
        """Add a trace entry.

        Args:
            operation: Operation name.
            details: Operation details.
        """
        with self._lock:
            self.trace.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation,
                "details": details or {},
            })

    # =========================================================================
    # Utility
    # =========================================================================

    def get_summary(self) -> str:
        """Get a formatted summary.

        Returns:
            Summary string.
        """
        with self._lock:
            lines = [
                "=" * 50,
                "EREN OS EXECUTION RESULT",
                "=" * 50,
                f"Execution ID: {self.execution_id}",
                f"Session ID: {self.session_id}",
                f"Status: {self.status.value}",
                f"Duration: {self.duration_ms}ms",
                f"Selected Pipeline: {self.selected_pipeline}",
                "",
                "Timing:",
                f"  Session Creation: {self.session_creation_time_ms}ms",
                f"  Routing: {self.routing_time_ms}ms",
                f"  Pipeline: {self.pipeline_time_ms}ms",
                f"  Context Update: {self.context_update_time_ms}ms",
                f"  Session Completion: {self.session_completion_time_ms}ms",
            ]

            if self.errors:
                lines.append("")
                lines.append(f"Errors ({len(self.errors)}):")
                for error in self.errors[:3]:
                    lines.append(f"  - {error}")

            if self.warnings:
                lines.append("")
                lines.append(f"Warnings ({len(self.warnings)}):")
                for warning in self.warnings[:3]:
                    lines.append(f"  - {warning}")

            lines.append("=" * 50)
            return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "execution_id": self.execution_id,
                "session_id": self.session_id,
                "status": self.status.value,
                "started_at": self.started_at.isoformat(),
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "duration_ms": self.duration_ms,
                "routing_result": self.routing_result,
                "pipeline_result": self.pipeline_result,
                "lifecycle_result": self.lifecycle_result,
                "context_updates": dict(self.context_updates),
                "session_creation_time_ms": self.session_creation_time_ms,
                "routing_time_ms": self.routing_time_ms,
                "pipeline_time_ms": self.pipeline_time_ms,
                "context_update_time_ms": self.context_update_time_ms,
                "session_completion_time_ms": self.session_completion_time_ms,
                "selected_pipeline": self.selected_pipeline,
                "policy_used": self.policy_used,
                "errors": list(self.errors),
                "warnings": list(self.warnings),
                "events": list(self.events),
                "trace": list(self.trace),
                "metadata": dict(self.metadata),
            }
