"""Device domain events.

These events represent significant business occurrences in the Device lifecycle.
They are immutable and published via the Transactional Outbox pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DeviceEvent:
    """Base class for device domain events."""

    device_id: str
    tenant_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    caused_by: str | None = None

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class DeviceRegistered(DeviceEvent):
    """Fired when a new device is registered in the system."""

    serial_number: str = ""
    name: str = ""
    device_type: str = ""
    manufacturer: str = ""
    model: str = ""
    location_building: str = ""
    location_department: str = ""
    is_critical: bool = False


@dataclass(frozen=True)
class DeviceUpdated(DeviceEvent):
    """Fired when device information is modified."""

    changes: dict = field(default_factory=dict)
    version: int = 1


@dataclass(frozen=True)
class DeviceTransferred(DeviceEvent):
    """Fired when a device is transferred to a new location."""

    previous_building: str = ""
    previous_floor: str | None = None
    previous_room: str | None = None
    previous_department: str = ""
    new_building: str = ""
    new_floor: str | None = None
    new_room: str | None = None
    new_department: str | None = None
    transfer_reason: str = ""


@dataclass(frozen=True)
class MaintenanceScheduled(DeviceEvent):
    """Fired when maintenance is scheduled for a device."""

    maintenance_id: str = ""
    maintenance_type: str = ""
    scheduled_date: str = ""
    estimated_duration_hours: int | None = None
    technician_id: str | None = None


@dataclass(frozen=True)
class MaintenanceStarted(DeviceEvent):
    """Fired when maintenance on a device begins."""

    maintenance_type: str = ""
    device_status_before: str = ""
    technician_id: str = ""


@dataclass(frozen=True)
class MaintenanceCompleted(DeviceEvent):
    """Fired when maintenance on a device is completed."""

    maintenance_type: str = ""
    device_status_after: str = "active"
    next_calibration_date: str | None = None
    completed_by: str = ""


@dataclass(frozen=True)
class CalibrationCompleted(DeviceEvent):
    """Fired when device calibration is completed."""

    calibration_certificate: str | None = None
    next_calibration_date: str = ""
    calibrated_by: str = ""
    device_status_after: str = "active"


@dataclass(frozen=True)
class DeviceOutOfService(DeviceEvent):
    """Fired when a device is taken out of service."""

    reason: str = ""
    previous_status: str = ""


@dataclass(frozen=True)
class DeviceReturnedToService(DeviceEvent):
    """Fired when a device is returned to service after being out of service."""

    previous_status: str = ""
    returned_by: str = ""


@dataclass(frozen=True)
class DeviceDecommissioned(DeviceEvent):
    """Fired when a device is permanently decommissioned."""

    reason: str = ""
    decommissioned_by: str = ""
    previous_status: str = ""
