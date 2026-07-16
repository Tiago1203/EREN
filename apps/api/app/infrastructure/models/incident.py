"""SQLAlchemy models for the Incident bounded context."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    pass


class IncidentModel(Base):
    """SQLAlchemy model for EngineeringIncident aggregate root."""

    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_tenant_id", "tenant_id"),
        Index("ix_incidents_device_id", "device_id"),
        Index("ix_incidents_status", "status"),
        Index("ix_incidents_priority", "priority"),
        Index("ix_incidents_assigned_to", "assigned_to"),
        Index("ix_incidents_created_at", "created_at"),
        {"schema": "incident"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    device_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reported_by: Mapped[str] = mapped_column(String(36), nullable=False)

    # Core fields
    symptom_description: Mapped[str] = mapped_column(Text, nullable=False)
    symptom_category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)

    # State
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="reported")

    # Classification
    safety_classification: Mapped[str] = mapped_column(
        String(50), nullable=False, default="recommendation"
    )

    # Assignment
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    triage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_resolution_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Resolution
    resolution_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Feedback
    feedback_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    feedback_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Correlation
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

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

    # Relationships
    investigations: Mapped[list[InvestigationModel]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "device_id": self.device_id,
            "reported_by": self.reported_by,
            "symptom_description": self.symptom_description,
            "symptom_category": self.symptom_category,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "safety_classification": self.safety_classification,
            "assigned_to": self.assigned_to,
            "triage_notes": self.triage_notes,
            "estimated_resolution_hours": self.estimated_resolution_hours,
            "resolution_description": self.resolution_description,
            "resolution_root_cause": self.resolution_root_cause,
            "resolution_time_minutes": self.resolution_time_minutes,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "closed_by": self.closed_by,
            "feedback_type": self.feedback_type,
            "feedback_content": self.feedback_content,
            "correlation_id": self.correlation_id,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class InvestigationModel(Base):
    """SQLAlchemy model for Investigation sub-aggregate."""

    __tablename__ = "investigations"
    __table_args__ = (
        Index("ix_investigations_incident_id", "incident_id"),
        {"schema": "incident"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incident.incidents.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    incident: Mapped[IncidentModel] = relationship(
        back_populates="investigations"
    )
    evidence: Mapped[list[EvidenceModel]] = relationship(
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    actions: Mapped[list[ActionModel]] = relationship(
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list[ConversationMessageModel]] = relationship(
        back_populates="investigation",
        cascade="all, delete-orphan",
    )


class EvidenceModel(Base):
    """SQLAlchemy model for Evidence."""

    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_investigation_id", "investigation_id"),
        {"schema": "incident"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incident.investigations.id"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    recorded_by: Mapped[str] = mapped_column(String(36), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    investigation: Mapped[InvestigationModel] = relationship(
        back_populates="evidence"
    )


class ActionModel(Base):
    """SQLAlchemy model for Action."""

    __tablename__ = "actions"
    __table_args__ = (
        Index("ix_actions_investigation_id", "investigation_id"),
        {"schema": "incident"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incident.investigations.id"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    performed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    investigation: Mapped[InvestigationModel] = relationship(
        back_populates="actions"
    )


class ConversationMessageModel(Base):
    """SQLAlchemy model for ConversationMessage."""

    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_messages_investigation_id", "investigation_id"),
        {"schema": "incident"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incident.investigations.id"),
        nullable=False,
    )
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ai_recommendation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    feedback_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    feedback_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    investigation: Mapped[InvestigationModel] = relationship(
        back_populates="messages"
    )
