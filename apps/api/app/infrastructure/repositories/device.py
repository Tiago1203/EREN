"""SQLAlchemy implementation of DeviceRepository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.device.domain.entities import Device
from core.device.domain.repositories import DeviceRepository as AbstractDeviceRepository
from core.device.domain.value_objects import (
    DeviceStatus,
    DeviceType,
    LocationInfo,
    ManufacturerInfo,
    SerialNumber,
)
from core.shared import DeviceId, EngineerId, Ok, Result, TenantId
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.device import DeviceModel

if TYPE_CHECKING:
    pass


def _model_to_entity(model: DeviceModel) -> Device:
    """Convert SQLAlchemy model to domain entity."""
    manufacturer = ManufacturerInfo(
        name=model.manufacturer_name,
        model=model.manufacturer_model,
        country_of_origin=model.manufacturer_country,
    )
    serial = SerialNumber(value=model.serial_number)
    device_type = DeviceType(value=model.device_type)
    location = LocationInfo(
        building=model.location_building,
        floor=model.location_floor,
        room=model.location_room,
        department=model.location_department,
    )

    device = Device.__new__(Device)
    device.id = DeviceId(value=str(model.id))
    device.tenant_id = TenantId(value=model.tenant_id)
    device.serial_number = serial
    device.manufacturer = manufacturer
    device.device_type = device_type
    device.name = model.name
    device.location = location
    device.location_id = None
    device.description = model.description
    device.is_critical = model.is_critical
    device.notes = model.notes
    device.calibration = None
    device.maintenance_schedule = None
    device.status = DeviceStatus(value=model.status)
    device.registered_at = model.registered_at
    device.registered_by = (
        EngineerId(value=model.registered_by) if model.registered_by else None
    )
    device.last_status_change = model.last_status_change
    device.version = model.version
    device.created_at = model.created_at
    device.updated_at = model.updated_at
    device._pending_events = []
    device._locked = True
    return device


def _entity_to_model(entity: Device) -> dict[str, Any]:
    return {
        "tenant_id": str(entity.tenant_id),
        "serial_number": str(entity.serial_number),
        "manufacturer_name": entity.manufacturer.name,
        "manufacturer_model": entity.manufacturer.model,
        "manufacturer_country": entity.manufacturer.country_of_origin,
        "device_type": str(entity.device_type),
        "name": entity.name,
        "description": entity.description,
        "is_critical": entity.is_critical,
        "status": str(entity.status),
        "location_building": entity.location.building,
        "location_floor": entity.location.floor,
        "location_room": entity.location.room,
        "location_department": entity.location.department,
        "notes": entity.notes,
        "registered_by": str(entity.registered_by) if entity.registered_by else None,
        "version": entity.version,
    }


class DeviceRepositoryImpl(AbstractDeviceRepository):
    """SQLAlchemy implementation of DeviceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, device: Device) -> Result[Device, str]:
        try:
            existing = await self._session.get(DeviceModel, device.id.value)
            data = _entity_to_model(device)
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.version = device.version
            else:
                model = DeviceModel(id=device.id.value, **data)
                self._session.add(model)
            await self._session.flush()
            return Ok(device)
        except Exception as e:
            return Ok(str(e))

    async def get_by_id(self, device_id: DeviceId) -> Result[Device | None, str]:
        try:
            model = await self._session.get(DeviceModel, device_id.value)
            return Ok(_model_to_entity(model) if model else None)
        except Exception:
            return Ok(None)

    async def get_by_serial(
        self, serial_number: str, tenant_id: TenantId
    ) -> Result[Device | None, str]:
        try:
            stmt = select(DeviceModel).where(
                DeviceModel.serial_number == serial_number,
                DeviceModel.tenant_id == str(tenant_id),
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return Ok(_model_to_entity(model) if model else None)
        except Exception:
            return Ok(None)

    async def get_by_tenant(
        self, tenant_id: TenantId, limit: int = 100, offset: int = 0
    ) -> Result[list[Device], str]:
        try:
            stmt = (
                select(DeviceModel)
                .where(DeviceModel.tenant_id == str(tenant_id))
                .limit(limit)
                .offset(offset)
                .order_by(DeviceModel.created_at.desc())
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_status(
        self, tenant_id: TenantId, status: str, limit: int = 50
    ) -> Result[list[Device], str]:
        try:
            stmt = (
                select(DeviceModel)
                .where(DeviceModel.tenant_id == str(tenant_id))
                .where(DeviceModel.status == status)
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_location(
        self,
        tenant_id: TenantId,
        building: str,
        floor: str | None = None,
        department: str | None = None,
    ) -> Result[list[Device], str]:
        try:
            stmt = select(DeviceModel).where(
                DeviceModel.tenant_id == str(tenant_id),
                DeviceModel.location_building == building,
            )
            if floor:
                stmt = stmt.where(DeviceModel.location_floor == floor)
            if department:
                stmt = stmt.where(DeviceModel.location_department == department)
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_critical_devices(
        self, tenant_id: TenantId
    ) -> Result[list[Device], str]:
        try:
            stmt = select(DeviceModel).where(
                DeviceModel.tenant_id == str(tenant_id),
                DeviceModel.is_critical == True,  # noqa: E712
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_needing_maintenance(
        self, tenant_id: TenantId
    ) -> Result[list[Device], str]:
        try:
            stmt = select(DeviceModel).where(
                DeviceModel.tenant_id == str(tenant_id),
                DeviceModel.status.in_(["in_maintenance", "out_of_service"]),
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_calibration_due(
        self, tenant_id: TenantId, days_threshold: int = 30
    ) -> Result[list[Device], str]:
        try:
            stmt = select(DeviceModel).where(
                DeviceModel.tenant_id == str(tenant_id),
                DeviceModel.status == "calibration_due",
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def delete(self, device_id: DeviceId) -> Result[bool, str]:
        try:
            model = await self._session.get(DeviceModel, device_id.value)
            if model:
                await self._session.delete(model)
                await self._session.flush()
            return Ok(True)
        except Exception:
            return Ok(False)
