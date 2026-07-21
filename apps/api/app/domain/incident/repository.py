"""Incident repository interface and SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.incident import IncidentModel


class IncidentRepository(Protocol):
    """Protocol for incident persistence operations."""

    async def save(
        self,
        tenant_id: str,
        incident_id: str,
        device_id: str,
        title: str,
        description: str,
        severity: str,
        status: str,
        reported_by: str | None,
        assigned_to: str | None,
        **kwargs: Any,
    ) -> IncidentModel: ...

    async def get_by_id(self, incident_id: str, tenant_id: str) -> IncidentModel | None: ...

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        severity_filter: str | None = None,
        device_id_filter: str | None = None,
        assigned_to_filter: str | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[IncidentModel], int]: ...

    async def get_open_incidents(self, tenant_id: str, limit: int = 100) -> list[IncidentModel]: ...

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 100) -> list[IncidentModel]: ...

    async def get_by_engineer(self, engineer_id: str, tenant_id: str, limit: int = 100) -> list[IncidentModel]: ...

    async def update(
        self,
        incident: IncidentModel,
        expected_version: int,
        **updates: Any,
    ) -> IncidentModel | None: ...

    async def delete(self, incident_id: str, tenant_id: str) -> bool: ...


@dataclass
class SQLAlchemyIncidentRepository:
    """SQLAlchemy implementation of IncidentRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(
        self,
        tenant_id: str,
        incident_id: str,
        device_id: str,
        title: str,
        description: str,
        severity: str,
        status: str,
        reported_by: str | None = None,
        assigned_to: str | None = None,
        **kwargs: Any,
    ) -> IncidentModel:
        from app.infrastructure.models.incident import IncidentModel

        model = IncidentModel(
            id=UUID(incident_id),
            tenant_id=tenant_id,
            device_id=UUID(device_id) if device_id else None,
            title=title,
            description=description,
            severity=severity,
            status=status,
            reported_by=reported_by,
            assigned_to=assigned_to,
        )
        self._db.add(model)
        await self._db.flush()
        return model

    async def get_by_id(self, incident_id: str, tenant_id: str) -> IncidentModel | None:
        from app.infrastructure.models.incident import IncidentModel

        result = await self._db.execute(
            select(IncidentModel).where(
                IncidentModel.id == UUID(incident_id),
                IncidentModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        severity_filter: str | None = None,
        device_id_filter: str | None = None,
        assigned_to_filter: str | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[IncidentModel], int]:
        from app.infrastructure.models.incident import IncidentModel

        base = select(IncidentModel).where(IncidentModel.tenant_id == tenant_id)

        if status_filter:
            base = base.where(IncidentModel.status == status_filter)
        if severity_filter:
            base = base.where(IncidentModel.severity == severity_filter)
        if device_id_filter:
            base = base.where(IncidentModel.device_id == UUID(device_id_filter))
        if assigned_to_filter:
            base = base.where(IncidentModel.assigned_to == assigned_to_filter)
        if search_query:
            base = base.where(
                IncidentModel.title.ilike(f"%{search_query}%") |
                IncidentModel.description.ilike(f"%{search_query}%")
            )

        # Count
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        sort_col = getattr(IncidentModel, sort_by, IncidentModel.created_at)
        if sort_order.lower() == "desc":
            base = base.order_by(sort_col.desc())
        else:
            base = base.order_by(sort_col.asc())
        base = base.offset(offset).limit(page_size)

        result = await self._db.execute(base)
        return list(result.scalars().all()), total

    async def get_open_incidents(self, tenant_id: str, limit: int = 100) -> list[IncidentModel]:
        from app.infrastructure.models.incident import IncidentModel

        result = await self._db.execute(
            select(IncidentModel).where(
                IncidentModel.tenant_id == tenant_id,
                IncidentModel.status.in_(["open", "in_progress", "escalated"]),
            ).order_by(IncidentModel.severity.desc(), IncidentModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 100) -> list[IncidentModel]:
        from app.infrastructure.models.incident import IncidentModel

        result = await self._db.execute(
            select(IncidentModel).where(
                IncidentModel.tenant_id == tenant_id,
                IncidentModel.device_id == UUID(device_id),
            ).order_by(IncidentModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_engineer(self, engineer_id: str, tenant_id: str, limit: int = 100) -> list[IncidentModel]:
        from app.infrastructure.models.incident import IncidentModel

        result = await self._db.execute(
            select(IncidentModel).where(
                IncidentModel.tenant_id == tenant_id,
                IncidentModel.assigned_to == engineer_id,
            ).order_by(IncidentModel.severity.desc(), IncidentModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        incident: IncidentModel,
        expected_version: int,
        **updates: Any,
    ) -> IncidentModel | None:
        if hasattr(incident, 'version') and incident.version != expected_version:
            return None

        for field_name, value in updates.items():
            if hasattr(incident, field_name) and value is not None:
                setattr(incident, field_name, value)

        if hasattr(incident, 'version'):
            incident.version = expected_version + 1
        await self._db.flush()
        return incident

    async def delete(self, incident_id: str, tenant_id: str) -> bool:
        model = await self.get_by_id(incident_id, tenant_id)
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.flush()
        return True


# Alias for compatibility with EPIC 10 imports
IncidentRepositoryImpl = SQLAlchemyIncidentRepository
