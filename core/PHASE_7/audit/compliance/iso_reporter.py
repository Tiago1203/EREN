"""
PHASE 7 - EPIC 1: ISO 13485 Compliance Reporter

Reportes ISO 13485:
- Quality Management Review
- CAPA Audit Trail
- Document Control Review
- Management Review Records
- Internal Audit Program
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import uuid


class ISOReportType(str, Enum):
    """Tipos de reportes ISO 13485."""
    MANAGEMENT_REVIEW = "management_review"
    INTERNAL_AUDIT = "internal_audit"
    CAPA_TRACKING = "capa_tracking"
    DOCUMENT_CONTROL = "document_control"
    SUPPLIER_AUDIT = "supplier_audit"


@dataclass
class ISOComplianceReport:
    """Reporte ISO 13485."""
    report_id: str
    report_type: ISOReportType
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    tenant_id: str

    # Metrics
    total_audit_events: int = 0
    nonconformities_identified: int = 0
    corrective_actions_open: int = 0
    preventive_actions_open: int = 0
    documents_reviewed: int = 0
    documents_approved: int = 0

    # Compliance
    iso_13485_compliant: bool = True
    clauses_evaluated: list = field(default_factory=list)
    gaps: list = field(default_factory=list)

    # Effectiveness
    effectiveness_score: float = 0.0
    recommendations: list = field(default_factory=list)


class ISOReporter:
    """Generador de reportes ISO 13485."""

    # Key ISO 13485 clauses relevant to audit trail
    ISO_13485_CLAUSES = {
        "4.1": "General quality management system requirements",
        "4.2": "Documentation requirements",
        "5.1": "Management commitment",
        "5.5": "Responsibility, authority and communication",
        "5.6": "Management review",
        "6.2": "Human resources",
        "6.3": "Infrastructure",
        "6.4": "Work environment and contamination control",
        "7.1": "Planning and realization of sterile medical device",
        "7.2": "Customer-related processes",
        "7.3": "Design and development",
        "7.4": "Purchasing",
        "7.5": "Production and service provision",
        "7.6": "Control of monitoring and measuring equipment",
        "8.1": "Measurement, analysis and improvement - general",
        "8.2": "Monitoring and measurement",
        "8.3": "Analysis of data",
        "8.4": "Control of records",
        "8.5": "Improvement",
    }

    def __init__(self, audit_repository: Any):
        self._repo = audit_repository

    def generate_management_review_report(
        self,
        tenant_id: str,
        period_days: int = 90,
    ) -> ISOComplianceReport:
        """Genera reporte de revisión por la dirección (ISO 13485:2016 §5.6)."""
        report_id = f"iso-mr-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .time_range(period_start, period_end)
            .pagination(limit=50000)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        # Categorize by clause
        events_by_category = self._categorize_events(events)

        nonconformities = self._detect_nonconformities(events)

        report = ISOComplianceReport(
            report_id=report_id,
            report_type=ISOReportType.MANAGEMENT_REVIEW,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_audit_events=len(events),
            nonconformities_identified=len(nonconformities),
            corrective_actions_open=len([n for n in nonconformities if "corrective" in n.get("type", "").lower()]),
            preventive_actions_open=len([n for n in nonconformities if "preventive" in n.get("type", "").lower()]),
            clauses_evaluated=list(self.ISO_13485_CLAUSES.keys()),
            gaps=self._identify_iso_gaps(events),
            effectiveness_score=self._calculate_effectiveness(events, nonconformities),
            recommendations=self._generate_iso_recommendations(nonconformities),
        )

        return report

    def generate_internal_audit_report(
        self,
        tenant_id: str,
        auditor_id: str,
        period_days: int = 365,
    ) -> ISOComplianceReport:
        """Genera reporte de auditoría interna (ISO 13485:2016 §8.2.2)."""
        report_id = f"iso-ia-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .actor(auditor_id)
            .category("compliance")
            .time_range(period_start, period_end)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        if not events:
            # Get all compliance events for this tenant
            builder = (
                AuditQueryBuilder()
                .tenant(tenant_id)
                .category("compliance")
                .time_range(period_start, period_end)
            )
            result = self._repo.query(builder.build())
            events = result.get("events", [])

        report = ISOComplianceReport(
            report_id=report_id,
            report_type=ISOReportType.INTERNAL_AUDIT,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_audit_events=len(events),
            nonconformities_identified=len(self._detect_nonconformities(events)),
            iso_13485_compliant=True,
            clauses_evaluated=["4.1", "5.1", "5.5", "5.6", "8.1", "8.2", "8.4", "8.5"],
            recommendations=["Continue periodic internal audits", "Document all audit findings"],
        )

        return report

    def generate_document_control_report(
        self,
        tenant_id: str,
        period_days: int = 180,
    ) -> ISOComplianceReport:
        """Genera reporte de control documental (ISO 13485:2016 §4.2.3, 4.2.4)."""
        report_id = f"iso-dc-{uuid.uuid4().hex[:12]}"
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        builder = (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .category("compliance")
            .action("approve")
            .time_range(period_start, period_end)
        )
        result = self._repo.query(builder.build())
        events = result.get("events", [])

        approved = [e for e in events if e.get("action") == "approve"]
        created = [e for e in events if e.get("action") == "create"]
        modified = [e for e in events if e.get("action") == "update"]

        report = ISOComplianceReport(
            report_id=report_id,
            report_type=ISOReportType.DOCUMENT_CONTROL,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            documents_reviewed=len(events),
            documents_approved=len(approved),
            total_audit_events=len(events),
            iso_13485_compliant=True,
            clauses_evaluated=["4.2.3", "4.2.4", "4.2.5"],
            recommendations=[
                "Ensure all controlled documents have approval records",
                "Verify document distribution tracking is complete",
            ],
        )

        return report

    def generate_capa_summary_report(
        self,
        tenant_id: str,
        period_days: int = 365,
    ) -> ISOComplianceReport:
        """Genera summary de CAPA (ISO 13485:2016 §8.5)."""
        report_id = f"iso-capa-{uuid.uuid4().hex[:12]}"
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

        # CAPA-related events
        capa_events = [e for e in events if "capa" in str(e.get("resource_type", "")).lower()]
        corrective = [e for e in events if "corrective" in str(e.get("metadata", {}))]
        preventive = [e for e in events if "preventive" in str(e.get("metadata", {}))]

        report = ISOComplianceReport(
            report_id=report_id,
            report_type=ISOReportType.CAPA_TRACKING,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
            total_audit_events=len(events),
            corrective_actions_open=len(corrective),
            preventive_actions_open=len(preventive),
            iso_13485_compliant=True,
            clauses_evaluated=["8.5.1", "8.5.2", "8.5.3"],
            effectiveness_score=80.0 if len(corrective) + len(preventive) > 0 else 100.0,
        )

        return report

    def _categorize_events(self, events: list[dict]) -> dict:
        """Categoriza eventos por clauses ISO 13485."""
        categories = {}
        for event in events:
            category = event.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(event)
        return categories

    def _detect_nonconformities(self, events: list[dict]) -> list[dict]:
        """Detecta no conformidades en eventos."""
        nonconformities = []
        for event in events:
            if not event.get("success", True):
                nonconformities.append({
                    "event_id": event.get("event_id", ""),
                    "type": "nonconformity",
                    "description": event.get("error_message", "Unknown error"),
                    "severity": event.get("severity", "medium"),
                })
            if event.get("metadata", {}).get("capa_trigger"):
                nonconformities.append({
                    "event_id": event.get("event_id", ""),
                    "type": "capa_trigger",
                    "description": event.get("metadata", {}).get("capa_description", ""),
                })
        return nonconformities

    def _identify_iso_gaps(self, events: list[dict]) -> list[str]:
        """Identifica gaps en compliance ISO 13485."""
        gaps = []
        if not any(e.get("category") == "compliance" for e in events):
            gaps.append("No compliance-related events found - verify audit coverage")
        if not any(e.get("action") == "approve" for e in events):
            gaps.append("No approval actions recorded - verify document control")
        return gaps

    def _calculate_effectiveness(self, events: list[dict], nonconformities: list) -> float:
        """Calcula score de efectividad."""
        total_events = len(events)
        if total_events == 0:
            return 100.0
        nc_rate = len(nonconformities) / total_events
        return max(0.0, 100.0 - (nc_rate * 1000))

    def _generate_iso_recommendations(self, nonconformities: list) -> list[str]:
        """Genera recomendaciones ISO."""
        if not nonconformities:
            return ["Quality management system appears effective", "Continue monitoring"]
        return [
            "Review all nonconformities and implement corrective actions",
            "Conduct root cause analysis for recurring issues",
            "Verify effectiveness of corrective actions taken",
        ]
