"""SQLAlchemy models for the Staffing bounded context."""

from __future__ import annotations

from datetime import datetime, date
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
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


class StaffModel(Base):
    """SQLAlchemy model for Staff aggregate root."""

    __tablename__ = "staff"
    __table_args__ = (
        Index("ix_staff_tenant_id", "tenant_id"),
        Index("ix_staff_staff_type", "staff_type"),
        Index("ix_staff_employment_status", "employment_status"),
        Index("ix_staff_email", "email"),
        {"schema": "staffing"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    staff_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    staff_type: Mapped[str] = mapped_column(String(20), nullable=False)
    employment_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    hire_date: Mapped[date] = mapped_column(Date(), nullable=False)
    primary_role_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    team_ids: Mapped[list | None] = mapped_column(JSON, nullable=True, server_default="[]")
    terminated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class RoleModel(Base):
    """SQLAlchemy model for Role."""

    __tablename__ = "roles"
    __table_args__ = (
        Index("ix_roles_tenant_id", "tenant_id"),
        Index("ix_roles_name", "name"),
        {"schema": "staffing"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    role_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    role_type: Mapped[str] = mapped_column(String(20), nullable=False)
    permissions: Mapped[list | None] = mapped_column(JSON, nullable=True, server_default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class TeamModel(Base):
    """SQLAlchemy model for Team."""

    __tablename__ = "teams"
    __table_args__ = (
        Index("ix_teams_tenant_id", "tenant_id"),
        Index("ix_teams_name", "name"),
        {"schema": "staffing"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    team_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    team_type: Mapped[str] = mapped_column(String(20), nullable=False)
    department_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    lead_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class ShiftModel(Base):
    """SQLAlchemy model for Shift."""

    __tablename__ = "shifts"
    __table_args__ = (
        Index("ix_shifts_tenant_id", "tenant_id"),
        Index("ix_shifts_staff_id", "staff_id"),
        Index("ix_shifts_status", "status"),
        {"schema": "staffing"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    shift_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    staff_id: Mapped[str] = mapped_column(String(36), nullable=False)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unit_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="scheduled")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
