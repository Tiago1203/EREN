"""Vendor entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, TenantId, VendorId

if TYPE_CHECKING:
    pass


class VendorType(str, Enum):
    DISTRIBUTOR = "distributor"
    MANUFACTURER_DIRECT = "manufacturer_direct"
    SERVICE_PROVIDER = "service_provider"
    THIRD_PARTY = "third_party"


@dataclass(eq=False)
class Vendor(AggregateRoot):
    """Vendor entity."""

    tenant_id: TenantId
    vendor_id: VendorId
    vendor_name: str
    vendor_type: VendorType
    tax_id: str | None = None
    credit_limit: Decimal = Decimal("0.00")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        vendor_name: str,
        vendor_type: VendorType,
        credit_limit: Decimal = Decimal("0.00"),
    ) -> Vendor:
        vendor_id = VendorId.generate()
        vendor = cls(
            id=vendor_id,
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            vendor_type=vendor_type,
            credit_limit=credit_limit,
        )
        vendor._mark_created()
        return vendor
