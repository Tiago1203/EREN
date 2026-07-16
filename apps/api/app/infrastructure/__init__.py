"""Infrastructure package.

Provides implementations of domain interfaces:
- SQLAlchemy repositories (incident, device, recommendation, knowledge)
- Redis caching service
- RabbitMQ event bus
- OpenTelemetry tracing and instrumentation
- Structured JSON logging
- Health check endpoints

The domain layer (core/) remains pure and free of infrastructure concerns.
"""
from app.infrastructure.events import EventBus
from app.infrastructure.messaging import (
    CacheService,
    EventBus as MessagingEventBus,
    cache_key,
    close_connection,
    close_redis,
    get_event_bus,
    get_redis,
)
from app.infrastructure.models import (
    ActionModel,
    ConversationMessageModel,
    DeviceModel,
    DomainEventModel,
    EvidenceModel,
    IncidentModel,
    InvestigationModel,
    KnowledgeArticleModel,
    RecommendationModel,
)
from app.infrastructure.observability import (
    configure_logging,
    setup_instrumentation,
    setup_tracing,
)
from app.infrastructure.repositories import (
    DeviceRepositoryImpl,
    IncidentRepositoryImpl,
    KnowledgeRepositoryImpl,
    RecommendationRepositoryImpl,
)

__all__ = [
    # Events (from existing)
    "EventBus",
    # Messaging
    "MessagingEventBus",
    "CacheService",
    "cache_key",
    "close_connection",
    "close_redis",
    "get_event_bus",
    "get_redis",
    # Observability
    "configure_logging",
    "setup_instrumentation",
    "setup_tracing",
    # Models
    "IncidentModel",
    "InvestigationModel",
    "EvidenceModel",
    "ActionModel",
    "ConversationMessageModel",
    "DeviceModel",
    "RecommendationModel",
    "KnowledgeArticleModel",
    "DomainEventModel",
    # Repositories
    "IncidentRepositoryImpl",
    "DeviceRepositoryImpl",
    "RecommendationRepositoryImpl",
    "KnowledgeRepositoryImpl",
]
