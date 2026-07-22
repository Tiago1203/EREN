"""
Clinical Intelligence Foundation

This module provides the foundational components for Clinical Intelligence,
including DTOs, contracts, models, interfaces, policies, and shared enums.

ARCHITECTURE PRINCIPLES:
1. SINGLE SOURCE OF TRUTH: All shared Enums are in enums.py
2. DEPENDENCY RULE: Foundation has NO dependencies on other modules
3. INTERFACE SEGREGATION: Contracts define what engines must implement
"""

# =============================================================================
# SHARED ENUMS - SINGLE SOURCE OF TRUTH
# =============================================================================
from core.intelligence.foundation.enums import (
    # Severity & Risk
    Severity,
    RiskLevel,
    # Confidence
    ConfidenceLevel,
    UncertaintyType,
    # Validation
    ValidationDecision,
    ValidationSeverity,
    ComplianceStatus,
    # Decision
    Priority,
    AutomationLevel,
    LanguageStyle,
    # Evidence
    EvidenceLevel,
    # Learning
    OutcomeType,
    FeedbackType,
    PatternType,
    # Revision
    RevisionStatus,
    ApprovalDecision,
    # Improvement
    RollbackTrigger,
    QualityDimension,
)

# =============================================================================
# DTOs
# =============================================================================
from core.intelligence.foundation.dto import (
    ClinicalFinding,
    DiagnosisCandidate,
    TreatmentRecommendation,
    ClinicalAlert,
    PatientSummary,
)

# =============================================================================
# MODELS
# =============================================================================
from core.intelligence.foundation.models import (
    Evidence,
    EvidenceSource,
    EvidenceChain,
    SafetyCheck,
    SafetyLevel,
    ClinicalWarning,
    ValidationResult,
    ValidationRule,
    ValidationPipeline,
    ConfidenceScore,
)

# =============================================================================
# CONTRACTS
# =============================================================================
from core.intelligence.foundation.contracts import (
    IClinicalReasoner,
    IEvidenceEvaluator,
    IClinicalValidator,
)

# =============================================================================
# INTERFACES
# =============================================================================
from core.intelligence.foundation.interfaces import (
    IConfidenceCalculator,
    IKnowledgeBase,
    IMedicalOntology,
    IGuidelineRepository,
)

# =============================================================================
# EXCEPTIONS
# =============================================================================
from core.intelligence.foundation.exceptions import (
    ClinicalIntelligenceError,
    EvidenceError,
    SafetyError,
    ValidationError,
    ConfidenceError,
)

__version__ = "1.0.0"

__all__ = [
    # ========== SHARED ENUMS (SINGLE SOURCE OF TRUTH) ==========
    "Severity",
    "RiskLevel",
    "ConfidenceLevel",
    "UncertaintyType",
    "ValidationDecision",
    "ValidationSeverity",
    "ComplianceStatus",
    "Priority",
    "AutomationLevel",
    "LanguageStyle",
    "EvidenceLevel",
    "OutcomeType",
    "FeedbackType",
    "PatternType",
    "RevisionStatus",
    "ApprovalDecision",
    "RollbackTrigger",
    "QualityDimension",
    # ========== DTOs ==========
    "ClinicalFinding",
    "DiagnosisCandidate",
    "TreatmentRecommendation",
    "ClinicalAlert",
    "PatientSummary",
    # ========== MODELS ==========
    "Evidence",
    "EvidenceSource",
    "EvidenceChain",
    "SafetyCheck",
    "SafetyLevel",
    "ClinicalWarning",
    "ValidationResult",
    "ValidationRule",
    "ValidationPipeline",
    "ConfidenceScore",
    # ========== CONTRACTS ==========
    "IClinicalReasoner",
    "IEvidenceEvaluator",
    "IClinicalValidator",
    # ========== INTERFACES ==========
    "IConfidenceCalculator",
    "IKnowledgeBase",
    "IMedicalOntology",
    "IGuidelineRepository",
    # ========== EXCEPTIONS ==========
    "ClinicalIntelligenceError",
    "EvidenceError",
    "SafetyError",
    "ValidationError",
    "ConfidenceError",
]
