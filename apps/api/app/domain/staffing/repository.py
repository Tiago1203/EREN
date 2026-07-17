"""Staffing repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.staffing import StaffModel, RoleModel, TeamModel, ShiftModel


class StaffingRepository(Protocol):
    """Protocol for staffing bounded context."""

    async def save_staff(self, tenant_id: str, staff_id: str, **kwargs) -> "StaffModel": ...
    async def get_staff(self, staff_id: str, tenant_id: str) -> "StaffModel | None": ...
    async def list_staff(self, tenant_id: str, staff_type: str | None = None, status: str | None = None, limit: int = 100) -> list["StaffModel"]: ...
    async def update_staff(self, staff_id: str, tenant_id: str, expected_version: int, **updates) -> "StaffModel | None": ...
    async def save_shift(self, tenant_id: str, shift_id: str, **kwargs) -> "ShiftModel": ...
    async def get_shift(self, shift_id: str, tenant_id: str) -> "ShiftModel | None": ...
    async def list_shifts(self, tenant_id: str, staff_id: str | None = None, limit: int = 100) -> list["ShiftModel"]: ...
    async def save_role(self, tenant_id: str, role_id: str, **kwargs) -> "RoleModel": ...
    async def save_team(self, tenant_id: str, team_id: str, **kwargs) -> "TeamModel": ...


@dataclass
class SQLAlchemyStaffingRepository:
    """SQLAlchemy implementation of StaffingRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_staff(self, tenant_id: str, staff_id: str, **kwargs) -> "StaffModel":
        from app.infrastructure.models.staffing import StaffModel
        model = StaffModel(id=UUID(staff_id), tenant_id=tenant_id, staff_id=staff_id, **kwargs)
        return await self._save(model)

    async def get_staff(self, staff_id: str, tenant_id: str) -> "StaffModel | None":
        from app.infrastructure.models.staffing import StaffModel
        stmt = select(StaffModel).where(
            StaffModel.staff_id == staff_id, StaffModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_staff(
        self, tenant_id: str, staff_type: str | None = None, status: str | None = None, limit: int = 100
    ) -> list["StaffModel"]:
        from app.infrastructure.models.staffing import StaffModel
        stmt = select(StaffModel).where(StaffModel.tenant_id == tenant_id)
        if staff_type:
            stmt = stmt.where(StaffModel.staff_type == staff_type)
        if status:
            stmt = stmt.where(StaffModel.employment_status == status)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_staff(
        self, staff_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "StaffModel | None":
        from app.infrastructure.models.staffing import StaffModel
        stmt = select(StaffModel).where(
            StaffModel.staff_id == staff_id, StaffModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
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

    async def save_shift(self, tenant_id: str, shift_id: str, **kwargs) -> "ShiftModel":
        from app.infrastructure.models.staffing import ShiftModel
        model = ShiftModel(id=UUID(shift_id), tenant_id=tenant_id, shift_id=shift_id, **kwargs)
        return await self._save(model)

    async def get_shift(self, shift_id: str, tenant_id: str) -> "ShiftModel | None":
        from app.infrastructure.models.staffing import ShiftModel
        stmt = select(ShiftModel).where(
            ShiftModel.shift_id == shift_id, ShiftModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_shifts(
        self, tenant_id: str, staff_id: str | None = None, limit: int = 100
    ) -> list["ShiftModel"]:
        from app.infrastructure.models.staffing import ShiftModel
        stmt = select(ShiftModel).where(ShiftModel.tenant_id == tenant_id)
        if staff_id:
            stmt = stmt.where(ShiftModel.staff_id == staff_id)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def save_role(self, tenant_id: str, role_id: str, **kwargs) -> "RoleModel":
        from app.infrastructure.models.staffing import RoleModel
        model = RoleModel(id=UUID(role_id), tenant_id=tenant_id, role_id=role_id, **kwargs)
        return await self._save(model)

    async def save_team(self, tenant_id: str, team_id: str, **kwargs) -> "TeamModel":
        from app.infrastructure.models.staffing import TeamModel
        model = TeamModel(id=UUID(team_id), tenant_id=tenant_id, team_id=team_id, **kwargs)
        return await self._save(model)
