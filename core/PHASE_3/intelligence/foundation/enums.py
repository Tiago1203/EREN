"""
Shared Enumerations for Clinical Intelligence

This module centralizes all shared Enums used across the Clinical Intelligence
Bounded Context to ensure consistency and avoid duplication.

ARCHITECTURE RULE:
All Enums that are used by multiple engines MUST be defined here.
Engine-specific Enums remain in their respective modules.
"""

from enum import Enum


# =============================================================================
# SHARED SEVERITY & RISK
# =============================================================================

class Severity(Enum):
    """
    Severity levels for violations and alerts.
    
    SHARED across: Rules, Safety, Validation, Decision
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(Enum):
    """
    Risk classification levels.
    
    SHARED across: Rules, Safety, Validation, Decision
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# CONFIDENCE & UNCERTAINTY
# =============================================================================

class ConfidenceLevel(Enum):
    """
    Confidence level classification.
    
    SHARED across: Confidence, Reasoning, Decision
    """
    VERY_HIGH = "very_high"  # > 0.95
    HIGH = "high"  # 0.85 - 0.95
    MODERATE = "moderate"  # 0.70 - 0.85
    LOW = "low"  # 0.50 - 0.70
    VERY_LOW = "very_low"  # < 0.50
    UNCERTAIN = "uncertain"


class UncertaintyType(Enum):
    """Types of uncertainty in clinical reasoning."""
    ALEATORY = "aleatory"  # Irreducible randomness
    EPISTEMIC = "epistemic"  # Lack of knowledge
    MODEL = "model"  # Model limitations
    MEASUREMENT = "measurement"  # Measurement uncertainty


# =============================================================================
# VALIDATION & COMPLIANCE
# =============================================================================

class ValidationDecision(Enum):
    """
    Outcomes of clinical validation.
    
    SHARED across: Validation, Decision
    """
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CORRECTION = "requires_correction"
    ESCALATE = "escalate"


class ValidationSeverity(Enum):
    """Severity of validation failures."""
    BLOCKING = "blocking"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceStatus(Enum):
    """Compliance status for standards."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    PENDING_REVIEW = "pending_review"


# =============================================================================
# DECISION & RECOMMENDATION
# =============================================================================

class Priority(Enum):
    """
    Priority levels for recommendations and decisions.
    
    SHARED across: Decision, Learning, Validation
    """
    CRITICAL = "critical"
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class AutomationLevel(Enum):
    """Level of automation for recommendations."""
    FULL_MANUAL = "full_manual"  # Human only
    ASSISTED = "assisted"  # Human with AI suggestion
    AUTOMATED_WITH_HUMAN_REVIEW = "automated_with_human_review"
    FULLY_AUTOMATED = "fully_automated"


class LanguageStyle(Enum):
    """Style for generating explanations."""
    TECHNICAL = "technical"
    CLINICAL = "clinical"
    PATIENT_FRIENDLY = "patient_friendly"
    ADMINISTRATIVE = "administrative"


# =============================================================================
# EVIDENCE & KNOWLEDGE
# =============================================================================

class EvidenceLevel(str, Enum):
    """
    Level of clinical evidence (Oxford Hierarchy + Clinical Engineering extensions).
    
    SHARED across: Evidence, Knowledge, Reasoning, PHASE_4
    
    Unified system using Oxford hierarchy with extensions for clinical engineering.
    This is the canonical EvidenceLevel for the entire EREN system.
    
    Oxford Hierarchy:
    - 1a/1b: RCTs and systematic reviews
    - 2a/2b: Cohort studies
    - 3a/3b: Case-control studies
    - 4: Case series
    - 5: Expert opinion
    
    Clinical Engineering Extensions:
    - device_spec: Device specifications and manuals
    - manufacturer_data: Manufacturer documentation
    - regulatory_clearance: FDA/EMA clearances
    - clinical_expertise: Expert clinical opinion
    - internal_standard: Hospital internal standards
    """
    # Oxford Hierarchy - Primary Evidence
    LEVEL_1A = "1a"  # Systematic review of RCTs
    LEVEL_1B = "1b"  # Individual RCT (with narrow confidence interval)
    LEVEL_2A = "2a"  # Systematic review of cohort studies
    LEVEL_2B = "2b"  # Individual cohort study (including low quality RCT)
    LEVEL_3A = "3a"  # Systematic review of case-control studies
    LEVEL_3B = "3b"  # Individual case-control study
    LEVEL_4 = "4"    # Case series (and poor-quality cohort)
    LEVEL_5 = "5"     # Expert opinion, bench research
    
    # Clinical Engineering Extensions
    DEVICE_SPEC = "device_spec"  # Device specifications and manuals
    MANUFACTURER_DATA = "manufacturer_data"  # Manufacturer documentation
    REGULATORY_CLEARANCE = "regulatory_clearance"  # FDA/EMA clearances
    CLINICAL_EXPERTISE = "clinical_expertise"  # Expert clinical opinion
    INTERNAL_STANDARD = "internal_standard"  # Hospital internal standards


# =============================================================================
# LEARNING & OUTCOMES
# =============================================================================

class OutcomeType(Enum):
    """
    Types of decision outcomes.
    
    SHARED across: Learning, Improvement
    """
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NO_ACTION = "no_action"
    UNKNOWN = "unknown"


class FeedbackType(Enum):
    """Types of user feedback."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    MISSING_CONTEXT = "missing_context"
    NEEDS_REVIEW = "needs_review"
    VERY_HELPFUL = "very_helpful"
    NOT_HELPFUL = "not_helpful"


