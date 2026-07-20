"""
Incident Domain Tools.

Tools for accessing incident data from the domain.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext

if TYPE_CHECKING:
    from core.ai.domain import IncidentGateway, DeviceGateway


class SearchIncidentTool(BaseDomainTool):
    """
    Tool for searching incidents.
    
    Usage:
        search_incident(query="ventilator alarm")
    """
    
    config = DomainToolConfig(
        name="search_incident",
        description="Search for incidents by title, description, or device.",
        category="domain.incident",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    )
    
    def __init__(self, incident_gateway: IncidentGateway):
        self._gateway = incident_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Search incidents."""
        try:
            self._validate_parameters(parameters, ["query"])
            
            filters = {}
            if status := parameters.get("status"):
                filters["status"] = status
            if severity := parameters.get("severity"):
                filters["severity"] = severity
            
            results = await self._gateway.search(
                query=parameters["query"],
                tenant_id=context.tenant_id,
                filters=filters if filters else None,
                limit=parameters.get("limit", 10),
            )
            
            return self._format_success([
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "status": i.status,
                    "device_name": i.device_name,
                }
                for i in results
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class GetIncidentHistoryTool(BaseDomainTool):
    """
    Tool for getting incident timeline/history.
    
    Usage:
        get_incident_history(incident_id="inc-001")
    """
    
    config = DomainToolConfig(
        name="get_incident_history",
        description="Get the complete timeline/history of an incident including all status changes.",
        category="domain.incident",
        parameters_schema={
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "Incident ID",
                },
            },
            "required": ["incident_id"],
        },
    )
    
    def __init__(self, incident_gateway: IncidentGateway):
        self._gateway = incident_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get incident history."""
        try:
            self._validate_parameters(parameters, ["incident_id"])
            
            history = await self._gateway.get_history(
                parameters["incident_id"],
                context.tenant_id,
            )
            
            return self._format_success(history)
            
        except Exception as e:
            return self._format_error(str(e))


class AnalyzeIncidentTool(BaseDomainTool):
    """
    Tool for analyzing an incident for root cause.
    
    Usage:
        analyze_incident(incident_id="inc-001")
    """
    
    config = DomainToolConfig(
        name="analyze_incident",
        description="Analyze an incident to identify root cause and contributing factors.",
        category="domain.incident",
        parameters_schema={
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "Incident ID",
                },
            },
            "required": ["incident_id"],
        },
    )
    
    def __init__(
        self,
        incident_gateway: IncidentGateway,
        device_gateway: DeviceGateway,
    ):
        self._incident = incident_gateway
        self._device = device_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Analyze incident."""
        try:
            self._validate_parameters(parameters, ["incident_id"])
            
            analysis = await self._incident.analyze(
                parameters["incident_id"],
                context.tenant_id,
            )
            
            return self._format_success(analysis)
            
        except Exception as e:
            return self._format_error(str(e))
