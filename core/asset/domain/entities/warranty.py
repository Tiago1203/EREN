"""Warranty entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, AssetId, TenantId, WarrantyId

if TYPE_CHECKING:
    pass


class WarrantyType(str, Enum):
    MANUFACTURER = "manufacturer"
    EXTENDED = "extended"
    SERVICE = "service"


@dataclass(eq=False)
class Warranty(AggregateRoot):
    """Warranty entity.

    Tracks warranty coverage for an asset.
    """

    tenant_id: TenantId
    warranty_id: WarrantyId
    asset_id: AssetId

    warranty_type: WarrantyType
    start_date: date
    end_date: date
    coverage_details: str | None = None
    warranty_provider: str | None = None
    claim_contact: str | None = None


    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        asset_id: AssetId,
        warranty_type: WarrantyType,
        start_date: date,
        end_date: date,
        coverage_details: str | None = None,
        warranty_provider: str | None = None,
    ) -> Warranty:
        if end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        warranty_id = WarrantyId.generate()
        warranty = cls(
            id=warranty_id,
            tenant_id=tenant_id,
            warranty_id=warranty_id,
            asset_id=asset_id,
            warranty_type=warranty_type,
            start_date=start_date,
            end_date=end_date,
            coverage_details=coverage_details,
            warranty_provider=warranty_provider,
        )
        warranty._mark_created()
        return warranty

    def is_active(self) -> bool:
        today = date.today()
        return self.start_date <= today <= self.end_date

    def days_remaining(self) -> int:
        today = date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
