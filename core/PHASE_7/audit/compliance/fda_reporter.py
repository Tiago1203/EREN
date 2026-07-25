"""
PHASE 7 - EPIC 1: FDA 21 CFR Part 11 Reporter

Reportes FDA 21 CFR Part 11:
- Electronic Record Audit Trail
- Electronic Signature Report
- Record Modification History
- System Validation Status
- Computerized System Inventory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import uuid


class FDAReportType(str, Enum):
    """Tipos de reportes FDA."""
    ELECTRONIC_RECORD = "electronic_record"
    ELECTRONIC_SIGNATURE = "electronic_signature"
    RECORD_MODIFICATION = "record_modification"
    SYSTEM_VALIDATION = "system_validation"
    AUDIT_TRAIL_REVIEW = "audit_trail_review"


@dataclass
class FDAComplianceReport:
    """Reporte FDA."""
    report_id: str
    report_type: FDAReportType
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    tenant_id: str

    # Electronic records
    total_electronic_records: int = 0
    total_modifications: int = 0
    total_signatures: int = 0

    # Signature breakdown
    approvals: int = 0
    rejections: int = 0

    # Validation
    validated_systems: int = 0
    pending_validations: int = 0

    # Audit trail
    audit_trail_events: int = 0
    chain_integrity_verified: bool = True
    integrity_errors: list = field(default_factory=list)

    # Compliance
    cfr_part_11_compliant: bool = True
    gaps: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


class FDAReporter:
    """Generador de reportes FDA 21 CFR Part 11."""

    CFR_PART_11_FIELDS = [
        "electronic_signatures",
        "audit_trail",
        "record_integrity",
        "access_controls",
        "system_validation",
    ]

    def __init__(self, audit_repository: Any):
        self._repo = audit_repository

    def generate_electronic_record_report(
        self,
        tenant_id: str,
        record_type: str,
        period_days: int = 365,
    ) -> FDAComplianceReport:
        """Genera reporte de registro electrónico (21 CFR 11.10)."""
        report_id = f"fda-er-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        # Query record events
        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .resource_type(record_type)
            .time_range(period_start, period_end)
            .pagination(limit=50000)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        modifications = [e for e in events if e.get("action") in ["update", "delete"]]
        signatures = [e for e in events if e.get("action") == "sign"]

        # Verify audit trail
        integrity_ok, errors = self._verify_audit_trail(events)

        # Identify gaps
        gaps = []
        if not integrity_ok:
            gaps.append("Audit trail integrity compromised")
        if len(modifications) > 0 and not self._has_modification_reason(events):
            gaps.append("Some modifications lack documented reason")
        if len(signatures) == 0:
            gaps.append("No electronic signatures found for record type")

        report = FDAComplianceReport(
            report_id=report_id,
            report_type=FDAReportType.ELECTRONIC_RECORD,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_electronic_records=len(events),
            total_modifications=len(modifications),
            total_signatures=len(signatures),
            audit_trail_events=len(events),
            chain_integrity_verified=integrity_ok,
            integrity_errors=errors[:10],
            cfr_part_11_compliant=len(gaps) == 0,
            gaps=gaps,
            recommendations=self._generate_recommendations(gaps),
        )

        return report

    def generate_electronic_signature_report(
        self,
        tenant_id: str,
        period_days: int = 365,
    ) -> FDAComplianceReport:
        """Genera reporte de firmas electrónicas (21 CFR 11.50, 11.100)."""
        report_id = f"fda-es-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .action("sign")
            .time_range(period_start, period_end)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        # Check signature components (21 CFR 11.50)
        missing_components = []
        for event in events[:100]:
            if not event.get("actor_name"):
                missing_components.append("signature")
            if not event.get("purpose"):
                missing_components.append("meaning")

        approvals = [e for e in events if e.get("metadata", {}).get("meaning") == "approved"]
        rejections = [e for e in events if e.get("metadata", {}).get("meaning") == "rejected"]

        gaps = []
        if missing_components:
            gaps.append(f"{len(missing_components)} signatures missing required components")

        report = FDAComplianceReport(
            report_id=report_id,
            report_type=FDAReportType.ELECTRONIC_SIGNATURE,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_signatures=len(events),
            approvals=len(approvals),
            rejections=len(rejections),
            cfr_part_11_compliant=len(gaps) == 0,
            gaps=gaps,
        )

        return report

    def generate_record_modification_report(
        self,
        tenant_id: str,
        record_id: str,
    ) -> FDAComplianceReport:
        """Genera historial de modificaciones de un registro."""
        report_id = f"fda-mod-{uuid.uuid4().hex[:12]}"

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .resource(record_id)
            .time_range(None, None)
            .pagination(limit=10000)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        modifications = [e for e in events if e.get("action") in ["update", "delete"]]
        integrity_ok, errors = self._verify_audit_trail(events)

        period_start = events[-1].get("timestamp") if events else datetime.min
        period_end = events[0].get("timestamp") if events else datetime.now(timezone.utc)

        report = FDAComplianceReport(
            report_id=report_id,
            report_type=FDAReportType.RECORD_MODIFICATION,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_electronic_records=len(events),
            total_modifications=len(modifications),
            audit_trail_events=len(events),
            chain_integrity_verified=integrity_ok,
            integrity_errors=errors,
            cfr_part_11_compliant=integrity_ok,
        )

        return report

    def generate_cfr_part_11_compliance_summary(
        self,
        tenant_id: str,
        period_days: int = 365,
    ) -> dict:
        """Genera summary de compliance CFR Part 11 completo."""
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        # All events
        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .time_range(period_start, period_end)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        integrity_ok, errors = self._verify_audit_trail(events)

        # Check each requirement
        requirements = {
            "audit_trail": {
                "cfr_section": "11.10(e)",
                "description": "Audit trails for record changes",
                "compliant": len([e for e in events if e.get("action") == "update"]) > 0,
                "events": len([e for e in events if e.get("action") == "update"]),
            },
            "electronic_signature": {
                "cfr_section": "11.50, 11.100",
                "description": "Electronic signatures linked to electronic records",
                "compliant": len([e for e in events if e.get("action") == "sign"]) > 0,
                "events": len([e for e in events if e.get("action") == "sign"]),
            },
            "integrity": {
                "cfr_section": "11.10(c)",
                "description": "Procedures and controls to ensure integrity",
                "compliant": integrity_ok,
                "errors": len(errors),
            },
            "access_controls": {
                "cfr_section": "11.10(d)",
                "description": "Limiting system access to authorized individuals",
                "compliant": len([e for e in events if e.get("action") == "login"]) > 0,
                "events": len([e for e in events if e.get("action") == "login"]),
            },
        }

        compliant_count = sum(1 for r in requirements.values() if r["compliant"])

        return {
            "report_id": f"fda-summary-{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "period_days": period_days,
            "total_events_analyzed": len(events),
            "compliance_percentage": (compliant_count / len(requirements)) * 100,
            "cfr_part_11_compliant": compliant_count == len(requirements),
            "requirements": requirements,
            "integrity_errors": errors[:5],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _verify_audit_trail(self, events: list[dict]) -> tuple[bool, list[str]]:
        """Verifica integridad del audit trail."""
        errors = []
        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]
            if prev.get("event_id") != curr.get("previous_event_hash"):
                errors.append(f"Chain broken between {prev.get('event_id')} and {curr.get('event_id')}")
        return len(errors) == 0, errors

    def _has_modification_reason(self, events: list[dict]) -> bool:
        """Verifica si modificaciones tienen razón documentada."""
        for event in events:
            if event.get("action") in ["update", "delete"]:
                if not event.get("reason") and not event.get("change_summary"):
                    return False
        return True

    def _generate_recommendations(self, gaps: list[str]) -> list[str]:
        """Genera recomendaciones basadas en gaps."""
        recommendations = []
        for gap in gaps:
            if "integrity" in gap.lower():
                recommendations.append("Implement cryptographic hash chaining for audit trail")
            if "modification" in gap.lower():
                recommendations.append("Require documented reason for all record modifications")
            if "signature" in gap.lower():
                recommendations.append("Implement electronic signatures per 21 CFR 11.50")
        if not recommendations:
            recommendations.append("Continue monitoring and periodic review")
        return recommendations
