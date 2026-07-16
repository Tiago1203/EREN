"""API schemas (Pydantic v2 DTOs) for request/response bodies."""

from app.schemas.device import (
    CalibrationRequest,
    DecommissionRequest,
    DeviceCreate,
    DeviceDeleteResponse,
    DeviceListResponse,
    DeviceResponse,
    DeviceTransfer,
    DeviceTypeEnum,
    DeviceUpdate,
    ErrorResponse,
    MaintenanceFinishRequest,
    MaintenanceScheduleRequest,
    MaintenanceStartRequest,
    OutOfServiceRequest,
    ReturnToServiceRequest,
    SortOrder,
)
from app.schemas.health import HealthResponse

__all__ = [
    # Device
    "CalibrationRequest",
    "DecommissionRequest",
    "DeviceCreate",
    "DeviceDeleteResponse",
    "DeviceListResponse",
    "DeviceResponse",
    "DeviceTransfer",
    "DeviceTypeEnum",
    "DeviceUpdate",
    "ErrorResponse",
    "HealthResponse",
    "MaintenanceFinishRequest",
    "MaintenanceScheduleRequest",
    "MaintenanceStartRequest",
    "OutOfServiceRequest",
    "ReturnToServiceRequest",
    "SortOrder",
]
