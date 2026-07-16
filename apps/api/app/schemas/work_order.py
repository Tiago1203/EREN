"""Pydantic v2 schemas for Work Order API request/response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# ─── Enums ────────────────────────────────────────────────────────────────────


class WorkOrderStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PENDING_PARTS = "pending_parts"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class WorkOrderType(StrEnum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


# ─── Request Schemas ───────────────────────────────────────────────────────────


class WorkOrderCreate(BaseModel):
    """Request schema for creating a new work order."""

    device_id: Annotated[str, Field(min_length=1, max_length=36)]
    device_name: str = ""
    device_serial: str = ""
    work_order_type: WorkOrderType
    description: Annotated[str, Field(min_length=1, max_length=2000)]
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    incident_id: str | None = None
    preventive_schedule_id: str | None = None


class WorkOrderSchedule(BaseModel):
    """Request schema for scheduling a work order."""

    scheduled_date: datetime
    estimated_duration_hours: float | None = Field(default=None, ge=0.5, le=999)
    assigned_to: str | None = None


class WorkOrderAssign(BaseModel):
    """Request schema for assigning a work order to a technician."""

    assigned_to: Annotated[str, Field(min_length=1, max_length=36)]


class WorkOrderComplete(BaseModel):
    """Request schema for completing a work order."""

    resolution_summary: str = ""
    parts_used: list[str] | None = None
    labor_hours: float | None = Field(default=None, ge=0, le=999)
    next_calibration_date: datetime | None = None


class WorkOrderCancel(BaseModel):
    """Request schema for cancelling a work order."""

    cancellation_reason: Annotated[str, Field(min_length=1, max_length=500)]


class WorkOrderHold(BaseModel):
    """Request schema for putting a work order on hold."""

    hold_reason: Annotated[str, Field(min_length=1, max_length=500)]


class WorkOrderUpdate(BaseModel):
    """Request schema for updating a work order."""

    description: str | None = Field(default=None, max_length=2000)
    priority: WorkOrderPriority | None = None
    scheduled_date: datetime | None = None
    estimated_duration_hours: float | None = Field(default=None, ge=0.5, le=999)
    notes: str | None = Field(default=None, max_length=2000)


# ─── Response Schemas ─────────────────────────────────────────────────────────


class WorkOrderResponse(BaseModel):
    """Response schema for a single work order."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    device_id: str
    work_order_type: str
    description: str
    notes: str | None = None
    resolution_summary: str | None = None
    cancellation_reason: str | None = None
    priority: str
    status: str
    assigned_to: str | None = None
    assigned_by: str | None = None
    assigned_at: datetime | None = None
    scheduled_date: datetime | None = None
    estimated_duration_hours: float | None = None
    actual_labor_hours: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    completed_by: str | None = None
    sla_deadline: datetime | None = None
    sla_breached: str | None = None
    on_hold_reason: str | None = None
    on_hold_at: datetime | None = None
    incident_id: str | None = None
    preventive_schedule_id: str | None = None
    parts_used: list[str] | None = None
    next_calibration_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    cancelled_by: str | None = None
    version: int


class WorkOrderListResponse(BaseModel):
    """Response schema for paginated work order list."""

    items: list[WorkOrderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class WorkOrderDeleteResponse(BaseModel):
    """Response schema for work order deletion."""

    deleted: bool
    work_order_id: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
