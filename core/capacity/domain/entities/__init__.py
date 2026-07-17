"""Capacity domain entities."""

from core.capacity.domain.entities.bed import Bed, BedStatus, BedType
from core.capacity.domain.entities.building import Building, BuildingStatus, BuildingType
from core.capacity.domain.entities.campus import Campus, CampusStatus
from core.capacity.domain.entities.floor import Floor, FloorStatus, FloorType
from core.capacity.domain.entities.room import Room, RoomStatus, RoomType

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
