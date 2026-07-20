"""Repository interface for WorkOrder."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.shared import Result, TenantId, WorkOrderId

from .work_order import WorkOrder

if TYPE_CHECKING:
    pass


class WorkOrderRepository(ABC):
    """Repository interface for WorkOrder aggregate."""

    @abstractmethod
    async def save(self, work_order: WorkOrder) -> Result[WorkOrder, str]:
        """Save a work order (insert or update)."""
        ...

    @abstractmethod
    async def get_by_id(
        self, work_order_id: WorkOrderId, tenant_id: TenantId
    ) -> Result[WorkOrder | None, str]:
        """Get a work order by ID within tenant scope."""
        ...

    @abstractmethod
    async def get_by_incident(
        self, incident_id: str, tenant_id: TenantId
    ) -> Result[list[WorkOrder], str]:
        """Get all work orders for an incident."""
        ...

    @abstractmethod
    async def get_by_device(
        self, device_id: str, tenant_id: TenantId
    ) -> Result[list[WorkOrder], str]:
        """Get all work orders for a device."""
        ...

    @abstractmethod
    async def get_sla_breached(
        self, tenant_id: TenantId
    ) -> Result[list[WorkOrder], str]:
        """Get all SLA-breached work orders."""
        ...

    @abstractmethod
    async def get_pending(
        self,
        tenant_id: TenantId,
        technician_id: str | None = None,
        limit: int = 100,
    ) -> Result[list[WorkOrder], str]:
        """Get pending (non-terminal) work orders."""
        ...
