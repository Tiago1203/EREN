"""Domain Events for EREN.

Domain events represent significant business occurrences that happened
in the past. They are immutable facts that other parts of the system
can react to.

Key principles:
1. Events are named in past tense (IncidentReported, not ReportIncident)
2. Events contain all data needed by consumers
3. Events should be self-contained (no entity references)
4. Events are immutable once published
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4, UUID


def _generate_event_id() -> str:
    """Generate a unique event ID with time-ordering prefix."""
    timestamp = int(time.time() * 1000)
    random_part = uuid4().hex[:12]
    return f"evt_{timestamp:013d}_{random_part}"


if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base class for all domain events in EREN.

    All domain events should inherit from this class and be decorated
    with @dataclass(frozen=True).

    Attributes:
        event_id: Unique identifier for this event.
        occurred_at: Timestamp when the event occurred.
        event_type: Full name of the event class.
        version: Version number for event schema evolution.

    Usage:
        @dataclass(frozen=True)
        class IncidentReported(DomainEvent):
            incident_id: str
            device_id: str
            reported_by: str
            symptom: str
            priority: str

        event = IncidentReported(
            incident_id="inc_123",
            device_id="dev_456",
            reported_by="engineer_789",
            symptom="High pressure alarm",
            priority="high",
        )
    """

    event_id: str = field(default_factory=_generate_event_id, kw_only=True)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC), kw_only=True)
    event_type: str = field(default="", init=False, repr=False)
    version: int = field(default=1, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.event_type:
            # Auto-set event_type from class name
            pass  # Will be set by subclasses

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        result = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "version": self.version,
        }
        # Get all dataclass fields
        for field_name in self.__dataclass_fields__:
            if not field_name.startswith("_"):
                value = getattr(self, field_name)
                if isinstance(value, datetime):
                    result[field_name] = value.isoformat()
                else:
                    result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DomainEvent:
        """Reconstruct event from dictionary."""
        # Remove meta fields that are set by __post_init__
        meta_fields = {"event_id", "occurred_at", "event_type", "version"}
        event_data = {k: v for k, v in data.items() if k not in meta_fields}
        return cls(**event_data)


# =============================================================================
# Engineering Incident Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class IncidentReported(DomainEvent):
    """Fired when a new engineering incident is reported."""

    incident_id: str = field(kw_only=True)
    tenant_id: str = field(kw_only=True)
    device_id: str = field(kw_only=True)
    reported_by: str = field(kw_only=True)
    symptom: str = field(kw_only=True)
    description: str = field(kw_only=True)
    priority: str = field(kw_only=True)
    correlation_id: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentReported")


@dataclass(frozen=True, slots=True)
class IncidentTriaged(DomainEvent):
    """Fired when an incident is triaged and assigned priority."""

    incident_id: str = field(kw_only=True)
    priority: str = field(kw_only=True)
    triage_notes: str = field(kw_only=True)
    triaged_by: str = field(kw_only=True)
    safety_classification: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentTriaged")


@dataclass(frozen=True, slots=True)
class IncidentOpened(DomainEvent):
    """Fired when an engineer accepts and opens an incident."""

    incident_id: str = field(kw_only=True)
    engineer_id: str = field(kw_only=True)
    estimated_resolution_time: int | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentOpened")


@dataclass(frozen=True, slots=True)
class IncidentProgressed(DomainEvent):
    """Fired when new information is added to an incident."""

    incident_id: str = field(kw_only=True)
    action_taken: str = field(kw_only=True)
    action_type: str = field(kw_only=True)
    performed_by: str = field(kw_only=True)
    notes: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentProgressed")


@dataclass(frozen=True, slots=True)
class IncidentEscalated(DomainEvent):
    """Fired when an incident is escalated to higher priority."""

    incident_id: str = field(kw_only=True)
    reason: str = field(kw_only=True)
    escalated_by: str = field(kw_only=True)
    escalation_level: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentEscalated")


