"""SQLAlchemy models for the Capacity bounded context."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CampusModel(Base):
    """SQLAlchemy model for Campus aggregate root."""

    __tablename__ = "campuses"
    __table_args__ = (
        Index("ix_campuses_tenant_id", "tenant_id"),
        Index("ix_campuses_organization_id", "organization_id"),
        Index("ix_campuses_campus_code", "campus_code"),
        {"schema": "capacity"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    campus_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    campus_code: Mapped[str] = mapped_column(String(20), nullable=False)
    campus_name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class BuildingModel(Base):
    """SQLAlchemy model for Building."""

    __tablename__ = "buildings"
    __table_args__ = (
        Index("ix_buildings_tenant_id", "tenant_id"),
        Index("ix_buildings_campus_id", "campus_id"),
        Index("ix_buildings_building_code", "building_code"),
        {"schema": "capacity"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    campus_id: Mapped[str] = mapped_column(String(36), nullable=False)
    building_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    building_code: Mapped[str] = mapped_column(String(20), nullable=False)
    building_name: Mapped[str] = mapped_column(String(200), nullable=False)
    building_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="main")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="operational")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class FloorModel(Base):
    """SQLAlchemy model for Floor."""

    __tablename__ = "floors"
    __table_args__ = (
        Index("ix_floors_tenant_id", "tenant_id"),
        Index("ix_floors_building_id", "building_id"),
        {"schema": "capacity"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    building_id: Mapped[str] = mapped_column(String(36), nullable=False)
    floor_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="standard")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="operational")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class RoomModel(Base):
    """SQLAlchemy model for Room."""

    __tablename__ = "rooms"
    __table_args__ = (
        Index("ix_rooms_tenant_id", "tenant_id"),
        Index("ix_rooms_floor_id", "floor_id"),
        Index("ix_rooms_room_number", "room_number"),
        {"schema": "capacity"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    floor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    room_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)
    room_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="patient")
    bed_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="operational")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class BedModel(Base):
    """SQLAlchemy model for Bed aggregate root."""

    __tablename__ = "beds"
    __table_args__ = (
        Index("ix_beds_tenant_id", "tenant_id"),
        Index("ix_beds_room_id", "room_id"),
        Index("ix_beds_status", "status"),
        Index("ix_beds_bed_type", "bed_type"),
        Index("ix_beds_patient_id", "patient_id"),
        {"schema": "capacity"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    campus_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    building_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    floor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    room_id: Mapped[str] = mapped_column(String(36), nullable=False)
    bed_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    bed_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bed_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="standard")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="available")
    negative_pressure: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    patient_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    occupied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vacated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
