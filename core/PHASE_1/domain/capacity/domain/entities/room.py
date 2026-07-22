"""Room entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from core.PHASE_1.infrastructure.shared import AggregateRoot, FloorId, RoomId, TenantId


class RoomStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class RoomType(str, Enum):
    PATIENT = "patient"
    OPERATING_ROOM = "operating_room"
    PROCEDURE = "procedure"
    STORAGE = "storage"
    UTILITY = "utility"


@dataclass(eq=False)
class Room(AggregateRoot):
    """Room entity.

    A room belongs to exactly one floor.
    Each room contains zero or more beds.

    Invariants:
    1. Room must belong to exactly one Floor
    2. bed_count must be non-negative
    """

    tenant_id: TenantId
    campus_id: RoomId  # carried from hierarchy
    building_id: RoomId  # carried from hierarchy
    floor_id: FloorId
    room_id: RoomId
    room_number: str
    room_type: RoomType = RoomType.PATIENT
    bed_count: int = 0
    status: RoomStatus = RoomStatus.OPERATIONAL

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campus_id: RoomId,
        building_id: RoomId,
        floor_id: FloorId,
        room_number: str,
        room_type: RoomType = RoomType.PATIENT,
        bed_count: int = 0,
    ) -> Room:
        if bed_count < 0:
            raise ValueError("bed_count must be non-negative")
        room_id = RoomId.generate()
        room = cls(
            id=room_id,
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            room_number=room_number,
            room_type=room_type,
            bed_count=bed_count,
        )
        room._mark_created()
        return room

    def change_status(self, status: RoomStatus) -> None:
        self.status = status
        self._mark_updated()
