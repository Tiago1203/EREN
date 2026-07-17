"""Department repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.department import DepartmentModel, UnitModel


class DepartmentRepository(Protocol):
    """Protocol for department bounded context."""

    async def save_department(self, tenant_id: str, department_id: str, **kwargs) -> "DepartmentModel": ...
    async def get_department(self, department_id: str, tenant_id: str) -> "DepartmentModel | None": ...
    async def list_departments(self, tenant_id: str, organization_id: str | None = None, limit: int = 100) -> list["DepartmentModel"]: ...
    async def update_department(self, department_id: str, tenant_id: str, expected_version: int, **updates) -> "DepartmentModel | None": ...
    async def save_unit(self, tenant_id: str, unit_id: str, **kwargs) -> "UnitModel": ...
    async def get_unit(self, unit_id: str, tenant_id: str) -> "UnitModel | None": ...
    async def list_units(self, tenant_id: str, department_id: str | None = None, limit: int = 100) -> list["UnitModel"]: ...


@dataclass
class SQLAlchemyDepartmentRepository:
    """SQLAlchemy implementation of DepartmentRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_department(self, tenant_id: str, department_id: str, **kwargs) -> "DepartmentModel":
        from app.infrastructure.models.department import DepartmentModel
        model = DepartmentModel(
            id=UUID(department_id), tenant_id=tenant_id, department_id=department_id, **kwargs
        )
        return await self._save(model)

    async def get_department(self, department_id: str, tenant_id: str) -> "DepartmentModel | None":
        from app.infrastructure.models.department import DepartmentModel
        stmt = select(DepartmentModel).where(
            DepartmentModel.department_id == department_id,
            DepartmentModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_departments(
        self, tenant_id: str, organization_id: str | None = None, limit: int = 100
    ) -> list["DepartmentModel"]:
        from app.infrastructure.models.department import DepartmentModel
        stmt = select(DepartmentModel).where(DepartmentModel.tenant_id == tenant_id)
        if organization_id:
            stmt = stmt.where(DepartmentModel.organization_id == organization_id)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_department(
        self, department_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "DepartmentModel | None":
        from app.infrastructure.models.department import DepartmentModel
        stmt = select(DepartmentModel).where(
            DepartmentModel.department_id == department_id,
            DepartmentModel.tenant_id == tenant_id,
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

    async def save_unit(self, tenant_id: str, unit_id: str, **kwargs) -> "UnitModel":
        from app.infrastructure.models.department import UnitModel
        model = UnitModel(id=UUID(unit_id), tenant_id=tenant_id, unit_id=unit_id, **kwargs)
        return await self._save(model)

    async def get_unit(self, unit_id: str, tenant_id: str) -> "UnitModel | None":
        from app.infrastructure.models.department import UnitModel
        stmt = select(UnitModel).where(
            UnitModel.unit_id == unit_id, UnitModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_units(
        self, tenant_id: str, department_id: str | None = None, limit: int = 100
    ) -> list["UnitModel"]:
        from app.infrastructure.models.department import UnitModel
        stmt = select(UnitModel).where(UnitModel.tenant_id == tenant_id)
        if department_id:
            stmt = stmt.where(UnitModel.department_id == department_id)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())
