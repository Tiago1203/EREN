"""
Tests for PHASE 7 - EPIC 0: FDA Compliance

FDA 21 CFR Part 11 module tests:
- Traceability
- Audit Trail
- Validation
"""

import pytest
from datetime import datetime


class TestFDATraceability:
    """Tests for FDATraceabilityManager."""

    def test_create_electronic_signature(self):
        """Test FDA electronic signature creation."""
        from core.PHASE_7.compliance.fda import (
            FDATraceabilityManager,
            SignatureMeaning,
        )

        manager = FDATraceabilityManager()
        sig = manager.create_electronic_signature(
            signer_id="user-001",
            signer_name="Dr. Jane Smith",
            signer_role="Clinical Engineer",
            record_id="equipment-cal-001",
            record_type="calibration",
            meaning=SignatureMeaning.APPROVED,
            workstation="WS-ENG-01",
            reason="Equipment calibration verified",
            record_content="Calibration complete: measurement error within tolerance",
        )

        assert sig.signature_id.startswith("sig-")
        assert sig.signer_name == "Dr. Jane Smith"
        assert sig.signature_hash != ""
        assert sig.signature_type.value == "electronic"

    def test_verify_signature(self):
        """Test signature verification."""
        from core.PHASE_7.compliance.fda import (
            FDATraceabilityManager,
            SignatureMeaning,
        )

        manager = FDATraceabilityManager()
        sig = manager.create_electronic_signature(
            signer_id="user-001",
            signer_name="Dr. Jane Smith",
            signer_role="Clinical Engineer",
            record_id="cal-002",
            record_type="calibration",
            meaning=SignatureMeaning.APPROVED,
            workstation="WS-01",
            reason="OK",
            record_content="Content",
        )

        assert manager.verify_signature(sig.signature_id)

    def test_record_versioning(self):
        """Test document version control."""
        from core.PHASE_7.compliance.fda import FDATraceabilityManager

        manager = FDATraceabilityManager()

        manager.create_record_version(
            record_id="doc-001",
            content="Initial content",
            created_by="admin",
            changes_summary="Initial version",
        )
        manager.create_record_version(
            record_id="doc-001",
            content="Updated content",
            created_by="admin",
            changes_summary="Updated sections 1-3",
        )

        history = manager.get_record_history("doc-001")
        assert len(history) == 2
        assert history[0].version_number == 1
        assert history[1].version_number == 2
        assert history[1].previous_version_id == history[0].version_id

    def test_record_linking(self):
        """Test linking records."""
        from core.PHASE_7.compliance.fda import FDATraceabilityManager

        manager = FDATraceabilityManager()
        link = manager.link_records(
            source_id="cal-001",
            target_id="equipment-001",
            link_type="references",
        )

        assert link.link_id.startswith("link-")
        links = manager.get_record_links("cal-001")
        assert len(links) >= 1


class TestFDAAuditTrail:
    """Tests for FDAAuditTrail."""

    def test_log_entry(self):
        """Test audit trail logging."""
        from core.PHASE_7.compliance.fda import FDAAuditTrail, AuditEntryType

        trail = FDAAuditTrail()
        entry = trail.log(
            operator_id="user-001",
            operator_name="John Doe",
            operator_role="Technician",
            workstation="WS-TECH-01",
            action=AuditEntryType.UPDATE,
            record_type="equipment",
            record_id="eq-001",
            record_name="Infusion Pump Model A",
            reason="Preventive maintenance performed",
        )

        assert entry.entry_id.startswith("fda-audit-")
        assert entry.operator_name == "John Doe"
        assert entry.action == AuditEntryType.UPDATE
        assert entry.entry_hash != ""

    def test_chain_integrity(self):
        """Test tamper-evident chain integrity."""
        from core.PHASE_7.compliance.fda import FDAAuditTrail, AuditEntryType

        trail = FDAAuditTrail()

        for i in range(5):
            trail.log(
                operator_id=f"user-{i}",
                operator_name=f"User {i}",
                operator_role="Engineer",
                workstation=f"WS-{i}",
                action=AuditEntryType.CREATE,
                record_type="equipment",
                record_id=f"eq-{i}",
                record_name=f"Equipment {i}",
            )

        valid, errors = trail.verify_chain_integrity()
        assert valid
        assert len(errors) == 0

    def test_compliance_report(self):
        """Test FDA compliance report generation."""
        from core.PHASE_7.compliance.fda import FDAAuditTrail, AuditEntryType
        from datetime import timedelta

        trail = FDAAuditTrail()
        now = datetime.utcnow()
        since = now - timedelta(days=7)
        until = now

        trail.log(
            operator_id="user-001",
            operator_name="John Doe",
            operator_role="Engineer",
            workstation="WS-01",
            action=AuditEntryType.CREATE,
            record_type="equipment",
            record_id="eq-001",
            record_name="Equipment",
        )

        report = trail.generate_compliance_report(since, until)
        assert report["total_entries"] >= 1
        assert "entries_by_action" in report
        assert report["integrity_verified"]


class TestFDAValidation:
    """Tests for FDAValidationManager."""

    def test_create_validation_plan(self):
        """Test validation plan creation."""
        from core.PHASE_7.compliance.fda import FDAValidationManager

        manager = FDAValidationManager()
        plan = manager.create_validation_plan(
            project_name="Clinical Platform",
            software_name="EREN System",
            version="1.0.0",
            risk_class="B",
        )

        assert plan.plan_id.startswith("val-")
        assert plan.risk_class == "B"
        assert plan.iq is not None
        assert plan.oq is not None
        assert plan.pq is not None

    def test_add_requirement(self):
        """Test adding validation requirement."""
        from core.PHASE_7.compliance.fda import FDAValidationManager

        manager = FDAValidationManager()
        plan = manager.create_validation_plan("Project", "Software", "1.0")

        req = manager.add_requirement(
            plan_id=plan.plan_id,
            title="PHI Encryption Required",
            description="All PHI data must be encrypted at rest",
            source="HIPAA 164.312(a)(1)",
            software_requirement="REQ-SEC-001",
        )

        assert req.requirement_id.startswith(plan.plan_id)
        assert req.title == "PHI Encryption Required"
