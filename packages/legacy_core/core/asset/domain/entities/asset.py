"""Asset aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import (
    AggregateRoot,
    AssetId,
    ContractId,
    DepartmentId,
    DeviceId,
    ManufacturerId,
    RoomId,
    TenantId,
    VendorId,
    WarrantyId,
)

if TYPE_CHECKING:
    pass


class AssetStatus(str, Enum):
    ACTIVE = "active"
    IN_STORAGE = "in_storage"
    UNDER_MAINTENANCE = "under_maintenance"
    DECOMMISSIONED = "decommissioned"
    DISPOSED = "disposed"


class DepreciationMethod(str, Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


@dataclass(eq=False)
class Asset(AggregateRoot):
    """Asset aggregate root.

    Tracks the business side of medical equipment lifecycle.
    Links to Device Context via device_id.

    Invariants:
    1. current_value ≤ acquisition_cost (depreciation)
    2. An Asset may link to exactly one Device
    """

    tenant_id: TenantId
    asset_id: AssetId

    # Identification
    asset_tag: str  # Hospital inventory number
    name: str

    # Device linkage (EPIC 2 Device Context)
    device_id: DeviceId | None = None

    # Vendor and manufacturer
    manufacturer_id: ManufacturerId | None = None
    vendor_id: VendorId | None = None

    # Financial
    acquisition_date: date = field(default_factory=date.today)
    acquisition_cost: Decimal = Decimal("0.00")
    current_value: Decimal = Decimal("0.00")
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    useful_life_years: int = 5

    # Location
    location_id: RoomId | None = None  # From Capacity Context
    department_id: DepartmentId | None = None

    # Status
    status: AssetStatus = AssetStatus.ACTIVE

    # Contracts and warranties
    active_contract_id: ContractId | None = None
    active_warranty_id: WarrantyId | None = None

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        asset_tag: str,
        name: str,
        acquisition_date: date | None = None,
        acquisition_cost: Decimal = Decimal("0.00"),
        useful_life_years: int = 5,
        depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE,
    ) -> Asset:
        if acquisition_cost < 0:
            raise ValueError("acquisition_cost cannot be negative")
        asset_id = AssetId.generate()
        asset = cls(
            id=asset_id,
            tenant_id=tenant_id,
            asset_id=asset_id,
            asset_tag=asset_tag,
            name=name,
            acquisition_date=acquisition_date or date.today(),
            acquisition_cost=acquisition_cost,
            current_value=acquisition_cost,
            useful_life_years=useful_life_years,
            depreciation_method=depreciation_method,
        )
        asset._mark_created()
        return asset

    def link_device(self, device_id: DeviceId) -> None:
        """Link this asset to a device in Device Context."""
        self.device_id = device_id
        self._mark_updated()

    def decommission(self) -> None:
        """Decommission the asset."""
        if self.status == AssetStatus.DISPOSED:
            raise ValueError("Cannot decommission a disposed asset")
        self.status = AssetStatus.DECOMMISSIONED
        self._mark_updated()

    def transfer(self, location_id: RoomId, department_id: DepartmentId) -> None:
        """Transfer asset to new location and department."""
        self.location_id = location_id
        self.department_id = department_id
        self._mark_updated()

    def update_value(self, new_value: Decimal) -> None:
        """Update current value (depreciation)."""
        if new_value > self.acquisition_cost:
            raise ValueError("current_value cannot exceed acquisition_cost")
        self.current_value = new_value
        self._mark_updated()
