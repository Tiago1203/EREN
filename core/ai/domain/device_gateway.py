"""
Device Gateway.

Gateway implementation for Device domain.
Provides AI Core with access to device data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .contracts import DeviceDTO, IDeviceGateway
from .exceptions import DeviceNotFoundError

if TYPE_CHECKING:
    from core.device.domain.repositories import DeviceRepository
    from core.ai.memory import MemoryManager


class DeviceGateway(IDeviceGateway):
    """
    Gateway for Device domain.
    
    AI Core uses this gateway to access device data without
    knowing about repository implementations.
    
    NOTE: This is a placeholder implementation. When FASE 1 EPIC 11
    is implemented (Application Services), this gateway will use
    those services instead of direct repository access.
    """
    
    def __init__(
        self,
        repository: DeviceRepository | None = None,
        memory_manager: MemoryManager | None = None,
    ):
        self._repository = repository
        self._memory = memory_manager
    
    @property
    def name(self) -> str:
        return "device"
    
    async def get_by_id(
        self,
        device_id: str,
        tenant_id: str,
    ) -> DeviceDTO | None:
        """Get device by ID."""
        if self._repository is None:
            return self._mock_get_by_id(device_id)
        
        from core.shared import DeviceId, TenantId
        result = await self._repository.get_by_id(
            DeviceId(device_id),
            TenantId(tenant_id),
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
    ) -> list[DeviceDTO]:
        """Search devices by name, type, or serial."""
        # Mock implementation for now
        return self._mock_search(query, limit)
    
    async def get_by_status(
        self,
        tenant_id: str,
        status: str,
        limit: int = 50,
    ) -> list[DeviceDTO]:
        """Get devices by status."""
        if self._repository is None:
            return self._mock_get_by_status(status, limit)
        
        from core.shared import TenantId
        result = await self._repository.get_by_status(
            TenantId(tenant_id),
            status,
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(d) for d in result.value]
        return []
    
    async def get_critical_devices(
        self,
        tenant_id: str,
    ) -> list[DeviceDTO]:
        """Get all critical devices."""
        if self._repository is None:
            return self._mock_get_critical()
        
        from core.shared import TenantId
        result = await self._repository.get_critical_devices(
            TenantId(tenant_id),
        )
        
        if result.is_ok():
            return [self._entity_to_dto(d) for d in result.value]
        return []
    
    async def get_needing_maintenance(
        self,
        tenant_id: str,
    ) -> list[DeviceDTO]:
        """Get devices needing maintenance."""
        if self._repository is None:
            return self._mock_get_needing_maintenance()
        
        from core.shared import TenantId
        result = await self._repository.get_needing_maintenance(
            TenantId(tenant_id),
        )
        
        if result.is_ok():
            return [self._entity_to_dto(d) for d in result.value]
        return []
    
    async def get_history(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Get device maintenance/incident history."""
        # Mock implementation
        return {
            "device_id": device_id,
            "maintenance_records": [
                {
                    "date": "2024-01-15",
                    "type": "preventive",
                    "description": "Annual calibration",
                },
                {
                    "date": "2024-02-20",
                    "type": "corrective",
                    "description": "Replaced sensor",
                },
            ],
            "incidents": [
                {
                    "date": "2024-02-15",
                    "title": "Sensor malfunction",
                    "severity": "medium",
                },
            ],
        }
    
    async def get_location(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Get device location details."""
        return {
            "device_id": device_id,
            "building": "Main Hospital",
            "floor": "3",
            "department": "ICU",
            "room": "301",
        }
    
    # =============================================================================
    # Helper methods
    # =============================================================================
    
    def _entity_to_dto(self, entity: Any) -> DeviceDTO:
        """Convert Device entity to DeviceDTO."""
        return DeviceDTO(
            id=str(entity.id),
            serial_number=str(entity.serial_number),
            name=entity.name,
            device_type=str(entity.device_type),
            status=str(entity.status),
            manufacturer=entity.manufacturer.name,
            model=entity.manufacturer.model,
            is_critical=entity.is_critical,
            location=entity.location.to_dict() if hasattr(entity, 'location') else {},
            last_maintenance=getattr(entity, 'last_maintenance', None),
            next_maintenance=getattr(entity, 'next_maintenance', None),
            created_at=entity.created_at,
        )
    
    # =============================================================================
    # Mock implementations for testing
    # =============================================================================
    
    def _mock_get_by_id(self, device_id: str) -> DeviceDTO | None:
        """Mock implementation for testing."""
        mock_devices = {
            "dev-001": DeviceDTO(
                id="dev-001",
                serial_number="SN-12345",
                name="Ventilator Model A",
                device_type="Ventilator",
                status="active",
                manufacturer="Medtronic",
                model="Pulmonetics",
                is_critical=True,
                location={"building": "Main", "floor": "3", "room": "ICU-1"},
            ),
            "dev-002": DeviceDTO(
                id="dev-002",
                serial_number="SN-67890",
                name="Infusion Pump",
                device_type="Pump",
                status="active",
                manufacturer="Baxter",
                model="Sigma",
                is_critical=False,
                location={"building": "Main", "floor": "2", "room": "201"},
            ),
        }
        return mock_devices.get(device_id)
    
    def _mock_search(self, query: str, limit: int) -> list[DeviceDTO]:
        """Mock search implementation."""
        all_devices = [
            DeviceDTO(
                id="dev-001",
                serial_number="SN-12345",
                name="Ventilator Model A",
                device_type="Ventilator",
                status="active",
                manufacturer="Medtronic",
                model="Pulmonetics",
                is_critical=True,
                location={"building": "Main", "floor": "3", "room": "ICU-1"},
            ),
            DeviceDTO(
                id="dev-002",
                serial_number="SN-67890",
                name="Infusion Pump",
                device_type="Pump",
                status="active",
                manufacturer="Baxter",
                model="Sigma",
                is_critical=False,
                location={"building": "Main", "floor": "2", "room": "201"},
            ),
            DeviceDTO(
                id="dev-003",
                serial_number="SN-11111",
                name="Patient Monitor",
                device_type="Monitor",
                status="maintenance",
                manufacturer="Philips",
                model="IntelliVue",
                is_critical=True,
                location={"building": "Main", "floor": "1", "room": "ER-1"},
            ),
        ]
        
        query_lower = query.lower()
        results = [
            d for d in all_devices
            if query_lower in d.name.lower()
            or query_lower in d.device_type.lower()
            or query_lower in d.serial_number.lower()
        ]
        return results[:limit]
    
    def _mock_get_by_status(self, status: str, limit: int) -> list[DeviceDTO]:
        """Mock get by status."""
        all_devices = self._mock_search("", 100)
        return [d for d in all_devices if d.status == status][:limit]
    
    def _mock_get_critical(self) -> list[DeviceDTO]:
        """Mock get critical devices."""
        all_devices = self._mock_search("", 100)
        return [d for d in all_devices if d.is_critical]
    
    def _mock_get_needing_maintenance(self) -> list[DeviceDTO]:
        """Mock get devices needing maintenance."""
        all_devices = self._mock_search("", 100)
        return [d for d in all_devices if d.status == "maintenance"]
