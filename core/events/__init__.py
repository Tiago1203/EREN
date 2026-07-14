"""EREN internal event system.

Provides the event catalog (`EventType`), the immutable `Event` base and its
specific events, the publish/subscribe contracts (`EventPublisher`,
`EventSubscriber`), the `EventBus` implementation, and event exceptions.

Architecture only — no business logic, no AI, no dispatching behavior.
"""

from __future__ import annotations

from core.events.bus import (
    AsyncEventHandler,
    EventBus,
    EventHandler,
    EventPublisher,
    EventSubscriber,
    get_global_bus,
    reset_global_bus,
    set_global_bus,
)
from core.events.exceptions import (
    CircuitBreakerOpenError,
    EventBusClosedError,
    EventError,
    EventValidationError,
    PublishError,
    SubscriberError,
    SubscriptionError,
)
from core.events.models import (
    EVENT_TYPE_TO_CLASS,
    DiagnosticCompleted,
    DiagnosticFinished,
    # Diagnostic events
    DiagnosticStarted,
    # System events
    EngineError,
    EngineInitialized,
    EngineShutdown,
    Event,
    EventType,
    HypothesisEvaluated,
    HypothesisGenerated,
    IntentDetected,
    # Intent events
    IntentReceived,
    # Knowledge events
    KnowledgeRequested,
    KnowledgeRetrieved,
    KnowledgeSearchFailed,
    # Memory events
    MemoryRequested,
    MemoryRetrieved,
    MemoryStored,
    PlanCompleted,
    # Plan events
    PlanCreated,
    PlanFailed,
    PlanUpdated,
    ReasoningFinished,
    # Reasoning events
    ReasoningStarted,
    ResponseGenerated,
    # Response events
    ResponseReady,
    StepExecuted,
    ToolExecuted,
    ToolFailed,
    # Tool events
    ToolRequested,
    # Voice events
    VoiceInputReceived,
    VoiceOutputGenerated,
    WorkflowCompleted,
    WorkflowFinished,
    # Workflow events
    WorkflowStarted,
    create_event,
)
from core.events.publisher import (
    CircuitBreakerPublisher,
    EventAggregator,
    EventContext,
    EventPublisherMixin,
)
from core.events.subscriber import (
    AuditSubscriber,
    BaseSubscriber,
    FunctionSubscriber,
    LoggingSubscriber,
    MetricSubscriber,
    MultiHandlerSubscriber,
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
