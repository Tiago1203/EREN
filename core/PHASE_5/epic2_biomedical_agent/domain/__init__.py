"""
PHASE 5 - EPIC 2: Biomedical Domain Objects

Domain objects especializados para Ingeniería Clínica:
- BiomedicalTask
- DeviceAssessment
- MaintenanceRecommendation
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

class BiomedicalTaskType(str, Enum):
    """Tipos de tarea biomédica."""
    DEVICE_ANALYSIS = "device_analysis"       # Análisis de equipo
    MAINTENANCE_PLANNING = "maintenance_planning"  # Planificación de mantenimiento
    CALIBRATION_CHECK = "calibration_check"   # Verificación de calibración
    COMPLIANCE_AUDIT = "compliance_audit"     # Auditoría de cumplimiento
    RISK_ASSESSMENT = "risk_assessment"       # Evaluación de riesgo
    INCIDENT_INVESTIGATION = "incident_investigation"  # Investigación de incidentes
    MANUAL_REVIEW = "manual_review"           # Revisión de manuales
    SPECIFICATION_ANALYSIS = "specification_analysis"  # Análisis de especificaciones


class AssessmentSeverity(str, Enum):
    """Severidad de una evaluación."""
    CRITICAL = "critical"       # Requiere acción inmediata
    HIGH = "high"               # Requiere acción soon
    MEDIUM = "medium"           # Requiere atención
    LOW = "low"                # Monitorear
    INFO = "info"              # Informativo


class AssessmentStatus(str, Enum):
    """Estado de una evaluación."""
    PENDING = "pending"           # Pendiente
    IN_PROGRESS = "in_progress"    # En progreso
    COMPLETED = "completed"        # Completada
    FAILED = "failed"            # Fallida
    CANCELLED = "cancelled"      # Cancelada


class MaintenancePriority(str, Enum):
    """Prioridad de mantenimiento."""
    URGENT = "urgent"             # Inmediato (0-24h)
    HIGH = "high"                 # Alta (1-7 días)
    MEDIUM = "medium"             # Media (1-4 semanas)
    LOW = "low"                  # Baja (1-3 meses)
    SCHEDULED = "scheduled"       # Programado


class MaintenanceType(str, Enum):
    """Tipos de mantenimiento."""
    PREVENTIVE = "preventive"         # Preventivo
    CORRECTIVE = "corrective"         # Correctivo
    PREDICTIVE = "predictive"         # Predictivo
    CALIBRATION = "calibration"        # Calibración
    SAFETY = "safety"                 # Seguridad
    EMERGENCY = "emergency"           # Emergencia
    INSPECTION = "inspection"         # Inspección


# =============================================================================
# BIOMEDICAL TASK - Tarea biomédica
# =============================================================================

@dataclass
class BiomedicalTask:
    """Tarea especializada en Ingeniería Clínica."""
    task_id: str = ""
    task_type: BiomedicalTaskType = BiomedicalTaskType.MANUAL_REVIEW
    
    # Dispositivo
    device_id: str | None = None
    device_name: str = ""
    device_type: str = ""
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    
    # Descripción
    description: str = ""
    user_query: str = ""
    
    # Context
    context: dict = field(default_factory=dict)
    
    # Constraints
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    timeout_seconds: int = 300
    
    # State
    status: AssessmentStatus = AssessmentStatus.PENDING
    
    # Resultado
    result: dict = field(default_factory=dict)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
    
    @property
    def is_complete(self) -> bool:
        return self.status == AssessmentStatus.COMPLETED
    
    @property
    def duration_ms(self) -> int | None:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None


# =============================================================================
# DEVICE ASSESSMENT - Evaluación de dispositivo
# =============================================================================

@dataclass
class DeviceAssessment:
    """Evaluación de un dispositivo médico."""
    assessment_id: str
    device_id: str
    
    # Evaluación
    assessment_type: str = ""
    description: str = ""
    
    # Resultados
    severity: AssessmentSeverity = AssessmentSeverity.INFO
    risk_level: float = 0.0  # 0.0 - 1.0
    
    # Findings
    findings: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    # Compliance
    compliance_status: dict = field(default_factory=dict)  # standard -> status
    violations: list[dict] = field(default_factory=list)
    
    # State
    status: AssessmentStatus = AssessmentStatus.PENDING
    
    # Evidencia
    evidence: list[dict] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    
    # Metadatos
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assessor: str = "biomedical_agent"
    
    def __post_init__(self):
        if not self.assessment_id:
            self.assessment_id = str(uuid.uuid4())
    
    def add_finding(
        self,
        title: str,
        description: str,
        severity: AssessmentSeverity,
        recommendation: str | None = None,
    ) -> None:
        """Agrega un finding a la evaluación."""
        self.findings.append({
            "title": title,
            "description": description,
            "severity": severity.value,
            "recommendation": recommendation,
        })
    
    def calculate_risk(self) -> float:
        """Calcula el nivel de riesgo general."""
        if not self.findings:
            return 0.0
        
        severity_weights = {
            AssessmentSeverity.CRITICAL: 1.0,
            AssessmentSeverity.HIGH: 0.75,
            AssessmentSeverity.MEDIUM: 0.5,
            AssessmentSeverity.LOW: 0.25,
            AssessmentSeverity.INFO: 0.0,
        }
        
        total = sum(severity_weights.get(f["severity"], 0.5) for f in self.findings)
        return min(total / len(self.findings), 1.0)


# =============================================================================
# MAINTENANCE RECOMMENDATION - Recomendación de mantenimiento
# =============================================================================

@dataclass
class MaintenanceRecommendation:
    """Recomendación de mantenimiento."""
    recommendation_id: str = ""
    device_id: str = ""
    
    # Tipo
    maintenance_type: MaintenanceType = MaintenanceType.PREVENTIVE
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    
    # Descripción
    title: str = ""
    description: str = ""
    
    # Detalles técnicos
    procedure: str = ""
    estimated_duration_minutes: int = 0
    required_tools: list[str] = field(default_factory=list)
    required_parts: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    
    # Frecuencia
    frequency_days: int | None = None  # None = one-time
    
    # Parts y costos
    estimated_cost: float = 0.0
    parts_cost: float = 0.0
    labor_cost: float = 0.0
    
    # Referencias
    standards: list[str] = field(default_factory=list)  # IEC, ISO, etc.
    manufacturer_guidelines: str = ""
    citations: list[str] = field(default_factory=list)
    
    # Scheduling
    scheduled_date: datetime | None = None
    completed_date: datetime | None = None
    
    # State
    is_applicable: bool = True
    notes: str = ""
    
    def __post_init__(self):
        if not self.recommendation_id:
            self.recommendation_id = str(uuid.uuid4())
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si está vencida."""
        if not self.scheduled_date:
            return False
        return datetime.now(UTC) > self.scheduled_date
    
    @property
    def total_cost(self) -> float:
        """Calcula costo total."""
        return self.parts_cost + self.labor_cost


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums - Task
    "BiomedicalTaskType",
    # Enums - Assessment
    "AssessmentSeverity",
    "AssessmentStatus",
    # Enums - Maintenance
    "MaintenancePriority",
    "MaintenanceType",
    # Domain Objects
    "BiomedicalTask",
    "DeviceAssessment",
    "MaintenanceRecommendation",
]
