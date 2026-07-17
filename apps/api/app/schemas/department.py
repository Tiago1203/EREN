"""Pydantic v2 schemas for Department API."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    department_code: str = Field(min_length=1, max_length=50)
    department_name: str = Field(min_length=1, max_length=200)
    department_type: str = Field(min_length=1)
    parent_department_id: str | None = None
    cost_center: str | None = None
    budget_allocated: Decimal | None = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: str
    department_code: str
    department_name: str
    department_type: str
    parent_department_id: str | None = None
    cost_center: str | None = None
    budget_allocated: Decimal | None = None
    status: str
