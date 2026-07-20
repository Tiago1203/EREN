"""
Incident Context Provider.

Provides incident context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.ai.domain import IncidentGateway


class IncidentContextProvider(BaseContextProvider):
    """
    Provides incident context for the AI.
    
    Retrieves active incidents and incident history.
    """
    
    def __init__(
        self,
        incident_gateway: IncidentGateway | None = None,
    ):
        self._incident = incident_gateway
    
    @property
    def name(self) -> str:
        return "incident"
    
    @property
    def priority(self) -> int:
        return 35  # High priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get incident context."""
        items = []
        
        # Get open incidents
        open_incidents = await self._get_open_safe(query.tenant_id)
        if open_incidents:
            items.append(self._create_open_incidents_context(open_incidents))
        
        # Check for specific incident mentions
        incident_ids = self._extract_incident_references(query.query)
        for incident_id in incident_ids:
            incident = await self._get_incident_safe(incident_id, query.tenant_id)
            if incident:
                items.append(self._incident_to_context(incident))
        
        return items
    
    async def _get_open_safe(self, tenant_id: str) -> list[dict]:
        """Safely get open incidents."""
        if self._incident is None:
            return self._mock_get_open()
        try:
            results = await self._incident.get_open_incidents(tenant_id, limit=10)
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "severity": r.severity,
                    "status": r.status,
                    "device_name": r.device_name,
                }
                for r in results
            ]
        except Exception:
            return []
    
    async def _get_incident_safe(self, incident_id: str, tenant_id: str) -> dict | None:
        """Safely get incident."""
        if self._incident is None:
            return None
        try:
            result = await self._incident.get_by_id(incident_id, tenant_id)
            if result:
                return {
                    "id": result.id,
                    "title": result.title,
                    "description": result.description,
                    "severity": result.severity,
                    "status": result.status,
                    "device_name": result.device_name,
                }
        except Exception:
            pass
        return None
    
    def _extract_incident_references(self, text: str) -> list[str]:
        """Extract incident IDs from text."""
        import re
        matches = re.findall(r'inc-?\d+', text, re.IGNORECASE)
        return [m.replace('-', '') for m in matches]
    
    def _create_open_incidents_context(self, incidents: list[dict]) -> ContextItem:
        """Create context for open incidents."""
        critical = [i for i in incidents if i["severity"] in ("critical", "high")]
        other = [i for i in incidents if i not in critical]
        
        lines = []
        if critical:
            lines.append("CRITICAL/HIGH Incidents:")
            for i in critical[:5]:
                lines.append(f"- {i['title']} ({i['severity']}) - {i['status']}")
        
        if other:
            lines.append("\nOther Open Incidents:")
            for i in other[:5]:
                lines.append(f"- {i['title']} - {i['status']}")
        
        return self._create_item(
            content="\n".join(lines),
            relevance_score=0.75,
            metadata={"type": "open_incidents", "count": len(incidents)},
        )
    
    def _incident_to_context(self, incident: dict) -> ContextItem:
        """Convert incident to ContextItem."""
        return self._create_item(
            content=f"Incident: {incident['title']}\n"
                   f"ID: {incident['id']} | Severity: {incident['severity']} | Status: {incident['status']}\n"
                   f"Description: {incident.get('description', 'N/A')}",
            relevance_score=0.9,
            metadata={"type": "incident", "incident_id": incident["id"]},
        )
    
    def _mock_get_open(self) -> list[dict]:
        """Mock get open incidents."""
        return [
            {"id": "inc-001", "title": "Ventilator Alarm Malfunction", "severity": "high", "status": "open"},
            {"id": "inc-002", "title": "Monitor Display Issue", "severity": "medium", "status": "in_progress"},
        ]
