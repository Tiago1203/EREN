"""Floor entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from core.shared import AggregateRoot, BuildingId, FloorId, TenantId


class FloorStatus(str, Enum):
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    CLOSED = "closed"


class FloorType(str, Enum):
    BASEMENT = "basement"
    GROUND = "ground"
    STANDARD = "standard"
    ROOFTOP = "rooftop"


@dataclass(eq=False)
class Floor(AggregateRoot):
    """Floor entity.

    A floor belongs to exactly one building.
    Each floor contains one or more rooms.

    Invariants:
    1. Floor must belong to exactly one Building
    2. Floor number must be non-negative
    """

    tenant_id: TenantId
    campus_id: BuildingId  # carried from hierarchy
    building_id: BuildingId
    floor_id: FloorId
    floor_number: int
    floor_type: FloorType = FloorType.STANDARD
    status: FloorStatus = FloorStatus.OPERATIONAL

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campus_id: BuildingId,
        building_id: BuildingId,
        floor_number: int,
        floor_type: FloorType = FloorType.STANDARD,
    ) -> Floor:
        if floor_number < 0:
            raise ValueError("Floor number must be non-negative")
        floor_id = FloorId.generate()
        floor = cls(
            id=floor_id,
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            floor_number=floor_number,
            floor_type=floor_type,
        )
        floor._mark_created()
        return floor
