"""PurchaseOrder aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import (
    AggregateRoot,
    PurchaseOrderId,
    StaffId,
    SupplierId,
    TenantId,
    WarehouseId,
)

if TYPE_CHECKING:
    pass


class POStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass(eq=False)
class PurchaseOrder(AggregateRoot):
    """PurchaseOrder aggregate.

    Represents a purchase order for spare parts.

    Invariants:
    1. total = sum of line_item totals
    2. Supplier must be active to create PO
    """

    # Identity — no defaults first
    tenant_id: TenantId
    purchase_order_id: PurchaseOrderId
    po_number: str  # Auto-generated
    supplier_id: SupplierId
    warehouse_id: WarehouseId  # Destination warehouse

    # Dates
    order_date: date = field(default_factory=date.today)
    expected_delivery_date: date | None = None

    # Financial
    total_value: Decimal = Decimal("0.00")
    approval_required: bool = True
    approved_by_staff_id: StaffId | None = None
    approved_at: datetime | None = None

    # Status
    status: POStatus = POStatus.DRAFT
    notes: str | None = None

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        supplier_id: SupplierId,
        warehouse_id: WarehouseId,
        expected_delivery_date: date | None = None,
        approval_required: bool = True,
    ) -> PurchaseOrder:
        po_id = PurchaseOrderId.generate()
        po = cls(
            id=po_id,
            tenant_id=tenant_id,
            purchase_order_id=po_id,
            po_number=f"PO-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            expected_delivery_date=expected_delivery_date,
            approval_required=approval_required,
        )
        po._mark_created()
        return po

    def submit(self) -> None:
        if self.status != POStatus.DRAFT:
            raise ValueError(f"Cannot submit PO in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = POStatus.SUBMITTED
        self._relock_after_mutation()

    def approve(self, staff_id: StaffId) -> None:
        if self.status not in (POStatus.SUBMITTED, POStatus.DRAFT):
            raise ValueError(f"Cannot approve PO in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = POStatus.APPROVED
        self.approved_by_staff_id = staff_id
        self.approved_at = datetime.now(UTC)
        self._relock_after_mutation()

    def receive(self) -> None:
        if self.status not in (POStatus.APPROVED, POStatus.PARTIALLY_RECEIVED):
            raise ValueError(f"Cannot receive PO in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = POStatus.RECEIVED
        self._relock_after_mutation()

    def cancel(self) -> None:
        if self.status == POStatus.RECEIVED:
            raise ValueError("Cannot cancel a received PO")
        self._unlock_for_mutation()
        self.status = POStatus.CANCELLED
        self._relock_after_mutation()
