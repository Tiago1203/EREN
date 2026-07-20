"""Workflow events for EREN Cognitive Workflow Engine.

Event definitions for workflow operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class WorkflowEventType(str, Enum):
    """Types of workflow events."""

    WORKFLOW_CREATED = "workflow_created"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    NODE_SKIPPED = "node_skipped"
    CHECKPOINT_CREATED = "checkpoint_created"
    CHECKPOINT_RESTORED = "checkpoint_restored"


@dataclass
class WorkflowEvent:
    """A workflow event."""

    event_type: WorkflowEventType
    workflow_id: str
    execution_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Event-specific data
    node_id: str | None = None
    checkpoint_id: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "node_id": self.node_id,
            "checkpoint_id": self.checkpoint_id,
            "metadata": self.metadata,
        }


class WorkflowEventBus:
    """Event bus for workflow events.

    The Event Bus does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Publishes events
    - Notifies subscribers
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[WorkflowEventType, list] = {
            event_type: [] for event_type in WorkflowEventType
        }
        self._history: list[WorkflowEvent] = []

    def subscribe(
        self,
        event_type: WorkflowEventType,
        callback,
    ) -> None:
        """Subscribe to events.

        Args:
            event_type: Event type.
            callback: Callback function.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: WorkflowEventType,
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
        for event_type in WorkflowEventType:
            self.subscribe(event_type, callback)

    def publish(self, event: WorkflowEvent) -> None:
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
        workflow_id: str | None = None,
        event_type: WorkflowEventType | None = None,
        limit: int = 100,
    ) -> list[WorkflowEvent]:
        """Get event history.

        Args:
            workflow_id: Filter by workflow ID.
            event_type: Filter by event type.
            limit: Maximum events.

        Returns:
            List of events.
        """
        events = self._history

        if workflow_id:
            events = [e for e in events if e.workflow_id == workflow_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def clear(self) -> None:
        """Clear event history."""
        self._history.clear()


# Global event bus
_event_bus: WorkflowEventBus | None = None
_event_lock = __import__("threading").Lock()


def get_event_bus() -> WorkflowEventBus:
    """Get the global event bus.

    Returns:
        Global WorkflowEventBus instance.
    """
    global _event_bus
    with _event_lock:
        if _event_bus is None:
            _event_bus = WorkflowEventBus()
        return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _event_bus
    with _event_lock:
        _event_bus = None
