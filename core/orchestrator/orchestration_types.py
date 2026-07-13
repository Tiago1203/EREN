"""Type definitions for the Cognitive Orchestrator.

Provides comprehensive type definitions for orchestration operations.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Session States
# =============================================================================


class OrchestrationState(str, Enum):
    """States of a cognitive orchestration session.

    These states represent the complete lifecycle of a cognitive session
    from creation to completion.
    """

    # Lifecycle states
    CREATED = "created"  # Session created, not started
    INITIALIZING = "initializing"  # Session initialization

    # Processing states
    PLANNING = "planning"  # Planning phase
    COLLECTING_EVIDENCE = "collecting_evidence"  # Evidence collection
    REASONING = "reasoning"  # Reasoning phase
    DECIDING = "deciding"  # Decision phase
    EXECUTING = "executing"  # Execution phase
    WAITING_EVENTS = "waiting_events"  # Waiting for events

    # State management
    UPDATING_CONTEXT = "updating_context"  # Context update

    # Completion states
    FINISHED = "finished"  # Successfully completed
    FAILED = "failed"  # Failed
    CANCELLED = "cancelled"  # Cancelled


# =============================================================================
# Session Types
# =============================================================================


class SessionType(str, Enum):
    """Types of orchestration sessions."""

    TROUBLESHOOTING = "troubleshooting"  # Device troubleshooting
    MAINTENANCE = "maintenance"  # Device maintenance
    COMPLIANCE = "compliance"  # Compliance check
    DIAGNOSTIC = "diagnostic"  # Diagnostic session
    CONSULTATION = "consultation"  # General consultation


# =============================================================================
# Protocols
# =============================================================================


class EventPublisher(Protocol):
    """Protocol for event publishing."""

    def publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish an event."""
        ...


class ContextManager(Protocol):
    """Protocol for context management."""

    def create_context(self, session_id: str) -> dict:
        """Create a new context."""
        ...

    def get_context(self, context_id: str) -> dict | None:
        """Get context by ID."""
        ...


class CapabilityRegistry(Protocol):
    """Protocol for capability registry."""

    def get_capabilities(self) -> list[dict]:
        """Get all registered capabilities."""
        ...


# =============================================================================
# Session Data
# =============================================================================


@dataclass(frozen=True)
class SessionMetadata:
    """Metadata for a cognitive session."""

    session_id: str
    correlation_id: str
    context_id: str
    session_type: SessionType = SessionType.TROUBLESHOOTING
    user_id: str = ""
    created_at: str = ""
    started_at: str = ""
    finished_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class StateTransition:
    """A state transition in the orchestration."""

    transition_id: str
    from_state: OrchestrationState
    to_state: OrchestrationState
    reason: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class TraceEntry:
    """A trace entry for audit trail."""

    entry_id: str
    timestamp: str
    from_state: OrchestrationState | None
    to_state: OrchestrationState
    reason: str
    correlation_id: str
    motor_active: str = ""
    events_count: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())


# =============================================================================
# Session Metrics
# =============================================================================


@dataclass
class SessionMetrics:
    """Metrics for a cognitive session."""

    duration_ms: int = 0
    events_processed: int = 0
    motors_used: int = 0
    decisions_taken: int = 0
    tools_executed: int = 0
    cognitive_iterations: int = 0
    context_updates: int = 0
    errors_count: int = 0
    warnings_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "duration_ms": self.duration_ms,
            "events_processed": self.events_processed,
            "motors_used": self.motors_used,
            "decisions_taken": self.decisions_taken,
            "tools_executed": self.tools_executed,
            "cognitive_iterations": self.cognitive_iterations,
            "context_updates": self.context_updates,
            "errors_count": self.errors_count,
            "warnings_count": self.warnings_count,
        }


# =============================================================================
# Cognitive Session
# =============================================================================


