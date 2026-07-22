"""
WorkOrder Gateway.

Gateway implementation for WorkOrder domain.
Provides AI Core with access to work order data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .contracts import WorkOrderDTO, IWorkOrderGateway
from .exceptions import WorkOrderNotFoundError

if TYPE_CHECKING:
    from core.PHASE_1.domain.incident.domain.work_order.repository import WorkOrderRepository


class WorkOrderGateway(IWorkOrderGateway):
    """
    Gateway for WorkOrder domain.
    
    AI Core uses this gateway to access work order data.
    """
    
    def __init__(
        self,
        repository: WorkOrderRepository | None = None,
    ):
        self._repository = repository
    
    @property
    def name(self) -> str:
        return "workorder"
    
    async def get_by_id(
        self,
        work_order_id: str,
        tenant_id: str,
    ) -> WorkOrderDTO | None:
        """Get work order by ID."""
        if self._repository is None:
            return self._mock_get_by_id(work_order_id)
        
        from core.PHASE_1.infrastructure.shared import WorkOrderId, TenantId
        result = await self._repository.get_by_id(
            WorkOrderId(work_order_id),
            TenantId(tenant_id),
        )
        
        if result.is_ok() and result.value:
            return self._entity_to_dto(result.value)
        return None
    
    async def get_pending(
        self,
        tenant_id: str,
        technician_id: str | None = None,
        limit: int = 20,
    ) -> list[WorkOrderDTO]:
        """Get pending work orders."""
        if self._repository is None:
            return self._mock_get_pending(technician_id, limit)
        
        from core.PHASE_1.infrastructure.shared import TenantId
        result = await self._repository.get_pending(
            TenantId(tenant_id),
            technician_id,
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(w) for w in result.value]
        return []
    
    async def get_sla_breached(
        self,
        tenant_id: str,
    ) -> list[WorkOrderDTO]:
        """Get SLA-breached work orders."""
        if self._repository is None:
            return self._mock_get_sla_breached()
        
        from core.PHASE_1.infrastructure.shared import TenantId
        result = await self._repository.get_sla_breached(
            TenantId(tenant_id),
        )
        
        if result.is_ok():
            return [self._entity_to_dto(w) for w in result.value]
        return []
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[WorkOrderDTO]:
        """Get work orders for a device."""
        if self._repository is None:
            return self._mock_get_by_device(device_id)
        
        from core.PHASE_1.infrastructure.shared import TenantId
        result = await self._repository.get_by_device(
            device_id,
            TenantId(tenant_id),
        )
        
        if result.is_ok():
            return [self._entity_to_dto(w) for w in result.value]
        return []
    
    def _entity_to_dto(self, entity) -> WorkOrderDTO:
        """Convert WorkOrder entity to WorkOrderDTO."""
        return WorkOrderDTO(
            id=str(entity.id),
            title=entity.title,
            description=entity.description,
            status=str(entity.status),
            priority=str(entity.priority),
            device_id=str(entity.device_id) if entity.device_id else None,
            assigned_to=str(entity.assigned_to) if entity.assigned_to else None,
            scheduled_date=entity.scheduled_date,
            completed_at=entity.completed_at,
        )
    
    # =============================================================================
    # Mock implementations
    # =============================================================================
    
    def _mock_get_by_id(self, work_order_id: str) -> WorkOrderDTO | None:
        """Mock implementation."""
        mock_orders = {
            "wo-001": WorkOrderDTO(
                id="wo-001",
                title="Preventive maintenance - Ventilator",
                description="Annual preventive maintenance check",
                status="pending",
                priority="medium",
                device_id="dev-001",
                assigned_to="tech-001",
            ),
        }
        return mock_orders.get(work_order_id)
    
    def _mock_get_pending(self, technician_id: str | None, limit: int) -> list[WorkOrderDTO]:
        """Mock get pending."""
        all_orders = [
            WorkOrderDTO(
                id="wo-001",
                title="Preventive maintenance - Ventilator",
                description="Annual preventive maintenance",
                status="pending",
                priority="medium",
                device_id="dev-001",
                assigned_to="tech-001",
            ),
            WorkOrderDTO(
                id="wo-002",
                title="Calibration - Infusion Pump",
                description="Quarterly calibration",
                status="pending",
                priority="low",
                device_id="dev-002",
                assigned_to="tech-002",
            ),
            WorkOrderDTO(
                id="wo-003",
                title="Emergency repair - Monitor",
                description="Screen not displaying",
                status="in_progress",
                priority="high",
                device_id="dev-003",
                assigned_to="tech-001",
            ),
        ]
        
        if technician_id:
            return [o for o in all_orders if o.assigned_to == technician_id][:limit]
        return all_orders[:limit]
    
    def _mock_get_sla_breached(self) -> list[WorkOrderDTO]:
        """Mock get SLA breached."""
        return [
            WorkOrderDTO(
                id="wo-003",
                title="Emergency repair - Monitor",
                description="Screen not displaying",
                status="in_progress",
                priority="high",
                device_id="dev-003",
                assigned_to="tech-001",
            ),
        ]
    
    def _mock_get_by_device(self, device_id: str) -> list[WorkOrderDTO]:
        """Mock get by device."""
        return [o for o in self._mock_get_pending(None, 100) if o.device_id == device_id]
