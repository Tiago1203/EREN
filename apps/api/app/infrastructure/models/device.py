"""SQLAlchemy models for the Device bounded context."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DeviceModel(Base):
    """SQLAlchemy model for Device aggregate root."""

    __tablename__ = "devices"
    __table_args__ = (
        Index("ix_devices_tenant_id", "tenant_id"),
        Index("ix_devices_serial_number", "tenant_id", "serial_number", unique=True),
        Index("ix_devices_status", "status"),
        Index("ix_devices_type", "device_type"),
        Index("ix_devices_building", "location_building"),
        {"schema": "device"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Serial number & Manufacturer
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer_model: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer_country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Classification
    device_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Location
    location_building: Mapped[str] = mapped_column(String(255), nullable=False)
    location_floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="registered")

    # Calibration & Maintenance
    calibration_last: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    calibration_next: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    calibration_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maintenance_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Registration
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    registered_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_status_change: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

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
            "serial_number": self.serial_number,
            "manufacturer_name": self.manufacturer_name,
            "manufacturer_model": self.manufacturer_model,
            "manufacturer_country": self.manufacturer_country,
            "device_type": self.device_type,
            "name": self.name,
            "description": self.description,
            "is_critical": self.is_critical,
            "status": self.status,
            "location_building": self.location_building,
            "location_floor": self.location_floor,
            "location_room": self.location_room,
            "location_department": self.location_department,
            "calibration_last": (
                self.calibration_last.isoformat() if self.calibration_last else None
            ),
            "calibration_next": (
                self.calibration_next.isoformat() if self.calibration_next else None
            ),
            "calibration_interval_days": self.calibration_interval_days,
            "maintenance_interval_days": self.maintenance_interval_days,
            "notes": self.notes,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "registered_by": self.registered_by,
            "last_status_change": (
                self.last_status_change.isoformat() if self.last_status_change else None
            ),
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
