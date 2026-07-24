"""
Domain objects para EPIC 12: Clinical Context Builder
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class RiskLevel(Enum):
    """Nivel de riesgo."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CalibrationStatus(Enum):
    """Estado de calibración."""
    VALID = "valid"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class ContextMetadata:
    """Metadatos de contexto."""
    created_at: datetime
    updated_at: datetime
    created_by: str
    session_id: str
    version: int = 1
    
    def is_stale(self, threshold_hours: int = 24) -> bool:
        """Verifica si está obsoleto."""
        age_hours = (datetime.now() - self.updated_at).total_seconds() / 3600
        return age_hours > threshold_hours


@dataclass
class MedicalHistory:
    """Historia médica."""
    history_id: str
    conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    procedures: list[str] = field(default_factory=list)


@dataclass
class PatientDemographics:
    """Demográficos de paciente."""
    age: int
    gender: str
    blood_type: Optional[str] = None


@dataclass
class PatientContext:
    """Contexto de paciente."""
    patient_id: str
    medical_history: MedicalHistory
    active_conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    demographics: Optional[PatientDemographics] = None
    
    def get_critical_conditions(self) -> list[str]:
        """Obtiene condiciones críticas."""
        critical = ["diabetes", "cardiac", "respiratory"]
        return [c for c in self.active_conditions if any(cc in c.lower() for cc in critical)]


@dataclass
class MaintenanceRecord:
    """Registro de mantenimiento."""
    record_id: str
    date: datetime
    type: str
    description: str
    technician: str


@dataclass
class Incident:
    """Incidente."""
    incident_id: str
    date: datetime
    type: str
    severity: str
    resolution: str


@dataclass
class DeviceContext:
    """Contexto de dispositivo."""
    device_id: str
    device_type: str
    manufacturer: str
    model: str
    maintenance_history: list[MaintenanceRecord] = field(default_factory=list)
    incident_history: list[Incident] = field(default_factory=list)
    calibration_status: CalibrationStatus = CalibrationStatus.VALID
    risk_classification: str = "CLASS_B"
    
    def needs_maintenance(self) -> bool:
        """Verifica si necesita mantenimiento."""
        if self.calibration_status == CalibrationStatus.EXPIRED:
            return True
        last_maintenance = max((r.date for r in self.maintenance_history), default=None)
        if last_maintenance:
            days_since = (datetime.now() - last_maintenance).days
            return days_since > 90
        return False


@dataclass
class DepartmentContext:
    """Contexto de departamento."""
    department_id: str
    name: str
    specialty: str


@dataclass
class UnitContext:
    """Contexto de unidad."""
    unit_id: str
    name: str
    department_id: str


@dataclass
class BedAvailability:
    """Disponibilidad de camas."""
    total: int
    occupied: int
    available: int


@dataclass
class StaffAvailability:
    """Disponibilidad de staff."""
    total: int
    on_duty: int


@dataclass
class ResourceCapacity:
    """Capacidad de recursos."""
    equipment: dict[str, int] = field(default_factory=dict)
    consumables: dict[str, int] = field(default_factory=dict)


@dataclass
class HospitalContext:
    """Contexto hospitalario."""
    hospital_id: str
    department: DepartmentContext
    unit: Optional[UnitContext] = None
    bed_availability: Optional[BedAvailability] = None
    staff_availability: Optional[StaffAvailability] = None
    resource_capacity: Optional[ResourceCapacity] = None
    
    def get_resource_constraints(self) -> list[str]:
        """Obtiene restricciones de recursos."""
        constraints = []
        if self.bed_availability and self.bed_availability.available < 5:
            constraints.append("Limited bed availability")
        if self.staff_availability and self.staff_availability.on_duty < 3:
            constraints.append("Limited staff availability")
        return constraints


@dataclass
class ClinicalTimeline:
    """Línea de tiempo clínica."""
    events: list[dict] = field(default_factory=list)
    
    def add_event(self, event: dict) -> None:
        """Agrega evento."""
        self.events.append(event)


@dataclass
class RiskFactor:
    """Factor de riesgo."""
    factor_id: str
    description: str
    level: RiskLevel
    source: str


@dataclass
class ClinicalContext:
    """Contexto clínico unificado."""
    context_id: str
    patient_context: PatientContext
    device_context: DeviceContext
    hospital_context: HospitalContext
    timeline: ClinicalTimeline
    metadata: ContextMetadata
    risk_factors: list[RiskFactor] = field(default_factory=list)
    
    def get_patient_id(self) -> str:
        """Obtiene ID de paciente."""
        return self.patient_context.patient_id
    
    def get_device_id(self) -> str:
        """Obtiene ID de dispositivo."""
        return self.device_context.device_id
    
    def get_active_conditions(self) -> list[str]:
        """Obtiene condiciones activas."""
        return self.patient_context.active_conditions
    
    def get_risk_level(self) -> RiskLevel:
        """Obtiene nivel de riesgo."""
        if self.risk_factors:
            return max(self.risk_factors, key=lambda x: x.level).level
        return RiskLevel.LOW


@dataclass
class ClinicalContextConfig:
    """Configuración para ClinicalContextAgent."""
    include_history: bool = True
    include_conditions: bool = True
    include_maintenance: bool = True
    include_incidents: bool = True
    context_timeout_hours: int = 24
