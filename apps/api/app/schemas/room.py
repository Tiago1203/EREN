"""Pydantic v2 schemas for Room API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    room_number: str = Field(min_length=1, max_length=50)
    room_type: str = Field(min_length=1, max_length=20)
    bed_count: int = Field(default=0, ge=0)


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    room_id: str
    floor_id: str
    room_number: str
    room_type: str
    bed_count: int
    status: str
