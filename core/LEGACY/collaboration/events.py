"""Collaboration events for EREN Multi-Agent Collaboration Engine.

Event definitions for collaboration operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class CollaborationEventType(str, Enum):
    """Types of collaboration events."""

    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_CANCELLED = "session_cancelled"
    AGENT_JOINED = "agent_joined"
    AGENT_LEFT = "agent_left"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    PROPOSAL_CREATED = "proposal_created"
    VOTE_SUBMITTED = "vote_submitted"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    RESULT_ADDED = "result_added"
    RESULT_AGGREGATED = "result_aggregated"


@dataclass
class CollaborationEvent:
    """A collaboration event."""

    event_type: CollaborationEventType
    session_id: str
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Event-specific data
    other_agent_id: str | None = None
    message_id: str | None = None
    proposal_id: str | None = None
    conflict_id: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "other_agent_id": self.other_agent_id,
            "message_id": self.message_id,
            "proposal_id": self.proposal_id,
            "conflict_id": self.conflict_id,
            "metadata": self.metadata,
        }


class CollaborationEventBus:
    """Event bus for collaboration events.

    The Event Bus does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Publishes events
    - Notifies subscribers
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[CollaborationEventType, list] = {
            event_type: [] for event_type in CollaborationEventType
        }
        self._history: list[CollaborationEvent] = []

    def subscribe(
        self,
        event_type: CollaborationEventType,
        callback,
    ) -> None:
        """Subscribe to events.

        Args:
            event_type: Event type to subscribe to.
            callback: Callback function.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: CollaborationEventType,
        callback,
    ) -> None:
        """Unsubscribe from events.

        Args:
            event_type: Event type.
            callback: Callback to remove.
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type]
                if cb != callback
            ]

    def subscribe_all(self, callback) -> None:
        """Subscribe to all events.

        Args:
            callback: Callback function.
        """
        for event_type in CollaborationEventType:
            self.subscribe(event_type, callback)

    def publish(self, event: CollaborationEvent) -> None:
        """Publish event.

        Args:
            event: Event to publish.
        """
        # Store in history
        self._history.append(event)

        # Keep history limited
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        # Notify subscribers
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    pass

    def get_history(
        self,
        session_id: str | None = None,
        event_type: CollaborationEventType | None = None,
        limit: int = 100,
    ) -> list[CollaborationEvent]:
        """Get event history.

        Args:
            session_id: Filter by session ID.
            event_type: Filter by event type.
            limit: Maximum events to return.

        Returns:
            List of events.
        """
        events = self._history

        if session_id:
            events = [e for e in events if e.session_id == session_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def clear(self) -> None:
        """Clear event history."""
        self._history.clear()


# Global event bus
_global_event_bus: CollaborationEventBus | None = None
_event_lock = __import__("threading").Lock()


def get_event_bus() -> CollaborationEventBus:
    """Get the global event bus.

    Returns:
        Global CollaborationEventBus instance.
    """
    global _global_event_bus
    with _event_lock:
        if _global_event_bus is None:
            _global_event_bus = CollaborationEventBus()
        return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    with _event_lock:
        _global_event_bus = None
