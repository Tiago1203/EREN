"""Capacity domain entities."""

from core.PHASE_1.domain.capacity.domain.entities.bed import Bed, BedStatus, BedType
from core.PHASE_1.domain.capacity.domain.entities.building import Building, BuildingStatus, BuildingType
from core.PHASE_1.domain.capacity.domain.entities.campus import Campus, CampusStatus
from core.PHASE_1.domain.capacity.domain.entities.floor import Floor, FloorStatus, FloorType
from core.PHASE_1.domain.capacity.domain.entities.room import Room, RoomStatus, RoomType

__all__ = [
    "Bed",
    "BedStatus",
    "BedType",
    "Building",
    "BuildingStatus",
    "BuildingType",
    "Campus",
    "CampusStatus",
    "Floor",
    "FloorStatus",
    "FloorType",
    "Room",
    "RoomStatus",
    "RoomType",
]
