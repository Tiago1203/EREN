"""SQLAlchemy models for the Organization bounded context."""

from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    Date,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OrganizationModel(Base):
    """SQLAlchemy model for Organization aggregate root."""

    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_tenant_id", "tenant_id"),
        {"schema": "organization"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    doing_business_as: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ownership_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="private")
    founded_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class HospitalModel(Base):
    """SQLAlchemy model for Hospital."""

    __tablename__ = "hospitals"
    __table_args__ = (
        Index("ix_hospitals_tenant_id", "tenant_id"),
        Index("ix_hospitals_organization_id", "organization_id"),
        Index("ix_hospitals_hospital_code", "hospital_code"),
        {"schema": "organization"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    hospital_code: Mapped[str] = mapped_column(String(20), nullable=False)
    hospital_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hospital_type: Mapped[str] = mapped_column(String(20), nullable=False)
    license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    accreditation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )
    license_expiry_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
