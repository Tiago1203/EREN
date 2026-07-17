"""Pydantic v2 schemas for Warehouse API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WarehouseCreate(BaseModel):
    warehouse_code: str = Field(min_length=1, max_length=20)
    warehouse_name: str = Field(min_length=1, max_length=200)
    warehouse_type: str = Field(default="main", max_length=20)
    address: str | None = None
    capacity_sqft: int | None = Field(default=None, ge=0)


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    warehouse_id: str
    warehouse_code: str
    warehouse_name: str
    warehouse_type: str
    address: str | None = None
    is_active: bool
