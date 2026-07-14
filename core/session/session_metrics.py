"""Session metrics for the Cognitive Session Manager.

Collects and calculates session metrics.

Architecture only -- no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class SessionMetricsCollector:
    """Collects session management metrics."""

    sessions_created: int = 0
    sessions_activated: int = 0
    sessions_completed: int = 0
    sessions_failed: int = 0
    sessions_cancelled: int = 0
    sessions_archived: int = 0
    sessions_deleted: int = 0
    sessions_paused: int = 0
    sessions_recovered: int = 0
    sessions_expired: int = 0

    active_sessions: int = 0
    peak_active_sessions: int = 0
    total_sessions: int = 0

    average_session_duration_ms: float = 0.0
    total_session_duration_ms: int = 0

    def record_session_created(self) -> None:
        """Record session creation."""
        self.sessions_created += 1
        self.total_sessions += 1

    def record_session_activated(self) -> None:
        """Record session activation."""
        self.sessions_activated += 1
        self.active_sessions += 1
        if self.active_sessions > self.peak_active_sessions:
            self.peak_active_sessions = self.active_sessions

    def record_session_completed(self, duration_ms: int) -> None:
        """Record session completion."""
        self.sessions_completed += 1
        self.active_sessions = max(0, self.active_sessions - 1)
        self.total_session_duration_ms += duration_ms

        if self.sessions_completed > 0:
            self.average_session_duration_ms = (
                self.total_session_duration_ms / self.sessions_completed
            )

    def record_session_failed(self) -> None:
        """Record session failure."""
        self.sessions_failed += 1
        self.active_sessions = max(0, self.active_sessions - 1)

    def record_session_cancelled(self) -> None:
        """Record session cancellation."""
        self.sessions_cancelled += 1
        self.active_sessions = max(0, self.active_sessions - 1)

    def record_session_archived(self) -> None:
        """Record session archival."""
        self.sessions_archived += 1

    def record_session_deleted(self) -> None:
        """Record session deletion."""
        self.sessions_deleted += 1

    def record_session_paused(self) -> None:
        """Record session pause."""
        self.sessions_paused += 1

    def record_session_recovered(self) -> None:
        """Record session recovery."""
        self.sessions_recovered += 1

    def record_session_expired(self) -> None:
        """Record session expiration."""
        self.sessions_expired += 1
        self.active_sessions = max(0, self.active_sessions - 1)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "sessions_created": self.sessions_created,
            "sessions_activated": self.sessions_activated,
            "sessions_completed": self.sessions_completed,
            "sessions_failed": self.sessions_failed,
            "sessions_cancelled": self.sessions_cancelled,
            "sessions_archived": self.sessions_archived,
            "sessions_deleted": self.sessions_deleted,
            "sessions_paused": self.sessions_paused,
            "sessions_recovered": self.sessions_recovered,
            "sessions_expired": self.sessions_expired,
            "active_sessions": self.active_sessions,
            "peak_active_sessions": self.peak_active_sessions,
            "total_sessions": self.total_sessions,
            "average_session_duration_ms": self.average_session_duration_ms,
        }


@dataclass
class SessionHealthCheck:
    """Health check for session management."""

    is_healthy: bool = True
    active_sessions: int = 0
    total_sessions: int = 0
    error_rate: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(UTC).isoformat())
