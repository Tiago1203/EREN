"""Pydantic v2 schemas for Bed API."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class BedStatusEnum(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class BedTypeEnum(StrEnum):
    STANDARD = "standard"
    ICU = "icu"
    PEDIATRIC = "pediatric"
    NEONATAL = "neonatal"
    MATERNITY = "maternity"
    ISOLATION = "isolation"
    EMERGENCY = "emergency"


class BedCreate(BaseModel):
    bed_number: str = Field(min_length=1, max_length=50)
    bed_type: BedTypeEnum = BedTypeEnum.STANDARD
    negative_pressure: bool = False


class BedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bed_id: str
    room_id: str
    bed_number: str
    bed_type: str
    status: str
    negative_pressure: bool
    patient_id: str | None = None
    device_id: str | None = None
    occupied_at: datetime | None = None


class BedOccupyRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=100)


class BedListResponse(BaseModel):
    beds: list[BedResponse]
    total: int
    available_count: int
    occupied_count: int
