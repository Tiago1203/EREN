"""SQLAlchemy models for the Inventory bounded context."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal

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


class SparePartModel(Base):
    """SQLAlchemy model for SparePart aggregate root."""

    __tablename__ = "spare_parts"
    __table_args__ = (
        Index("ix_spare_parts_tenant_id", "tenant_id"),
        Index("ix_spare_parts_part_number", "part_number"),
        Index("ix_spare_parts_warehouse_id", "warehouse_id"),
        Index("ix_spare_parts_status", "status"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    spare_part_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    part_number: Mapped[str] = mapped_column(String(50), nullable=False)
    part_name: Mapped[str] = mapped_column(String(200), nullable=False)
    part_description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    manufacturer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, server_default="piece")
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default="0.00")
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    reorder_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    warehouse_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    storage_location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lot_tracking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    expiry_tracking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    shelf_life_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class WarehouseModel(Base):
    """SQLAlchemy model for Warehouse."""

    __tablename__ = "warehouses"
    __table_args__ = (
        Index("ix_warehouses_tenant_id", "tenant_id"),
        Index("ix_warehouses_warehouse_code", "warehouse_code"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    warehouse_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    warehouse_code: Mapped[str] = mapped_column(String(20), nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(200), nullable=False)
    warehouse_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="main")
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    capacity_sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manager_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class SupplierModel(Base):
    """SQLAlchemy model for Supplier."""

    __tablename__ = "suppliers"
    __table_args__ = (
        Index("ix_suppliers_tenant_id", "tenant_id"),
        Index("ix_suppliers_supplier_code", "supplier_code"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_code: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_type: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="7")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class PurchaseOrderModel(Base):
    """SQLAlchemy model for PurchaseOrder."""

    __tablename__ = "purchase_orders"
    __table_args__ = (
        Index("ix_purchase_orders_tenant_id", "tenant_id"),
        Index("ix_purchase_orders_supplier_id", "supplier_id"),
        Index("ix_purchase_orders_status", "status"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    purchase_order_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    po_number: Mapped[str] = mapped_column(String(30), nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(36), nullable=False)
    warehouse_id: Mapped[str] = mapped_column(String(36), nullable=False)
    order_date: Mapped[date] = mapped_column(Date(), nullable=False)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    total_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default="0.00")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    approved_by_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
