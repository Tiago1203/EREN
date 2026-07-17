"""Diagnosis domain events.

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
class DiagnosisEvent:
    """Base class for diagnosis domain events."""

    diagnosis_id: str
    tenant_id: str
    patient_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    caused_by: str | None = None

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class DiagnosisRecorded(DiagnosisEvent):
    """Fired when a new diagnosis is recorded."""

    diagnosis_code: str = ""
    diagnosis_name: str = ""
    description: str | None = None


@dataclass(frozen=True)
class DiagnosisAmended(DiagnosisEvent):
    """Fired when diagnosis information is corrected."""

    changes: dict = field(default_factory=dict)
    previous_version: int = 0


@dataclass(frozen=True)
class DiagnosisDeleted(DiagnosisEvent):
    """Fired when a diagnosis is soft-deleted."""

    pass
