"""RabbitMQ event bus for domain events."""
from __future__ import annotations

import json
import logging
from typing import Any, Callable

import aio_pika
from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

_connection: AbstractConnection | None = None
_channel: AbstractChannel | None = None
_exchange: AbstractExchange | None = None


async def get_connection() -> AbstractConnection:
    """Get or create RabbitMQ connection."""
    global _connection
    if _connection is None or _connection.is_closed:
        settings = get_settings()
        _connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            timeout=10,
        )
    return _connection


async def get_channel() -> AbstractChannel:
    """Get or create RabbitMQ channel."""
    global _channel
    if _channel is None or _channel.is_closed:
        conn = await get_connection()
        _channel = await conn.channel()
        _channel.set_qos(prefetch_count=10)
    return _channel


async def get_exchange() -> AbstractExchange:
    """Get or create the events exchange."""
    global _exchange
    if _exchange is None:
        channel = await get_channel()
        _exchange = await channel.declare_exchange(
            "eren.events",
            ExchangeType.TOPIC,
            durable=True,
        )
    return _exchange


async def close_connection() -> None:
    """Close RabbitMQ connection gracefully."""
    global _connection, _channel, _exchange
    if _channel is not None and not _channel.is_closed:
        await _channel.close()
    if _connection is not None and not _connection.is_closed:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None


class EventBus:
    """RabbitMQ-backed event bus for publishing domain events."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], Any]]] = {}

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None:
        """Publish an event to a topic."""
        try:
            exchange = await get_exchange()
            message = Message(
                body=json.dumps(payload).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id or "",
            )
            await exchange.publish(message, routing_key=topic)
            logger.debug("Published event to %s: %s", topic, payload.get("event_type", ""))
        except Exception as e:
            logger.error("Failed to publish event to %s: %s", topic, e)

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[dict[str, Any]], Any],
    ) -> None:
        """Subscribe to a topic with a handler."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)


_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
