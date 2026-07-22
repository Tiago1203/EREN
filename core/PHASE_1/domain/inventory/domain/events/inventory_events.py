"""Inventory domain events."""

from __future__ import annotations

from dataclasses import dataclass

from core.PHASE_1.infrastructure.shared.events import DomainEvent


@dataclass(frozen=True)
class SparePartAdded(DomainEvent):
    tenant_id: str
    spare_part_id: str
    part_number: str
    quantity: int
    warehouse_id: str | None


@dataclass(frozen=True)
class SparePartConsumed(DomainEvent):
    tenant_id: str
    spare_part_id: str
    quantity: int
    work_order_id: str | None = None


@dataclass(frozen=True)
class SparePartLowStock(DomainEvent):
    tenant_id: str
    spare_part_id: str
    current_stock: int
    reorder_point: int


@dataclass(frozen=True)
class PurchaseOrderCreated(DomainEvent):
    tenant_id: str
    purchase_order_id: str
    po_number: str
    supplier_id: str


@dataclass(frozen=True)
class PurchaseOrderApproved(DomainEvent):
    tenant_id: str
    purchase_order_id: str
    approved_by: str


@dataclass(frozen=True)
class PurchaseOrderReceived(DomainEvent):
    tenant_id: str
    purchase_order_id: str
    total_value: str
