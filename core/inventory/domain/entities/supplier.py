"""Supplier entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, SupplierId, TenantId

if TYPE_CHECKING:
    pass


class SupplierType(str, Enum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    DIRECT = "direct"


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    DISCONTINUED = "discontinued"


@dataclass(eq=False)
class Supplier(AggregateRoot):
    """Supplier entity."""

    tenant_id: TenantId
    supplier_id: SupplierId
    supplier_name: str
    supplier_code: str
    supplier_type: SupplierType
    tax_id: str | None = None
    address: str | None = None
    contact_person: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    payment_terms: str | None = None
    lead_time_days: int = 7
    minimum_order_value: Decimal = Decimal("0.00")
    status: SupplierStatus = SupplierStatus.ACTIVE

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        supplier_name: str,
        supplier_code: str,
        supplier_type: SupplierType,
        lead_time_days: int = 7,
    ) -> Supplier:
        supplier_id = SupplierId.generate()
        supplier = cls(
            id=supplier_id,
            tenant_id=tenant_id,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            supplier_code=supplier_code,
            supplier_type=supplier_type,
            lead_time_days=lead_time_days,
        )
        supplier._mark_created()
        return supplier
