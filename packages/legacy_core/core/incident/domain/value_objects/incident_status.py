"""Incident-specific value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.shared import ValueObject

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class IncidentStatus(ValueObject):
    """Status of an engineering incident.

    Status transitions:
    REPORTED → TRIAGED → OPEN → IN_PROGRESS → RESOLVED → CLOSED
           ↘ CANCELLED
    """

    value: str

    def __post_init__(self) -> None:
        valid_statuses = {
            "reported",
            "triaged",
            "open",
            "in_progress",
            "escalated",
            "resolved",
            "closed",
            "cancelled",
        }
        if self.value.lower() not in valid_statuses:
            msg = f"Invalid incident status: {self.value}. Must be one of {valid_statuses}"
            raise ValueError(msg)

    @classmethod
    def reported(cls) -> IncidentStatus:
        return cls(value="reported")

    @classmethod
    def triaged(cls) -> IncidentStatus:
        return cls(value="triaged")

    @classmethod
    def open(cls) -> IncidentStatus:
        return cls(value="open")

    @classmethod
    def in_progress(cls) -> IncidentStatus:
        return cls(value="in_progress")

    @classmethod
    def escalated(cls) -> IncidentStatus:
        return cls(value="escalated")

    @classmethod
    def resolved(cls) -> IncidentStatus:
        return cls(value="resolved")

    @classmethod
    def closed(cls) -> IncidentStatus:
        return cls(value="closed")

    @classmethod
    def cancelled(cls) -> IncidentStatus:
        return cls(value="cancelled")

    def can_transition_to(self, target: IncidentStatus) -> bool:
        """Check if transition to target status is valid."""
        transitions = {
            "reported": {"triaged", "cancelled"},
            "triaged": {"open", "cancelled"},
            "open": {"in_progress", "cancelled"},
            "in_progress": {"resolved", "escalated"},
            "escalated": {"in_progress"},
            "resolved": {"closed"},
            "closed": set(),
            "cancelled": set(),
        }
        return target.value in transitions.get(self.value, set())

    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self.value in {"closed", "cancelled"}

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Symptom(ValueObject):
    """Description of the symptom reported by the engineer."""

    description: str
    category: str | None = None

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            msg = "Symptom description cannot be empty"
            raise ValueError(msg)
        # Normalize whitespace
        object.__setattr__(self, "description", " ".join(self.description.split()))


@dataclass(frozen=True)
class Resolution(ValueObject):
    """Resolution description for a closed incident."""

    description: str
    root_cause: str | None = None
    resolution_type: str | None = None

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            msg = "Resolution description cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class ActionType(ValueObject):
    """Type of action taken during investigation."""

    value: str

    def __post_init__(self) -> None:
        valid_types = {
            "test",
            "repair",
            "replace",
            "calibrate",
            "clean",
            "update",
            "inspect",
            "configure",
            "other",
        }
        if self.value.lower() not in valid_types:
            msg = f"Invalid action type: {self.value}. Must be one of {valid_types}"
            raise ValueError(msg)

    @classmethod
    def test(cls) -> ActionType:
        return cls(value="test")

    @classmethod
    def repair(cls) -> ActionType:
        return cls(value="repair")

    @classmethod
    def replace(cls) -> ActionType:
        return cls(value="replace")

    @classmethod
    def calibrate(cls) -> ActionType:
        return cls(value="calibrate")

    @classmethod
    def inspect(cls) -> ActionType:
        return cls(value="inspect")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ActionResult(ValueObject):
    """Result of an action taken."""

    value: str

    def __post_init__(self) -> None:
        valid_results = {"success", "failure", "partial", "inconclusive"}
        if self.value.lower() not in valid_results:
            msg = f"Invalid action result: {self.value}. Must be one of {valid_results}"
            raise ValueError(msg)

    @classmethod
    def success(cls) -> ActionResult:
        return cls(value="success")

    @classmethod
    def failure(cls) -> ActionResult:
        return cls(value="failure")

    @classmethod
    def partial(cls) -> ActionResult:
        return cls(value="partial")

    @classmethod
    def inconclusive(cls) -> ActionResult:
        return cls(value="inconclusive")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Feedback(ValueObject):
    """Feedback from engineer on a recommendation or incident."""

    feedback_type: str
    content: str
    recommendation_id: str | None = None

    def __post_init__(self) -> None:
        valid_types = {"positive", "negative", "neutral", "correction"}
        if self.feedback_type.lower() not in valid_types:
            msg = f"Invalid feedback type: {self.feedback_type}. Must be one of {valid_types}"
            raise ValueError(msg)
        if not self.content or not self.content.strip():
            msg = "Feedback content cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class MessageSender(ValueObject):
    """Sender type for conversation messages."""

    value: str

    def __post_init__(self) -> None:
        valid_senders = {"engineer", "ai", "system"}
        if self.value.lower() not in valid_senders:
            msg = f"Invalid sender: {self.value}. Must be one of {valid_senders}"
            raise ValueError(msg)

    @classmethod
    def engineer(cls) -> MessageSender:
        return cls(value="engineer")

    @classmethod
    def ai(cls) -> MessageSender:
        return cls(value="ai")

    @classmethod
    def system(cls) -> MessageSender:
        return cls(value="system")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EvidenceType(ValueObject):
    """Type of evidence recorded during investigation."""

    value: str

    def __post_init__(self) -> None:
        valid_types = {"measurement", "observation", "test_result", "photo", "document", "log"}
        if self.value.lower() not in valid_types:
            msg = f"Invalid evidence type: {self.value}. Must be one of {valid_types}"
            raise ValueError(msg)

    @classmethod
    def measurement(cls) -> EvidenceType:
        return cls(value="measurement")

    @classmethod
    def observation(cls) -> EvidenceType:
        return cls(value="observation")

    @classmethod
    def test_result(cls) -> EvidenceType:
        return cls(value="test_result")

    def __str__(self) -> str:
        return self.value
