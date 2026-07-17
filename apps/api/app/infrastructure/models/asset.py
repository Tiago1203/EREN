"""SQLAlchemy models for the Asset Management bounded context."""

from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AssetModel(Base):
    """SQLAlchemy model for Asset aggregate root."""

    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_assets_tenant_id", "tenant_id"),
        Index("ix_assets_asset_tag", "asset_tag"),
        Index("ix_assets_device_id", "device_id"),
        Index("ix_assets_status", "status"),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    asset_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    manufacturer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    vendor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    acquisition_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    acquisition_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default="0.00")
    current_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default="0.00")
    depreciation_method: Mapped[str] = mapped_column(String(20), nullable=False, server_default="straight_line")
    useful_life_years: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    location_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    active_contract_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    active_warranty_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class ManufacturerModel(Base):
    """SQLAlchemy model for Manufacturer."""

    __tablename__ = "manufacturers"
    __table_args__ = (
        Index("ix_manufacturers_tenant_id", "tenant_id"),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    manufacturer_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class VendorModel(Base):
    """SQLAlchemy model for Vendor."""

    __tablename__ = "vendors"
    __table_args__ = (
        Index("ix_vendors_tenant_id", "tenant_id"),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    vendor_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class ContractModel(Base):
    """SQLAlchemy model for Contract."""

    __tablename__ = "contracts"
    __table_args__ = (
        Index("ix_contracts_tenant_id", "tenant_id"),
        Index("ix_contracts_asset_id", "asset_id"),
        Index("ix_contracts_vendor_id", "vendor_id"),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    contract_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    vendor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date(), nullable=False)
    end_date: Mapped[date] = mapped_column(Date(), nullable=False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default="0.00")
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    renewal_terms: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class WarrantyModel(Base):
    """SQLAlchemy model for Warranty."""

    __tablename__ = "warranties"
    __table_args__ = (
        Index("ix_warranties_tenant_id", "tenant_id"),
        Index("ix_warranties_asset_id", "asset_id"),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    warranty_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    warranty_type: Mapped[str] = mapped_column(String(20), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date(), nullable=False)
    end_date: Mapped[date] = mapped_column(Date(), nullable=False)
    coverage_details: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
