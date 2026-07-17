"""Pydantic v2 schemas for Floor API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FloorCreate(BaseModel):
    floor_number: int = Field(ge=-5, le=200)
    floor_type: str = Field(min_length=1, max_length=20)


class FloorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    floor_id: str
    building_id: str
    floor_number: int
    floor_type: str
    status: str
