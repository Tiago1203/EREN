"""
Audit Capability Contract.

Philosophy: EREN must log all significant actions.
Audit trail is immutable and required for HIPAA compliance.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Types
# =============================================================================


class AuditLevel(Enum):
    """Severity level of audit events."""

    CRITICAL = "critical"  # Security breaches, data access
    HIGH = "high"  # Important actions
    MEDIUM = "medium"  # Normal operations
    LOW = "low"  # Informational


class AuditCategory(Enum):
    """Categories of auditable events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_CREATION = "data_creation"
    DATA_DELETION = "data_deletion"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    CLINICAL = "clinical"
    DEVICE = "device"
    ALERT = "alert"
    DECISION = "decision"  # CDS recommendations
    POLICY = "policy"


class PHIExposure(Enum):
    """Level of PHI exposure in an event."""

    NONE = "none"  # No PHI
    MINIMAL = "minimal"  # Only metadata
    MODERATE = "moderate"  # Some PHI fields
    FULL = "full"  # Full PHI record


@dataclass(frozen=True)
class AuditEvent:
    """A single audit event.

    Audit events are immutable once created.
    They cannot be modified or deleted.
    """

    event_id: str  # UUID
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Who
    principal_id: str | None
    principal_type: str | None  # human, device, system
    session_id: str | None
    ip_address: str | None
    user_agent: str | None

    # What
    category: AuditCategory
    action: str  # Specific action performed
    level: AuditLevel
    outcome: str  # success, failure, partial

    # Where
    resource_type: str | None
    resource_id: str | None
    component: str | None  # Which service/module

    # Details
    description: str
    details: tuple[tuple[str, Any], ...] = field(default_factory=tuple)  # key-value details

    # PHI
    phi_exposure: PHIExposure = PHIExposure.NONE
    patient_id: str | None = None  # If PHI involved
    patient_accessed: bool = False

    # Metadata
    correlation_id: str | None = None  # For tracing
    causation_id: str | None = None  # What triggered this
    request_id: str | None = None  # HTTP request ID
    version: str = "1.0"

    def has_phi(self) -> bool:
        """Check if this event contains PHI."""
        return self.phi_exposure != PHIExposure.NONE

    def is_patient_access(self) -> bool:
        """Check if this is a patient data access event."""
        return self.patient_accessed or self.category == AuditCategory.DATA_ACCESS


@dataclass(frozen=True)
class AuditQuery:
    """Query parameters for searching audit events."""

    principal_id: str | None = None
    session_id: str | None = None
    patient_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    category: AuditCategory | None = None
    level: AuditLevel | None = None
    outcome: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    contains_phi: bool | None = None
    correlation_id: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class AuditQueryResult:
    """Result of an audit query."""

    events: tuple[AuditEvent, ...]
    total_count: int
    offset: int
    limit: int
    has_more: bool


