"""
Hospital Context Provider.

Provides hospital structure and capacity context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.PHASE_2.ai.domain import HospitalGateway


class HospitalContextProvider(BaseContextProvider):
    """
    Provides hospital context for the AI.
    
    Retrieves department info, bed capacity, and hospital structure.
    """
    
    def __init__(
        self,
        hospital_gateway: HospitalGateway | None = None,
    ):
        self._hospital = hospital_gateway
    
    @property
    def name(self) -> str:
        return "hospital"
    
    @property
    def priority(self) -> int:
        return 70  # Low priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get hospital context."""
        items = []
        
        # Get capacity overview
        capacity = await self._get_capacity_safe("campus-001", query.tenant_id)
        if capacity:
            items.append(self._capacity_to_context(capacity))
        
        return items
    
    async def _get_capacity_safe(self, campus_id: str, tenant_id: str) -> dict | None:
        """Safely get capacity."""
        if self._hospital is None:
            return self._mock_get_capacity()
        try:
            result = await self._hospital.get_capacity(campus_id, tenant_id)
            return {
                "campus_name": result.campus_name,
                "total_beds": result.total_beds,
                "available_beds": result.available_beds,
                "occupancy_rate": result.occupancy_rate,
                "departments": result.departments,
            }
        except Exception:
            return None
    
    def _capacity_to_context(self, capacity: dict) -> ContextItem:
        """Create capacity context."""
        occupancy_pct = capacity["occupancy_rate"] * 100
        lines = [
            f"Hospital Capacity - {capacity['campus_name']}:",
            f"Total Beds: {capacity['total_beds']} | Available: {capacity['available_beds']}",
            f"Occupancy: {occupancy_pct:.1f}%",
        ]
        
        if capacity.get("departments"):
            lines.append("\nDepartment Status:")
            for dept in capacity["departments"][:5]:
                lines.append(f"- {dept['name']}: {dept.get('available', 0)} beds available")
        
        return self._create_item(
            content="\n".join(lines),
            relevance_score=0.5,
            metadata={"type": "hospital_capacity"},
        )
    
    def _mock_get_capacity(self) -> dict:
        """Mock capacity for testing."""
        return {
            "campus_name": "Main Hospital",
            "total_beds": 500,
            "available_beds": 45,
            "occupancy_rate": 0.91,
            "departments": [
                {"name": "ICU", "available": 5},
                {"name": "Emergency", "available": 8},
                {"name": "Surgery", "available": 12},
            ],
        }
