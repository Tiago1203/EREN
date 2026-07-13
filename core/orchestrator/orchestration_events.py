"""Events for the Cognitive Orchestrator.

Defines all orchestration events.

Architecture only -- no implementations.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Event Types
# =============================================================================


class OrchestrationEventType(str, Enum):
    """Types of orchestration events."""

    # Session events
    SESSION_STARTED = "SessionStarted"
    SESSION_COMPLETED = "SessionCompleted"
    SESSION_FAILED = "SessionFailed"
    SESSION_CANCELLED = "SessionCancelled"

    # State events
    STATE_CHANGED = "StateChanged"
    STATE_TRANSITION = "StateTransition"

    # Lifecycle events
    ORCHESTRATION_PAUSED = "OrchestrationPaused"
    ORCHESTRATION_RESUMED = "OrchestrationResumed"
    ORCHESTRATION_TIMEOUT = "OrchestrationTimeout"

    # Motor events
    MOTOR_STARTED = "MotorStarted"
    MOTOR_COMPLETED = "MotorCompleted"
    MOTOR_FAILED = "MotorFailed"

    # Context events
    CONTEXT_CREATED = "ContextCreated"
    CONTEXT_UPDATED = "ContextUpdated"
    CONTEXT_LOCKED = "ContextLocked"
    CONTEXT_UNLOCKED = "ContextUnlocked"

    # Decision events
    DECISION_MADE = "DecisionMade"
    DECISION_ESCALATED = "DecisionEscalated"

    # Evidence events
    EVIDENCE_COLLECTED = "EvidenceCollected"
    EVIDENCE_UPDATED = "EvidenceUpdated"

    # Custom events
    CUSTOM_EVENT = "CustomEvent"


# =============================================================================
# Event Publisher
# =============================================================================


class OrchestrationEventPublisher:
    """Publishes orchestration events to the EventBus."""

    def __init__(self) -> None:
        """Initialize the event publisher."""
        self._enabled = True
        self._events_published = 0

    def publish(
        self,
        event_type: str,
        **data: Any,
    ) -> None:
        """Publish an event.

        Args:
            event_type: Type of event.
            **data: Event data.
        """
        self._events_published += 1

        # Try to publish to EventBus if available
        if _HAS_EVENT_BUS:
            try:
                bus = get_global_bus()
                if bus:
                    event = Event(
                        event_type=f"orchestration.{event_type}",
                        data=data,
                    )
                    bus.publish(event)
            except Exception:
                pass

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


# Import EventBus for type hints
try:
    from core.events import Event
    _HAS_EVENT_BUS = True
except ImportError:
    _HAS_EVENT_BUS = False
