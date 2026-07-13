"""EREN internal event system.

Provides the event catalog (`EventType`), the immutable `Event` base and its
specific events, the publish/subscribe contracts (`EventPublisher`,
`EventSubscriber`), the `EventBus` implementation, and event exceptions.

Architecture only — no business logic, no AI, no dispatching behavior.
"""

from __future__ import annotations

from core.events.bus import (
    EventBus,
    EventHandler,
    AsyncEventHandler,
    EventPublisher,
    EventSubscriber,
    get_global_bus,
    set_global_bus,
    reset_global_bus,
)
from core.events.exceptions import (
    EventError,
    PublishError,
    SubscriptionError,
    EventValidationError,
    EventBusClosedError,
    CircuitBreakerOpenError,
    SubscriberError,
)
from core.events.models import (
    Event,
    EventType,
    create_event,
    EVENT_TYPE_TO_CLASS,
    # Voice events
    VoiceInputReceived,
    VoiceOutputGenerated,
    # Intent events
    IntentReceived,
    IntentDetected,
    # Plan events
    PlanCreated,
    PlanUpdated,
    PlanCompleted,
    PlanFailed,
    # Knowledge events
    KnowledgeRequested,
    KnowledgeRetrieved,
    KnowledgeSearchFailed,
    # Memory events
    MemoryRequested,
    MemoryRetrieved,
    MemoryStored,
    # Reasoning events
    ReasoningStarted,
    ReasoningFinished,
    HypothesisGenerated,
    HypothesisEvaluated,
    # Diagnostic events
    DiagnosticStarted,
    DiagnosticFinished,
    DiagnosticCompleted,
    # Workflow events
    WorkflowStarted,
    WorkflowFinished,
    WorkflowCompleted,
    StepExecuted,
    # Tool events
    ToolRequested,
    ToolExecuted,
    ToolFailed,
    # Response events
    ResponseReady,
    ResponseGenerated,
    # System events
    EngineError,
    EngineInitialized,
    EngineShutdown,
)
from core.events.publisher import (
    EventPublisherMixin,
    EventContext,
    EventAggregator,
    CircuitBreakerPublisher,
)
from core.events.subscriber import (
    BaseSubscriber,
    FunctionSubscriber,
    MultiHandlerSubscriber,
    LoggingSubscriber,
    AuditSubscriber,
    MetricSubscriber,
)

__all__ = [
    # Core abstractions
    "Event",
    "EventType",
    "EventBus",
    "EventPublisher",
    "EventSubscriber",
    "EventHandler",
    "AsyncEventHandler",
    "create_event",
    "EVENT_TYPE_TO_CLASS",
    # Global bus
    "get_global_bus",
    "set_global_bus",
    "reset_global_bus",
    # Voice events
    "VoiceInputReceived",
    "VoiceOutputGenerated",
    # Intent events
    "IntentReceived",
    "IntentDetected",
    # Plan events
    "PlanCreated",
    "PlanUpdated",
    "PlanCompleted",
    "PlanFailed",
    # Knowledge events
    "KnowledgeRequested",
    "KnowledgeRetrieved",
    "KnowledgeSearchFailed",
    # Memory events
    "MemoryRequested",
    "MemoryRetrieved",
    "MemoryStored",
    # Reasoning events
    "ReasoningStarted",
    "ReasoningFinished",
    "HypothesisGenerated",
    "HypothesisEvaluated",
    # Diagnostic events
    "DiagnosticStarted",
    "DiagnosticFinished",
    "DiagnosticCompleted",
    # Workflow events
    "WorkflowStarted",
    "WorkflowFinished",
    "WorkflowCompleted",
    "StepExecuted",
    # Tool events
    "ToolRequested",
    "ToolExecuted",
    "ToolFailed",
    # Response events
    "ResponseReady",
    "ResponseGenerated",
    # System events
    "EngineError",
    "EngineInitialized",
    "EngineShutdown",
    # Exceptions
    "EventError",
    "PublishError",
    "SubscriptionError",
    "EventValidationError",
    "EventBusClosedError",
    "CircuitBreakerOpenError",
    "SubscriberError",
    # Publisher patterns
    "EventPublisherMixin",
    "EventContext",
    "EventAggregator",
    "CircuitBreakerPublisher",
    # Subscriber patterns
    "BaseSubscriber",
    "FunctionSubscriber",
    "MultiHandlerSubscriber",
    "LoggingSubscriber",
    "AuditSubscriber",
    "MetricSubscriber",
]
