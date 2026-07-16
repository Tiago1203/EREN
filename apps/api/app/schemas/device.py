"""Pydantic v2 schemas for Device API request/response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# ─── Enums ────────────────────────────────────────────────────────────────────


class DeviceStatusEnum(StrEnum):
    REGISTERED = "registered"
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    CALIBRATION_DUE = "calibration_due"
    OUT_OF_SERVICE = "out_of_service"
    DECOMMISSIONED = "decommissioned"


class DeviceTypeEnum(StrEnum):
    DIAGNOSTIC = "diagnostic"
    THERAPEUTIC = "therapeutic"
    MONITORING = "monitoring"
    LIFE_SUPPORT = "life_support"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    SURGICAL = "surgical"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


# ─── Request Schemas ───────────────────────────────────────────────────────────


class DeviceCreate(BaseModel):
    """Request schema for registering a new device."""

    serial_number: Annotated[str, Field(min_length=3, max_length=100)]
    name: Annotated[str, Field(min_length=1, max_length=255)]
    device_type: DeviceTypeEnum
    manufacturer_name: Annotated[str, Field(min_length=1, max_length=255)]
    manufacturer_model: Annotated[str, Field(min_length=1, max_length=255)]
    manufacturer_country: str | None = Field(default=None, max_length=100)
    building: Annotated[str, Field(min_length=1, max_length=255)]
    floor: str | None = Field(default=None, max_length=50)
    room: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_critical: bool = False
    calibration_last: datetime | None = None
    calibration_next: datetime | None = None
    calibration_interval_days: int | None = Field(default=None, ge=1, le=3650)
    maintenance_interval_days: int | None = Field(default=None, ge=1, le=3650)


class DeviceUpdate(BaseModel):
    """Request schema for updating device fields (PATCH semantics)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    serial_number: str | None = Field(default=None, min_length=3, max_length=100)
    building: str | None = Field(default=None, max_length=255)
    floor: str | None = Field(default=None, max_length=50)
    room: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_critical: bool | None = None
    calibration_last: datetime | None = None
    calibration_next: datetime | None = None
    calibration_interval_days: int | None = Field(default=None, ge=1, le=3650)
    maintenance_interval_days: int | None = Field(default=None, ge=1, le=3650)
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class DeviceTransfer(BaseModel):
    """Request schema for transferring a device to a new location."""

    building: Annotated[str, Field(min_length=1, max_length=255)]
    floor: str | None = Field(default=None, max_length=50)
    room: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    reason: str = Field(default="", max_length=500)
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class MaintenanceScheduleRequest(BaseModel):
    """Request schema for scheduling maintenance."""

    maintenance_type: Annotated[str, Field(min_length=1, max_length=50)]
    scheduled_date: Annotated[str, Field(min_length=1, max_length=50)]
    estimated_duration_hours: int | None = Field(default=None, ge=1)
    technician_id: str | None = None
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class MaintenanceStartRequest(BaseModel):
    """Request schema for starting maintenance."""

    maintenance_type: Annotated[str, Field(min_length=1, max_length=50)]
    technician_id: Annotated[str, Field(min_length=1, max_length=100)]
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class MaintenanceFinishRequest(BaseModel):
    """Request schema for finishing maintenance."""

    next_calibration_date: datetime | None = None
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class CalibrationRequest(BaseModel):
    """Request schema for recording device calibration."""

    calibration_last: Annotated[datetime, Field(description="Date of calibration")]
    calibration_next: Annotated[datetime, Field(description="Next calibration date")]
    calibration_interval_days: Annotated[int, Field(ge=1, le=3650)]
    calibration_certificate: str | None = None
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class OutOfServiceRequest(BaseModel):
    """Request schema for taking device out of service."""

    reason: Annotated[str, Field(min_length=1, max_length=500)]
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class ReturnToServiceRequest(BaseModel):
    """Request schema for returning device to service."""

    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


class DecommissionRequest(BaseModel):
    """Request schema for decommissioning a device."""

    reason: Annotated[str, Field(min_length=1, max_length=500)]
    version: int = Field(description="Expected version for optimistic locking")

    model_config = ConfigDict(extra="forbid")


# ─── Response Schemas ──────────────────────────────────────────────────────────


class DeviceResponse(BaseModel):
    """Response schema for a single device."""

    id: str
    tenant_id: str
    serial_number: str
    manufacturer_name: str
    manufacturer_model: str
    manufacturer_country: str | None
    device_type: str
    name: str
    description: str | None
    is_critical: bool
    status: str
    location_building: str
    location_floor: str | None
    location_room: str | None
    location_department: str | None
    calibration_last: datetime | None
    calibration_next: datetime | None
    calibration_interval_days: int | None
    maintenance_interval_days: int | None
    notes: str | None
    registered_at: datetime | None
    registered_by: str | None
    last_status_change: datetime | None
    version: int
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    """Paginated list response for devices."""

    items: list[DeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class DeviceDeleteResponse(BaseModel):
    """Response schema for device deletion."""

    deleted: bool
    device_id: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: str | None = None
