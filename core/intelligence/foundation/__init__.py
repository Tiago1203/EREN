"""
Clinical Intelligence Foundation

This module provides the foundational components for Clinical Intelligence,
including DTOs, contracts, models, interfaces, and policies.
"""

from core.intelligence.foundation.dto import (
    ClinicalFinding,
    DiagnosisCandidate,
    TreatmentRecommendation,
    ClinicalAlert,
    PatientSummary,
)
from core.intelligence.foundation.models import (
    Evidence,
    EvidenceLevel,
    EvidenceSource,
    EvidenceChain,
    SafetyCheck,
    SafetyLevel,
    ClinicalWarning,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    ValidationPipeline,
    ConfidenceScore,
    ConfidenceLevel,
)
from core.intelligence.foundation.contracts import (
    IClinicalReasoner,
    IEvidenceEvaluator,
    IClinicalValidator,
)
from core.intelligence.foundation.interfaces import (
    IConfidenceCalculator,
    IKnowledgeBase,
    IMedicalOntology,
    IGuidelineRepository,
)
from core.intelligence.foundation.exceptions import (
    ClinicalIntelligenceError,
    EvidenceError,
    SafetyError,
    ValidationError,
    ConfidenceError,
)

__version__ = "0.1.0"

__all__ = [
    # DTOs
    "ClinicalFinding",
    "DiagnosisCandidate",
    "TreatmentRecommendation",
    "ClinicalAlert",
    "PatientSummary",
    # Models
    "Evidence",
    "EvidenceLevel",
    "EvidenceSource",
    "EvidenceChain",
    "SafetyCheck",
    "SafetyLevel",
    "ClinicalWarning",
    "ValidationResult",
    "ValidationRule",
    "ValidationSeverity",
    "ValidationPipeline",
    "ConfidenceScore",
    "ConfidenceLevel",
    # Contracts
    "IClinicalReasoner",
    "IEvidenceEvaluator",
    "IClinicalValidator",
    # Interfaces
    "IConfidenceCalculator",
    "IKnowledgeBase",
    "IMedicalOntology",
    "IGuidelineRepository",
    # Exceptions
    "ClinicalIntelligenceError",
    "EvidenceError",
    "SafetyError",
    "ValidationError",
    "ConfidenceError",
]
