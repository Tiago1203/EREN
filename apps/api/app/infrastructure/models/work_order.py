"""SQLAlchemy model for the Work Order bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WorkOrderModel(Base):
    """SQLAlchemy model for WorkOrder aggregate root."""

    __tablename__ = "work_orders"
    __table_args__ = (
        Index("ix_work_orders_tenant_id", "tenant_id"),
        Index("ix_work_orders_device_id", "device_id"),
        Index("ix_work_orders_status", "status"),
        Index("ix_work_orders_priority", "priority"),
        Index("ix_work_orders_assigned_to", "assigned_to"),
        Index("ix_work_orders_sla_deadline", "sla_deadline"),
        Index("ix_work_orders_tenant_status", "tenant_id", "status"),
        Index("ix_work_orders_incident_id", "incident_id"),
        {"schema": "work_order"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Device reference
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    # Classification
    work_order_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # corrective | preventive

    # Content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Priority
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # low | medium | high | urgent | emergency

    # Status
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="draft"
    )  # draft | scheduled | in_progress | pending_parts | on_hold | completed | cancelled

    # Assignment
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Scheduling
    scheduled_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estimated_duration_hours: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    actual_labor_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # SLA
    sla_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_breached: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Hold
    on_hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    on_hold_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Cross-references
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    preventive_schedule_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )

    # Parts
    parts_used: Mapped[list[str] | None] = mapped_column(
        JSON, default=None
    )

    # Calibration follow-up
    next_calibration_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # SQLAlchemy optimistic locking
    __mapper_args__: ClassVar[dict[str, Any]] = {"version_id_col": version}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "device_id": str(self.device_id),
            "work_order_type": self.work_order_type,
            "description": self.description,
            "notes": self.notes,
            "resolution_summary": self.resolution_summary,
            "cancellation_reason": self.cancellation_reason,
            "priority": self.priority,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "scheduled_date": (
                self.scheduled_date.isoformat() if self.scheduled_date else None
            ),
            "estimated_duration_hours": self.estimated_duration_hours,
            "actual_labor_hours": self.actual_labor_hours,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "completed_by": self.completed_by,
            "sla_deadline": (
                self.sla_deadline.isoformat() if self.sla_deadline else None
            ),
            "sla_breached": self.sla_breached,
            "on_hold_reason": self.on_hold_reason,
            "on_hold_at": self.on_hold_at.isoformat() if self.on_hold_at else None,
            "incident_id": str(self.incident_id) if self.incident_id else None,
            "preventive_schedule_id": self.preventive_schedule_id,
            "parts_used": self.parts_used,
            "next_calibration_date": (
                self.next_calibration_date.isoformat()
                if self.next_calibration_date
                else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "cancelled_by": self.cancelled_by,
            "version": self.version,
        }