class PatternType(Enum):
    """Types of discovered patterns."""
    TIME_BASED = "time_based"
    DEVICE_SPECIFIC = "device_specific"
    ENVIRONMENTAL = "environmental"
    RECOMMENDATION = "recommendation"
    SYMPTOM_DIAGNOSIS = "symptom_diagnosis"


# =============================================================================
# REVISION & GOVERNANCE
# =============================================================================

class RevisionStatus(Enum):
    """Status of knowledge revision."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ApprovalDecision(Enum):
    """Approval decision outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    ESCALATE = "escalate"


# =============================================================================
# IMPROVEMENT & ROLLBACK
# =============================================================================

class RollbackTrigger(Enum):
    """Triggers for rollback operations."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"


class QualityDimension(str, Enum):
    """
    Dimensions of knowledge quality.
    
    Unified across PHASE_3 and PHASE_4 for consistent quality assessment.
    Combines clinical intelligence dimensions with knowledge infrastructure dimensions.
    
    Clinical Intelligence (PHASE_3):
    - ACCURACY: Truthfulness and correctness of knowledge
    - CONSISTENCY: Internal consistency with established facts
    - EVIDENCE: Quality of supporting evidence
    - REPEATABILITY: Reproducibility of findings
    - COVERAGE: Breadth of knowledge coverage
    - IMPACT: Clinical/practical significance
    
    Knowledge Infrastructure (PHASE_4 extensions):
    - COMPLETENESS: Full coverage of topic
    - CURRENCY: Up-to-date information
    - RELEVANCE: Appropriateness to query/task
    - TRUSTWORTHINESS: Source reliability and credibility
    """
    # Clinical Intelligence Dimensions
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    EVIDENCE = "evidence"
    REPEATABILITY = "repeatability"
    COVERAGE = "coverage"
    IMPACT = "impact"
    
    # Knowledge Infrastructure Dimensions
    COMPLETENESS = "completeness"
    CURRENCY = "currency"
    RELEVANCE = "relevance"
    TRUSTWORTHINESS = "trustworthiness"


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Shared Severity & Risk
    "Severity",
    "RiskLevel",
    # Confidence
    "ConfidenceLevel",
    "UncertaintyType",
    # Validation
    "ValidationDecision",
    "ValidationSeverity",
    "ComplianceStatus",
    # Decision
    "Priority",
    "AutomationLevel",
    "LanguageStyle",
    # Evidence
    "EvidenceLevel",
    # Learning
    "OutcomeType",
    "FeedbackType",
    "PatternType",
    # Revision
    "RevisionStatus",
    "ApprovalDecision",
    # Improvement
    "RollbackTrigger",
    "QualityDimension",
]
