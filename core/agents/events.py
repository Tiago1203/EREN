"""Agent events for EREN Cognitive Agent Runtime.

Event definitions for agent operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class AgentEventType(str, Enum):
    """Types of agent events."""

    # Lifecycle
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_ERROR = "agent_error"

    # Health
    AGENT_HEALTHY = "agent_healthy"
    AGENT_DEGRADED = "agent_degraded"
    AGENT_UNHEALTHY = "agent_unhealthy"
    AGENT_FAILED = "agent_failed"

    # Tasks
    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    TASK_RETRY = "task_retry"

    # Communication
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_REPLY = "message_reply"

    # Runtime
    RUNTIME_STARTED = "runtime_started"
    RUNTIME_STOPPED = "runtime_stopped"


@dataclass
class AgentEvent:
    """An agent event."""

    event_type: AgentEventType
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Event-specific data
    task_id: str | None = None
    capability: str | None = None
    message_id: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "capability": self.capability,
            "message_id": self.message_id,
            "error": self.error,
            "metadata": self.metadata,
        }


class AgentEventBus:
    """Event bus for agent events.

    The Event Bus does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Publishes events
    - Notifies subscribers
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[AgentEventType, list] = {
            event_type: [] for event_type in AgentEventType
        }
        self._history: list[AgentEvent] = []

    def subscribe(
        self,
        event_type: AgentEventType,
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
        event_type: AgentEventType,
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
        for event_type in AgentEventType:
            self.subscribe(event_type, callback)

    def publish(self, event: AgentEvent) -> None:
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
        agent_id: str | None = None,
        event_type: AgentEventType | None = None,
        limit: int = 100,
    ) -> list[AgentEvent]:
        """Get event history.

        Args:
            agent_id: Filter by agent ID.
            event_type: Filter by event type.
            limit: Maximum events to return.

        Returns:
            List of events.
        """
        events = self._history

        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def clear(self) -> None:
        """Clear event history."""
        self._history.clear()


# Global event bus
_global_event_bus: AgentEventBus | None = None
_event_lock = __import__("threading").Lock()


def get_event_bus() -> AgentEventBus:
    """Get the global agent event bus.

    Returns:
        Global AgentEventBus instance.
    """
    global _global_event_bus
    with _event_lock:
        if _global_event_bus is None:
            _global_event_bus = AgentEventBus()
        return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global agent event bus."""
    global _global_event_bus
    with _event_lock:
        _global_event_bus = None
