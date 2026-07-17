"""Organization repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.organization import OrganizationModel, HospitalModel


class OrganizationRepository(Protocol):
    """Protocol for organization bounded context."""

    async def save_organization(self, tenant_id: str, organization_id: str, **kwargs) -> "OrganizationModel": ...
    async def get_organization(self, organization_id: str, tenant_id: str) -> "OrganizationModel | None": ...
    async def list_organizations(self, tenant_id: str, limit: int = 100) -> list["OrganizationModel"]: ...
    async def save_hospital(self, tenant_id: str, hospital_id: str, **kwargs) -> "HospitalModel": ...
    async def get_hospital(self, hospital_id: str, tenant_id: str) -> "HospitalModel | None": ...
    async def list_hospitals(self, tenant_id: str, organization_id: str | None = None, limit: int = 100) -> list["HospitalModel"]: ...


    async def update_organization(
        self, organization_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "OrganizationModel | None": ...
    async def update_hospital(
        self, hospital_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "HospitalModel | None": ...


@dataclass
class SQLAlchemyOrganizationRepository:
    """SQLAlchemy implementation of OrganizationRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_organization(self, tenant_id: str, organization_id: str, **kwargs) -> "OrganizationModel":
        from app.infrastructure.models.organization import OrganizationModel
        model = OrganizationModel(
            id=UUID(organization_id), tenant_id=tenant_id, organization_id=organization_id, **kwargs
        )
        return await self._save(model)

    async def get_organization(self, organization_id: str, tenant_id: str) -> "OrganizationModel | None":
        from app.infrastructure.models.organization import OrganizationModel
        result = await self._db.execute(select(OrganizationModel).where(
            OrganizationModel.organization_id == organization_id,
            OrganizationModel.tenant_id == tenant_id,
        ))
        return result.scalar_one_or_none()

    async def list_organizations(self, tenant_id: str, limit: int = 100) -> list["OrganizationModel"]:
        from app.infrastructure.models.organization import OrganizationModel
        result = await self._db.execute(
            select(OrganizationModel)
            .where(OrganizationModel.tenant_id == tenant_id)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_organization(
        self, organization_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "OrganizationModel | None":
        from app.infrastructure.models.organization import OrganizationModel
        result = await self._db.execute(select(OrganizationModel).where(
            OrganizationModel.organization_id == organization_id,
            OrganizationModel.tenant_id == tenant_id,
        ))
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

    async def save_hospital(self, tenant_id: str, hospital_id: str, **kwargs) -> "HospitalModel":
        from app.infrastructure.models.organization import HospitalModel
        model = HospitalModel(
            id=UUID(hospital_id), tenant_id=tenant_id, hospital_id=hospital_id, **kwargs
        )
        return await self._save(model)

    async def get_hospital(self, hospital_id: str, tenant_id: str) -> "HospitalModel | None":
        from app.infrastructure.models.organization import HospitalModel
        result = await self._db.execute(select(HospitalModel).where(
            HospitalModel.hospital_id == hospital_id,
            HospitalModel.tenant_id == tenant_id,
        ))
        return result.scalar_one_or_none()

    async def list_hospitals(
        self, tenant_id: str, organization_id: str | None = None, limit: int = 100
    ) -> list["HospitalModel"]:
        from app.infrastructure.models.organization import HospitalModel
        query = select(HospitalModel).where(HospitalModel.tenant_id == tenant_id)
        if organization_id:
            query = query.where(HospitalModel.organization_id == organization_id)
        query = query.limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update_hospital(
        self, hospital_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "HospitalModel | None":
        from app.infrastructure.models.organization import HospitalModel
        stmt = select(HospitalModel).where(
            HospitalModel.hospital_id == hospital_id,
            HospitalModel.tenant_id == tenant_id,
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
