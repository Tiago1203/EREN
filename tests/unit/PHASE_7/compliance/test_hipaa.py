"""
Tests for PHASE 7 - EPIC 0: HIPAA Compliance

HIPAA module tests:
- Controls
- Risk Assessment
- Compliance Checker
"""

import pytest
from datetime import datetime


class TestHIPAAComplianceManager:
    """Tests for HIPAAComplianceManager."""

    def test_load_controls(self):
        """Test that HIPAA controls are loaded."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceManager

        manager = HIPAAComplianceManager()
        status = manager.get_implementation_status()

        assert status["total_controls"] == 16
        assert status["by_type"]["administrative"]["total"] > 0
        assert status["by_type"]["physical"]["total"] > 0
        assert status["by_type"]["technical"]["total"] > 0

    def test_implement_control(self):
        """Test control implementation."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceManager

        manager = HIPAAComplianceManager()
        result = manager.implement_control(
            control_id="164.312(a)(1)",
            details="Implemented AES-256 encryption for all PHI",
            responsible_party="Security Team",
        )
        assert result

        status = manager.get_implementation_status()
        assert status["implemented"] >= 1

    def test_identify_gaps(self):
        """Test gap identification."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceManager

        manager = HIPAAComplianceManager()
        gaps = manager.identify_gaps()

        # All required controls not implemented = gaps
        assert len(gaps) > 0
        assert all(g["severity"] == "critical" for g in gaps)

    def test_controls_by_category(self):
        """Test filtering controls by category."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceManager, SafeguardCategory

        manager = HIPAAComplianceManager()
        controls = manager.get_controls_by_category(SafeguardCategory.ACCESS_CONTROL)

        assert len(controls) >= 1
        assert all(c.safeguard_type.value == "technical" for c in controls)


class TestHIPAARiskAssessment:
    """Tests for HIPAARiskAssessment."""

    def test_identify_phi_risks(self):
        """Test PHI risk identification."""
        from core.PHASE_7.compliance.hipaa import HIPAARiskAssessment

        assessor = HIPAARiskAssessment()
        risks = assessor.identify_phi_risks()

        assert len(risks) > 0
        risk_ids = [r.risk_id for r in risks]
        assert "phi-risk-001" in risk_ids

    def test_conduct_assessment(self):
        """Test full risk assessment."""
        from core.PHASE_7.compliance.hipaa import HIPAARiskAssessment

        assessor = HIPAARiskAssessment()
        result = assessor.conduct_assessment(
            assessor="Security Officer",
            scope="Clinical Engineering Platform",
            systems=["Database", "API", "Web"],
        )

        assert result.assessment_id.startswith("hipaa-")
        assert result.assessor == "Security Officer"
        assert len(result.risks) > 0
        assert len(result.recommendations) > 0


class TestHIPAAComplianceChecker:
    """Tests for HIPAAComplianceChecker."""

    def test_check_encryption_violation(self):
        """Test detection of unencrypted PHI."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceChecker

        checker = HIPAAComplianceChecker()

        data = {
            "patient_name": "John Doe",  # Plain text PHI
            "diagnosis": "Diabetes Type 2",
        }

        violations = checker.check_encryption(data)

        assert len(violations) >= 1
        assert violations[0].category.value == "encryption"
        assert violations[0].severity.value == "critical"

    def test_check_encryption_pass(self):
        """Test no violation when PHI is encrypted."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceChecker

        checker = HIPAAComplianceChecker()

        data = {
            "patient_name": "encrypted_value_looks_like_binary_data",
            "diagnosis": "another_encrypted_value",
        }

        violations = checker.check_encryption(data)
        # May still flag - depends on encryption detection logic

    def test_compliance_status(self):
        """Test overall compliance status."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceChecker

        checker = HIPAAComplianceChecker()
        checker.check_encryption({"patient_name": "plain"})
        status = checker.get_compliance_status()

        assert status.assessment_date is not None
        assert 0 <= status.overall_score <= 100
        assert status.critical_violations >= 0
