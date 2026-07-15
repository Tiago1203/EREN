"""Event publisher service.

Publishes domain events using the outbox pattern.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.outbox import OutboxMessage, OutboxStatus, create_outbox_message
from app.middleware.request_context import get_request_context

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing domain events using outbox pattern.

    Events are first written to the outbox table, then published by a background worker.
    This ensures at-least-once delivery.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def publish(
        self,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: dict[str, Any],
        tenant_id: str | None = None,
        correlation_id: str | None = None,
    ) -> OutboxMessage:
        """Publish a domain event.

        Args:
            aggregate_type: Type of aggregate (e.g., 'Patient')
            aggregate_id: ID of the aggregate instance
            event_type: Type of event (e.g., 'PatientCreated')
            payload: Event payload
            tenant_id: Tenant ID for multi-tenancy
            correlation_id: Correlation ID for tracing

        Returns:
            Created outbox message
        """
        # Enrich payload with context
        enriched_payload = {
            "event_id": None,  # Will be set after creation
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "payload": payload,
        }

        # Get context for additional metadata
        try:
            ctx = get_request_context()
            enriched_payload["request_id"] = ctx.request_id
        except Exception:
            pass

        # Create outbox message
        outbox_message = create_outbox_message(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=enriched_payload,
        )

        # Set event_id in payload
        enriched_payload["event_id"] = outbox_message.id
        outbox_message.payload = json.dumps(enriched_payload)

        self._db.add(outbox_message)
        await self._db.flush()

        logger.info(
            "event_created",
            extra={
                "event_id": outbox_message.id,
                "event_type": event_type,
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
            },
        )

        return outbox_message


async def process_pending_outbox(db: AsyncSession) -> int:
    """Process pending outbox messages.

    This would be called by a background worker in production.
    For MVP, this is a placeholder.

    Args:
        db: Database session

    Returns:
        Number of messages processed
    """
    # Get pending messages
    result = await db.execute(
        select(OutboxMessage)
        .where(OutboxMessage.status == OutboxStatus.PENDING.value)
        .order_by(OutboxMessage.created_at)
        .limit(100)
    )
    messages = list(result.scalars().all())

    for message in messages:
        try:
            # Mark as processing
            message.status = OutboxStatus.PROCESSING.value

            # In production, this would publish to message broker
            # For MVP, we just mark as published
            logger.info(
                "event_published",
                extra={
                    "event_id": message.id,
                    "event_type": message.event_type,
                },
            )

            # Mark as published
            message.status = OutboxStatus.PUBLISHED.value
            message.processed_at = datetime.now(UTC)

        except Exception as e:
            logger.error(
                "event_publish_failed",
                extra={
                    "event_id": message.id,
                    "error": str(e),
                },
            )
            message.retry_count += 1
            if message.retry_count >= message.max_retries:
                message.status = OutboxStatus.FAILED.value
                message.error_message = str(e)
            else:
                message.status = OutboxStatus.PENDING.value

    await db.commit()
    return len(messages)
