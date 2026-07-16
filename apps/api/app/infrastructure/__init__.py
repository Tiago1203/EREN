"""Infrastructure package.

Provides implementations of domain interfaces:
- SQLAlchemy repositories (device)
- Redis caching service
- RabbitMQ event bus
- Transactional Outbox pattern for reliable event publishing
- OpenTelemetry tracing and instrumentation
- Structured JSON logging with correlation IDs
- Health check endpoints

The domain layer remains pure and free of infrastructure concerns.
"""
from app.infrastructure.events import EventBus
from app.infrastructure.messaging import (
    CacheService,
    OutboxEventModel,
    OutboxWorker,
    TransactionalOutbox,
    cache_key,
    close_connection,
    close_redis,
    get_event_bus,
    get_redis,
)
from app.infrastructure.messaging import (
    EventBus as MessagingEventBus,
)
from app.infrastructure.models import (
    DeviceModel,
    DomainEventModel,
)
from app.infrastructure.observability import (
    configure_logging,
    setup_instrumentation,
    setup_tracing,
)
from app.infrastructure.repositories import (
    DeviceRepositoryImpl,
)

__all__ = [
    "CacheService",
    "DeviceModel",
    "DeviceRepositoryImpl",
    "DomainEventModel",
    "EventBus",
    "MessagingEventBus",
    "OutboxEventModel",
    "OutboxWorker",
    "TransactionalOutbox",
    "cache_key",
    "close_connection",
    "close_redis",
    "configure_logging",
    "get_event_bus",
    "get_redis",
    "setup_instrumentation",
    "setup_tracing",
]
