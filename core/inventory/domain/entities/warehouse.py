"""Warehouse entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, TenantId, WarehouseId

if TYPE_CHECKING:
    pass


class WarehouseType(str, Enum):
    MAIN = "main"
    SATELLITE = "satellite"
    ON_SITE = "on_site"


class WarehouseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FULL = "full"


@dataclass(eq=False)
class Warehouse(AggregateRoot):
    """Warehouse entity."""

    tenant_id: TenantId
    warehouse_id: WarehouseId
    warehouse_code: str
    warehouse_name: str
    warehouse_type: WarehouseType = WarehouseType.MAIN
    address: str | None = None
    capacity_sqft: int | None = None
    status: WarehouseStatus = WarehouseStatus.ACTIVE

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        warehouse_code: str,
        warehouse_name: str,
        warehouse_type: WarehouseType = WarehouseType.MAIN,
        address: str | None = None,
        capacity_sqft: int | None = None,
    ) -> Warehouse:
        wh_id = WarehouseId.generate()
        wh = cls(
            id=wh_id,
            tenant_id=tenant_id,
            warehouse_id=wh_id,
            warehouse_code=warehouse_code,
            warehouse_name=warehouse_name,
            warehouse_type=warehouse_type,
            address=address,
            capacity_sqft=capacity_sqft,
        )
        wh._mark_created()
        return wh
