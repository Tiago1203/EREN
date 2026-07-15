"""Outbox pattern for reliable event publishing.

The outbox pattern ensures that:
1. Events are persisted in the same transaction as the domain entity
2. Events are eventually published to the message broker
3. No events are lost if the system crashes

This is a simplified implementation for MVP.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

if TYPE_CHECKING:
    pass


class OutboxStatus(StrEnum):
    """Status of outbox messages."""

    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class OutboxMessage(Base):
    """Outbox message for reliable event publishing.

    Every domain event is first written here, then published by a background worker.
    """

    __tablename__ = "outbox"
    __table_args__ = (
        Index("ix_outbox_status", "status"),
        Index("ix_outbox_aggregate_type", "aggregate_type"),
        Index("ix_outbox_created_at", "created_at"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Event metadata
    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of aggregate (e.g., 'Patient', 'Diagnosis')",
    )
    aggregate_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        comment="ID of the aggregate instance",
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of event (e.g., 'PatientCreated')",
    )

    # Payload
    payload: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON-encoded event payload",
    )

    # Processing
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=OutboxStatus.PENDING.value,
        comment="Current processing status",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of publish attempts",
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum retry attempts",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message if failed",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="When the event was created",
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the event was successfully published",
    )


def create_outbox_message(
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> OutboxMessage:
    """Factory function to create an outbox message."""
    import json

    return OutboxMessage(
        id=str(uuid.uuid4()),
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=json.dumps(payload),
        status=OutboxStatus.PENDING.value,
    )
