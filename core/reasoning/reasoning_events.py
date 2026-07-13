"""Reasoning event system.

Publishes events for observability.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass


# =============================================================================
# Event Types
# =============================================================================


class ReasoningEventType:
    """Standard reasoning event types."""

    # Session events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"

    # Hypothesis events
    HYPOTHESIS_CREATED = "hypothesis_created"
    HYPOTHESIS_UPDATED = "hypothesis_updated"
    HYPOTHESIS_CONFIRMED = "hypothesis_confirmed"
    HYPOTHESIS_REJECTED = "hypothesis_rejected"
    CONFIDENCE_UPDATED = "confidence_updated"

    # Evidence events
    EVIDENCE_ADDED = "evidence_added"
    EVIDENCE_REMOVED = "evidence_removed"
    EVIDENCE_INCORPORATED = "evidence_incorporated"
    RELATION_CHANGED = "relation_changed"

    # Decision events
    DECISION_GENERATED = "decision_generated"
    DECISION_ACCEPTED = "decision_accepted"
    DECISION_REJECTED = "decision_rejected"

    # Chain events
    CHAIN_BUILT = "chain_built"
    CHAIN_VALIDATED = "chain_validated"

    # Stage events
    STAGE_CHANGED = "stage_changed"


# =============================================================================
# Event Publisher
# =============================================================================


@dataclass
class ReasoningEvent:
    """A reasoning event."""

    event_type: str
    timestamp: str = ""
    session_id: str = ""
    data: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())


class ReasoningEventPublisher:
    """Publishes reasoning events to subscribers."""

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._subscribers: list[Callable[[ReasoningEvent], None]] = []
        self._event_log: list[ReasoningEvent] = []

    def subscribe(self, callback: Callable[[ReasoningEvent], None]) -> None:
        """Subscribe to events.

        Args:
            callback: Function to call with events.
        """
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[ReasoningEvent], None]) -> None:
        """Unsubscribe from events.

        Args:
            callback: The callback to remove.
        """
        self._subscribers = [s for s in self._subscribers if s != callback]

    def publish(self, event_type: str, session_id: str = "", **data: Any) -> None:
        """Publish an event.

        Args:
            event_type: Type of event.
            session_id: Session ID.
            **data: Event data.
        """
        event = ReasoningEvent(
            event_type=event_type,
            session_id=session_id,
            data=data,
        )

        self._event_log.append(event)

        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def get_events(
        self,
        event_type: str | None = None,
        session_id: str | None = None,
    ) -> list[ReasoningEvent]:
        """Get logged events.

        Args:
            event_type: Filter by type.
            session_id: Filter by session.

        Returns:
            List of events.
        """
        events = self._event_log

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if session_id:
            events = [e for e in events if e.session_id == session_id]

        return events

    def clear(self) -> None:
        """Clear event log."""
        self._event_log.clear()
