"""Messaging infrastructure (caching, event bus & transactional outbox)."""
from app.infrastructure.messaging.cache import (
    CacheService,
    cache_key,
    close_redis,
    get_redis,
)
from app.infrastructure.messaging.outbox import (
    OutboxEventModel,
    OutboxWorker,
    TransactionalOutbox,
)
from app.infrastructure.messaging.rabbitmq import (
    EventBus,
    close_connection,
    get_event_bus,
    get_exchange,
)

__all__ = [
    # Caching
    "CacheService",
    "cache_key",
    "close_redis",
    "get_redis",
    # Event bus
    "EventBus",
    "close_connection",
    "get_event_bus",
    "get_exchange",
    # Outbox
    "TransactionalOutbox",
    "OutboxEventModel",
    "OutboxWorker",
]
