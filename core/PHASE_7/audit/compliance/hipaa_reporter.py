"""
PHASE 7 - EPIC 1: HIPAA Compliance Reporter

Reportes de cumplimiento HIPAA:
- HIPAA Access Report (§164.312(b))
- Minimum Necessary Review
- Breach Assessment
- Risk Assessment Integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import uuid


class HIPAAReportType(str, Enum):
    """Tipos de reportes HIPAA."""
    ACCESS_LOG = "access_log"
    MINIMUM_NECESSARY = "minimum_necessary"
    BREACH_ASSESSMENT = "breach_assessment"
    SANCTION_SCREEN = "sanction_screening"
    WORKFORCE_AUDIT = "workforce_audit"
    RISK_ANALYSIS = "risk_analysis"


@dataclass
class HIPAAReport:
    """Reporte HIPAA."""
    report_id: str
    report_type: HIPAAReportType
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    tenant_id: str

    # Summary
    total_phi_accesses: int = 0
    unique_patients_accessed: int = 0
    unique_users_with_phi_access: int = 0

    # Violations
    unauthorized_accesses: int = 0
    minimum_necessary_violations: int = 0

    # Events
    phi_access_events: list = field(default_factory=list)
    violations: list = field(default_factory=list)

    # Metadata
    generated_by: str = "system"
    compliance_score: float = 0.0
    risk_level: str = "Low"


@dataclass
class HIPAAViolation:
    """Violación HIPAA."""
    violation_id: str
    event_id: str
    violation_type: str
    description: str
    severity: str
    affected_patients: int = 0
    detected_at: datetime = field(default_factory=datetime.utcnow)


class HIPAAReporter:
    """Generador de reportes HIPAA."""

    # Minimum necessary: employees should only access PHI needed for their role
    MIN_ACCESS_THRESHOLD = 50  # Max accesses per user per day without flag

    def __init__(self, audit_repository: Any):
        self._repo = audit_repository

    def generate_access_report(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> HIPAAReport:
        """Genera reporte de acceso HIPAA (§164.312(b))."""
        report_id = f"hipaa-access-{uuid.uuid4().hex[:12]}"

        # Query PHI access events
        query = {
            "query_id": report_id,
            "categories": ["phi_access"],
            "since": period_start,
            "until": period_end,
            "tenant_ids": [tenant_id],
            "limit": 50000,
        }

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder
        builder = AuditQueryBuilder()
        builder.category("phi_access").time_range(period_start, period_end)
        if tenant_id:
            builder.tenant(tenant_id)
        result = self._repo.query(builder.build())

        events = result.get("events", [])

        # Calculate summary
        patient_ids = set()
        user_ids = set()

        for event in events:
            if event.get("resource_id"):
                patient_ids.add(event["resource_id"])
            if event.get("actor_id"):
                user_ids.add(event["actor_id"])

        # Detect violations
        violations = self._detect_violations(events)

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(len(violations), len(events))

        report = HIPAAReport(
            report_id=report_id,
            report_type=HIPAAReportType.ACCESS_LOG,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_phi_accesses=len(events),
            unique_patients_accessed=len(patient_ids),
            unique_users_with_phi_access=len(user_ids),
            unauthorized_accesses=len([v for v in violations if "unauthorized" in v.violation_type]),
            phi_access_events=events[:1000],  # Limit events in report
            violations=violations,
            compliance_score=compliance_score,
            risk_level=self._risk_level(compliance_score),
        )

        return report

    def generate_minimum_necessary_report(
        self,
        actor_id: str,
        tenant_id: str,
        period_days: int = 30,
    ) -> HIPAAReport:
        """Genera reporte de minimum necessary."""
        report_id = f"hipaa-minnec-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder
        builder = (
            AuditQueryBuilder()
            .actor(actor_id)
            .category("phi_access")
            .time_range(period_start, period_end)
            .tenant(tenant_id)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        # Count accesses by resource type
        by_resource_type = {}
        for event in events:
            rt = event.get("resource_type", "unknown")
            by_resource_type[rt] = by_resource_type.get(rt, 0) + 1

        violations = []
        for rt, count in by_resource_type.items():
            if count > self.MIN_ACCESS_THRESHOLD:
                violations.append(HIPAAViolation(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    event_id="",
                    violation_type="minimum_necessary",
                    description=f"User accessed {rt} {count} times in {period_days} days (threshold: {self.MIN_ACCESS_THRESHOLD})",
                    severity="medium",
                ))

        compliance = self._calculate_compliance_score(len(violations), len(events))

        return HIPAAReport(
            report_id=report_id,
            report_type=HIPAAReportType.MINIMUM_NECESSARY,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_phi_accesses=len(events),
            unique_patients_accessed=len(set(e.get("resource_id") for e in events)),
            unique_users_with_phi_access=1,
            minimum_necessary_violations=len(violations),
            violations=violations,
            compliance_score=compliance,
            risk_level=self._risk_level(compliance),
        )

    def assess_breach_risk(
        self,
        tenant_id: str,
        period_days: int = 30,
    ) -> dict:
        """Evalúa riesgo de breach."""
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder
        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .time_range(period_start, period_end)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        # Risk factors
        failed_logins = [e for e in events if e.get("action") == "login_failed"]
        unauthorized = [e for e in events if e.get("action") in ["access_denied", "access_attempt"]]
        phi_exports = [e for e in events if e.get("action") == "export_data" and e.get("is_phi_access")]
        bulk_access = [e for e in events if e.get("action") == "read" and e.get("metadata", {}).get("bulk", False)]

        # Breach indicators
        indicators = {
            "failed_login_spike": len(failed_logins) > 100,
            "unauthorized_access_attempts": len(unauthorized) > 10,
            "phi_bulk_exports": len(phi_exports) > 5,
            "unusual_access_patterns": len(bulk_access) > 20,
        }

        risk_score = sum(indicators.values()) / len(indicators)

        return {
            "assessment_id": f"breach-{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "period_days": period_days,
            "risk_score": risk_score,
            "risk_level": self._risk_level(1 - risk_score),
            "indicators": indicators,
            "total_events_analyzed": len(events),
            "failed_logins": len(failed_logins),
            "unauthorized_attempts": len(unauthorized),
            "phi_exports": len(phi_exports),
            "bulk_access_events": len(bulk_access),
            "assessed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _detect_violations(self, events: list[dict]) -> list[HIPAAViolation]:
        """Detecta violaciones HIPAA."""
        violations = []

        # Check for unauthorized access attempts
        for event in events:
            if not event.get("success", True):
                violations.append(HIPAAViolation(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    event_id=event.get("event_id", ""),
                    violation_type="unauthorized_access",
                    description=f"Failed access attempt: {event.get('error_message', 'Unknown error')}",
                    severity="high",
                ))

            # Check for suspicious volume
            # (simplified - real impl would aggregate by day)
            if event.get("metadata", {}).get("suspicious_pattern"):
                violations.append(HIPAAViolation(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    event_id=event.get("event_id", ""),
                    violation_type="suspicious_pattern",
                    description="Access pattern flagged as suspicious",
                    severity="medium",
                ))

        return violations

    def _calculate_compliance_score(self, violations: int, total_events: int) -> float:
        """Calcula score de compliance (0-100)."""
        if total_events == 0:
            return 100.0
        violation_rate = violations / total_events
        return max(0.0, 100.0 - (violation_rate * 1000))

    def _risk_level(self, score: float) -> str:
        """Determina nivel de riesgo."""
        if score >= 90:
            return "Low"
        elif score >= 70:
            return "Medium"
        elif score >= 50:
            return "High"
        return "Critical"
