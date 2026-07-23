"""
Tests for core.intelligence.foundation.enums module.

These tests verify that all shared enums are properly defined and exported
from the SINGLE SOURCE OF TRUTH location.
"""

import pytest
from core.PHASE_3.intelligence.foundation.enums import (
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


class TestSeverityEnum:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test Severity enum has correct values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_severity_count(self):
        """Test Severity enum has correct number of values."""
        assert len(Severity) == 4


class TestRiskLevelEnum:
    """Tests for RiskLevel enum."""

    def test_risk_level_values(self):
        """Test RiskLevel enum has correct values."""
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.LOW.value == "low"

    def test_risk_level_count(self):
        """Test RiskLevel enum has correct number of values."""
        assert len(RiskLevel) == 4


class TestConfidenceLevelEnum:
    """Tests for ConfidenceLevel enum."""

    def test_confidence_level_values(self):
        """Test ConfidenceLevel enum has correct values."""
        assert ConfidenceLevel.VERY_HIGH.value == "very_high"
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MODERATE.value == "moderate"
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.VERY_LOW.value == "very_low"
        assert ConfidenceLevel.UNCERTAIN.value == "uncertain"

    def test_confidence_level_count(self):
        """Test ConfidenceLevel enum has correct number of values."""
        assert len(ConfidenceLevel) == 6

    def test_confidence_level_ordering(self):
        """Test ConfidenceLevel values are ordered by confidence."""
        levels = [
            ConfidenceLevel.VERY_HIGH,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MODERATE,
            ConfidenceLevel.LOW,
            ConfidenceLevel.VERY_LOW,
            ConfidenceLevel.UNCERTAIN,
        ]
        for i, level in enumerate(levels):
            assert levels.index(level) == i


class TestEvidenceLevelEnum:
    """Tests for EvidenceLevel enum."""

    def test_evidence_level_values(self):
        """Test EvidenceLevel enum has correct values."""
        assert EvidenceLevel.A_SYSTEMATIC.value == "a_systematic"
        assert EvidenceLevel.A_RCT_HIGH.value == "a_rct_high"
        assert EvidenceLevel.B_COHORT.value == "b_cohort"
        assert EvidenceLevel.B_RCT_LOW.value == "b_rct_low"
        assert EvidenceLevel.C_CASE_CONTROL.value == "c_case_control"
        assert EvidenceLevel.C_CASE_SERIES.value == "c_case_series"
        assert EvidenceLevel.D_EXPERT_OPINION.value == "d_expert_opinion"
        assert EvidenceLevel.D_BENCH_RESEARCH.value == "d_bench_research"

    def test_evidence_level_count(self):
        """Test EvidenceLevel enum has correct number of values."""
        assert len(EvidenceLevel) == 8

    def test_evidence_level_categories(self):
        """Test EvidenceLevel is organized by category (A, B, C, D)."""
        level_a = [e for e in EvidenceLevel if e.name.startswith("A_")]
        level_b = [e for e in EvidenceLevel if e.name.startswith("B_")]
        level_c = [e for e in EvidenceLevel if e.name.startswith("C_")]
        level_d = [e for e in EvidenceLevel if e.name.startswith("D_")]
        
        assert len(level_a) == 2
        assert len(level_b) == 2
        assert len(level_c) == 2
        assert len(level_d) == 2


class TestValidationSeverityEnum:
    """Tests for ValidationSeverity enum."""

    def test_validation_severity_values(self):
        """Test ValidationSeverity enum has correct values."""
        assert ValidationSeverity.BLOCKING.value == "blocking"
        assert ValidationSeverity.HIGH.value == "high"
        assert ValidationSeverity.MEDIUM.value == "medium"
        assert ValidationSeverity.LOW.value == "low"
        assert ValidationSeverity.INFO.value == "info"

    def test_validation_severity_count(self):
        """Test ValidationSeverity enum has correct number of values."""
        assert len(ValidationSeverity) == 5


class TestLanguageStyleEnum:
    """Tests for LanguageStyle enum."""

    def test_language_style_values(self):
        """Test LanguageStyle enum has correct values."""
        assert LanguageStyle.TECHNICAL.value == "technical"
        assert LanguageStyle.CLINICAL.value == "clinical"
        assert LanguageStyle.PATIENT_FRIENDLY.value == "patient_friendly"
        assert LanguageStyle.ADMINISTRATIVE.value == "administrative"

    def test_language_style_count(self):
        """Test LanguageStyle enum has correct number of values."""
        assert len(LanguageStyle) == 4


class TestPriorityEnum:
    """Tests for Priority enum."""

    def test_priority_values(self):
        """Test Priority enum has correct values."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.URGENT.value == "urgent"
        assert Priority.HIGH.value == "high"
        assert Priority.NORMAL.value == "normal"
        assert Priority.LOW.value == "low"

    def test_priority_count(self):
        """Test Priority enum has correct number of values."""
        assert len(Priority) == 5


class TestComplianceStatusEnum:
    """Tests for ComplianceStatus enum."""

    def test_compliance_status_values(self):
        """Test ComplianceStatus enum has correct values."""
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"
        assert ComplianceStatus.PARTIAL.value == "partial"
        assert ComplianceStatus.NOT_APPLICABLE.value == "not_applicable"
        assert ComplianceStatus.PENDING_REVIEW.value == "pending_review"

    def test_compliance_status_count(self):
        """Test ComplianceStatus enum has correct number of values."""
        assert len(ComplianceStatus) == 5


class TestAllEnumsExported:
    """Tests that verify all enums are properly exported."""

    def test_all_enums_in_module_all(self):
        """Test all enums are in __all__ list."""
        from core.PHASE_3.intelligence.foundation import enums
        
        expected_enums = [
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
        ]
        
        for enum_name in expected_enums:
            assert enum_name in enums.__all__, f"{enum_name} not in __all__"
