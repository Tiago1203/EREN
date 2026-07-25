"""
PHASE 7 - EPIC 0: IEC 62304 Software Lifecycle

Gestión del ciclo de vida del software médico:
- Development planning
- Software maintenance planning
- Risk management integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class LifecyclePhase(str, Enum):
    """Fases del ciclo de vida."""
    PLANNING = "planning"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    DETAILED_DESIGN = "detailed_design"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    VALIDATION = "validation"
    RELEASE = "release"
    MAINTENANCE = "maintenance"


class MaintenanceType(str, Enum):
    """Tipos de mantenimiento."""
    CORRECTIVE = "corrective"       # Fix defects
    ADAPTIVE = "adaptive"           #适应环境变化
    PERFECTIVE = "perfective"      # Improve performance
    PREVENTIVE = "preventive"      # Prevent future issues


@dataclass
class SoftwareDevelopmentPlan:
    """Plan de desarrollo de software."""
    plan_id: str
    software_name: str
    software_class: str           # A, B, C
    current_phase: LifecyclePhase = LifecyclePhase.PLANNING
    created_at: datetime = field(default_factory=datetime.utcnow)
    phases_completed: list[str] = field(default_factory=list)
    milestones: list[dict] = field(default_factory=list)


@dataclass
class MaintenanceRecord:
    """Registro de mantenimiento."""
    record_id: str
    maintenance_type: MaintenanceType
    description: str
    affected_components: list[str] = field(default_factory=list)
    risk_assessment: str = ""
    impact_analysis: str = ""
    implemented_by: str = ""
    implemented_at: datetime = field(default_factory=datetime.utcnow)


class SoftwareLifecycleManager:
    """Gestor del ciclo de vida del software."""

    def __init__(self):
        self._plans: dict[str, SoftwareDevelopmentPlan] = {}
        self._maintenance_records: list[MaintenanceRecord] = []

    def create_development_plan(
        self,
        software_name: str,
        software_class: str,
    ) -> SoftwareDevelopmentPlan:
        """Crea plan de desarrollo."""
        plan = SoftwareDevelopmentPlan(
            plan_id=f"dev-plan-{software_name.lower().replace(' ', '-')}",
            software_name=software_name,
            software_class=software_class,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def transition_phase(
        self,
        plan_id: str,
        new_phase: LifecyclePhase,
    ) -> bool:
        """Transiciona a nueva fase."""
        plan = self._plans.get(plan_id)
        if not plan:
            return False

        plan.phases_completed.append(plan.current_phase.value)
        plan.current_phase = new_phase
        return True

    def record_maintenance(
        self,
        maintenance_type: MaintenanceType,
        description: str,
        affected_components: list[str],
        risk_assessment: str,
        impact_analysis: str,
        implemented_by: str,
    ) -> MaintenanceRecord:
        """Registra actividad de mantenimiento."""
        record = MaintenanceRecord(
            record_id=f"maint-{len(self._maintenance_records) + 1:04d}",
            maintenance_type=maintenance_type,
            description=description,
            affected_components=affected_components,
            risk_assessment=risk_assessment,
            impact_analysis=impact_analysis,
            implemented_by=implemented_by,
        )
        self._maintenance_records.append(record)
        return record

    def get_development_status(self, plan_id: str) -> dict:
        """Obtiene estado de desarrollo."""
        plan = self._plans.get(plan_id)
        if not plan:
            return {}

        total_phases = len(LifecyclePhase)
        completed = len(plan.phases_completed)

        return {
            "plan_id": plan_id,
            "software_name": plan.software_name,
            "software_class": plan.software_class,
            "current_phase": plan.current_phase.value,
            "phases_completed": completed,
            "completion_percentage": (completed / total_phases) * 100,
            "milestones": plan.milestones,
        }
