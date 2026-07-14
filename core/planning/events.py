"""Planning events for EREN Cognitive Planning Engine.

Event definitions for planning operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class PlanningEventType(str, Enum):
    """Types of planning events."""

    PLANNING_STARTED = "planning_started"
    GOAL_ANALYZED = "goal_analyzed"
    TASKS_DECOMPOSED = "tasks_decomposed"
    DEPENDENCIES_RESOLVED = "dependencies_resolved"
    PLAN_BUILT = "plan_built"
    PLAN_VALIDATED = "plan_validated"
    PLAN_READY = "plan_ready"
    PLAN_EXECUTING = "plan_executing"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"
    PLANNING_ERROR = "planning_error"


@dataclass
class PlanningEvent:
    """A planning event."""

    event_type: PlanningEventType
    plan_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Event-specific data
    task_id: str | None = None
    goal_type: str | None = None
    task_count: int = 0
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "plan_id": self.plan_id,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "goal_type": self.goal_type,
            "task_count": self.task_count,
            "error": self.error,
            "metadata": self.metadata,
        }


class PlanningEventBus:
    """Event bus for planning events.

    The Event Bus does NOT:
    - Execute tasks
    - Query providers

    It ONLY:
    - Publishes events
    - Notifies subscribers
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[PlanningEventType, list] = {
            event_type: [] for event_type in PlanningEventType
        }
        self._history: list[PlanningEvent] = []

    def subscribe(
        self,
        event_type: PlanningEventType,
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
        event_type: PlanningEventType,
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

    def publish(self, event: PlanningEvent) -> None:
        """Publish event.

        Args:
            event: Event to publish.
        """
        # Store in history
        self._history.append(event)

        # Notify subscribers
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    pass  # Don't let subscriber errors break publishing

    def get_history(
        self,
        plan_id: str | None = None,
        event_type: PlanningEventType | None = None,
        limit: int = 100,
    ) -> list[PlanningEvent]:
        """Get event history.

        Args:
            plan_id: Filter by plan ID.
            event_type: Filter by event type.
            limit: Maximum events to return.

        Returns:
            List of events.
        """
        events = self._history

        if plan_id:
            events = [e for e in events if e.plan_id == plan_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def clear(self) -> None:
        """Clear event history."""
        self._history.clear()


# Global event bus
_global_event_bus: PlanningEventBus | None = None
_event_bus_lock = __import__("threading").Lock()


def get_event_bus() -> PlanningEventBus:
    """Get the global event bus.

    Returns:
        Global PlanningEventBus instance.
    """
    global _global_event_bus
    with _event_bus_lock:
        if _global_event_bus is None:
            _global_event_bus = PlanningEventBus()
        return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    with _event_bus_lock:
        _global_event_bus = None
