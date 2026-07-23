"""
PHASE 5 - EPIC 6: Planning Domain Objects

Domain objects especializados para planificación:
- ActionPlan
- ClinicalPlan
- ExecutionTask
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class ActionPriority(str, Enum):
    """Prioridad de acción."""
    CRITICAL = "critical"           # Crítica - acción inmediata
    HIGH = "high"                   # Alta - ASAP
    MEDIUM = "medium"               # Media - esta semana
    LOW = "low"                    # Baja - planificar
    ROUTINE = "routine"            # Rutina - cuando sea posible


class ActionStatus(str, Enum):
    """Estado de acción."""
    PENDING = "pending"           # Pendiente
    SCHEDULED = "scheduled"       # Programada
    IN_PROGRESS = "in_progress"   # En progreso
    COMPLETED = "completed"       # Completada
    CANCELLED = "cancelled"      # Cancelada
    FAILED = "failed"            # Fallida


class TaskType(str, Enum):
    """Tipos de tarea."""
    CLINICAL = "clinical"         # Clínica
    TECHNICAL = "technical"       # Técnica
    MAINTENANCE = "maintenance"   # Mantenimiento
    CALIBRATION = "calibration"   # Calibración
    INSPECTION = "inspection"     # Inspección
    TRAINING = "training"          # Capacitación
    DOCUMENTATION = "documentation"  # Documentación
    COORDINATION = "coordination"  # Coordinación


class TaskStatus(str, Enum):
    """Estado de tarea."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class ClinicalPhase(str, Enum):
    """Fases clínicas."""
    ASSESSMENT = "assessment"       # Evaluación
    PLANNING = "planning"          # Planificación
    PREPARATION = "preparation"    # Preparación
    IMPLEMENTATION = "implementation"  # Implementación
    MONITORING = "monitoring"      # Monitoreo
    EVALUATION = "evaluation"      # Evaluación


# =============================================================================
# ACTION ITEM - Elemento de acción
# =============================================================================

@dataclass
class ActionItem:
    """Elemento individual de un plan de acción."""
    item_id: str = ""
    
    # Descripción
    title: str = ""
    description: str = ""
    
    # Prioridad y estado
    priority: ActionPriority = ActionPriority.MEDIUM
    status: ActionStatus = ActionStatus.PENDING
    
    # Asignación
    assigned_to: str = ""
    estimated_duration_minutes: int = 0
    
    # Dependencias
    dependencies: list[str] = field(default_factory=list)
    
    # Riesgos
    risk_level: float = 0.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.item_id:
            self.item_id = str(uuid.uuid4())


# =============================================================================
# ACTION PLAN - Plan de acción
# =============================================================================

@dataclass
class ActionPlan:
    """Plan de acción completo."""
    plan_id: str = ""
    context_id: str = ""  # Incident, diagnosis, etc.
    
    # Título y descripción
    title: str = ""
    description: str = ""
    
    # Acciones
    actions: list[ActionItem] = field(default_factory=list)
    
    # Stats
    total_actions: int = 0
    completed_actions: int = 0
    critical_actions: int = 0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    estimated_completion: datetime | None = None
    
    def __post_init__(self):
        if not self.plan_id:
            self.plan_id = str(uuid.uuid4())
        
        self.total_actions = len(self.actions)
        self.completed_actions = len([a for a in self.actions if a.status == ActionStatus.COMPLETED])
        self.critical_actions = len([a for a in self.actions if a.priority == ActionPriority.CRITICAL])
    
    def add_action(self, action: ActionItem) -> None:
        """Agrega una acción al plan."""
        self.actions.append(action)
        self.total_actions = len(self.actions)
        self.completed_actions = len([a for a in self.actions if a.status == ActionStatus.COMPLETED])
        self.critical_actions = len([a for a in self.actions if a.priority == ActionPriority.CRITICAL])
    
    def get_actions_by_priority(self, priority: ActionPriority) -> list[ActionItem]:
        """Obtiene acciones por prioridad."""
        return [a for a in self.actions if a.priority == priority]
    
    def get_critical_path(self) -> list[ActionItem]:
        """Obtiene el camino crítico (acciones CRITICAL y HIGH)."""
        critical = [a for a in self.actions if a.priority in [ActionPriority.CRITICAL, ActionPriority.HIGH]]
        return sorted(critical, key=lambda x: x.estimated_duration_minutes, reverse=True)
    
    def get_progress_percentage(self) -> float:
        """Obtiene el porcentaje de progreso."""
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100


