"""
Device Domain Tools.

Tools for accessing device data from the domain.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext

if TYPE_CHECKING:
    from core.ai.domain import DeviceGateway, IncidentGateway


class SearchDeviceTool(BaseDomainTool):
    """
    Tool for searching devices.
    
    Usage:
        search_device(query="ventilator", status="active")
    """
    
    config = DomainToolConfig(
        name="search_device",
        description="Search for devices by name, type, or serial number. Returns device details including status and location.",
        category="domain.device",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (device name, type, or serial number)",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "maintenance", "decommissioned"],
                    "description": "Filter by device status",
                },
                "is_critical": {
                    "type": "boolean",
                    "description": "Filter only critical devices",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of results",
                },
            },
            "required": ["query"],
        },
    )
    
    def __init__(self, device_gateway: DeviceGateway):
        self._gateway = device_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Search devices."""
        try:
            self._validate_parameters(parameters, ["query"])
            
            filters = {}
            if status := parameters.get("status"):
                filters["status"] = status
            if parameters.get("is_critical"):
                filters["is_critical"] = True
            
            results = await self._gateway.search(
                query=parameters["query"],
                tenant_id=context.tenant_id,
                filters=filters if filters else None,
                limit=parameters.get("limit", 10),
            )
            
            return self._format_success([
                {
                    "id": d.id,
                    "name": d.name,
                    "device_type": d.device_type,
                    "status": d.status,
                    "is_critical": d.is_critical,
                    "location": d.location,
                }
                for d in results
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class GetDeviceHistoryTool(BaseDomainTool):
    """
    Tool for getting device maintenance and incident history.
    
    Usage:
        get_device_history(device_id="dev-001")
    """
    
    config = DomainToolConfig(
        name="get_device_history",
        description="Get complete history for a device including maintenance records and related incidents.",
        category="domain.device",
        parameters_schema={
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID",
                },
            },
            "required": ["device_id"],
        },
    )
    
    def __init__(
        self,
        device_gateway: DeviceGateway,
        incident_gateway: IncidentGateway,
    ):
        self._device = device_gateway
        self._incident = incident_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get device history."""
        try:
            self._validate_parameters(parameters, ["device_id"])
            
            device_id = parameters["device_id"]
            
            # Get device
            device = await self._device.get_by_id(device_id, context.tenant_id)
            if not device:
                return self._format_not_found("Device", device_id)
            
            # Get maintenance history
            history = await self._device.get_history(device_id, context.tenant_id)
            
            # Get related incidents
            incidents = await self._incident.get_by_device(
                device_id, context.tenant_id, limit=10
            )
            
            return self._format_success({
                "device": {
                    "id": device.id,
                    "name": device.name,
                    "type": device.device_type,
                    "status": device.status,
                },
                "maintenance": history.get("maintenance_records", []),
                "incidents": [
                    {
                        "id": i.id,
                        "title": i.title,
                        "severity": i.severity,
                        "status": i.status,
                    }
                    for i in incidents
                ],
            })
            
        except Exception as e:
            return self._format_error(str(e))


class GetDeviceLocationTool(BaseDomainTool):
    """
    Tool for getting device location details.
    
    Usage:
        get_device_location(device_id="dev-001")
    """
    
    config = DomainToolConfig(
        name="get_device_location",
        description="Get the physical location of a device including building, floor, and room.",
        category="domain.device",
        parameters_schema={
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID",
                },
            },
            "required": ["device_id"],
        },
    )
    
    def __init__(self, device_gateway: DeviceGateway):
        self._gateway = device_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get device location."""
        try:
            self._validate_parameters(parameters, ["device_id"])
            
            location = await self._gateway.get_location(
                parameters["device_id"],
                context.tenant_id,
            )
            
            return self._format_success(location)
            
        except Exception as e:
            return self._format_error(str(e))


class GetDeviceMaintenanceTool(BaseDomainTool):
    """
    Tool for getting devices that need maintenance.
    
    Usage:
        get_device_maintenance()
    """
    
    config = DomainToolConfig(
        name="get_device_maintenance",
        description="Get list of devices that need maintenance or are overdue for maintenance.",
        category="domain.device",
        parameters_schema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of results",
                },
            },
        },
    )
    
    def __init__(self, device_gateway: DeviceGateway):
        self._gateway = device_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get devices needing maintenance."""
        try:
            devices = await self._gateway.get_needing_maintenance(
                context.tenant_id,
            )
            
            limit = parameters.get("limit", 20)
            
            return self._format_success([
                {
                    "id": d.id,
                    "name": d.name,
                    "device_type": d.device_type,
                    "status": d.status,
                    "last_maintenance": str(d.last_maintenance) if d.last_maintenance else None,
                }
                for d in devices[:limit]
            ])
            
        except Exception as e:
            return self._format_error(str(e))
