"""Pydantic v2 schemas for Unit API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UnitCreate(BaseModel):
    unit_code: str = Field(min_length=1, max_length=50)
    unit_name: str = Field(min_length=1, max_length=200)
    unit_type: str = Field(default="inpatient", max_length=20)


class UnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unit_id: str
    department_id: str
    unit_code: str
    unit_name: str
    unit_type: str
    status: str
