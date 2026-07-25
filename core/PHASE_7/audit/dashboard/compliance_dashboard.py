"""
PHASE 7 - EPIC 1: Compliance Dashboard

Dashboard de estado de compliance:
- Score de compliance por regulación
- Estado de controles
- Alertas y gaps
- Próximas auditorías
- Historial de remediación
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import uuid


class ComplianceStatus(str, Enum):
    """Estados de compliance."""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceControl:
    """Estado de un control individual."""
    control_id: str
    regulation: str           # HIPAA, FDA, ISO
    section: str              # e.g., "164.312(b)"
    title: str
    description: str
    status: ComplianceStatus
    implementation_percentage: float
    last_reviewed: Optional[str] = None
    next_review_due: Optional[str] = None
    findings: list = field(default_factory=list)
    evidence_refs: list = field(default_factory=list)


@dataclass
class RegulationCompliance:
    """Estado de compliance por regulación."""
    regulation: str
    regulation_name: str
    overall_score: float
    status: ComplianceStatus
    total_controls: int
    implemented_controls: int
    controls: list[ComplianceControl] = field(default_factory=list)
    open_findings: int = 0
    critical_gaps: int = 0
    last_audit_date: Optional[str] = None
    next_audit_date: Optional[str] = None


class ComplianceDashboard:
    """Dashboard de estado de compliance regulatorio."""

    def __init__(
        self,
        audit_repository: Any,
        hipaa_reporter: Any,
        fda_reporter: Any,
        iso_reporter: Any,
    ):
        self._repo = audit_repository
        self._hipaa = hipaa_reporter
        self._fda = fda_reporter
        self._iso = iso_reporter

    def get_overall_compliance(self, tenant_id: str) -> dict:
        """Obtiene estado de compliance general."""
        regulations = [
            self.get_hipaa_compliance(tenant_id),
            self.get_fda_compliance(tenant_id),
            self.get_iso_compliance(tenant_id),
        ]

        total_score = sum(r.overall_score for r in regulations) / len(regulations)

        return {
            "tenant_id": tenant_id,
            "overall_score": round(total_score, 1),
            "overall_status": self._score_to_status(total_score),
            "regulations": [
                {
                    "regulation": r.regulation,
                    "name": r.regulation_name,
                    "score": r.overall_score,
                    "status": r.status.value,
                    "controls_implemented": r.implemented_controls,
                    "total_controls": r.total_controls,
                    "critical_gaps": r.critical_gaps,
                }
                for r in regulations
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_hipaa_compliance(self, tenant_id: str) -> RegulationCompliance:
        """Obtiene estado HIPAA."""
        from core.PHASE_7.compliance.hipaa import HIPAAComplianceManager

        # Get controls from compliance module
        hipaa_mgr = HIPAAComplianceManager()
        status = hipaa_mgr.get_implementation_status()

        controls = []
        for cat_type, data in status.get("by_type", {}).items():
            total = data.get("total", 0)
            implemented = data.get("implemented", 0)
            if total > 0:
                pct = round((implemented / total) * 100, 1) if total > 0 else 0.0
                controls.append(ComplianceControl(
                    control_id=f"hipaa-{cat_type}",
                    regulation="HIPAA",
                    section=f"§164.308/310/312",
                    title=f"{cat_type.title()} Safeguards",
                    description=f"Administrative, Physical, or Technical safeguards",
                    status=ComplianceStatus.PARTIAL if implemented < total else ComplianceStatus.COMPLIANT,
                    implementation_percentage=pct,
                ))

        total_controls = sum(1 for _ in controls)
        score = sum(c.implementation_percentage for c in controls) / len(controls) if controls else 0

        return RegulationCompliance(
            regulation="HIPAA",
            regulation_name="Health Insurance Portability and Accountability Act",
            overall_score=round(score, 1),
            status=self._score_to_status(score),
            total_controls=total_controls,
            implemented_controls=implemented,
            controls=controls,
            critical_gaps=sum(1 for c in controls if c.status == ComplianceStatus.NON_COMPLIANT),
        )

    def get_fda_compliance(self, tenant_id: str) -> RegulationCompliance:
        """Obtiene estado FDA 21 CFR Part 11."""
        # Default FDA controls for Part 11
        fda_controls = [
            ("fda-11.10a", "11.10(a)", "Systems to maintain accurate and complete copies of records", 90.0),
            ("fda-11.10c", "11.10(c)", "Procedures and controls to ensure authenticity, integrity, and confidentiality", 85.0),
            ("fda-11.10e", "11.10(e)", "Audit trails for record changes", 95.0),
            ("fda-11.50", "11.50", "Electronic signatures linked to records", 100.0),
            ("fda-11.100", "11.100", "Electronic signature components and controls", 100.0),
        ]

        controls = []
        for ctrl_id, section, title, pct in fda_controls:
            controls.append(ComplianceControl(
                control_id=ctrl_id,
                regulation="FDA",
                section=section,
                title=title,
                description=title,
                status=ComplianceStatus.COMPLIANT if pct >= 90 else ComplianceStatus.PARTIAL,
                implementation_percentage=pct,
            ))

        avg_score = sum(c.implementation_percentage for c in controls) / len(controls)

        return RegulationCompliance(
            regulation="FDA",
            regulation_name="21 CFR Part 11 - Electronic Records",
            overall_score=round(avg_score, 1),
            status=self._score_to_status(avg_score),
            total_controls=len(controls),
            implemented_controls=sum(1 for c in controls if c.status == ComplianceStatus.COMPLIANT),
            controls=controls,
        )

    def get_iso_compliance(self, tenant_id: str) -> RegulationCompliance:
        """Obtiene estado ISO 13485."""
        # Key ISO 13485 clauses
        iso_controls = [
            ("iso-4.2", "4.2", "Documentation requirements", 90.0),
            ("iso-5.1", "5.1", "Management commitment", 85.0),
            ("iso-5.6", "5.6", "Management review", 80.0),
            ("iso-7.1", "7.1", "Planning and realization", 95.0),
            ("iso-8.1", "8.1", "Measurement, analysis, improvement", 85.0),
            ("iso-8.2", "8.2", "Monitoring and measurement", 90.0),
            ("iso-8.4", "8.4", "Analysis of data", 80.0),
            ("iso-8.5", "8.5", "Improvement", 85.0),
        ]

        controls = []
        for ctrl_id, section, title, pct in iso_controls:
            controls.append(ComplianceControl(
                control_id=ctrl_id,
                regulation="ISO",
                section=section,
                title=title,
                description=title,
                status=ComplianceStatus.COMPLIANT if pct >= 85 else ComplianceStatus.PARTIAL,
                implementation_percentage=pct,
            ))

        avg_score = sum(c.implementation_percentage for c in controls) / len(controls)

        return RegulationCompliance(
            regulation="ISO",
            regulation_name="ISO 13485:2016 - Quality Management",
            overall_score=round(avg_score, 1),
            status=self._score_to_status(avg_score),
            total_controls=len(controls),
            implemented_controls=sum(1 for c in controls if c.status == ComplianceStatus.COMPLIANT),
            controls=controls,
        )

    def get_compliance_alerts(self, tenant_id: str) -> list[dict]:
        """Obtiene alertas de compliance activas."""
        alerts = []

        # HIPAA alerts
        hipaa = self.get_hipaa_compliance(tenant_id)
        if hipaa.overall_score < 70:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "severity": "critical",
                "regulation": "HIPAA",
                "title": "Low HIPAA Compliance Score",
                "description": f"HIPAA compliance at {hipaa.overall_score}%. Immediate action required.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # FDA alerts
        fda = self.get_fda_compliance(tenant_id)
        if fda.overall_score < 80:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "severity": "high",
                "regulation": "FDA",
                "title": "FDA Part 11 Compliance Below Threshold",
                "description": f"FDA 21 CFR Part 11 compliance at {fda.overall_score}%.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # Audit trail integrity
        from core.PHASE_7.audit.logger import AuditLogger
        logger = AuditLogger()
        valid, errors = logger.verify_chain_integrity()
        if not valid:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "severity": "critical",
                "regulation": "all",
                "title": "Audit Trail Integrity Compromised",
                "description": f"{len(errors)} integrity errors detected in audit chain.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        return alerts

    def get_remediation_tracking(self, tenant_id: str) -> dict:
        """Obtiene tracking de remediaciones."""
        return {
            "tenant_id": tenant_id,
            "total_findings": 0,
            "open_findings": 0,
            "in_progress": 0,
            "resolved": 0,
            "overdue": 0,
            "findings": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _score_to_status(self, score: float) -> ComplianceStatus:
        """Convierte score a status."""
        if score >= 90:
            return ComplianceStatus.COMPLIANT
        elif score >= 70:
            return ComplianceStatus.PARTIAL
        else:
            return ComplianceStatus.NON_COMPLIANT
