"""Pydantic v2 schemas for Asset Management API."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AssetStatusEnum(StrEnum):
    ACTIVE = "active"
    IN_STORAGE = "in_storage"
    UNDER_MAINTENANCE = "under_maintenance"
    DECOMMISSIONED = "decommissioned"
    DISPOSED = "disposed"


class AssetCreate(BaseModel):
    asset_tag: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    device_id: str | None = None
    acquisition_date: date | None = None
    acquisition_cost: Decimal = Decimal("0.00")
    useful_life_years: int = Field(default=5, ge=1, le=30)


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: str
    asset_tag: str
    name: str
    device_id: str | None = None
    acquisition_cost: Decimal
    current_value: Decimal
    status: str


class PurchaseOrderCreate(BaseModel):
    supplier_id: str = Field(min_length=1)
    warehouse_id: str = Field(min_length=1)
    expected_delivery_date: date | None = None


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    purchase_order_id: str
    po_number: str
    supplier_id: str
    warehouse_id: str
    total_value: Decimal
    status: str
