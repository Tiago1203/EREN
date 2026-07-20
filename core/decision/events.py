"""Decision events for EREN Cognitive Decision Engine.

Event definitions for decision operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DecisionEventType(str, Enum):
    """Types of decision events."""

    DECISION_STARTED = "decision_started"
    GOAL_ANALYZED = "goal_analyzed"
    STRATEGY_SELECTED = "strategy_selected"
    RISK_EVALUATED = "risk_evaluated"
    TASKS_DECOMPOSED = "tasks_decomposed"
    DEPENDENCIES_RESOLVED = "dependencies_resolved"
    DECISION_BUILT = "decision_built"
    DECISION_VALIDATED = "decision_validated"
    DECISION_APPROVED = "decision_approved"
    DECISION_READY = "decision_ready"
    DECISION_EXECUTING = "decision_executing"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DECISION_COMPLETED = "decision_completed"
    DECISION_FAILED = "decision_failed"
    DECISION_REPLANNED = "decision_replanned"
    DECISION_CANCELLED = "decision_cancelled"
    ESCALATION_REQUIRED = "escalation_required"
    DECISION_ERROR = "decision_error"


@dataclass
class DecisionEvent:
    """A decision event."""

    event_type: DecisionEventType
    plan_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Event-specific data
    task_id: str | None = None
    goal_type: str | None = None
    strategy: str | None = None
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
            "strategy": self.strategy,
            "task_count": self.task_count,
            "error": self.error,
            "metadata": self.metadata,
        }


class DecisionEventBus:
    """Event bus for decision events.

    The Event Bus does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Publishes events
    - Notifies subscribers
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[DecisionEventType, list] = {
            event_type: [] for event_type in DecisionEventType
        }
        self._history: list[DecisionEvent] = []

    def subscribe(
        self,
        event_type: DecisionEventType,
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
        event_type: DecisionEventType,
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

    def publish(self, event: DecisionEvent) -> None:
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
                    pass

    def get_history(
        self,
        plan_id: str | None = None,
        event_type: DecisionEventType | None = None,
        limit: int = 100,
    ) -> list[DecisionEvent]:
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
_global_event_bus: DecisionEventBus | None = None
_event_bus_lock = __import__("threading").Lock()


def get_event_bus() -> DecisionEventBus:
    """Get the global event bus.

    Returns:
        Global DecisionEventBus instance.
    """
    global _global_event_bus
    with _event_bus_lock:
        if _global_event_bus is None:
            _global_event_bus = DecisionEventBus()
        return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    with _event_bus_lock:
        _global_event_bus = None
