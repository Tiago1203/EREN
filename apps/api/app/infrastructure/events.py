"""Event Bus infrastructure.

Wraps outbox pattern with a clean interface for domain services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    pass


class EventBus:
    """Simple event bus using outbox pattern.

    Domain services use this to publish events.
    The infrastructure layer handles the details.
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
    ) -> None:
        """Publish a domain event via outbox.

        The event is written to the outbox table in the same transaction
        as the aggregate, ensuring atomicity.
        """
        from app.events.outbox import OutboxMessage, OutboxStatus, create_outbox_message

        outbox_message = create_outbox_message(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload={
                "event_type": event_type,
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "payload": payload,
            },
        )

        self._db.add(outbox_message)
        await self._db.flush()
