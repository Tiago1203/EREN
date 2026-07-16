"""Device repository interface and SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.infrastructure.models.device import DeviceModel


class DeviceRepository(Protocol):
    """Protocol for device persistence operations."""

    async def save(
        self,
        tenant_id: str,
        device_id: str,
        serial_number: str,
        name: str,
        device_type: str,
        manufacturer_name: str,
        manufacturer_model: str,
        manufacturer_country: str | None,
        building: str,
        floor: str | None,
        room: str | None,
        department: str | None,
        description: str | None,
        is_critical: bool,
        calibration_last: datetime | None,
        calibration_next: datetime | None,
        calibration_interval_days: int | None,
        maintenance_interval_days: int | None,
        registered_by: str | None,
        status: str,
        **kwargs: Any,
    ) -> DeviceModel:
        ...

    async def get_by_id(self, device_id: str, tenant_id: str) -> DeviceModel | None:
        ...

    async def get_by_serial(
        self, serial_number: str, tenant_id: str
    ) -> DeviceModel | None:
        ...

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        device_type_filter: str | None = None,
        building_filter: str | None = None,
        department_filter: str | None = None,
        is_critical: bool | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[DeviceModel], int]:
        ...

    async def update(
        self,
        device: DeviceModel,
        expected_version: int,
        **updates: Any,
    ) -> DeviceModel | None:
        ...

    async def delete(self, device_id: str, tenant_id: str) -> bool:
        ...


@dataclass
class SQLAlchemyDeviceRepository:
    """SQLAlchemy implementation of DeviceRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(
        self,
        tenant_id: str,
        device_id: str,
        serial_number: str,
        name: str,
        device_type: str,
        manufacturer_name: str,
        manufacturer_model: str,
        manufacturer_country: str | None,
        building: str,
        floor: str | None,
        room: str | None,
        department: str | None,
        description: str | None,
        is_critical: bool,
        calibration_last: datetime | None,
        calibration_next: datetime | None,
        calibration_interval_days: int | None,
        maintenance_interval_days: int | None,
        registered_by: str | None,
        status: str,
        **kwargs: Any,
    ) -> DeviceModel:
        from uuid import UUID

        from app.infrastructure.models.device import DeviceModel

        model = DeviceModel(
            id=UUID(device_id),
            tenant_id=tenant_id,
            serial_number=serial_number,
            name=name,
            device_type=device_type,
            manufacturer_name=manufacturer_name,
            manufacturer_model=manufacturer_model,
            manufacturer_country=manufacturer_country,
            location_building=building,
            location_floor=floor,
            location_room=room,
            location_department=department,
            description=description,
            is_critical=is_critical,
            calibration_last=calibration_last,
            calibration_next=calibration_next,
            calibration_interval_days=calibration_interval_days,
            maintenance_interval_days=maintenance_interval_days,
            registered_by=registered_by,
            status=status,
        )
        self._db.add(model)
        await self._db.flush()
        return model

    async def get_by_id(
        self, device_id: str, tenant_id: str
    ) -> DeviceModel | None:
        from uuid import UUID

        from app.infrastructure.models.device import DeviceModel

        result = await self._db.execute(
            select(DeviceModel).where(
                DeviceModel.id == UUID(device_id),
                DeviceModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_serial(
        self, serial_number: str, tenant_id: str
    ) -> DeviceModel | None:
        from app.infrastructure.models.device import DeviceModel

        result = await self._db.execute(
            select(DeviceModel).where(
                DeviceModel.serial_number == serial_number,
                DeviceModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        device_type_filter: str | None = None,
        building_filter: str | None = None,
        department_filter: str | None = None,
        is_critical: bool | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[DeviceModel], int]:
        from app.infrastructure.models.device import DeviceModel

        base = select(DeviceModel).where(DeviceModel.tenant_id == tenant_id)

        if status_filter:
            base = base.where(DeviceModel.status == status_filter)
        if device_type_filter:
            base = base.where(DeviceModel.device_type == device_type_filter)
        if building_filter:
            base = base.where(DeviceModel.location_building == building_filter)
        if department_filter:
            base = base.where(DeviceModel.location_department == department_filter)
        if is_critical is not None:
            base = base.where(DeviceModel.is_critical == is_critical)
        if search_query:
            search = f"%{search_query}%"
            base = base.where(
                DeviceModel.name.ilike(search)
                | DeviceModel.serial_number.ilike(search)
                | DeviceModel.manufacturer_name.ilike(search)
                | DeviceModel.manufacturer_model.ilike(search)
            )

        # Count
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        sort_col = getattr(DeviceModel, sort_by, DeviceModel.created_at)
        if sort_order.lower() == "desc":
            base = base.order_by(sort_col.desc())
        else:
            base = base.order_by(sort_col.asc())
        base = base.offset(offset).limit(page_size)

        result = await self._db.execute(base)
        return list(result.scalars().all()), total

    async def update(
        self,
        device: DeviceModel,
        expected_version: int,
        **updates: Any,
    ) -> DeviceModel | None:
        if device.version != expected_version:
            return None  # Concurrent modification

        for field_name, value in updates.items():
            if hasattr(device, field_name) and value is not None:
                setattr(device, field_name, value)

        device.version = expected_version + 1
        await self._db.flush()
        return device

    async def delete(self, device_id: str, tenant_id: str) -> bool:
        model = await self.get_by_id(device_id, tenant_id)
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.flush()
        return True