# =============================================================================
# CLINICAL PHASE ITEM
# =============================================================================

@dataclass
class ClinicalPhaseItem:
    """Elemento de una fase clínica."""
    phase_id: str = ""
    phase: ClinicalPhase = ClinicalPhase.ASSESSMENT
    
    # Descripción
    objectives: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    
    # Duración
    estimated_duration_minutes: int = 0
    
    # Criterios de salida
    exit_criteria: list[str] = field(default_factory=list)
    
    # Metadatos
    order: int = 0
    
    def __post_init__(self):
        if not self.phase_id:
            self.phase_id = str(uuid.uuid4())


# =============================================================================
# CLINICAL PLAN - Plan clínico
# =============================================================================

@dataclass
class ClinicalPlan:
    """Plan clínico estructurado."""
    plan_id: str = ""
    patient_id: str = ""
    
    # Título
    title: str = ""
    description: str = ""
    
    # Fases
    phases: list[ClinicalPhaseItem] = field(default_factory=list)
    
    # Progreso
    current_phase_index: int = 0
    progress_percentage: float = 0.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    start_date: datetime | None = None
    estimated_end_date: datetime | None = None
    
    def __post_init__(self):
        if not self.plan_id:
            self.plan_id = str(uuid.uuid4())
        self._calculate_progress()
    
    def add_phase(self, phase: ClinicalPhaseItem) -> None:
        """Agrega una fase al plan."""
        self.phases.append(phase)
        self.phases.sort(key=lambda x: x.order)
        self._calculate_progress()
    
    def get_current_phase(self) -> ClinicalPhaseItem | None:
        """Obtiene la fase actual."""
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None
    
    def advance_phase(self) -> bool:
        """Avanza a la siguiente fase."""
        if self.current_phase_index < len(self.phases) - 1:
            self.current_phase_index += 1
            self._calculate_progress()
            return True
        return False
    
    def _calculate_progress(self) -> None:
        """Calcula el progreso del plan."""
        if len(self.phases) == 0:
            self.progress_percentage = 0.0
        else:
            self.progress_percentage = (self.current_phase_index / len(self.phases)) * 100
    
    def to_timeline(self) -> list[dict]:
        """Convierte a formato de línea de tiempo."""
        timeline = []
        for phase in self.phases:
            timeline.append({
                "phase": phase.phase.value,
                "duration_minutes": phase.estimated_duration_minutes,
                "objectives": phase.objectives,
            })
        return timeline


# =============================================================================
# EXECUTION TASK - Tarea de ejecución
# =============================================================================

@dataclass
class ExecutionTask:
    """Tarea ejecutable."""
    task_id: str = ""
    plan_id: str = ""
    
    # Descripción
    title: str = ""
    description: str = ""
    
    # Tipo y estado
    task_type: TaskType = TaskType.TECHNICAL
    status: TaskStatus = TaskStatus.PENDING
    
    # Asignación
    assigned_to: str = ""
    assigned_role: str = ""
    
    # Timing
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    
    # Recursos
    required_resources: list[str] = field(default_factory=list)
    estimated_duration_minutes: int = 0
    
    # Dependencias
    dependencies: list[str] = field(default_factory=list)
    
    # Resultado
    output: str = ""
    notes: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: int = 5
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
    
    def is_overdue(self) -> bool:
        """Verifica si la tarea está vencida."""
        if self.scheduled_end and self.status != TaskStatus.COMPLETED:
            return datetime.now(UTC) > self.scheduled_end
        return False
    
    def get_duration_actual_minutes(self) -> int | None:
        """Obtiene la duración real en minutos."""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return None
    
    def complete(self, output: str = "") -> None:
        """Marca la tarea como completada."""
        self.status = TaskStatus.COMPLETED
        self.actual_end = datetime.now(UTC)
        self.output = output


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ActionPriority",
    "ActionStatus",
    "TaskType",
    "TaskStatus",
    "ClinicalPhase",
    # Domain Objects
    "ActionItem",
    "ActionPlan",
    "ClinicalPhaseItem",
    "ClinicalPlan",
    "ExecutionTask",
]
