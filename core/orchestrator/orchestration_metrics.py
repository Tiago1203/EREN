"""Metrics for the Cognitive Orchestrator.

Collects and calculates orchestration metrics.

Architecture only -- no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Metrics Collector
# =============================================================================


@dataclass
class OrchestrationMetricsCollector:
    """Collects orchestration metrics."""

    # Session metrics
    sessions_created: int = 0
    sessions_completed: int = 0
    sessions_failed: int = 0
    sessions_cancelled: int = 0

    # State transition metrics
    state_transitions: int = 0
    transitions_by_state: dict[str, int] = field(default_factory=dict)

    # Event metrics
    events_published: int = 0
    events_by_type: dict[str, int] = field(default_factory=dict)

    # Motor metrics
    motors_coordinated: int = 0
    motor_usage: dict[str, int] = field(default_factory=dict)

    # Performance metrics
    average_duration_ms: float = 0.0
    total_duration_ms: int = 0

    # Error metrics
    errors_count: int = 0
    timeouts_count: int = 0

    def record_session_created(self) -> None:
        """Record a session creation."""
        self.sessions_created += 1

    def record_session_completed(self, duration_ms: int) -> None:
        """Record a session completion.

        Args:
            duration_ms: Session duration.
        """
        self.sessions_completed += 1
        self.total_duration_ms += duration_ms

        if self.sessions_completed > 0:
            self.average_duration_ms = (
                self.total_duration_ms / self.sessions_completed
            )

    def record_session_failed(self) -> None:
        """Record a session failure."""
        self.sessions_failed += 1

    def record_session_cancelled(self) -> None:
        """Record a session cancellation."""
        self.sessions_cancelled += 1

    def record_state_transition(self, from_state: str, to_state: str) -> None:
        """Record a state transition.

        Args:
            from_state: Previous state.
            to_state: New state.
        """
        self.state_transitions += 1
        self.transitions_by_state[to_state] = (
            self.transitions_by_state.get(to_state, 0) + 1
        )

    def record_event_published(self, event_type: str) -> None:
        """Record an event publication.

        Args:
            event_type: Type of event.
        """
        self.events_published += 1
        self.events_by_type[event_type] = (
            self.events_by_type.get(event_type, 0) + 1
        )

    def record_motor_coordinated(self, motor_id: str) -> None:
        """Record motor coordination.

        Args:
            motor_id: Motor ID.
        """
        self.motors_coordinated += 1
        self.motor_usage[motor_id] = self.motor_usage.get(motor_id, 0) + 1

    def record_error(self) -> None:
        """Record an error."""
        self.errors_count += 1

    def record_timeout(self) -> None:
        """Record a timeout."""
        self.timeouts_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Metrics as dictionary.
        """
        return {
            "sessions_created": self.sessions_created,
            "sessions_completed": self.sessions_completed,
            "sessions_failed": self.sessions_failed,
            "sessions_cancelled": self.sessions_cancelled,
            "state_transitions": self.state_transitions,
            "events_published": self.events_published,
            "motors_coordinated": self.motors_coordinated,
            "average_duration_ms": self.average_duration_ms,
            "errors_count": self.errors_count,
            "timeouts_count": self.timeouts_count,
        }


# =============================================================================
# Health Check
# =============================================================================


@dataclass
class OrchestrationHealthCheck:
    """Health check for the orchestrator."""

    is_healthy: bool = True
    active_sessions: int = 0
    completed_sessions: int = 0
    failed_sessions: int = 0
    error_rate: float = 0.0
    average_duration_ms: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(timezone.utc).isoformat())
