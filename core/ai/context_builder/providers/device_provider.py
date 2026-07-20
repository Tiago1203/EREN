"""
Device Context Provider.

Provides device context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.ai.domain import DeviceGateway, IncidentGateway


class DeviceContextProvider(BaseContextProvider):
    """
    Provides device context for the AI.
    
    Retrieves device status, location, maintenance info,
    and related incidents.
    """
    
    def __init__(
        self,
        device_gateway: DeviceGateway | None = None,
        incident_gateway: IncidentGateway | None = None,
    ):
        self._device = device_gateway
        self._incident = incident_gateway
    
    @property
    def name(self) -> str:
        return "device"
    
    @property
    def priority(self) -> int:
        return 25  # High priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get device context."""
        items = []
        
        # Check if query mentions specific devices
        device_ids = self._extract_device_references(query.query)
        
        for device_id in device_ids:
            device = await self._get_device_safe(device_id, query.tenant_id)
            if device:
                items.append(self._device_to_context(device))
                
                # Get related incidents
                incidents = await self._get_incidents_safe(device_id, query.tenant_id)
                for incident in incidents[:3]:
                    items.append(self._incident_to_context(incident))
        
        # If no specific device, get critical devices overview
        if not device_ids:
            critical = await self._get_critical_safe(query.tenant_id)
            if critical:
                items.append(self._create_critical_overview(critical))
            
            needing_maintenance = await self._get_needing_maintenance_safe(query.tenant_id)
            if needing_maintenance:
                items.append(self._create_maintenance_overview(needing_maintenance))
        
        return items
    
    async def _get_device_safe(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict | None:
        """Safely get device data."""
        if self._device is None:
            return self._mock_device(device_id)
        try:
            result = await self._device.get_by_id(device_id, tenant_id)
            if result:
                return {
                    "id": result.id,
                    "name": result.name,
                    "type": result.device_type,
                    "status": result.status,
                    "critical": result.is_critical,
                    "location": result.location,
                }
        except Exception:
            pass
        return None
    
    async def _get_incidents_safe(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[dict]:
        """Safely get device incidents."""
        if self._incident is None:
            return []
        try:
            results = await self._incident.get_by_device(device_id, tenant_id, limit=3)
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "severity": r.severity,
                    "status": r.status,
                }
                for r in results
            ]
        except Exception:
            return []
    
    async def _get_critical_safe(self, tenant_id: str) -> list[dict]:
        """Safely get critical devices."""
        if self._device is None:
            return []
        try:
            results = await self._device.get_critical_devices(tenant_id)
            return [
                {"id": r.id, "name": r.name, "status": r.status}
                for r in results[:5]
            ]
        except Exception:
            return []
    
    async def _get_needing_maintenance_safe(self, tenant_id: str) -> list[dict]:
        """Safely get devices needing maintenance."""
        if self._device is None:
            return []
        try:
            results = await self._device.get_needing_maintenance(tenant_id)
            return [
                {"id": r.id, "name": r.name, "type": r.device_type}
                for r in results[:5]
            ]
        except Exception:
            return []
    
    def _extract_device_references(self, text: str) -> list[str]:
        """Extract device IDs from text."""
        import re
        # Look for patterns like "device dev-001" or "dev-001"
        patterns = [
            r'device\s+([a-zA-Z0-9\-]+)',
            r'dev-?\d{3}',
            r'equipment\s+([a-zA-Z0-9\-]+)',
        ]
        device_ids = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            device_ids.update(matches)
        return list(device_ids)
    
    def _device_to_context(self, device: dict) -> ContextItem:
        """Convert device to ContextItem."""
        critical_str = "CRITICAL" if device.get("critical") else "standard"
        location = device.get("location", {})
        location_str = f"{location.get('building', '')}/{location.get('floor', '')}/{location.get('room', '')}"
        
        return self._create_item(
            content=f"Device: {device['name']} (ID: {device['id']})\n"
                   f"Type: {device['type']} | Status: {device['status']}\n"
                   f"Critical: {critical_str} | Location: {location_str}",
            relevance_score=0.9,
            metadata={"type": "device", "device_id": device["id"]},
        )
    
    def _incident_to_context(self, incident: dict) -> ContextItem:
        """Convert incident to ContextItem."""
        return self._create_item(
            content=f"Related Incident: {incident['title']} (ID: {incident['id']})\n"
                   f"Severity: {incident['severity']} | Status: {incident['status']}",
            relevance_score=0.7,
            metadata={"type": "incident", "incident_id": incident["id"]},
        )
    
    def _create_critical_overview(self, devices: list[dict]) -> ContextItem:
        """Create overview of critical devices."""
        device_list = "\n".join([f"- {d['name']} ({d['status']})" for d in devices])
        return self._create_item(
            content=f"Critical Devices:\n{device_list}",
            relevance_score=0.6,
            metadata={"type": "critical_devices_overview"},
        )
    
    def _create_maintenance_overview(self, devices: list[dict]) -> ContextItem:
        """Create overview of devices needing maintenance."""
        device_list = "\n".join([f"- {d['name']} ({d['type']})" for d in devices])
        return self._create_item(
            content=f"Devices Needing Maintenance:\n{device_list}",
            relevance_score=0.5,
            metadata={"type": "maintenance_overview"},
        )
    
    def _mock_device(self, device_id: str) -> dict | None:
        """Mock device for testing."""
        mock = {
            "dev-001": {
                "id": "dev-001",
                "name": "Ventilator Model A",
                "type": "Ventilator",
                "status": "active",
                "critical": True,
                "location": {"building": "Main", "floor": "3", "room": "ICU-1"},
            },
        }
        return mock.get(device_id)
