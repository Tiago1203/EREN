"""SparePart aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, ManufacturerId, SparePartId, TenantId, WarehouseId

if TYPE_CHECKING:
    pass


class PartCategory(str, Enum):
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    OPTICAL = "optical"
    FLUID = "fluid"
    CONSUMABLE = "consumable"
    ACCESSORY = "accessory"


class SparePartStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    RECALLED = "recalled"


@dataclass(eq=False)
class SparePart(AggregateRoot):
    """SparePart aggregate root.

    Tracks spare parts inventory for hospital equipment maintenance.

    Invariants:
    1. current_stock ≥ 0 always
    2. reorder_point > 0 if reorder_enabled = True
    """

    tenant_id: TenantId
    spare_part_id: SparePartId

    # Identification — no defaults first
    part_number: str  # Manufacturer part number
    part_name: str
    category: PartCategory

    # Vendor
    manufacturer_id: ManufacturerId | None = None

    # Optional fields with defaults
    part_description: str | None = None

    # Inventory
    unit_of_measure: str = "piece"
    unit_cost: Decimal = Decimal("0.00")

    # Stock levels
    reorder_point: int = 0  # Minimum stock level
    reorder_quantity: int = 0
    current_stock: int = 0

    # Storage
    warehouse_id: WarehouseId | None = None
    storage_location: str | None = None  # e.g., "Shelf A-3"

    # Tracking
    lot_tracking_enabled: bool = False
    expiry_tracking_enabled: bool = False
    shelf_life_days: int | None = None

    # Status
    status: SparePartStatus = SparePartStatus.ACTIVE

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        part_number: str,
        part_name: str,
        category: PartCategory,
        unit_cost: Decimal = Decimal("0.00"),
        reorder_point: int = 0,
        reorder_quantity: int = 0,
        current_stock: int = 0,
        lot_tracking_enabled: bool = False,
        expiry_tracking_enabled: bool = False,
    ) -> SparePart:
        if current_stock < 0:
            raise ValueError("current_stock cannot be negative")
        part_id = SparePartId.generate()
        part = cls(
            id=part_id,
            tenant_id=tenant_id,
            spare_part_id=part_id,
            part_number=part_number,
            part_name=part_name,
            category=category,
            unit_cost=unit_cost,
            reorder_point=reorder_point,
            reorder_quantity=reorder_quantity,
            current_stock=current_stock,
            lot_tracking_enabled=lot_tracking_enabled,
            expiry_tracking_enabled=expiry_tracking_enabled,
        )
        part._mark_created()
        return part

    def consume(self, quantity: int) -> None:
        """Consume parts from inventory."""
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        if quantity > self.current_stock:
            raise ValueError(
                f"Cannot consume {quantity} parts — only {self.current_stock} in stock"
            )
        self._unlock_for_mutation()
        self.current_stock -= quantity
        self._relock_after_mutation()

    def restock(self, quantity: int, warehouse_id: WarehouseId | None = None) -> None:
        """Add parts to inventory."""
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        self._unlock_for_mutation()
        self.current_stock += quantity
        if warehouse_id:
            self.warehouse_id = warehouse_id
        self._relock_after_mutation()

    def is_below_reorder_point(self) -> bool:
        """Check if stock is below reorder threshold."""
        return self.current_stock <= self.reorder_point

    def is_out_of_stock(self) -> bool:
        """Check if part is out of stock."""
        return self.current_stock == 0
