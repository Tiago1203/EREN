"""Device aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import (
    AggregateRoot,
    DeviceId,
    EngineerId,
    LocationId,
    TenantId,
)
from core.PHASE_1.infrastructure.shared.events import (
    DeviceLocationChanged,
    DeviceRegistered,
    DeviceStatusChanged,
)

from ..value_objects import (
    CalibrationInfo,
    DeviceStatus,
    DeviceType,
    LocationInfo,
    ManufacturerInfo,
    MaintenanceSchedule,
    SerialNumber,
)

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class Device(AggregateRoot):
    """Biomedical Device aggregate root.

    Represents a physical medical device in a hospital.
    Each device has a lifecycle, location, and maintenance schedule.

    Invariants:
    1. Device must have valid serial number
    2. Device must have valid manufacturer info
    3. Location must be specified
    """

    # Identity
    tenant_id: TenantId
    serial_number: SerialNumber
    manufacturer: ManufacturerInfo

    # Classification
    device_type: DeviceType
    name: str

    # Location
    location: LocationInfo
    location_id: LocationId | None = None

    # Metadata (defaults)
    description: str | None = None
    is_critical: bool = False
    notes: str | None = None
    calibration: CalibrationInfo | None = None
    maintenance_schedule: MaintenanceSchedule | None = None

    # Status
    status: DeviceStatus = field(default_factory=DeviceStatus.registered)

    # Audit (defaults)
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    registered_by: EngineerId | None = None
    last_status_change: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate()
        # Publish registration event
        self.add_event(
            DeviceRegistered(
                device_id=str(self.id),
                tenant_id=str(self.tenant_id),
                serial_number=str(self.serial_number),
                model=self.manufacturer.model,
                manufacturer=self.manufacturer.name,
                registered_by=str(self.registered_by) if self.registered_by else "",
            ),
        )

    def _validate(self) -> None:
        """Validate device invariants."""
        if not self.name or not self.name.strip():
            msg = "Device name cannot be empty"
            raise ValueError(msg)

    def activate(
        self,
        activated_by: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Activate device for clinical use."""
        self._assert_version(expected_version)

        if self.status == DeviceStatus.decommissioned():
            msg = "Cannot activate decommissioned device"
            raise ValueError(msg)

        old_status = self.status
        self._unlock_for_mutation()
        self.status = DeviceStatus.active()
        self.last_status_change = datetime.now(UTC)
        self._relock_after_mutation()

        self._publish_status_change(old_status, self.status)

    def take_out_of_service(
        self,
        reason: str,
        taken_by: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Take device out of service."""
        self._assert_version(expected_version)

        old_status = self.status
        self._unlock_for_mutation()
        self.status = DeviceStatus.out_of_service()
        self.notes = (self.notes or "") + f"\nOut of service: {reason}"
        self.last_status_change = datetime.now(UTC)
        self._relock_after_mutation()

        self._publish_status_change(old_status, self.status)

    def start_maintenance(
        self,
        maintenance_type: str,
        engineer_id: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Start maintenance on device."""
        self._assert_version(expected_version)

        if self.status == DeviceStatus.decommissioned():
            msg = "Cannot perform maintenance on decommissioned device"
            raise ValueError(msg)

        old_status = self.status
        self._unlock_for_mutation()
        self.status = DeviceStatus.in_maintenance()
        self.notes = (self.notes or "") + f"\nMaintenance started: {maintenance_type}"
        self.last_status_change = datetime.now(UTC)
        self._relock_after_mutation()

        self._publish_status_change(old_status, self.status)

    def complete_maintenance(
        self,
        completed_by: EngineerId,
        next_calibration_date: str | None = None,
        expected_version: int = 1,
    ) -> None:
        """Complete maintenance and return to active status."""
        self._assert_version(expected_version)

        if self.status != DeviceStatus.in_maintenance():
            msg = "Device is not in maintenance"
            raise ValueError(msg)

        old_status = self.status
        self._unlock_for_mutation()
        self.status = DeviceStatus.active()
        if next_calibration_date and self.calibration:
            self.calibration = CalibrationInfo(
                last_calibration_date=self.calibration.next_calibration_date,
                next_calibration_date=next_calibration_date,
                calibration_interval_days=self.calibration.calibration_interval_days,
            )
        self.last_status_change = datetime.now(UTC)
        self._relock_after_mutation()

        self._publish_status_change(old_status, self.status)

    def mark_calibration_due(
        self,
        expected_version: int = 1,
    ) -> None:
        """Mark that calibration is due."""
        self._assert_version(expected_version)

        if self.status == DeviceStatus.active():
            old_status = self.status
            self._unlock_for_mutation()
            self.status = DeviceStatus.calibration_due()
            self.last_status_change = datetime.now(UTC)
            self._relock_after_mutation()
            self._publish_status_change(old_status, self.status)

    def decommission(
        self,
        reason: str,
        decommissioned_by: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Decommission the device permanently."""
        self._assert_version(expected_version)

        old_status = self.status
        self._unlock_for_mutation()
        self.status = DeviceStatus.decommissioned()
        self.notes = (self.notes or "") + f"\nDecommissioned: {reason}"
        self.last_status_change = datetime.now(UTC)
        self._relock_after_mutation()

        self._publish_status_change(old_status, self.status)

    def relocate(
        self,
        new_location: LocationInfo,
        relocated_by: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Relocate device to a new location."""
        self._assert_version(expected_version)

        old_location = self.location
        self._unlock_for_mutation()
        self.location = new_location
        self._relock_after_mutation()

        self.add_event(
            DeviceLocationChanged(
                device_id=str(self.id),
                previous_location=old_location.full_address(),
                new_location=new_location.full_address(),
                changed_by=str(relocated_by),
            ),
        )

    def update_calibration(
        self,
        calibration: CalibrationInfo,
        updated_by: EngineerId,
        expected_version: int = 1,
    ) -> None:
        """Update calibration information."""
        self._assert_version(expected_version)

        self._unlock_for_mutation()
        self.calibration = calibration
        if self.status == DeviceStatus.calibration_due():
            self.status = DeviceStatus.active()
        self._relock_after_mutation()

    def _publish_status_change(
        self,
        old_status: DeviceStatus,
        new_status: DeviceStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> None:
        """Publish status change event."""
        self.add_event(
            DeviceStatusChanged(
                device_id=str(self.id),
                previous_status=str(old_status),
                new_status=str(new_status),
                reason=reason,
                changed_by=changed_by,
            ),
        )

    def is_operational(self) -> bool:
        """Check if device is currently operational."""
        return self.status.is_operational()

    def requires_maintenance(self) -> bool:
        """Check if device requires maintenance attention."""
        return self.status.requires_attention()

    def is_high_risk_device(self) -> bool:
        """Check if device is high risk."""
        return self.device_type.is_high_risk()

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update(
            {
                "tenant_id": str(self.tenant_id),
                "serial_number": str(self.serial_number),
                "manufacturer_name": self.manufacturer.name,
                "manufacturer_model": self.manufacturer.model,
                "manufacturer_country": self.manufacturer.country_of_origin,
                "device_type": str(self.device_type),
                "name": self.name,
                "description": self.description,
                "status": str(self.status),
                "location_building": self.location.building,
                "location_floor": self.location.floor,
                "location_room": self.location.room,
                "location_department": self.location.department,
                "is_critical": self.is_critical,
                "notes": self.notes,
                "registered_at": self.registered_at.isoformat(),
                "registered_by": str(self.registered_by) if self.registered_by else None,
                "last_status_change": self.last_status_change.isoformat(),
            },
        )
        return base
