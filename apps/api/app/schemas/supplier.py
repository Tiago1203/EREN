"""Pydantic v2 schemas for Supplier API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SupplierCreate(BaseModel):
    supplier_name: str = Field(min_length=1, max_length=255)
    supplier_code: str = Field(min_length=1, max_length=50)
    supplier_type: str = Field(min_length=1, max_length=20)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)
    address: str | None = None
    lead_time_days: int = Field(default=7, ge=0)


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: str
    supplier_name: str
    supplier_code: str
    supplier_type: str
    lead_time_days: int
    is_active: bool
