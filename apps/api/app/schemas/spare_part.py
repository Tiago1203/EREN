"""Pydantic v2 schemas for SparePart API."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SparePartCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=50)
    part_name: str = Field(min_length=1, max_length=200)
    part_description: str | None = None
    category: str = Field(min_length=1, max_length=20)
    unit_of_measure: str = Field(default="piece", max_length=20)
    unit_cost: Decimal = Decimal("0.00")
    reorder_point: int = Field(default=0, ge=0)
    reorder_quantity: int = Field(default=0, ge=0)
    current_stock: int = Field(default=0, ge=0)
    warehouse_id: str | None = None
    storage_location: str | None = Field(default=None, max_length=50)


class SparePartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spare_part_id: str
    part_number: str
    part_name: str
    category: str
    current_stock: int
    reorder_point: int
    warehouse_id: str | None = None
    status: str


class PurchaseOrderCreate(BaseModel):
    po_number: str = Field(min_length=1, max_length=30)
    supplier_id: str = Field(min_length=1)
    warehouse_id: str = Field(min_length=1)
    expected_delivery_date: str | None = None
    notes: str | None = None


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    purchase_order_id: str
    po_number: str
    supplier_id: str
    warehouse_id: str
    total_value: Decimal
    status: str
