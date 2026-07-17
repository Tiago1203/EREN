"""Building entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from core.shared import AggregateRoot, BuildingId, CampusId, TenantId


class BuildingStatus(str, Enum):
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    CLOSED = "closed"


class BuildingType(str, Enum):
    MAIN = "main"
    PAVILION = "pavilion"
    ANNEX = "annex"
    PARKING = "parking"
    UTILITY = "utility"


@dataclass(eq=False)
class Building(AggregateRoot):
    """Building entity.

    A building belongs to exactly one campus.
    Each building contains one or more floors.

    Invariants:
    1. Building must belong to exactly one Campus
    2. Building must have a valid status
    """

    tenant_id: TenantId
    campus_id: CampusId
    building_id: BuildingId
    building_code: str
    building_name: str
    building_type: BuildingType = BuildingType.MAIN
    status: BuildingStatus = BuildingStatus.OPERATIONAL

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campus_id: CampusId,
        building_code: str,
        building_name: str,
        building_type: BuildingType = BuildingType.MAIN,
    ) -> Building:
        building_id = BuildingId.generate()
        building = cls(
            id=building_id,
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            building_code=building_code,
            building_name=building_name,
            building_type=building_type,
        )
        building._mark_created()
        return building

    def close(self) -> None:
        if self.status != BuildingStatus.CLOSED:
            self.status = BuildingStatus.CLOSED
            self._mark_updated()
