"""Execution Context for EREN OS Cognitive Execution Coordinator.

Provides the complete context for cognitive execution cycles.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class ExecutionContext:
    """Complete context for a cognitive execution cycle.

    Contains all information needed throughout the execution lifecycle:
    - Runtime information
    - Session information
    - Lifecycle state
    - Routing and pipeline results
    - Scheduler context
    - Trace data
    """

    # Identity
    execution_id: str = ""
    session_id: str = ""
    correlation_id: str = ""

    # Intent
    intent_type: str = ""
    intent_data: dict = field(default_factory=dict)

    # User/Tenant
    user_id: str = ""
    tenant_id: str = ""
    hospital_id: str = ""

    # Priority
    priority: int = 0

    # Component references (set during initialization)
    runtime_id: str = ""
    lifecycle_id: str = ""
    scheduler_id: str = ""

    # Sub-results
    routing_context: dict = field(default_factory=dict)
    pipeline_context: dict = field(default_factory=dict)
    context_updates: dict = field(default_factory=dict)

    # State
    current_state: str = "created"
    previous_state: str = ""

    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None

    # Errors
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Trace
    trace_entries: list[dict] = field(default_factory=list)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        if self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # State Management
    # =========================================================================

    def transition_to(self, new_state: str) -> None:
        """Transition to a new state.

        Args:
            new_state: New state name.
        """
        with self._lock:
            self.previous_state = self.current_state
            self.current_state = new_state
            self._add_trace_entry("state_transition", {
                "from": self.previous_state,
                "to": new_state,
            })

    def start(self) -> None:
        """Mark execution as started."""
        with self._lock:
            self.started_at = datetime.now(UTC)
            self.transition_to("initializing")

    def finish(self) -> None:
        """Mark execution as finished."""
        with self._lock:
            self.finished_at = datetime.now(UTC)

    # =========================================================================
    # Data Operations
    # =========================================================================

    def set_routing_context(self, context: dict) -> None:
        """Set routing context.

        Args:
            context: Routing context dict.
        """
        with self._lock:
            self.routing_context = context

    def get_routing_context(self) -> dict:
        """Get routing context."""
        with self._lock:
            return dict(self.routing_context)

    def set_pipeline_context(self, context: dict) -> None:
        """Set pipeline context.

        Args:
            context: Pipeline context dict.
        """
        with self._lock:
            self.pipeline_context = context

    def get_pipeline_context(self) -> dict:
        """Get pipeline context."""
        with self._lock:
            return dict(self.pipeline_context)

    def add_context_update(self, key: str, value: Any) -> None:
        """Add a context update.

        Args:
            key: Update key.
            value: Update value.
        """
        with self._lock:
            self.context_updates[key] = value

    def get_context_updates(self) -> dict:
        """Get all context updates."""
        with self._lock:
            return dict(self.context_updates)

    # =========================================================================
    # Error Handling
    # =========================================================================

    def add_error(self, error: str) -> None:
        """Add an error.

        Args:
            error: Error message.
        """
        with self._lock:
            self.errors.append(error)
            self._add_trace_entry("error", {"message": error})

    def add_warning(self, warning: str) -> None:
        """Add a warning.

        Args:
            warning: Warning message.
        """
        with self._lock:
            self.warnings.append(warning)
            self._add_trace_entry("warning", {"message": warning})

    # =========================================================================
    # Trace
    # =========================================================================

    def _add_trace_entry(self, operation: str, details: dict | None = None) -> None:
        """Add a trace entry.

        Args:
            operation: Operation name.
            details: Operation details.
        """
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "operation": operation,
            "state": self.current_state,
            "details": details or {},
        }
        self.trace_entries.append(entry)

    def add_trace(self, operation: str, details: dict | None = None) -> None:
        """Add a trace entry (public method).

        Args:
            operation: Operation name.
            details: Operation details.
        """
        with self._lock:
            self._add_trace_entry(operation, details)

    # =========================================================================
    # Metadata
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
    # Timing
    # =========================================================================

    def get_duration_ms(self) -> int:
        """Calculate execution duration in milliseconds.

        Returns:
            Duration in ms.
        """
        with self._lock:
            if not self.started_at:
                return 0
            end = self.finished_at or datetime.now(UTC)
            return int((end - self.started_at).total_seconds() * 1000)

    def get_routing_duration_ms(self) -> int:
        """Get routing duration from context.

        Returns:
            Routing duration in ms.
        """
        with self._lock:
            return self.routing_context.get("duration_ms", 0)

    def get_pipeline_duration_ms(self) -> int:
        """Get pipeline duration from context.

        Returns:
            Pipeline duration in ms.
        """
        with self._lock:
            return self.pipeline_context.get("duration_ms", 0)

    # =========================================================================
    # Utility
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "execution_id": self.execution_id,
                "session_id": self.session_id,
                "correlation_id": self.correlation_id,
                "intent_type": self.intent_type,
                "intent_data": dict(self.intent_data),
                "user_id": self.user_id,
                "tenant_id": self.tenant_id,
                "hospital_id": self.hospital_id,
                "priority": self.priority,
                "runtime_id": self.runtime_id,
                "lifecycle_id": self.lifecycle_id,
                "scheduler_id": self.scheduler_id,
                "routing_context": dict(self.routing_context),
                "pipeline_context": dict(self.pipeline_context),
                "context_updates": dict(self.context_updates),
                "current_state": self.current_state,
                "previous_state": self.previous_state,
                "created_at": self.created_at.isoformat(),
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "duration_ms": self.get_duration_ms(),
                "errors": list(self.errors),
                "warnings": list(self.warnings),
                "trace_entries": list(self.trace_entries),
                "metadata": dict(self.metadata),
            }

    def copy(self) -> ExecutionContext:
        """Create a deep copy.

        Returns:
            New ExecutionContext with copied data.
        """
        with self._lock:
            return ExecutionContext(
                execution_id=self.execution_id,
                session_id=self.session_id,
                correlation_id=self.correlation_id,
                intent_type=self.intent_type,
                intent_data=dict(self.intent_data),
                user_id=self.user_id,
                tenant_id=self.tenant_id,
                hospital_id=self.hospital_id,
                priority=self.priority,
                runtime_id=self.runtime_id,
                lifecycle_id=self.lifecycle_id,
                scheduler_id=self.scheduler_id,
                routing_context=dict(self.routing_context),
                pipeline_context=dict(self.pipeline_context),
                context_updates=dict(self.context_updates),
                current_state=self.current_state,
                previous_state=self.previous_state,
                started_at=self.started_at,
                finished_at=self.finished_at,
                errors=list(self.errors),
                warnings=list(self.warnings),
                trace_entries=list(self.trace_entries),
                metadata=dict(self.metadata),
            )
