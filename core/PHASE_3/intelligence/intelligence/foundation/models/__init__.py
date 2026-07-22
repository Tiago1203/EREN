"""
Clinical Intelligence Models

NOTE: All shared Enums (EvidenceLevel, ValidationSeverity, ConfidenceLevel, etc.)
are defined in core.intelligence.foundation.enums - this module only contains
Domain Models (dataclasses) and Engine-specific Enums.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# Import shared enums from SINGLE SOURCE OF TRUTH
from core.PHASE_3.intelligence.foundation.enums import (
    EvidenceLevel,
    ValidationSeverity,
    ConfidenceLevel,
)

__all__ = [
    # Shared enums (imported from foundation.enums)
    "EvidenceLevel",
    "ValidationSeverity",
    "ConfidenceLevel",
    # Domain Models
    "EvidenceSource",
    "Evidence",
    "EvidenceChain",
    "SafetyLevel",
    "SafetyCheck",
    "ClinicalWarning",
    "ValidationRule",
    "ValidationResult",
    "ValidationPipeline",
    "ConfidenceScore",
]


# ============================================================================
# EVIDENCE MODELS
# ============================================================================

class EvidenceSourceType(Enum):
    """Tipos de fuente de evidencia."""
    RANDOMIZED_CONTROLLED_TRIAL = "rct"
    META_ANALYSIS = "meta_analysis"
    COHORT_STUDY = "cohort"
    CASE_CONTROL_STUDY = "case_control"
    CASE_SERIES = "case_series"
    GUIDELINE = "guideline"
    EXPERT_OPINION = "expert_opinion"
    PATIENT_RECORD = "patient_record"
    DEVICE_DATA = "device_data"
    REAL_WORLD_EVIDENCE = "rwe"


@dataclass(frozen=True)
class EvidenceSource:
    """Fuente de evidencia."""
    source_type: EvidenceSourceType
    source_id: str
    source_name: str
    citation: Optional[str] = None
    url: Optional[str] = None
    access_date: Optional[datetime] = None


@dataclass(frozen=True)
class Evidence:
    """
    Evidencia clínica.
    
    Representa una pieza individual de evidencia con su
    nivel, fuente y peso.
    """
    evidence_id: str
    level: EvidenceLevel
    source: EvidenceSource
    content: str
    weight: float  # 0.0 - 1.0
    applicability: float = 1.0  # 0.0 - 1.0
    quality: float = 1.0  # 0.0 - 1.0
    retrieved_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass(frozen=True)
class EvidenceChain:
    """
    Cadena de evidencia.
    
    Agrega evidencia primaria, de soporte y contradictoria
    para un hallazgo clínico.
    """
    chain_id: str
    primary_evidence: list[Evidence]
    supporting_evidence: list[Evidence]
    contradicting_evidence: list[Evidence]
    overall_consistency: float  # 0.0 - 1.0
    confidence_modifier: float = 1.0


# ============================================================================
# SAFETY MODELS
# ============================================================================

class SafetyLevel(Enum):
    """
    Nivel de seguridad clínica.
    
    Clasifica la severidad de problemas de seguridad
    desde crítica hasta informacional.
    """
    CRITICAL = "critical"  # Pone en riesgo la vida
    HIGH = "high"  # Daño serio potencial
    MEDIUM = "medium"  # Daño moderado potencial
    LOW = "low"  # Informacional
    INFORMATIONAL = "informational"


class SafetyCheckType(Enum):
    """Tipos de verificación de seguridad."""
    DRUG_INTERACTION = "drug_interaction"
    ALLERGY_CHECK = "allergy_check"
    CONTRAINDICATION = "contraindication"
    DOSE_RANGE = "dose_range"
    DUPLICATE_THERAPY = "duplicate_therapy"
    AGE_APPROPRIATENESS = "age_appropriateness"
    PREGNANCY_CHECK = "pregnancy_check"
    LAB_VALUE = "lab_value"
    VITAL_SIGN = "vital_sign"
    CUSTOM = "custom"


@dataclass(frozen=True)
class SafetyCheck:
    """Verificación de seguridad."""
    check_id: str
    check_type: SafetyCheckType
    description: str
    level: SafetyLevel
    rule_id: str
    patient_context: dict
    recommendation: str
    requires_acknowledgment: bool = True


@dataclass(frozen=True)
class ClinicalWarning:
    """Advertencia clínica."""
    warning_id: str
    level: SafetyLevel
    title: str
    message: str
    affected_entities: list[str]
    actions_required: list[str]
    escalation_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


# ============================================================================
# VALIDATION MODELS
# ============================================================================
# NOTE: ValidationSeverity is now imported from core.PHASE_3.intelligence.foundation.enums
# ValidationSeverity enum is shared across Validation, Decision, and Rules engines

class ValidationRuleType(Enum):
    """Tipos de reglas de validación."""
    SAFETY = "safety"
    EFFICACY = "efficacy"
    DOSAGE = "dosage"
    INTERACTION = "interaction"
    ALLERGY = "allergy"
    CONTRAINDICATION = "contraindication"
    COST_EFFECTIVENESS = "cost_effectiveness"
    GUIDELINE_COMPLIANCE = "guideline_compliance"
    DOCUMENTATION = "documentation"


@dataclass(frozen=True)
class ValidationRule:
    """Regla de validación."""
    rule_id: str
    rule_type: ValidationRuleType
    description: str
    severity: ValidationSeverity
    enabled: bool = True
    can_skip: bool = False


@dataclass(frozen=True)
class ValidationResult:
    """Resultado de validación."""
    is_valid: bool
    validation_id: str
    rule_id: str
    severity: ValidationSeverity
    message: str
    details: Optional[dict] = None
    failed_at: datetime = field(default_factory=datetime.now)
    can_override: bool = False


@dataclass(frozen=True)
class ValidationReport:
    """Reporte de validación completo."""
    report_id: str
    is_valid: bool
    results: list[ValidationResult]
    blocking_issues: list[ValidationResult]
    warnings: list[ValidationResult]
    passed_at: datetime = field(default_factory=datetime.now)


# ============================================================================
# CONFIDENCE MODELS
# ============================================================================
# NOTE: ConfidenceLevel is now imported from core.PHASE_3.intelligence.foundation.enums
# ConfidenceLevel enum is shared across Confidence, Reasoning, and Decision engines

class ConfidenceFactorType(Enum):
    """Tipos de factores de confianza."""
    EVIDENCE_QUALITY = "evidence_quality"
    EVIDENCE_QUANTITY = "evidence_quantity"
    CONSISTENCY = "consistency"
    NOVELTY = "novelty"
    PATIENT_MATCH = "patient_match"
    MODEL_CONFIDENCE = "model_confidence"
    SOURCE_RELIABILITY = "source_reliability"


@dataclass(frozen=True)
class ConfidenceFactor:
    """Factor que afecta la confianza."""
    factor_type: ConfidenceFactorType
    contribution: float
    description: str
    source_evidence: str


@dataclass(frozen=True)
class CalibrationData:
    """Datos de calibración."""
    calibration_date: datetime
    predicted_probabilities: list[float]
    observed_outcomes: list[float]
    calibration_slope: float
    calibration_intercept: float


@dataclass(frozen=True)
class ConfidenceScore:
    """
    Score de confianza.
    
    Representa la confianza en una recomendación o hallazgo
    con factores que la componen.
    """
    value: float  # 0.0 - 1.0
    confidence_level: ConfidenceLevel
    factors: list[ConfidenceFactor]
    calibration_data: Optional[CalibrationData] = None
    estimated_accuracy: Optional[float] = None


# ============================================================================
# VALIDATION PIPELINE (Forward Reference)
# ============================================================================

class ValidationPipeline:
    """
    Pipeline de validación clínica.
    
    Ejecuta reglas de validación en secuencia y genera
    un reporte completo.
    """
    
    def __init__(
        self,
        rules: list[ValidationRule],
    ):
        self._rules = [r for r in rules if r.enabled]
    
    async def validate(
        self,
        recommendation: "TreatmentRecommendation",
        patient_context: dict,
    ) -> ValidationReport:
        """Ejecuta validación completa."""
        results = []
        blocking_issues = []
        warnings = []
        
        for rule in self._rules:
            result = await self._check_rule(rule, recommendation, patient_context)
            results.append(result)
            
            if not result.is_valid:
                if result.severity == ValidationSeverity.BLOCKING:
                    blocking_issues.append(result)
                else:
                    warnings.append(result)
        
        return ValidationReport(
            report_id=f"report_{datetime.now().timestamp()}",
            is_valid=len(blocking_issues) == 0,
            results=results,
            blocking_issues=blocking_issues,
            warnings=warnings,
        )
    
    async def _check_rule(
        self,
        rule: ValidationRule,
        recommendation: "TreatmentRecommendation",
        patient_context: dict,
    ) -> ValidationResult:
        """Verifica una regla individual."""
        # Placeholder - implementación específica por tipo de regla
        return ValidationResult(
            is_valid=True,
            validation_id=f"val_{rule.rule_id}",
            rule_id=rule.rule_id,
            severity=rule.severity,
            message=f"Validation passed for {rule.description}",
        )