@dataclass
class CognitiveSession:
    """A complete cognitive orchestration session.

    Represents the full lifecycle of orchestrating cognitive engines
    through a complete processing cycle.
    """

    # Core identifiers
    metadata: SessionMetadata

    # State
    state: OrchestrationState = OrchestrationState.CREATED

    # History
    state_history: tuple[StateTransition, ...] = field(default_factory=tuple)
    trace_history: tuple[TraceEntry, ...] = field(default_factory=tuple)
    events_history: tuple[str, ...] = field(default_factory=tuple)

    # Metrics
    metrics: SessionMetrics = field(default_factory=SessionMetrics)

    # State management
    active_motor: str = ""
    active_phase: str = ""
    is_active: bool = False

    # Error handling
    last_error: str = ""
    error_count: int = 0

    def transition_to(
        self,
        new_state: OrchestrationState,
        reason: str = "",
    ) -> StateTransition:
        """Transition to a new state.

        Args:
            new_state: Target state.
            reason: Reason for transition.

        Returns:
            The state transition.
        """
        transition = StateTransition(
            transition_id=f"tr_{len(self.state_history)}",
            from_state=self.state,
            to_state=new_state,
            reason=reason,
        )

        self.state_history = self.state_history + (transition,)
        self.state = new_state

        return transition

    def add_trace_entry(
        self,
        to_state: OrchestrationState,
        reason: str,
        correlation_id: str,
    ) -> TraceEntry:
        """Add a trace entry.

        Args:
            to_state: Target state.
            reason: Reason for entry.
            correlation_id: Correlation ID.

        Returns:
            The trace entry.
        """
        entry = TraceEntry(
            entry_id=f"trace_{len(self.trace_history)}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            from_state=self.state,
            to_state=to_state,
            reason=reason,
            correlation_id=correlation_id,
            motor_active=self.active_motor,
            events_count=self.metrics.events_processed,
        )

        self.trace_history = self.trace_history + (entry,)

        return entry

    def record_event(self, event_type: str) -> None:
        """Record an event.

        Args:
            event_type: Type of event.
        """
        self.events_history = self.events_history + (event_type,)
        self.metrics.events_processed += 1

    def record_error(self, error: str) -> None:
        """Record an error.

        Args:
            error: Error message.
        """
        self.last_error = error
        self.error_count += 1
        self.metrics.errors_count += 1

    def finish(self) -> None:
        """Mark session as finished."""
        from dataclasses import replace

        self.metadata = replace(
            self.metadata,
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        self.is_active = False

    def fail(self, reason: str) -> None:
        """Mark session as failed.

        Args:
            reason: Failure reason.
        """
        from dataclasses import replace

        self.last_error = reason
        self.state = OrchestrationState.FAILED
        self.metadata = replace(
            self.metadata,
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        self.is_active = False

    def cancel(self, reason: str) -> None:
        """Cancel the session.

        Args:
            reason: Cancellation reason.
        """
        from dataclasses import replace

        self.last_error = reason
        self.state = OrchestrationState.CANCELLED
        self.metadata = replace(
            self.metadata,
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        self.is_active = False


# =============================================================================
# Policies
# =============================================================================


@dataclass(frozen=True)
class OrchestrationPolicy:
    """Policy for orchestration behavior."""

    # Timeout policy
    session_timeout_ms: int = 300000  # 5 minutes
    phase_timeout_ms: int = 60000  # 1 minute
    event_timeout_ms: int = 30000  # 30 seconds

    # Retry policy
    max_retries: int = 3
    retry_delay_ms: int = 1000

    # Iteration limits
    max_iterations: int = 10
    max_context_updates: int = 100

    # Feature flags
    enable_parallel_execution: bool = False
    enable_context_caching: bool = True
    enable_metrics: bool = True


# =============================================================================
# Constants
# =============================================================================


# Valid state transitions
VALID_TRANSITIONS: dict[OrchestrationState, tuple[OrchestrationState, ...]] = {
    OrchestrationState.CREATED: (
        OrchestrationState.INITIALIZING,
    ),
    OrchestrationState.INITIALIZING: (
        OrchestrationState.PLANNING,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.PLANNING: (
        OrchestrationState.COLLECTING_EVIDENCE,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.COLLECTING_EVIDENCE: (
        OrchestrationState.REASONING,
        OrchestrationState.PLANNING,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.REASONING: (
        OrchestrationState.DECIDING,
        OrchestrationState.COLLECTING_EVIDENCE,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.DECIDING: (
        OrchestrationState.EXECUTING,
        OrchestrationState.REASONING,
        OrchestrationState.WAITING_EVENTS,
        OrchestrationState.FINISHED,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.EXECUTING: (
        OrchestrationState.WAITING_EVENTS,
        OrchestrationState.UPDATING_CONTEXT,
        OrchestrationState.DECIDING,
        OrchestrationState.FINISHED,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.WAITING_EVENTS: (
        OrchestrationState.UPDATING_CONTEXT,
        OrchestrationState.DECIDING,
        OrchestrationState.FINISHED,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.UPDATING_CONTEXT: (
        OrchestrationState.PLANNING,
        OrchestrationState.COLLECTING_EVIDENCE,
        OrchestrationState.REASONING,
        OrchestrationState.DECIDING,
        OrchestrationState.EXECUTING,
        OrchestrationState.FINISHED,
        OrchestrationState.FAILED,
        OrchestrationState.CANCELLED,
    ),
    OrchestrationState.FINISHED: (),
    OrchestrationState.FAILED: (),
    OrchestrationState.CANCELLED: (),
}
