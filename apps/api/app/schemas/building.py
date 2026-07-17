"""Pydantic v2 schemas for Building API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BuildingTypeEnum(str):
    MAIN = "main"
    OUTPATIENT = "outpatient"
    EMERGENCY = "emergency"
    RESEARCH = "research"
    ADMINISTRATIVE = "administrative"


class BuildingCreate(BaseModel):
    building_code: str = Field(min_length=1, max_length=20)
    building_name: str = Field(min_length=1, max_length=200)
    building_type: BuildingTypeEnum = BuildingTypeEnum.MAIN


class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    building_id: str
    campus_id: str
    building_code: str
    building_name: str
    building_type: str
    status: str
