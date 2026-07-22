"""
Hospital Gateway.

Gateway implementation for Hospital/Capacity domain.
Provides AI Core with access to hospital structure and capacity data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .contracts import HospitalDTO, DepartmentDTO, CapacityDTO, IHospitalGateway
from .exceptions import HospitalNotFoundError

if TYPE_CHECKING:
    from core.PHASE_1.domain.capacity.domain.repositories import BedRepository


class HospitalGateway(IHospitalGateway):
    """
    Gateway for Hospital/Capacity domain.
    
    AI Core uses this gateway to access hospital structure and capacity.
    """
    
    def __init__(
        self,
        bed_repository: BedRepository | None = None,
    ):
        self._bed_repository = bed_repository
    
    @property
    def name(self) -> str:
        return "hospital"
    
    async def get_by_id(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> HospitalDTO | None:
        """Get campus/hospital by ID."""
        if campus_id == "campus-001":
            return HospitalDTO(
                id="campus-001",
                name="Main Hospital",
                address="123 Medical Center Dr",
                departments=[
                    {"id": "dept-001", "name": "ICU"},
                    {"id": "dept-002", "name": "Emergency"},
                    {"id": "dept-003", "name": "Surgery"},
                ],
                total_beds=500,
                available_beds=45,
            )
        return None
    
    async def get_departments(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> list[DepartmentDTO]:
        """Get departments for a campus."""
        return [
            DepartmentDTO(
                id="dept-001",
                name="ICU",
                floor="3",
                building="Main",
                beds=50,
                available_beds=5,
            ),
            DepartmentDTO(
                id="dept-002",
                name="Emergency",
                floor="1",
                building="Main",
                beds=30,
                available_beds=8,
            ),
            DepartmentDTO(
                id="dept-003",
                name="Surgery",
                floor="2",
                building="Main",
                beds=40,
                available_beds=12,
            ),
        ]
    
    async def get_capacity(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> CapacityDTO:
        """Get capacity information."""
        return CapacityDTO(
            campus_id=campus_id,
            campus_name="Main Hospital",
            total_beds=500,
            occupied_beds=455,
            available_beds=45,
            occupancy_rate=0.91,
            departments=[
                {"name": "ICU", "beds": 50, "available": 5},
                {"name": "Emergency", "beds": 30, "available": 8},
                {"name": "Surgery", "beds": 40, "available": 12},
            ],
        )
    
    async def get_available_beds(
        self,
        tenant_id: str,
        department_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get available beds."""
        beds = [
            {"id": "bed-001", "department": "ICU", "room": "301", "type": "standard"},
            {"id": "bed-002", "department": "ICU", "room": "302", "type": "standard"},
            {"id": "bed-003", "department": "Emergency", "room": "101", "type": "emergency"},
            {"id": "bed-004", "department": "Surgery", "room": "201", "type": "recovery"},
        ]
        
        if department_id:
            beds = [b for b in beds if b["department"].lower() == department_id.lower()]
        
        return beds[:limit]
