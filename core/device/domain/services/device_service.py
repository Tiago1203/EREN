"""Domain service for Device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.shared import (
    DeviceId,
    EngineerId,
    LocationId,
    Result,
    TenantId,
)

from ..entities import Device
from ..repositories.device_repository import DeviceRepository
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


class DeviceService:
    """Domain service for Device operations."""

    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    async def register_device(
        self,
        tenant_id: TenantId,
        serial_number: str,
        manufacturer_name: str,
        manufacturer_model: str,
        device_type: str,
        name: str,
        building: str,
        floor: str,
        room: str,
        department: str,
        is_critical: bool = False,
        calibration_interval_days: int | None = None,
        maintenance_interval_days: int | None = None,
        registered_by: EngineerId | None = None,
    ) -> Result[Device, str]:
        """Register a new device."""
        # Check for duplicate serial number
        serial_check = await self._repository.get_by_serial(serial_number, tenant_id)
        if serial_check.is_ok() and serial_check.unwrap() is not None:
            return Result.Err(f"Device with serial {serial_number} already exists")

        # Create value objects
        serial = DeviceSerialNumber.from_string(serial_number)
        manufacturer = ManufacturerInfo(
            name=manufacturer_name,
            model=manufacturer_model,
            manufacturing_date="",  # Would be provided in real scenario
        )
        device_type_vo = DeviceType(value=device_type, risk_classification="class_b")
        location = LocationInfo(
            building=building,
            floor=floor,
            room=room,
            department=department,
        )

        # Create calibration if interval provided
        calibration = None
        if calibration_interval_days:
            calibration = CalibrationInfo(
                last_calibration_date="",
                next_calibration_date="",
                calibration_interval_days=calibration_interval_days,
            )

        # Create maintenance schedule if interval provided
        maintenance = None
        if maintenance_interval_days:
            maintenance = MaintenanceSchedule.preventive(maintenance_interval_days)

        # Create device
        device = Device(
            id=DeviceId.generate(),
            tenant_id=tenant_id,
            serial_number=serial,
            manufacturer=manufacturer,
            device_type=device_type_vo,
            name=name,
            location=location,
            is_critical=is_critical,
            calibration=calibration,
            maintenance_schedule=maintenance,
            registered_by=registered_by,
        )

        return await self._repository.save(device)

    async def activate_device(
        self,
        device_id: DeviceId,
        activated_by: EngineerId,
    ) -> Result[Device, str]:
        """Activate a device."""
        result = await self._repository.get_by_id(device_id)
        if result.is_err():
            return result

        device = result.unwrap()
        if device is None:
            return Result.Err(f"Device {device_id} not found")

        try:
            device.activate(activated_by=activated_by, expected_version=device.version)
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(device)

    async def take_out_of_service(
        self,
        device_id: DeviceId,
        reason: str,
        taken_by: EngineerId,
    ) -> Result[Device, str]:
        """Take a device out of service."""
        result = await self._repository.get_by_id(device_id)
        if result.is_err():
            return result

        device = result.unwrap()
        if device is None:
            return Result.Err(f"Device {device_id} not found")

        try:
            device.take_out_of_service(
                reason=reason,
                taken_by=taken_by,
                expected_version=device.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(device)

    async def relocate_device(
        self,
        device_id: DeviceId,
        new_building: str,
        new_floor: str,
        new_room: str,
        new_department: str,
        relocated_by: EngineerId,
    ) -> Result[Device, str]:
        """Relocate a device."""
        result = await self._repository.get_by_id(device_id)
        if result.is_err():
            return result

        device = result.unwrap()
        if device is None:
            return Result.Err(f"Device {device_id} not found")

        new_location = LocationInfo(
            building=new_building,
            floor=new_floor,
            room=new_room,
            department=new_department,
        )

        try:
            device.relocate(
                new_location=new_location,
                relocated_by=relocated_by,
                expected_version=device.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(device)

    async def decommission_device(
        self,
        device_id: DeviceId,
        reason: str,
        decommissioned_by: EngineerId,
    ) -> Result[Device, str]:
        """Decommission a device."""
        result = await self._repository.get_by_id(device_id)
        if result.is_err():
            return result

        device = result.unwrap()
        if device is None:
            return Result.Err(f"Device {device_id} not found")

        try:
            device.decommission(
                reason=reason,
                decommissioned_by=decommissioned_by,
                expected_version=device.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(device)

    async def get_operational_devices(
        self,
        tenant_id: TenantId,
    ) -> Result[list[Device], str]:
        """Get all operational devices."""
        result = await self._repository.get_by_tenant(tenant_id)
        if result.is_err():
            return result

        devices = result.unwrap()
        operational = [d for d in devices if d.is_operational()]
        return Result.Ok(operational)

    async def get_critical_devices_needing_attention(
        self,
        tenant_id: TenantId,
    ) -> Result[list[Device], str]:
        """Get critical devices that need attention."""
        result = await self._repository.get_critical_devices(tenant_id)
        if result.is_err():
            return result

        devices = result.unwrap()
        needs_attention = [d for d in devices if d.requires_maintenance()]
        return Result.Ok(needs_attention)
