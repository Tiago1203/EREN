"""Work Order repository interface and SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.infrastructure.models.work_order import WorkOrderModel


class WorkOrderRepository(Protocol):
    """Protocol for work order persistence operations."""

    async def save(
        self,
        tenant_id: str,
        work_order_id: str,
        device_id: str,
        work_order_type: str,
        description: str,
        priority: str,
        status: str,
        created_by: str | None,
        incident_id: str | None,
        preventive_schedule_id: str | None,
        **kwargs: Any,
    ) -> WorkOrderModel: ...

    async def get_by_id(self, work_order_id: str, tenant_id: str) -> WorkOrderModel | None: ...

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        priority_filter: str | None = None,
        assigned_to: str | None = None,
        device_id: str | None = None,
        work_order_type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[WorkOrderModel], int]: ...

    async def list_overdue(self, tenant_id: str) -> list[WorkOrderModel]: ...

    async def update(
        self,
        work_order: WorkOrderModel,
        expected_version: int,
        **updates: Any,
    ) -> WorkOrderModel | None: ...

    async def delete(self, work_order_id: str, tenant_id: str) -> bool: ...


@dataclass
class SQLAlchemyWorkOrderRepository:
    """SQLAlchemy implementation of WorkOrderRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(
        self,
        tenant_id: str,
        work_order_id: str,
        device_id: str,
        work_order_type: str,
        description: str,
        priority: str,
        status: str,
        created_by: str | None,
        incident_id: str | None,
        preventive_schedule_id: str | None,
        **kwargs: Any,
    ) -> WorkOrderModel:
        from uuid import UUID

        from app.infrastructure.models.work_order import WorkOrderModel

        model = WorkOrderModel(
            id=UUID(work_order_id),
            tenant_id=tenant_id,
            device_id=UUID(device_id),
            work_order_type=work_order_type,
            description=description,
            priority=priority,
            status=status,
            created_by=created_by,
            incident_id=UUID(incident_id) if incident_id else None,
            preventive_schedule_id=preventive_schedule_id,
        )
        self._db.add(model)
        await self._db.flush()
        return model

    async def get_by_id(self, work_order_id: str, tenant_id: str) -> WorkOrderModel | None:
        from uuid import UUID

        from app.infrastructure.models.work_order import WorkOrderModel

        result = await self._db.execute(
            select(WorkOrderModel).where(
                WorkOrderModel.id == UUID(work_order_id),
                WorkOrderModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        priority_filter: str | None = None,
        assigned_to: str | None = None,
        device_id: str | None = None,
        work_order_type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[WorkOrderModel], int]:
        from uuid import UUID

        from app.infrastructure.models.work_order import WorkOrderModel

        base = select(WorkOrderModel).where(WorkOrderModel.tenant_id == tenant_id)

        if status_filter:
            base = base.where(WorkOrderModel.status == status_filter)
        if priority_filter:
            base = base.where(WorkOrderModel.priority == priority_filter)
        if assigned_to:
            base = base.where(WorkOrderModel.assigned_to == assigned_to)
        if device_id:
            base = base.where(WorkOrderModel.device_id == UUID(device_id))
        if work_order_type:
            base = base.where(WorkOrderModel.work_order_type == work_order_type)

        # Count
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        sort_col = getattr(WorkOrderModel, sort_by, WorkOrderModel.created_at)
        if sort_order.lower() == "desc":
            base = base.order_by(sort_col.desc())
        else:
            base = base.order_by(sort_col.asc())
        base = base.offset(offset).limit(page_size)

        result = await self._db.execute(base)
        return list(result.scalars().all()), total

    async def list_overdue(self, tenant_id: str) -> list[WorkOrderModel]:
        from uuid import UUID

        from app.infrastructure.models.work_order import WorkOrderModel

        now = datetime.utcnow()
        result = await self._db.execute(
            select(WorkOrderModel).where(
                WorkOrderModel.tenant_id == tenant_id,
                WorkOrderModel.sla_deadline.isnot(None),
                WorkOrderModel.sla_deadline < now,
                WorkOrderModel.status.in_(["scheduled", "in_progress", "pending_parts"]),
            ).order_by(WorkOrderModel.sla_deadline.asc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        work_order: WorkOrderModel,
        expected_version: int,
        **updates: Any,
    ) -> WorkOrderModel | None:
        if work_order.version != expected_version:
            return None

        for field_name, value in updates.items():
            if hasattr(work_order, field_name) and value is not None:
                setattr(work_order, field_name, value)

        work_order.version = expected_version + 1
        await self._db.flush()
        return work_order

    async def delete(self, work_order_id: str, tenant_id: str) -> bool:
        model = await self.get_by_id(work_order_id, tenant_id)
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.flush()
        return True
