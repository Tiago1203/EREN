"""
Clinical DTOs - Data Transfer Objects for Clinical Intelligence
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

__all__ = [
    "ClinicalFinding",
    "DiagnosisCandidate",
    "TreatmentRecommendation",
    "ClinicalAlert",
    "PatientSummary",
    "ClinicalSignificance",
]


class ClinicalSignificance(Enum):
    """Significancia clínica de un hallazgo."""
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ClinicalFinding:
    """
    Hallazgo clínico con evidencia.
    
    Representa un hallazgo médico identificado durante el análisis
    clínico con toda su metadata de evidencia y confianza.
    """
    finding_id: str
    concept_id: str  # SNOMED, ICD-10, LOINC, etc.
    description: str
    evidence_level: "EvidenceLevel"
    source: "EvidenceSource"
    confidence: float  # 0.0 - 1.0
    patient_context: dict
    clinical_significance: ClinicalSignificance
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "finding_id": self.finding_id,
            "concept_id": self.concept_id,
            "description": self.description,
            "evidence_level": self.evidence_level.value if hasattr(self.evidence_level, 'value') else str(self.evidence_level),
            "confidence": self.confidence,
            "clinical_significance": self.clinical_significance.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class DiagnosisCandidate:
    """
    Candidato a diagnóstico.
    
    Representa un posible diagnóstico con su probabilidad,
    evidencia pendukung y conflictos.
    """
    diagnosis_id: str
    icd_code: str  # ICD-10/ICD-11
    description: str
    probability: float
    supporting_findings: list[str]
    conflicting_findings: list[str]
    evidence_chain: "EvidenceChain"
    confidence_score: "ConfidenceScore"
    explanation: str
    differential_rank: int = 0


@dataclass(frozen=True)
class TreatmentRecommendation:
    """
    Recomendación de tratamiento.
    
    Representa una recomendación de tratamiento con evidencia,
    contraindicaciones y alternativas.
    """
    recommendation_id: str
    treatment_type: str
    description: str
    dosage: Optional[str]
    contraindications: list[str]
    evidence_level: "EvidenceLevel"
    confidence_score: "ConfidenceScore"
    alternatives: list[str]
    monitoring_required: list[str]
    urgency: str = "routine"  # emergent, urgent, routine


@dataclass(frozen=True)
class ClinicalAlert:
    """
    Alerta clínica.
    
    Representa una alerta que requiere atención del clínico.
    """
    alert_id: str
    alert_type: str
    title: str
    message: str
    severity: str  # critical, high, medium, low
    affected_entities: list[str]
    actions_required: list[str]
    acknowledged: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PatientSummary:
    """
    Resumen del paciente.
    
    Aggrega información relevante del paciente para análisis clínico.
    """
    patient_id: str
    demographics: dict
    active_diagnoses: list[str]
    active_medications: list[str]
    allergies: list[str]
    lab_results: dict
    vital_signs: dict
    recent_findings: list[str]
    risk_factors: list[str]
    summary_date: datetime = field(default_factory=datetime.now)
