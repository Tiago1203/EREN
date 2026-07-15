"""EREN Device Context.

This package contains the Device bounded context,
which handles biomedical devices in hospitals.

Architecture:
- domain/entities: Device aggregate
- domain/value_objects: DeviceStatus, LocationInfo, etc.
- domain/services: DeviceService
- domain/repositories: Repository interfaces
"""

from .domain import (
    CalibrationInfo,
    Device,
    DeviceRepository,
    DeviceService,
    DeviceStatus,
    DeviceType,
    LocationInfo,
    ManufacturerInfo,
    MaintenanceSchedule,
    SerialNumber,
)

__all__ = [
    # Entities
    "Device",
    # Value Objects
    "DeviceStatus",
    "DeviceType",
    "SerialNumber",
    "ManufacturerInfo",
    "LocationInfo",
    "CalibrationInfo",
    "MaintenanceSchedule",
    # Services
    "DeviceService",
    # Repositories
    "DeviceRepository",
]