@dataclass(frozen=True)
class AuditReport:
    """Generated audit report."""

    report_id: str
    report_type: str  # e.g., "patient_access", "security", "compliance"
    start_time: datetime
    end_time: datetime
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str | None
    filters: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    summary: tuple[tuple[str, Any], ...] = field(default_factory=tuple)  # Statistics
    events: tuple[AuditEvent, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class HIPAAComplianceReport:
    """HIPAA-specific compliance report."""

    report_id: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Required HIPAA fields
    patient_access_count: int
    unauthorized_access_attempts: int
    breach_indicators: tuple[str, ...] = field(default_factory=tuple)
    user_activity_summary: tuple[tuple[str, int], ...]  # principal_id -> access_count
    data_export_audits: tuple[AuditEvent, ...] = field(default_factory=tuple)

    # Risk indicators
    high_risk_activities: tuple[AuditEvent, ...] = field(default_factory=tuple)
    anomalies_detected: tuple[str, ...] = field(default_factory=tuple)

    notes: str | None = None


@dataclass(frozen=True)
class AuditRetention:
    """Audit retention policy."""

    retention_days: int = 2555  # 7 years for HIPAA
    archive_after_days: int = 365
    archive_location: str | None = None
    compressed: bool = True
    encrypted: bool = True


# =============================================================================
# Provider Interface
# =============================================================================


class AuditProvider(Protocol):
    """Contract for audit logging services.

    Philosophy: All significant actions are logged.
    Audit trail is immutable and tamper-proof.

    HIPAA Requirements:
    - Log all PHI access
    - Log all authentication attempts
    - Log all authorization decisions
    - Retain for 7 years minimum
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def log(
        self,
        event: AuditEvent,
    ) -> str:
        """Log an audit event.

        This is the primary method for creating audit records.

        Args:
            event: The audit event to log

        Returns:
            Event ID of the logged event
        """
        ...

    async def log_authentication(
        self,
        principal_id: str | None,
        success: bool,
        method: str,
        ip_address: str | None = None,
        error: str | None = None,
    ) -> str:
        """Log an authentication attempt.

        Convenience method for authentication events.
        """
        ...

    async def log_authorization(
        self,
        principal_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None,
        granted: bool,
        reason: str | None = None,
    ) -> str:
        """Log an authorization decision.

        Convenience method for authorization events.
        """
        ...

    async def log_phi_access(
        self,
        principal_id: str,
        patient_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log PHI access.

        Required for HIPAA compliance.
        All access to Protected Health Information must be logged.
        """
        ...

    async def log_clinical_decision(
        self,
        principal_id: str,
        patient_id: str,
        decision_type: str,
        recommendation: str,
        confidence: float,
        evidence: tuple[str, ...],
        accepted: bool | None = None,
    ) -> str:
        """Log a clinical decision support recommendation.

        EREN Philosophy: EREN always explains its decisions.
        All CDS recommendations must be audited.
        """
        ...

    async def query(
        self,
        query: AuditQuery,
    ) -> AuditQueryResult:
        """Query audit events.

        Args:
            query: Query parameters

        Returns:
            Matching audit events with pagination
        """
        ...

    async def get_event(self, event_id: str) -> AuditEvent | None:
        """Get a specific audit event by ID.

        Args:
            event_id: Event identifier

        Returns:
            Audit event if found, None otherwise
        """
        ...

    async def get_patient_access_history(
        self,
        patient_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[AuditEvent, ...]:
        """Get complete access history for a patient.

        Required for HIPAA access reports.

        Args:
            patient_id: Patient identifier
            start_time: Start of period
            end_time: End of period

        Returns:
            All access events for the patient
        """
        ...

    async def get_principal_activity(
        self,
        principal_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[AuditEvent, ...]:
        """Get all activity for a specific principal.

        Args:
            principal_id: Principal identifier
            start_time: Start of period
            end_time: End of period

        Returns:
            All events for the principal
        """
        ...

    async def generate_report(
        self,
        report_type: str,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any] | None = None,
    ) -> AuditReport:
        """Generate an audit report.

        Args:
            report_type: Type of report
            start_time: Report period start
            end_time: Report period end
            filters: Additional filters

        Returns:
            Generated audit report
        """
        ...

    async def generate_hipaa_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> HIPAAComplianceReport:
        """Generate a HIPAA compliance report.

        Required annually for HIPAA compliance.

        Args:
            period_start: Start of reporting period
            period_end: End of reporting period

        Returns:
            HIPAA compliance report
        """
        ...

    async def get_retention_policy(self) -> AuditRetention:
        """Get current retention policy.

        Returns:
            Current retention settings
        """
        ...

    async def set_retention_policy(self, retention: AuditRetention) -> bool:
        """Set retention policy.

        Args:
            retention: New retention policy

        Returns:
            True if policy was updated
        """
        ...

    async def archive_old_events(
        self,
        before: datetime,
    ) -> int:
        """Archive old audit events.

        Moves events older than threshold to archive storage.

        Args:
            before: Archive events before this time

        Returns:
            Number of events archived
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class AuditEventLogged:
    """Fired when an audit event is logged."""

    event_id: str
    category: AuditCategory
    has_phi: bool


@dataclass(frozen=True)
class AuditReportGenerated:
    """Fired when an audit report is generated."""

    report_id: str
    report_type: str
    generated_by: str | None
    event_count: int


@dataclass(frozen=True)
class HIPAAAlert:
    """Fired when a potential HIPAA violation is detected."""

    alert_id: str
    indicator_type: str  # e.g., "unauthorized_access", "bulk_export"
    principal_id: str | None
    patient_id: str | None
    severity: AuditLevel
    description: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
