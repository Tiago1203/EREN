"""EREN internal event system.

Provides the event catalog (`EventType`), the immutable `Event` base and its
specific events, the publish/subscribe contracts (`EventPublisher`,
`EventSubscriber`), the `EventBus` skeleton, and event exceptions.

Architecture only — no business logic, no AI, no dispatching behavior.
"""

from __future__ import annotations

from core.events.bus import (
    EventBus,
    EventHandler,
    EventPublisher,
    EventSubscriber,
)
from core.events.exceptions import (
    EventError,
    PublishError,
    SubscriptionError,
)
from core.events.models import (
    DiagnosticCompleted,
    Event,
    EventType,
    IntentDetected,
    KnowledgeRetrieved,
    PlanCreated,
    ReasoningFinished,
    ReasoningStarted,
    ResponseGenerated,
    ToolExecuted,
    VoiceReceived,
    WorkflowCompleted,
)

__all__ = [
    # Core abstractions
    "Event",
    "EventType",
    "EventBus",
    "EventPublisher",
    "EventSubscriber",
    "EventHandler",
    # Exceptions
    "EventError",
    "PublishError",
    "SubscriptionError",
    # Specific events
    "VoiceReceived",
    "IntentDetected",
    "PlanCreated",
    "KnowledgeRetrieved",
    "ReasoningStarted",
    "ReasoningFinished",
    "ToolExecuted",
    "DiagnosticCompleted",
    "WorkflowCompleted",
    "ResponseGenerated",
]
