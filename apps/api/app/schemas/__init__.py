"""API schemas (Pydantic v2 DTOs) for request/response bodies."""

from app.schemas.device import (
    CalibrationRequest,
    DecommissionRequest,
    DeviceCreate,
    DeviceDeleteResponse,
    DeviceListResponse,
    DeviceResponse,
    DeviceTransfer,
    DeviceUpdate,
    DeviceTypeEnum,
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
    "HealthResponse",
    # Device
    "DeviceResponse",
    "DeviceListResponse",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceTransfer",
    "DeviceDeleteResponse",
    "MaintenanceScheduleRequest",
    "MaintenanceStartRequest",
    "MaintenanceFinishRequest",
    "CalibrationRequest",
    "OutOfServiceRequest",
    "ReturnToServiceRequest",
    "DecommissionRequest",
    "DeviceTypeEnum",
    "SortOrder",
    "ErrorResponse",
]
