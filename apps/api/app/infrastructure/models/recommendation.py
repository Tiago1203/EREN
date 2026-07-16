"""SQLAlchemy models for the Recommendation bounded context."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecommendationModel(Base):
    """SQLAlchemy model for AIRecommendation aggregate root."""

    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_tenant_id", "tenant_id"),
        Index("ix_recommendations_incident_id", "incident_id"),
        Index("ix_recommendations_device_id", "device_id"),
        Index("ix_recommendations_status", "status"),
        Index("ix_recommendations_confidence", "confidence_score"),
        Index("ix_recommendations_created_at", "created_at"),
        {"schema": "recommendation"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # References
    incident_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    device_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # AI metadata
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)

    # Priority
    urgency: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")

    # State
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="generated")

    # Feedback
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    engineer_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Supersession
    superseded_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    supersedes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # SQLAlchemy optimistic locking — auto-increments version on UPDATE
    __mapper_args__ = {"version_id_col": version}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "incident_id": self.incident_id,
            "device_id": self.device_id,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "category": self.category,
            "confidence_score": self.confidence_score,
            "model_version": self.model_version,
            "urgency": self.urgency,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "acceptance_note": self.acceptance_note,
            "engineer_feedback": self.engineer_feedback,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewed_by": self.reviewed_by,
            "superseded_by": self.superseded_by,
            "supersedes": self.supersedes,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
