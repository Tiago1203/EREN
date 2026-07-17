"""Capacity repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.capacity import (
        BedModel,
        BuildingModel,
        CampusModel,
        FloorModel,
        RoomModel,
    )


class CapacityRepository(Protocol):
    """Protocol for capacity bounded context."""

    async def save_campus(self, tenant_id: str, campus_id: str, **kwargs) -> "CampusModel": ...
    async def get_campus(self, campus_id: str, tenant_id: str) -> "CampusModel | None": ...
    async def list_campuses(self, tenant_id: str, limit: int = 100) -> list["CampusModel"]: ...
    async def save_building(self, tenant_id: str, building_id: str, **kwargs) -> "BuildingModel": ...
    async def get_building(self, building_id: str, tenant_id: str) -> "BuildingModel | None": ...
    async def save_floor(self, tenant_id: str, floor_id: str, **kwargs) -> "FloorModel": ...
    async def get_floor(self, floor_id: str, tenant_id: str) -> "FloorModel | None": ...
    async def save_room(self, tenant_id: str, room_id: str, **kwargs) -> "RoomModel": ...
    async def get_room(self, room_id: str, tenant_id: str) -> "RoomModel | None": ...
    async def save_bed(self, tenant_id: str, bed_id: str, **kwargs) -> "BedModel": ...
    async def get_bed(self, bed_id: str, tenant_id: str) -> "BedModel | None": ...
    async def list_beds(self, tenant_id: str, room_id: str | None = None, status: str | None = None, limit: int = 100) -> list["BedModel"]: ...
    async def update_bed(self, bed_id: str, tenant_id: str, expected_version: int, **updates) -> "BedModel | None": ...
    async def count_beds_by_status(self, tenant_id: str) -> dict[str, int]: ...


@dataclass
class SQLAlchemyCapacityRepository:
    """SQLAlchemy implementation of CapacityRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_campus(self, tenant_id: str, campus_id: str, **kwargs) -> "CampusModel":
        from app.infrastructure.models.capacity import CampusModel
        model = CampusModel(id=UUID(campus_id), tenant_id=tenant_id, campus_id=campus_id, **kwargs)
        return await self._save(model)

    async def get_campus(self, campus_id: str, tenant_id: str) -> "CampusModel | None":
        from app.infrastructure.models.capacity import CampusModel
        result = await self._db.execute(select(CampusModel).where(
            CampusModel.campus_id == campus_id, CampusModel.tenant_id == tenant_id))
        return result.scalar_one_or_none()

    async def list_campuses(self, tenant_id: str, limit: int = 100) -> list["CampusModel"]:
        from app.infrastructure.models.capacity import CampusModel
        result = await self._db.execute(
            select(CampusModel).where(CampusModel.tenant_id == tenant_id).limit(limit))
        return list(result.scalars().all())

    async def save_building(self, tenant_id: str, building_id: str, **kwargs) -> "BuildingModel":
        from app.infrastructure.models.capacity import BuildingModel
        model = BuildingModel(id=UUID(building_id), tenant_id=tenant_id, building_id=building_id, **kwargs)
        return await self._save(model)

    async def get_building(self, building_id: str, tenant_id: str) -> "BuildingModel | None":
        from app.infrastructure.models.capacity import BuildingModel
        result = await self._db.execute(select(BuildingModel).where(
            BuildingModel.building_id == building_id, BuildingModel.tenant_id == tenant_id))
        return result.scalar_one_or_none()

    async def save_floor(self, tenant_id: str, floor_id: str, **kwargs) -> "FloorModel":
        from app.infrastructure.models.capacity import FloorModel
        model = FloorModel(id=UUID(floor_id), tenant_id=tenant_id, floor_id=floor_id, **kwargs)
        return await self._save(model)

    async def get_floor(self, floor_id: str, tenant_id: str) -> "FloorModel | None":
        from app.infrastructure.models.capacity import FloorModel
        result = await self._db.execute(select(FloorModel).where(
            FloorModel.floor_id == floor_id, FloorModel.tenant_id == tenant_id))
        return result.scalar_one_or_none()

    async def save_room(self, tenant_id: str, room_id: str, **kwargs) -> "RoomModel":
        from app.infrastructure.models.capacity import RoomModel
        model = RoomModel(id=UUID(room_id), tenant_id=tenant_id, room_id=room_id, **kwargs)
        return await self._save(model)

    async def get_room(self, room_id: str, tenant_id: str) -> "RoomModel | None":
        from app.infrastructure.models.capacity import RoomModel
        result = await self._db.execute(select(RoomModel).where(
            RoomModel.room_id == room_id, RoomModel.tenant_id == tenant_id))
        return result.scalar_one_or_none()

    async def save_bed(self, tenant_id: str, bed_id: str, **kwargs) -> "BedModel":
        from app.infrastructure.models.capacity import BedModel
        model = BedModel(id=UUID(bed_id), tenant_id=tenant_id, bed_id=bed_id, **kwargs)
        return await self._save(model)

    async def get_bed(self, bed_id: str, tenant_id: str) -> "BedModel | None":
        from app.infrastructure.models.capacity import BedModel
        result = await self._db.execute(select(BedModel).where(
            BedModel.bed_id == bed_id, BedModel.tenant_id == tenant_id))
        return result.scalar_one_or_none()

    async def list_beds(
        self,
        tenant_id: str,
        room_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list["BedModel"]:
        from app.infrastructure.models.capacity import BedModel
        query = select(BedModel).where(BedModel.tenant_id == tenant_id)
        if room_id:
            query = query.where(BedModel.room_id == room_id)
        if status:
            query = query.where(BedModel.status == status)
        query = query.limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update_bed(
        self,
        bed_id: str,
        tenant_id: str,
        expected_version: int,
        **updates,
    ) -> "BedModel | None":
        from app.infrastructure.models.capacity import BedModel
        result = await self._db.execute(select(BedModel).where(
            BedModel.bed_id == bed_id, BedModel.tenant_id == tenant_id))
        model = result.scalar_one_or_none()
        if model is None or model.version != expected_version:
            return None
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.version = expected_version + 1
        model.updated_at = datetime.now()
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def count_beds_by_status(self, tenant_id: str) -> dict[str, int]:
        from app.infrastructure.models.capacity import BedModel
        result = await self._db.execute(
            select(BedModel.status, func.count(BedModel.id))
            .where(BedModel.tenant_id == tenant_id)
            .group_by(BedModel.status)
        )
        return {row[0]: row[1] for row in result.all()}
