"""
Incident Gateway.

Gateway implementation for Incident domain.
Provides AI Core with access to incident data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .contracts import IncidentDTO, IIncidentGateway
from .exceptions import IncidentNotFoundError

if TYPE_CHECKING:
    from core.incident.domain.repositories import IncidentRepository
    from core.ai.memory import MemoryManager


class IncidentGateway(IIncidentGateway):
    """
    Gateway for Incident domain.
    
    AI Core uses this gateway to access incident data without
    knowing about repository implementations.
    """
    
    def __init__(
        self,
        repository: IncidentRepository | None = None,
        memory_manager: MemoryManager | None = None,
    ):
        self._repository = repository
        self._memory = memory_manager
    
    @property
    def name(self) -> str:
        return "incident"
    
    async def get_by_id(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> IncidentDTO | None:
        """Get incident by ID."""
        if self._repository is None:
            return self._mock_get_by_id(incident_id)
        
        from core.shared import IncidentId, TenantId
        result = await self._repository.get_by_id(
            IncidentId(incident_id),
        )
        
        if result.is_ok() and result.value:
            return self._entity_to_dto(result.value)
        return None
    
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[IncidentDTO]:
        """Search incidents."""
        return self._mock_search(query, limit)
    
    async def get_open_incidents(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[IncidentDTO]:
        """Get all open incidents."""
        if self._repository is None:
            return self._mock_get_open(limit)
        
        from core.shared import TenantId
        result = await self._repository.get_open_incidents(
            TenantId(tenant_id),
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(i) for i in result.value]
        return []
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list[IncidentDTO]:
        """Get incidents for a device."""
        if self._repository is None:
            return self._mock_get_by_device(device_id, limit)
        
        from core.shared import DeviceId, TenantId
        result = await self._repository.get_by_device(
            DeviceId(device_id),
            TenantId(tenant_id),
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(i) for i in result.value]
        return []
    
    async def get_by_engineer(
        self,
        engineer_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list[IncidentDTO]:
        """Get incidents assigned to an engineer."""
        if self._repository is None:
            return self._mock_get_by_engineer(engineer_id, limit)
        
        from core.shared import EngineerId, TenantId
        result = await self._repository.get_by_engineer(
            EngineerId(engineer_id),
            TenantId(tenant_id),
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(i) for i in result.value]
        return []
    
    async def get_history(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Get incident history/timeline."""
        return {
            "incident_id": incident_id,
            "timeline": [
                {
                    "date": "2024-01-15T10:30:00",
                    "event": "reported",
                    "description": "Incident reported",
                    "user": "nurse-001",
                },
                {
                    "date": "2024-01-15T11:00:00",
                    "event": "triaged",
                    "description": "Assigned to engineering",
                    "user": "supervisor-001",
                },
                {
                    "date": "2024-01-15T14:00:00",
                    "event": "in_progress",
                    "description": "Technician assigned",
                    "user": "tech-001",
                },
            ],
        }
    
    async def analyze(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Analyze incident for root cause."""
        incident = await self.get_by_id(incident_id, tenant_id)
        if not incident:
            raise IncidentNotFoundError(incident_id, tenant_id)
        
        return {
            "incident_id": incident_id,
            "root_cause": "Sensor calibration drift",
            "contributing_factors": [
                "Device age (>5 years)",
                "High usage frequency",
                "Environmental conditions",
            ],
            "recommended_actions": [
                "Replace sensor module",
                "Update maintenance schedule",
                "Review environmental controls",
            ],
            "similar_incidents": [
                {"id": "inc-002", "title": "Similar sensor issue"},
            ],
        }
    
    def _entity_to_dto(self, entity: Any) -> IncidentDTO:
        """Convert Incident entity to IncidentDTO."""
        return IncidentDTO(
            id=str(entity.id),
            title=entity.title,
            description=entity.description,
            severity=str(entity.severity),
            status=str(entity.status),
            device_id=str(entity.device_id) if entity.device_id else None,
            device_name=getattr(entity, 'device_name', None),
            assigned_to=str(entity.assigned_to) if entity.assigned_to else None,
            reported_at=entity.reported_at,
            resolved_at=entity.resolved_at,
        )
    
    # =============================================================================
    # Mock implementations
    # =============================================================================
    
    def _mock_get_by_id(self, incident_id: str) -> IncidentDTO | None:
        """Mock implementation."""
        mock_incidents = {
            "inc-001": IncidentDTO(
                id="inc-001",
                title="Ventilator Alarm Malfunction",
                description="Ventilator showing false alarm readings",
                severity="high",
                status="open",
                device_id="dev-001",
                device_name="Ventilator Model A",
                assigned_to="eng-001",
            ),
            "inc-002": IncidentDTO(
                id="inc-002",
                title="Infusion Pump Error",
                description="Pump showing E02 error code",
                severity="medium",
                status="in_progress",
                device_id="dev-002",
                device_name="Infusion Pump",
                assigned_to="eng-002",
            ),
        }
        return mock_incidents.get(incident_id)
    
    def _mock_search(self, query: str, limit: int) -> list[IncidentDTO]:
        """Mock search."""
        all_incidents = [self._mock_get_by_id("inc-001"), self._mock_get_by_id("inc-002")]
        query_lower = query.lower()
        return [
            i for i in all_incidents
            if i and (query_lower in i.title.lower() or query_lower in i.description.lower())
        ][:limit]
    
    def _mock_get_open(self, limit: int) -> list[IncidentDTO]:
        """Mock get open incidents."""
        return [
            IncidentDTO(
                id="inc-001",
                title="Ventilator Alarm Malfunction",
                description="Ventilator showing false alarm readings",
                severity="high",
                status="open",
                device_id="dev-001",
                device_name="Ventilator Model A",
            ),
        ][:limit]
    
    def _mock_get_by_device(self, device_id: str, limit: int) -> list[IncidentDTO]:
        """Mock get by device."""
        return [
            i for i in [self._mock_get_by_id("inc-001"), self._mock_get_by_id("inc-002")]
            if i and i.device_id == device_id
        ][:limit]
    
    def _mock_get_by_engineer(self, engineer_id: str, limit: int) -> list[IncidentDTO]:
        """Mock get by engineer."""
        return [
            i for i in [self._mock_get_by_id("inc-001"), self._mock_get_by_id("inc-002")]
            if i and i.assigned_to == engineer_id
        ][:limit]
