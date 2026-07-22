"""
EREN Clinical Intelligence Module

This module provides clinical intelligence capabilities for EREN,
including reasoning, evidence evaluation, and clinical decision support.
"""

from core.PHASE_3.intelligence.foundation import (
    # DTOs
    ClinicalFinding,
    DiagnosisCandidate,
    TreatmentRecommendation,
    ClinicalAlert,
    PatientSummary,
    # Evidence
    Evidence,
    EvidenceLevel,
    EvidenceSource,
    EvidenceChain,
    # Safety
    SafetyCheck,
    SafetyLevel,
    ClinicalWarning,
    # Validation
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    ValidationPipeline,
    # Confidence
    ConfidenceScore,
    ConfidenceLevel,
    # Interfaces
    IClinicalReasoner,
    IEvidenceEvaluator,
    IClinicalValidator,
    IConfidenceCalculator,
    IKnowledgeBase,
    IMedicalOntology,
    IGuidelineRepository,
    # Exceptions
    ClinicalIntelligenceError,
    EvidenceError,
    SafetyError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # DTOs
    "ClinicalFinding",
    "DiagnosisCandidate",
    "TreatmentRecommendation",
    "ClinicalAlert",
    "PatientSummary",
    # Evidence
    "Evidence",
    "EvidenceLevel",
    "EvidenceSource",
    "EvidenceChain",
    # Safety
    "SafetyCheck",
    "SafetyLevel",
    "ClinicalWarning",
    # Validation
    "ValidationResult",
    "ValidationRule",
    "ValidationSeverity",
    "ValidationPipeline",
    # Confidence
    "ConfidenceScore",
    "ConfidenceLevel",
    # Interfaces
    "IClinicalReasoner",
    "IEvidenceEvaluator",
    "IClinicalValidator",
    "IConfidenceCalculator",
    "IKnowledgeBase",
    "IMedicalOntology",
    "IGuidelineRepository",
    # Exceptions
    "ClinicalIntelligenceError",
    "EvidenceError",
    "SafetyError",
    "ValidationError",
]
