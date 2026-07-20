"""Session events for the Cognitive Session Manager.

Defines all session events.

Architecture only -- no implementations.
"""

from __future__ import annotations

from enum import Enum


class SessionEventType(str, Enum):
    """Types of session events."""

    SESSION_CREATED = "SessionCreated"
    SESSION_ACTIVATED = "SessionActivated"
    SESSION_DEACTIVATED = "SessionDeactivated"
    SESSION_PAUSED = "SessionPaused"
    SESSION_RESUMED = "SessionResumed"
    SESSION_WAITING = "SessionWaiting"
    SESSION_RECOVERED = "SessionRecovered"
    SESSION_COMPLETED = "SessionCompleted"
    SESSION_FAILED = "SessionFailed"
    SESSION_CANCELLED = "SessionCancelled"
    SESSION_ARCHIVED = "SessionArchived"
    SESSION_DELETED = "SessionDeleted"
    SESSION_CLEANED = "SessionCleaned"
    SESSION_EXPIRED = "SessionExpired"
    SESSION_LIMIT_REACHED = "SessionLimitReached"


class SessionEventPublisher:
    """Publishes session events."""

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._enabled = True
        self._events_published = 0

    def publish(
        self,
        event_type: str,
        **data,
    ) -> None:
        """Publish an event.

        Args:
            event_type: Type of event.
            **data: Event data.
        """
        self._events_published += 1

    @property
    def events_published(self) -> int:
        """Get number of events published."""
        return self._events_published

    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False

    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = True
