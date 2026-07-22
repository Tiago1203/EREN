"""
Hospital Domain Tools.

Tools for accessing hospital/capacity data from the domain.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext

if TYPE_CHECKING:
    from core.PHASE_2.ai.domain import HospitalGateway


class GetCapacityInfoTool(BaseDomainTool):
    """
    Tool for getting hospital capacity information.
    
    Usage:
        get_capacity_info(campus_id="campus-001")
    """
    
    config = DomainToolConfig(
        name="get_capacity_info",
        description="Get hospital bed capacity information including occupancy rates by department.",
        category="domain.hospital",
        parameters_schema={
            "type": "object",
            "properties": {
                "campus_id": {
                    "type": "string",
                    "default": "campus-001",
                    "description": "Campus/Hospital ID",
                },
            },
        },
    )
    
    def __init__(self, hospital_gateway: HospitalGateway):
        self._gateway = hospital_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get capacity info."""
        try:
            campus_id = parameters.get("campus_id", "campus-001")
            
            capacity = await self._gateway.get_capacity(
                campus_id,
                context.tenant_id,
            )
            
            return self._format_success({
                "campus_name": capacity.campus_name,
                "total_beds": capacity.total_beds,
                "occupied_beds": capacity.occupied_beds,
                "available_beds": capacity.available_beds,
                "occupancy_rate": f"{capacity.occupancy_rate * 100:.1f}%",
                "departments": capacity.departments,
            })
            
        except Exception as e:
            return self._format_error(str(e))


class GetDepartmentInfoTool(BaseDomainTool):
    """
    Tool for getting department information.
    
    Usage:
        get_department_info(campus_id="campus-001")
    """
    
    config = DomainToolConfig(
        name="get_department_info",
        description="Get information about hospital departments including bed availability.",
        category="domain.hospital",
        parameters_schema={
            "type": "object",
            "properties": {
                "campus_id": {
                    "type": "string",
                    "default": "campus-001",
                    "description": "Campus/Hospital ID",
                },
            },
        },
    )
    
    def __init__(self, hospital_gateway: HospitalGateway):
        self._gateway = hospital_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get department info."""
        try:
            campus_id = parameters.get("campus_id", "campus-001")
            
            departments = await self._gateway.get_departments(
                campus_id,
                context.tenant_id,
            )
            
            return self._format_success([
                {
                    "id": d.id,
                    "name": d.name,
                    "floor": d.floor,
                    "building": d.building,
                    "beds": d.beds,
                    "available_beds": d.available_beds,
                }
                for d in departments
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class GetAvailableBedsTool(BaseDomainTool):
    """
    Tool for getting available beds.
    
    Usage:
        get_available_beds(department_id="ICU")
    """
    
    config = DomainToolConfig(
        name="get_available_beds",
        description="Get list of available beds, optionally filtered by department.",
        category="domain.hospital",
        parameters_schema={
            "type": "object",
            "properties": {
                "department_id": {
                    "type": "string",
                    "description": "Department name to filter by",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                },
            },
        },
    )
    
    def __init__(self, hospital_gateway: HospitalGateway):
        self._gateway = hospital_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get available beds."""
        try:
            beds = await self._gateway.get_available_beds(
                tenant_id=context.tenant_id,
                department_id=parameters.get("department_id"),
                limit=parameters.get("limit", 20),
            )
            
            return self._format_success(beds)
            
        except Exception as e:
            return self._format_error(str(e))
