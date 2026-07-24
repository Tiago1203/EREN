"""
HospitalContextBuilder: Constructor de contexto hospitalario
"""

from typing import Optional

from core.PHASE_5.epic12_clinical_context.domain import (
    HospitalContext,
    DepartmentContext,
    UnitContext,
    BedAvailability,
    StaffAvailability,
    ResourceCapacity,
)


class HospitalContextBuilder:
    """Constructor de contexto hospitalario."""
    
    async def build(
        self,
        hospital_id: str,
        include_departments: bool = True,
        include_capacity: bool = True,
    ) -> HospitalContext:
        """
        Construye contexto hospitalario.
        
        Args:
            hospital_id: ID del hospital
            include_departments: Incluir departamentos
            include_capacity: Incluir capacidad
        
        Returns:
            HospitalContext construido
        """
        # En implementación real, esto consultaría FASE 1/Hospital
        department = DepartmentContext(
            department_id=f"dept_{hospital_id}_1",
            name="Intensive Care Unit",
            specialty="critical_care",
        ) if include_departments else None
        
        hospital_context = HospitalContext(
            hospital_id=hospital_id,
            department=department,
            unit=None,
            bed_availability=BedAvailability(total=20, occupied=15, available=5) if include_capacity else None,
            staff_availability=StaffAvailability(total=50, on_duty=35),
            resource_capacity=ResourceCapacity() if include_capacity else None,
        )
        
        return hospital_context
    
    async def get_department_context(
        self,
        department_id: str,
    ) -> DepartmentContext:
        """Obtiene contexto de departamento."""
        return DepartmentContext(
            department_id=department_id,
            name="Intensive Care Unit",
            specialty="critical_care",
        )
    
    async def get_resource_availability(
        self,
        hospital_id: str,
    ) -> dict:
        """Obtiene disponibilidad de recursos."""
        return {
            "beds": {"total": 20, "available": 5},
            "staff": {"total": 50, "on_duty": 35},
            "equipment": {"ventilators": 10, "monitors": 25},
        }
