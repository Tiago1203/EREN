"""Patient domain events.

Domain events are created by the domain layer, not infrastructure.
They are immutable and represent something that happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class PatientEvent:
    """Base class for patient domain events."""

    patient_id: str
    tenant_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    caused_by: str | None = None  # Principal ID

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class PatientCreated(PatientEvent):
    """Fired when a new patient is created."""

    mrn: str = ""
    given_name: str = ""
    family_name: str = ""


@dataclass(frozen=True)
class PatientUpdated(PatientEvent):
    """Fired when patient data is modified."""

    changes: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PatientDeleted(PatientEvent):
    """Fired when a patient is soft-deleted."""

    pass
