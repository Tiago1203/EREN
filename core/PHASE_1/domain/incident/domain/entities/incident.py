"""Engineering Incident aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import (
    AggregateRoot,
    ConcurrencyError,
    DeviceId,
    EngineerId,
    IncidentId,
    Priority,
    SafetyLevel,
    TenantId,
)
from core.PHASE_1.infrastructure.shared.events import IncidentClosed, IncidentEscalated, IncidentOpened, IncidentProgressed, IncidentReported, IncidentResolved, IncidentTriaged

from ..value_objects import Feedback, IncidentStatus, Resolution, Symptom

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class EngineeringIncident(AggregateRoot):
    """Engineering Incident aggregate root.

    An Engineering Incident represents a problem reported by a biomedical engineer
    that requires investigation and resolution.

    The incident goes through the following lifecycle:
    REPORTED → TRIAGED → OPEN → IN_PROGRESS → RESOLVED → CLOSED
               ↘ CANCELLED                           ↑
                                                    │
                                          (can reopen with new evidence)

    Invariants:
    1. Incident must have a device
    2. Incident must have a reporter
    3. Incident cannot be closed without at least one action
    4. Incident cannot transition to invalid states
    5. Closed incidents cannot be modified
    """

    # Identity
    tenant_id: TenantId
    device_id: DeviceId
    reported_by: EngineerId

    # Core data
    symptom: Symptom
    description: str
    priority: Priority

    # State
    status: IncidentStatus = field(default_factory=IncidentStatus.reported)
    safety_classification: SafetyLevel = field(default_factory=SafetyLevel.recommendation)

    # Investigation tracking
    assigned_to: EngineerId | None = None
    triage_notes: str | None = None
    estimated_resolution_hours: int | None = None

    # Resolution
    resolution: Resolution | None = None
    closed_at: datetime | None = None
    closed_by: EngineerId | None = None
    resolution_time_minutes: int | None = None

    # Feedback
    feedback: Feedback | None = None

    # Correlation
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate()
        # Publish IncidentReported event on creation
        self.add_event(
            IncidentReported(
                incident_id=str(self.id),
                tenant_id=str(self.tenant_id),
                device_id=str(self.device_id),
                reported_by=str(self.reported_by),
                symptom=self.symptom.description,
                description=self.description,
                priority=str(self.priority),
                correlation_id=self.correlation_id,
            ),
        )

    def _validate(self) -> None:
        """Validate invariant constraints."""
        if not self.description or not self.description.strip():
            msg = "Incident description cannot be empty"
            raise ValueError(msg)

    def triage(
        self,
        priority: Priority,
        safety_classification: SafetyLevel,
        triage_notes: str,
        expected_version: int,
    ) -> None:
        """Triage the incident and assign priority and safety classification."""
        self._assert_version(expected_version)
        self._assert_status(IncidentStatus.reported())

        if not self.status.can_transition_to(IncidentStatus.triaged()):
            msg = f"Cannot triage incident from status {self.status}"
            raise ConcurrencyError(
                entity_type="EngineeringIncident",
                entity_id=str(self.id),
                expected_version=expected_version,
                actual_version=self.version,
            )

        self._unlock_for_mutation()
        self.priority = priority
        self.safety_classification = safety_classification
        self.triage_notes = triage_notes
        self.status = IncidentStatus.triaged()
        self._relock_after_mutation()

        self.add_event(
            IncidentTriaged(
                incident_id=str(self.id),
                priority=str(priority),
                triage_notes=triage_notes,
                triaged_by=str(self.reported_by),
                safety_classification=str(safety_classification),
            ),
        )

    def assign(self, engineer_id: EngineerId, expected_version: int) -> None:
        """Assign incident to an engineer."""
        self._assert_version(expected_version)
        self._assert_status(IncidentStatus.triaged())

        self._unlock_for_mutation()
        self.assigned_to = engineer_id
        self.status = IncidentStatus.open()
        self._relock_after_mutation()

        self.add_event(
            IncidentOpened(
                incident_id=str(self.id),
                engineer_id=str(engineer_id),
                estimated_resolution_time=self.estimated_resolution_hours,
            ),
        )

    def start_investigation(self, expected_version: int) -> None:
        """Start the investigation phase."""
        self._assert_version(expected_version)
        self._assert_status(IncidentStatus.open())

        self._unlock_for_mutation()
        self.status = IncidentStatus.in_progress()
        self._relock_after_mutation()

    def escalate(
        self,
        reason: str,
        escalated_by: EngineerId,
        expected_version: int,
    ) -> None:
        """Escalate the incident to higher priority."""
        self._assert_version(expected_version)
        self._assert_status(IncidentStatus.in_progress())

        self._unlock_for_mutation()
        self.status = IncidentStatus.escalated()
        self._relock_after_mutation()

        self.add_event(
            IncidentEscalated(
                incident_id=str(self.id),
                reason=reason,
                escalated_by=str(escalated_by),
                escalation_level=str(self.priority),
            ),
        )

    def resolve(
        self,
        resolution: Resolution,
        resolved_by: EngineerId,
        actions_count: int,
        expected_version: int,
    ) -> None:
        """Resolve the incident."""
        self._assert_version(expected_version)

        if actions_count < 1:
            msg = "Cannot resolve incident without at least one action"
            raise ValueError(msg)

        # Calculate resolution time before mutation
        resolution_time = 0
        if self.created_at:
            now = datetime.now(UTC)
            resolution_time = int((now - self.created_at).total_seconds() / 60)

        self._unlock_for_mutation()
        self.status = IncidentStatus.resolved()
        self.resolution = resolution
        self.resolution_time_minutes = resolution_time
        self._relock_after_mutation()

        self.add_event(
            IncidentResolved(
                incident_id=str(self.id),
                resolution=resolution.description,
                resolved_by=str(resolved_by),
                resolution_time_minutes=resolution_time,
                actions_count=actions_count,
            ),
        )

    def close(
        self,
        feedback: Feedback | None,
        recommendation_accepted: bool,
        closed_by: EngineerId,
        expected_version: int,
    ) -> None:
        """Close the incident."""
        self._assert_version(expected_version)
        self._assert_status(IncidentStatus.resolved())

        self._unlock_for_mutation()
        self.status = IncidentStatus.closed()
        self.closed_at = datetime.now(UTC)
        self.closed_by = closed_by
        self.feedback = feedback
        self._relock_after_mutation()

        self.add_event(
            IncidentClosed(
                incident_id=str(self.id),
                closed_by=str(closed_by),
                feedback=str(feedback.content) if feedback else None,
                recommendation_accepted=recommendation_accepted,
            ),
        )

    def cancel(self, cancelled_by: EngineerId, reason: str, expected_version: int) -> None:
        """Cancel the incident."""
        self._assert_version(expected_version)

        if self.status.value not in {"reported", "triaged", "open"}:
            msg = f"Cannot cancel incident in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.status = IncidentStatus.cancelled()
        self._relock_after_mutation()

    def _assert_status(self, expected: IncidentStatus) -> None:
        """Assert that incident is in expected status."""
        if self.status != expected:
            msg = f"Incident is in status {self.status}, expected {expected}"
            raise ValueError(msg)

    def is_closed(self) -> bool:
        """Check if incident is in a terminal state."""
        return self.status.is_terminal()

    def can_be_modified(self) -> bool:
        """Check if incident can still be modified."""
        return not self.is_closed()

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update(
            {
                "tenant_id": str(self.tenant_id),
                "device_id": str(self.device_id),
                "reported_by": str(self.reported_by),
                "symptom_description": self.symptom.description,
                "symptom_category": self.symptom.category,
                "description": self.description,
                "priority": str(self.priority),
                "status": str(self.status),
                "safety_classification": str(self.safety_classification),
                "assigned_to": str(self.assigned_to) if self.assigned_to else None,
                "triage_notes": self.triage_notes,
                "estimated_resolution_hours": self.estimated_resolution_hours,
                "resolution_description": self.resolution.description if self.resolution else None,
                "resolution_root_cause": self.resolution.root_cause if self.resolution else None,
                "closed_at": self.closed_at.isoformat() if self.closed_at else None,
                "closed_by": str(self.closed_by) if self.closed_by else None,
                "resolution_time_minutes": self.resolution_time_minutes,
                "feedback_type": self.feedback.feedback_type if self.feedback else None,
                "feedback_content": self.feedback.content if self.feedback else None,
                "correlation_id": self.correlation_id,
            },
        )
        return base