@dataclass(frozen=True, slots=True)
class IncidentResolved(DomainEvent):
    """Fired when an incident is marked as resolved."""

    incident_id: str = field(kw_only=True)
    resolution: str = field(kw_only=True)
    resolved_by: str = field(kw_only=True)
    resolution_time_minutes: int = field(kw_only=True)
    actions_count: int = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentResolved")


@dataclass(frozen=True, slots=True)
class IncidentClosed(DomainEvent):
    """Fired when an incident is closed after confirmation."""

    incident_id: str = field(kw_only=True)
    closed_by: str = field(kw_only=True)
    feedback: str | None = field(default=None, kw_only=True)
    recommendation_accepted: bool = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "IncidentClosed")


# =============================================================================
# AI Recommendation Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class RecommendationGenerated(DomainEvent):
    """Fired when AI generates a recommendation."""

    incident_id: str = field(kw_only=True)
    recommendation_id: str = field(kw_only=True)
    content: str = field(kw_only=True)
    confidence_score: float = field(kw_only=True)
    evidence_count: int = field(kw_only=True)
    safety_level: str = field(kw_only=True)
    sources: tuple[str, ...] = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "RecommendationGenerated")


@dataclass(frozen=True, slots=True)
class RecommendationAccepted(DomainEvent):
    """Fired when an engineer accepts a recommendation."""

    incident_id: str = field(kw_only=True)
    recommendation_id: str = field(kw_only=True)
    accepted_by: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "RecommendationAccepted")


@dataclass(frozen=True, slots=True)
class RecommendationRejected(DomainEvent):
    """Fired when an engineer rejects a recommendation."""

    incident_id: str = field(kw_only=True)
    recommendation_id: str = field(kw_only=True)
    rejected_by: str = field(kw_only=True)
    reason: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "RecommendationRejected")


@dataclass(frozen=True, slots=True)
class FeedbackReceived(DomainEvent):
    """Fired when feedback is received on an incident."""

    incident_id: str = field(kw_only=True)
    feedback_type: str = field(kw_only=True)
    content: str = field(kw_only=True)
    provided_by: str = field(kw_only=True)
    recommendation_id: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "FeedbackReceived")


# =============================================================================
# Device Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class DeviceRegistered(DomainEvent):
    """Fired when a new device is registered."""

    device_id: str = field(kw_only=True)
    tenant_id: str = field(kw_only=True)
    serial_number: str = field(kw_only=True)
    model: str = field(kw_only=True)
    manufacturer: str = field(kw_only=True)
    registered_by: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "DeviceRegistered")


@dataclass(frozen=True, slots=True)
class DeviceStatusChanged(DomainEvent):
    """Fired when device operational status changes."""

    device_id: str = field(kw_only=True)
    previous_status: str = field(kw_only=True)
    new_status: str = field(kw_only=True)
    reason: str = field(kw_only=True)
    changed_by: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "DeviceStatusChanged")


@dataclass(frozen=True, slots=True)
class DeviceLocationChanged(DomainEvent):
    """Fired when device location changes."""

    device_id: str = field(kw_only=True)
    previous_location: str = field(kw_only=True)
    new_location: str = field(kw_only=True)
    changed_by: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "DeviceLocationChanged")


# =============================================================================
# Maintenance Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class MaintenanceScheduled(DomainEvent):
    """Fired when maintenance is scheduled."""

    maintenance_id: str = field(kw_only=True)
    device_id: str = field(kw_only=True)
    maintenance_type: str = field(kw_only=True)
    scheduled_date: datetime = field(kw_only=True)
    scheduled_by: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "MaintenanceScheduled")


@dataclass(frozen=True, slots=True)
class MaintenanceCompleted(DomainEvent):
    """Fired when maintenance is completed."""

    maintenance_id: str = field(kw_only=True)
    device_id: str = field(kw_only=True)
    incident_id: str | None = field(default=None, kw_only=True)
    completed_by: str = field(kw_only=True)
    parts_used: tuple[str, ...] = field(kw_only=True)
    duration_minutes: int = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "MaintenanceCompleted")
