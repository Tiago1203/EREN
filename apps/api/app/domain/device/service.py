"""Device application service.

Orchestrates domain operations, persistence, and event publishing for devices.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from app.domain.device.events import (
    CalibrationCompleted,
    DeviceDecommissioned,
    DeviceEvent,
    DeviceOutOfService,
    DeviceRegistered,
    DeviceReturnedToService,
    DeviceTransferred,
    DeviceUpdated,
    MaintenanceCompleted,
    MaintenanceScheduled,
    MaintenanceStarted,
)
from app.domain.device.repository import DeviceRepository

if TYPE_CHECKING:
    from app.infrastructure.messaging.outbox import TransactionalOutbox
    from app.infrastructure.models.device import DeviceModel

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class DeviceService:
    """Application service for Device lifecycle operations.

    Coordinates:
    1. Domain model mutations (via aggregate methods)
    2. Persistence (via repository)
    3. Event publishing (via TransactionalOutbox)
    4. Business validations
    5. Cache invalidation

    Does NOT contain:
    - HTTP handling (router)
    - Authentication (middleware)
    - Infrastructure details
    """

    repository: DeviceRepository
    outbox: TransactionalOutbox

    # ─── Device Registration ─────────────────────────────────────────────────

    async def register_device(
        self,
        *,
        tenant_id: str,
        serial_number: str,
        name: str,
        device_type: str,
        manufacturer_name: str,
        manufacturer_model: str,
        manufacturer_country: str | None = None,
        building: str,
        floor: str | None = None,
        room: str | None = None,
        department: str | None = None,
        description: str | None = None,
        is_critical: bool = False,
        calibration_last: datetime | None = None,
        calibration_next: datetime | None = None,
        calibration_interval_days: int | None = None,
        maintenance_interval_days: int | None = None,
        registered_by: str | None = None,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Register a new device.

        Raises:
            ValueError: If serial number is already in use for this tenant.
        """
        # Check for duplicate serial number
        existing = await self.repository.get_by_serial(serial_number, tenant_id)
        if existing is not None:
            raise ValueError(
                f"Device with serial number '{serial_number}' already exists "
                f"for this tenant (device_id={existing.id})."
            )

        device_id = str(uuid.uuid4())

        # Save to database
        device = await self.repository.save(
            tenant_id=tenant_id,
            device_id=device_id,
            serial_number=serial_number,
            name=name,
            device_type=device_type,
            manufacturer_name=manufacturer_name,
            manufacturer_model=manufacturer_model,
            manufacturer_country=manufacturer_country,
            building=building,
            floor=floor,
            room=room,
            department=department,
            description=description,
            is_critical=is_critical,
            calibration_last=calibration_last,
            calibration_next=calibration_next,
            calibration_interval_days=calibration_interval_days,
            maintenance_interval_days=maintenance_interval_days,
            registered_by=registered_by,
            status="registered",
        )

        # Publish domain event via outbox
        event = DeviceRegistered(
            device_id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            name=name,
            device_type=device_type,
            manufacturer=manufacturer_name,
            model=manufacturer_model,
            location_building=building,
            location_department=department or "",
            is_critical=is_critical,
            correlation_id=correlation_id,
            caused_by=registered_by,
        )
        self._publish_event(event)

        logger.info(
            "Device registered",
            extra={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "serial_number": serial_number,
                "correlation_id": correlation_id,
            },
        )
        return device

    # ─── Device Update ───────────────────────────────────────────────────────

    async def update_device(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        correlation_id: str | None = None,
        updated_by: str | None = None,
        **fields: Any,
    ) -> DeviceModel | None:
        """Update device fields with optimistic locking.

        Raises:
            ValueError: If device not found or version mismatch.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found for tenant '{tenant_id}'.")

        if device.version != expected_version:
            raise ValueError(
                f"Device '{device_id}' version mismatch: expected {expected_version}, "
                f"found {device.version}. Concurrent modification detected."
            )

        # Check for duplicate serial if being updated
        if "serial_number" in fields:
            existing = await self.repository.get_by_serial(fields["serial_number"], tenant_id)
            if existing is not None and str(existing.id) != device_id:
                raise ValueError(f"Serial number '{fields['serial_number']}' already in use.")

        # Filter allowed update fields
        allowed = {
            "name",
            "description",
            "is_critical",
            "location_building",
            "location_floor",
            "location_room",
            "location_department",
            "calibration_last",
            "calibration_next",
            "calibration_interval_days",
            "maintenance_interval_days",
            "serial_number",
        }
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError(f"Device '{device_id}' concurrent modification detected.")

        event = DeviceUpdated(
            device_id=device_id,
            tenant_id=tenant_id,
            changes=updates,
            version=expected_version + 1,
            correlation_id=correlation_id,
            caused_by=updated_by,
        )
        self._publish_event(event)

        logger.info(
            "Device updated",
            extra={"device_id": device_id, "tenant_id": tenant_id, "changes": updates},
        )
        return updated

    # ─── Device Transfer (Relocation) ────────────────────────────────────────

    async def transfer_device(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        new_building: str,
        new_floor: str | None = None,
        new_room: str | None = None,
        new_department: str | None = None,
        transfer_reason: str = "",
        transferred_by: str | None = None,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Transfer device to a new location.

        Raises:
            ValueError: If device is decommissioned or not found.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status == "decommissioned":
            raise ValueError(f"Cannot transfer decommissioned device '{device_id}'.")

        previous = {
            "building": device.location_building,
            "floor": device.location_floor,
            "room": device.location_room,
            "department": device.location_department,
        }

        updates = {
            "location_building": new_building,
            "location_floor": new_floor,
            "location_room": new_room,
            "location_department": new_department,
        }

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = DeviceTransferred(
            device_id=device_id,
            tenant_id=tenant_id,
            previous_building=previous.get("building") or "",
            previous_floor=previous.get("floor"),
            previous_room=previous.get("room"),
            previous_department=previous.get("department") or "",
            new_building=new_building,
            new_floor=new_floor,
            new_room=new_room,
            new_department=new_department or "",
            transfer_reason=transfer_reason,
            correlation_id=correlation_id,
            caused_by=transferred_by,
        )
        self._publish_event(event)

        logger.info(
            "Device transferred",
            extra={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "from": previous,
                "to": updates,
            },
        )
        return updated

    # ─── Maintenance Operations ───────────────────────────────────────────────

    async def schedule_maintenance(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        maintenance_type: str,
        scheduled_date: str,
        estimated_duration_hours: int | None = None,
        technician_id: str | None = None,
        scheduled_by: str | None = None,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Schedule maintenance for a device.

        Raises:
            ValueError: If device is decommissioned or already in maintenance.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")
        if device.status == "decommissioned":
            raise ValueError("Cannot schedule maintenance on decommissioned device.")
        if device.status == "in_maintenance":
            raise ValueError(f"Device '{device_id}' is already in maintenance.")

        maintenance_id = str(uuid.uuid4())

        event = MaintenanceScheduled(
            device_id=device_id,
            tenant_id=tenant_id,
            maintenance_id=maintenance_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            estimated_duration_hours=estimated_duration_hours,
            technician_id=technician_id,
            correlation_id=correlation_id,
            caused_by=scheduled_by,
        )
        self._publish_event(event)

        logger.info(
            "Maintenance scheduled",
            extra={
                "device_id": device_id,
                "maintenance_id": maintenance_id,
                "tenant_id": tenant_id,
            },
        )
        return device

    async def start_maintenance(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        maintenance_type: str,
        technician_id: str,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Start maintenance on a device.

        Raises:
            ValueError: If device is decommissioned or already in maintenance.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status == "decommissioned":
            raise ValueError("Cannot start maintenance on decommissioned device.")
        if device.status == "in_maintenance":
            raise ValueError(f"Device '{device_id}' is already in maintenance.")

        previous_status = device.status
        updates = {"status": "in_maintenance"}

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = MaintenanceStarted(
            device_id=device_id,
            tenant_id=tenant_id,
            maintenance_type=maintenance_type,
            device_status_before=previous_status,
            technician_id=technician_id,
            correlation_id=correlation_id,
            caused_by=technician_id,
        )
        self._publish_event(event)

        logger.info(
            "Maintenance started",
            extra={"device_id": device_id, "tenant_id": tenant_id},
        )
        return updated

    async def finish_maintenance(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        completed_by: str,
        next_calibration_date: datetime | None = None,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Finish maintenance and return device to active status.

        Raises:
            ValueError: If device is not currently in maintenance.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status != "in_maintenance":
            raise ValueError(
                f"Device '{device_id}' is not in maintenance (status={device.status})."
            )

        updates: dict[str, Any] = {"status": "active"}
        if next_calibration_date:
            updates["calibration_next"] = next_calibration_date

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = MaintenanceCompleted(
            device_id=device_id,
            tenant_id=tenant_id,
            maintenance_type="general",
            device_status_after="active",
            next_calibration_date=(
                next_calibration_date.isoformat() if next_calibration_date else None
            ),
            completed_by=completed_by,
            correlation_id=correlation_id,
            caused_by=completed_by,
        )
        self._publish_event(event)

        logger.info(
            "Maintenance completed",
            extra={"device_id": device_id, "tenant_id": tenant_id},
        )
        return updated

    # ─── Calibration ─────────────────────────────────────────────────────────

    async def calibrate_device(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        calibration_last: datetime,
        calibration_next: datetime,
        calibration_interval_days: int,
        calibration_certificate: str | None = None,
        calibrated_by: str,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Record device calibration.

        Raises:
            ValueError: If device is decommissioned or not found.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status == "decommissioned":
            raise ValueError(f"Cannot calibrate decommissioned device '{device_id}'.")

        updates = {
            "calibration_last": calibration_last,
            "calibration_next": calibration_next,
            "calibration_interval_days": calibration_interval_days,
            "status": "active",  # Return to active if was calibration_due
        }

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = CalibrationCompleted(
            device_id=device_id,
            tenant_id=tenant_id,
            calibration_certificate=calibration_certificate,
            next_calibration_date=calibration_next.isoformat(),
            calibrated_by=calibrated_by,
            device_status_after="active",
            correlation_id=correlation_id,
            caused_by=calibrated_by,
        )
        self._publish_event(event)

        logger.info(
            "Calibration completed",
            extra={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "calibration_next": calibration_next.isoformat(),
            },
        )
        return updated

    # ─── Out of Service ──────────────────────────────────────────────────────

    async def take_out_of_service(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        reason: str,
        taken_by: str,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Take device out of service.

        Raises:
            ValueError: If device is already out of service or decommissioned.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status == "out_of_service":
            raise ValueError(f"Device '{device_id}' is already out of service.")
        if device.status == "decommissioned":
            raise ValueError(f"Device '{device_id}' is decommissioned.")

        previous_status = device.status
        updates = {"status": "out_of_service"}

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = DeviceOutOfService(
            device_id=device_id,
            tenant_id=tenant_id,
            reason=reason,
            previous_status=previous_status,
            correlation_id=correlation_id,
            caused_by=taken_by,
        )
        self._publish_event(event)

        logger.info(
            "Device out of service",
            extra={"device_id": device_id, "tenant_id": tenant_id, "reason": reason},
        )
        return updated

    # ─── Return to Service ───────────────────────────────────────────────────

    async def return_to_service(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        returned_by: str,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Return device to active service.

        Validates that the device has a valid calibration before returning.

        Raises:
            ValueError: If device is not out of service, has no calibration,
                       or calibration is overdue.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status != "out_of_service":
            raise ValueError(
                f"Device '{device_id}' is not out of service (status={device.status})."
            )

        # Validate calibration
        if device.calibration_next is None:
            raise ValueError(
                f"Cannot return device '{device_id}' to service: no calibration date set."
            )
        if device.calibration_next < _utcnow():
            raise ValueError(
                f"Cannot return device '{device_id}' to service: calibration is overdue."
            )

        previous_status = device.status
        updates = {"status": "active"}

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = DeviceReturnedToService(
            device_id=device_id,
            tenant_id=tenant_id,
            previous_status=previous_status,
            returned_by=returned_by,
            correlation_id=correlation_id,
            caused_by=returned_by,
        )
        self._publish_event(event)

        logger.info(
            "Device returned to service",
            extra={"device_id": device_id, "tenant_id": tenant_id},
        )
        return updated

    # ─── Decommission ────────────────────────────────────────────────────────

    async def decommission_device(
        self,
        *,
        device_id: str,
        tenant_id: str,
        expected_version: int,
        reason: str,
        decommissioned_by: str,
        correlation_id: str | None = None,
    ) -> DeviceModel:
        """Permanently decommission a device.

        Raises:
            ValueError: If device is already decommissioned.
        """
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            raise ValueError(f"Device '{device_id}' not found.")

        if device.status == "decommissioned":
            raise ValueError(f"Device '{device_id}' is already decommissioned.")

        previous_status = device.status
        updates = {"status": "decommissioned"}

        updated = await self.repository.update(device, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = DeviceDecommissioned(
            device_id=device_id,
            tenant_id=tenant_id,
            reason=reason,
            decommissioned_by=decommissioned_by,
            previous_status=previous_status,
            correlation_id=correlation_id,
            caused_by=decommissioned_by,
        )
        self._publish_event(event)

        logger.info(
            "Device decommissioned",
            extra={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "reason": reason,
            },
        )
        return updated

    # ─── Queries ─────────────────────────────────────────────────────────────

    async def get_device(self, device_id: str, tenant_id: str) -> DeviceModel | None:
        """Get a device by ID within tenant scope."""
        return await self.repository.get_by_id(device_id, tenant_id)

    async def get_device_by_serial(self, serial_number: str, tenant_id: str) -> DeviceModel | None:
        """Get a device by serial number within tenant scope."""
        return await self.repository.get_by_serial(serial_number, tenant_id)

    async def list_devices(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status: str | None = None,
        device_type: str | None = None,
        building: str | None = None,
        department: str | None = None,
        is_critical: bool | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[DeviceModel], int]:
        """List devices with pagination and filters."""
        return await self.repository.list_by_tenant(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            status_filter=status,
            device_type_filter=device_type,
            building_filter=building,
            department_filter=department,
            is_critical=is_critical,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # ─── Delete ──────────────────────────────────────────────────────────────

    async def delete_device(self, device_id: str, tenant_id: str) -> bool:
        """Delete a device (hard delete — use decommission for normal lifecycle)."""
        device = await self.repository.get_by_id(device_id, tenant_id)
        if device is None:
            return False

        logger.info(
            "Device deleted",
            extra={"device_id": device_id, "tenant_id": tenant_id},
        )
        return await self.repository.delete(device_id, tenant_id)

    # ─── Internal ────────────────────────────────────────────────────────────

    def _publish_event(self, event: DeviceEvent) -> None:
        """Publish a domain event to the transactional outbox."""
        self.outbox.append(
            event_type=event.event_type,
            payload=event.to_dict()
            if hasattr(event, "to_dict")
            else {
                "device_id": event.device_id,
                "tenant_id": event.tenant_id,
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat(),
                "correlation_id": event.correlation_id,
                "caused_by": event.caused_by,
                # Add all dataclass fields
                **{f.name: getattr(event, f.name) for f in event.__dataclass_fields__.values()},
            },
            aggregate_type="Device",
            correlation_id=event.correlation_id,
        )
