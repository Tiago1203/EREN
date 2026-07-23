"""
PHASE 5 - EPIC 3: Diagnostic Domain Objects

Domain objects especializados para diagnóstico técnico:
- DiagnosticTask
- FailurePattern
- DiagnosticReport
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

class DiagnosticTaskType(str, Enum):
    """Tipos de tarea de diagnóstico."""
    FAILURE_ANALYSIS = "failure_analysis"           # Análisis de falla
    ROOT_CAUSE = "root_cause"                      # Análisis de causa raíz
    PREDICTIVE = "predictive"                       # Diagnóstico predictivo
    CORRELATION = "correlation"                     # Correlación de fallas
    TROUBLESHOOTING = "troubleshooting"             # Resolución de problemas
    INVESTIGATION = "investigation"                 # Investigación


class FailureSeverity(str, Enum):
    """Severidad de falla."""
    CRITICAL = "critical"           # Falla total del sistema
    HIGH = "high"                 # Falla con impacto significativo
    MEDIUM = "medium"             # Falla menor
    LOW = "low"                   # Anomalía menor
    WARNING = "warning"            # Advertencia


class DiagnosisConfidence(str, Enum):
    """Nivel de confianza del diagnóstico."""
    HIGH = "high"                 # > 90%
    MEDIUM = "medium"             # 70-90%
    LOW = "low"                  # 50-70%
    UNCERTAIN = "uncertain"       # < 50%


# =============================================================================
# DIAGNOSTIC TASK - Tarea de diagnóstico
# =============================================================================

@dataclass
class DiagnosticTask:
    """Tarea de diagnóstico técnico."""
    task_id: str = ""
    task_type: DiagnosticTaskType = DiagnosticTaskType.FAILURE_ANALYSIS
    
    # Dispositivo/Componente
    device_id: str = ""
    device_name: str = ""
    component: str = ""
    
    # Descripción del problema
    symptom: str = ""              # Síntoma observado
    error_codes: list[str] = field(default_factory=list)
    conditions: dict = field(default_factory=dict)
    
    # Contexto
    context: dict = field(default_factory=dict)
    
    # Constraints
    priority: int = 5
    timeout_seconds: int = 300
    
    # State
    status: str = "pending"
    
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
        return self.status == "completed"
    
    @property
    def duration_ms(self) -> int | None:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None


# =============================================================================
# FAILURE PATTERN - Patrón de falla
# =============================================================================

@dataclass
class FailurePattern:
    """Patrón de falla identificado."""
    pattern_id: str = ""
    pattern_name: str = ""
    
    # Descripción
    description: str = ""
    symptom_description: str = ""
    
    # Severidad
    severity: FailureSeverity = FailureSeverity.MEDIUM
    
    # Componentes afectados
    affected_components: list[str] = field(default_factory=list)
    
    # Condiciones de activación
    trigger_conditions: dict = field(default_factory=dict)
    
    # Causas conocidas
    known_causes: list[str] = field(default_factory=list)
    
    # Soluciones asociadas
    recommended_solutions: list[str] = field(default_factory=list)
    
    # Frecuencia
    occurrence_count: int = 0
    first_occurrence: datetime | None = None
    last_occurrence: datetime | None = None
    
    # Metadatos
    confidence: float = 0.0
    source: str = ""
    
    def __post_init__(self):
        if not self.pattern_id:
            self.pattern_id = str(uuid.uuid4())


# =============================================================================
# DIAGNOSTIC REPORT - Reporte de diagnóstico
# =============================================================================

@dataclass
class DiagnosticReport:
    """Reporte de diagnóstico."""
    report_id: str = ""
    task_id: str = ""
    
    # Resultado
    diagnosis: str = ""
    confidence: DiagnosisConfidence = DiagnosisConfidence.MEDIUM
    confidence_score: float = 0.0
    
    # Hipótesis
    hypotheses: list[dict] = field(default_factory=list)
    primary_cause: str = ""
    
    # Evidencia
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    
    # Patrones
    matched_patterns: list[FailurePattern] = field(default_factory=list)
    
    # Recomendaciones
    recommended_actions: list[dict] = field(default_factory=list)
    
    # Estado del sistema
    system_state: dict = field(default_factory=dict)
    
    # Incertidumbre
    uncertainty_factors: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    analyst_agent: str = "diagnostic_agent"
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
    
    def add_hypothesis(
        self,
        hypothesis: str,
        probability: float,
        evidence: list[str] | None = None,
    ) -> None:
        """Agrega una hipótesis al reporte."""
        self.hypotheses.append({
            "hypothesis": hypothesis,
            "probability": probability,
            "evidence": evidence or [],
        })
        # Ordenar por probabilidad
        self.hypotheses.sort(key=lambda h: h["probability"], reverse=True)
    
    def set_primary_cause(self, cause: str) -> None:
        """Establece la causa primaria."""
        self.primary_cause = cause
        if self.hypotheses:
            # Buscar la hipótesis correspondiente
            for h in self.hypotheses:
                if h["hypothesis"] == cause:
                    self.confidence_score = h["probability"]
                    if self.confidence_score >= 0.9:
                        self.confidence = DiagnosisConfidence.HIGH
                    elif self.confidence_score >= 0.7:
                        self.confidence = DiagnosisConfidence.MEDIUM
                    elif self.confidence_score >= 0.5:
                        self.confidence = DiagnosisConfidence.LOW
                    else:
                        self.confidence = DiagnosisConfidence.UNCERTAIN
                    break


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "DiagnosticTaskType",
    "FailureSeverity",
    "DiagnosisConfidence",
    # Domain Objects
    "DiagnosticTask",
    "FailurePattern",
    "DiagnosticReport",
]
