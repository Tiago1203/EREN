"""Recommendation-specific value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import ValueObject

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class RecommendationStatus(ValueObject):
    """Status of an AI recommendation."""

    value: str

    def __post_init__(self) -> None:
        valid_statuses = {
            "generated",
            "pending_review",
            "accepted",
            "rejected",
            "partially_accepted",
            "expired",
            "superseded",
        }
        if self.value.lower() not in valid_statuses:
            msg = f"Invalid recommendation status: {self.value}. Must be one of {valid_statuses}"
            raise ValueError(msg)

    @classmethod
    def generated(cls) -> RecommendationStatus:
        return cls(value="generated")

    @classmethod
    def pending_review(cls) -> RecommendationStatus:
        return cls(value="pending_review")

    @classmethod
    def accepted(cls) -> RecommendationStatus:
        return cls(value="accepted")

    @classmethod
    def rejected(cls) -> RecommendationStatus:
        return cls(value="rejected")

    @classmethod
    def partially_accepted(cls) -> RecommendationStatus:
        return cls(value="partially_accepted")

    @classmethod
    def expired(cls) -> RecommendationStatus:
        return cls(value="expired")

    @classmethod
    def superseded(cls) -> RecommendationStatus:
        return cls(value="superseded")

    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self.value in {"accepted", "rejected", "expired", "superseded"}

    def can_be_modified(self) -> bool:
        """Check if recommendation can still be modified."""
        return not self.is_terminal()

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RecommendationCategory(ValueObject):
    """Category of a recommendation."""

    value: str

    def __post_init__(self) -> None:
        valid_categories = {
            "preventive_maintenance",
            "calibration",
            "repair",
            "replacement",
            "inspection",
            "upgrade",
            "configuration",
            "safety",
            "performance",
            "efficiency",
        }
        if self.value.lower() not in valid_categories:
            msg = f"Invalid category: {self.value}. Must be one of {valid_categories}"
            raise ValueError(msg)

    @classmethod
    def preventive_maintenance(cls) -> RecommendationCategory:
        return cls(value="preventive_maintenance")

    @classmethod
    def calibration(cls) -> RecommendationCategory:
        return cls(value="calibration")

    @classmethod
    def repair(cls) -> RecommendationCategory:
        return cls(value="repair")

    @classmethod
    def replacement(cls) -> RecommendationCategory:
        return cls(value="replacement")

    @classmethod
    def safety(cls) -> RecommendationCategory:
        return cls(value="safety")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RecommendationConfidence(ValueObject):
    """Confidence level for recommendations."""

    score: float
    evidence_count: int
    model_version: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            msg = f"Confidence score must be between 0.0 and 1.0, got {self.score}"
            raise ValueError(msg)
        if self.evidence_count < 0:
            msg = f"Evidence count must be non-negative"
            raise ValueError(msg)

    @classmethod
    def from_score(cls, score: float, model_version: str = "v1") -> RecommendationConfidence:
        """Create with default evidence count."""
        return cls(score=score, evidence_count=1, model_version=model_version)

    @classmethod
    def high(cls) -> RecommendationConfidence:
        """High confidence (>0.8)."""
        return cls(score=0.85, evidence_count=10, model_version="v1")

    @classmethod
    def medium(cls) -> RecommendationConfidence:
        """Medium confidence (0.5-0.8)."""
        return cls(score=0.65, evidence_count=5, model_version="v1")

    @classmethod
    def low(cls) -> RecommendationConfidence:
        """Low confidence (<0.5)."""
        return cls(score=0.35, evidence_count=2, model_version="v1")

    def is_high(self) -> bool:
        return self.score >= 0.7

    def is_low(self) -> bool:
        return self.score < 0.5


@dataclass(frozen=True)
class RejectionReason(ValueObject):
    """Reason for rejecting a recommendation."""

    reason_code: str
    description: str
    alternative_suggestion: str | None = None

    def __post_init__(self) -> None:
        valid_codes = {
            "already_done",
            "not_applicable",
            "too_expensive",
            "insufficient_evidence",
            "safety_concern",
            "logistical_issue",
            "other",
        }
        if self.reason_code.lower() not in valid_codes:
            msg = f"Invalid reason code: {self.reason_code}"
            raise ValueError(msg)

    @classmethod
    def already_done(cls, description: str) -> RejectionReason:
        return cls(reason_code="already_done", description=description)

    @classmethod
    def not_applicable(cls, description: str) -> RejectionReason:
        return cls(reason_code="not_applicable", description=description)

    @classmethod
    def insufficient_evidence(cls, description: str, alternative: str | None = None) -> RejectionReason:
        return cls(reason_code="insufficient_evidence", description=description, alternative_suggestion=alternative)


@dataclass(frozen=True)
class AcceptanceNote(ValueObject):
    """Notes when accepting a recommendation."""

    content: str
    modifications: str | None = None
    expected_outcome: str | None = None

    def __post_init__(self) -> None:
        if not self.content or not self.content.strip():
            msg = "Acceptance note content cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class RecommendationUrgency(ValueObject):
    """Urgency level for recommendations."""

    value: str

    def __post_init__(self) -> None:
        valid_urgencies = {"immediate", "soon", "scheduled", "optional"}
        if self.value.lower() not in valid_urgencies:
            msg = f"Invalid urgency: {self.value}. Must be one of {valid_urgencies}"
            raise ValueError(msg)

    @classmethod
    def immediate(cls) -> RecommendationUrgency:
        return cls(value="immediate")

    @classmethod
    def soon(cls) -> RecommendationUrgency:
        return cls(value="soon")

    @classmethod
    def scheduled(cls) -> RecommendationUrgency:
        return cls(value="scheduled")

    @classmethod
    def optional(cls) -> RecommendationUrgency:
        return cls(value="optional")

    def __str__(self) -> str:
        return self.value
