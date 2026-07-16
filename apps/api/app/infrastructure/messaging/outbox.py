"""Transactional Outbox pattern for reliable event publishing.

Events are written to an `outbox_events` table inside the same transaction as
the domain data. A background worker polls the outbox and publishes to RabbitMQ.

This guarantees **at-least-once** delivery without distributed transactions.

Tables:
- outbox_events (incident schema) — stores pending domain events

Usage::

    outbox = TransactionalOutbox(session)
    outbox.append(event_type="incident.created", payload={"incident_id": "123"})
    await session.commit()   # event is persisted with the incident
    # Background worker publishes to RabbitMQ and marks as processed
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Index, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)

# ─── SQLAlchemy Model ──────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    pass


class OutboxEventModel(Base):
    """Persistent outbox entry written in the same transaction as domain data."""

    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_outbox_events_created_at", "created_at"),
        Index("ix_outbox_events_status_created", "status", "created_at"),
        {"schema": "incident"},
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    aggregate_type: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)


# ─── Transactional Outbox ──────────────────────────────────────────────────────


class TransactionalOutbox:
    """Appends domain events to the outbox table within the current transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._pending: list[dict[str, Any]] = []

    def append(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        aggregate_type: str = "unknown",
        correlation_id: str | None = None,
    ) -> None:
        """Register an event to be published when the transaction commits."""
        self._pending.append(
            {
                "aggregate_type": aggregate_type,
                "event_type": event_type,
                "payload": payload,
                "correlation_id": correlation_id,
            }
        )

    async def flush(self) -> None:
        """Write all pending events to the outbox table.

        Called automatically after a successful commit. Do not call manually.
        """
        if not self._pending:
            return

        models = [
            OutboxEventModel(
                aggregate_type=e["aggregate_type"],
                event_type=e["event_type"],
                payload=e["payload"],
                correlation_id=e["correlation_id"],
                status="pending",
            )
            for e in self._pending
        ]

        self._session.add_all(models)
        await self._session.flush()
        self._pending.clear()
        logger.debug("Flushed %d events to outbox", len(models))


# ─── Outbox Worker ─────────────────────────────────────────────────────────────


class OutboxWorker:
    """Background worker that polls the outbox and publishes events to RabbitMQ.

    Run as a separate process::

        asyncio.run(OutboxWorker().run())
    """

    def __init__(
        self,
        poll_interval: float = 1.0,
        batch_size: int = 100,
        max_retries: int = 3,
    ) -> None:
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_retries = max_retries

    async def run(self) -> None:
        """Poll the outbox indefinitely."""
        from app.core.database import get_session_factory
        from app.infrastructure.messaging.rabbitmq import get_event_bus

        factory = get_session_factory()
        event_bus = get_event_bus()

        logger.info("Outbox worker started (poll_interval=%ss)", self.poll_interval)

        while True:
            try:
                async with factory() as session:
                    events = await self._fetch_pending(session)
                    for event in events:
                        await self._publish(session, event, event_bus)
                    if events:
                        await session.commit()
            except Exception as e:
                logger.error("Outbox worker error: %s", e)

            await asyncio.sleep(self.poll_interval)

    async def _fetch_pending(self, session: AsyncSession) -> list[OutboxEventModel]:
        """Fetch the next batch of pending outbox events."""
        stmt = text("""
                SELECT id, aggregate_type, event_type, payload,
                       correlation_id, retry_count
                FROM incident.outbox_events
                WHERE status = 'pending' AND retry_count < :max_retries
                ORDER BY created_at ASC
                LIMIT :batch_size
                FOR UPDATE SKIP LOCKED
            """)
        result = await session.execute(
            stmt, {"max_retries": self.max_retries, "batch_size": self.batch_size}
        )
        rows = result.fetchall()

        models = []
        for row in rows:
            model = OutboxEventModel(
                id=row[0],
                aggregate_type=row[1],
                event_type=row[2],
                payload=row[3],
                correlation_id=row[4],
                retry_count=row[5],
                status="pending",
            )
            await session.refresh(model)
            models.append(model)

        return models

    async def _publish(
        self,
        session: AsyncSession,
        event: OutboxEventModel,
        event_bus: Any,
    ) -> None:
        """Publish a single event to RabbitMQ and mark it as processed."""
        topic = f"eren.{event.aggregate_type}.{event.event_type}"
        payload = {
            "event_type": event.event_type,
            "aggregate_type": event.aggregate_type,
            "data": event.payload,
        }

        try:
            await event_bus.publish(
                topic,
                payload,
                correlation_id=event.correlation_id,
            )
            event.status = "published"
            event.processed_at = datetime.now(UTC)
            logger.debug("Outbox published: %s", topic)
        except Exception as e:
            event.retry_count += 1
            event.last_error = str(e)[:1000]
            if event.retry_count >= self.max_retries:
                event.status = "failed"
            logger.warning(
                "Outbox publish failed (attempt %d/%d): %s",
                event.retry_count,
                self.max_retries,
                e,
            )
