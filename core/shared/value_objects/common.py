"""Common Value Objects used across EREN domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .base import ValueObject

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Priority(ValueObject):
    """Priority level for incidents and actions."""

    value: str

    def __post_init__(self) -> None:
        valid_priorities = {"critical", "high", "medium", "low"}
        normalized = self.value.lower()
        if normalized not in valid_priorities:
            msg = f"Invalid priority: {self.value}. Must be one of {valid_priorities}"
            raise ValueError(msg)
        # Store as lowercase
        object.__setattr__(self, "value", normalized)

    @classmethod
    def critical(cls) -> Priority:
        return cls(value="critical")

    @classmethod
    def high(cls) -> Priority:
        return cls(value="high")

    @classmethod
    def medium(cls) -> Priority:
        return cls(value="medium")

    @classmethod
    def low(cls) -> Priority:
        return cls(value="low")

    def __str__(self) -> str:
        return self.value

    def __int__(self) -> int:
        order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return order[self.value]


@dataclass(frozen=True)
class SafetyLevel(ValueObject):
    """Safety classification for recommendations and actions.

    Used to determine the level of human oversight required.
    """

    value: str

    def __post_init__(self) -> None:
        valid_levels = {"informational", "recommendation", "warning", "critical", "never_automate"}
        if self.value.lower() not in valid_levels:
            msg = f"Invalid safety level: {self.value}. Must be one of {valid_levels}"
            raise ValueError(msg)

    @classmethod
    def informational(cls) -> SafetyLevel:
        return cls(value="informational")

    @classmethod
    def recommendation(cls) -> SafetyLevel:
        return cls(value="recommendation")

    @classmethod
    def warning(cls) -> SafetyLevel:
        return cls(value="warning")

    @classmethod
    def critical(cls) -> SafetyLevel:
        return cls(value="critical")

    @classmethod
    def never_automate(cls) -> SafetyLevel:
        return cls(value="never_automate")

    def requires_human_approval(self) -> bool:
        """Check if this safety level requires human approval."""
        return self.value in {"critical", "never_automate"}

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Confidence(ValueObject):
    """Confidence score for AI recommendations.

    Represents how certain the AI is about a recommendation.
    Score is between 0.0 and 1.0.
    """

    score: float
    evidence_count: int
    consensus: float
    freshness: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            msg = f"Confidence score must be between 0.0 and 1.0, got {self.score}"
            raise ValueError(msg)
        if self.evidence_count < 0:
            msg = f"Evidence count must be non-negative, got {self.evidence_count}"
            raise ValueError(msg)
        if not 0.0 <= self.consensus <= 1.0:
            msg = f"Consensus must be between 0.0 and 1.0, got {self.consensus}"
            raise ValueError(msg)
        if not 0.0 <= self.freshness <= 1.0:
            msg = f"Freshness must be between 0.0 and 1.0, got {self.freshness}"
            raise ValueError(msg)

    @classmethod
    def from_score(cls, score: float) -> Confidence:
        """Create Confidence with only score, defaults for other fields."""
        return cls(
            score=score,
            evidence_count=0,
            consensus=0.0,
            freshness=1.0,
        )

    @classmethod
    def low(cls) -> Confidence:
        """Create a low confidence instance."""
        return cls(score=0.3, evidence_count=1, consensus=0.3, freshness=0.5)

    @classmethod
    def medium(cls) -> Confidence:
        """Create a medium confidence instance."""
        return cls(score=0.6, evidence_count=5, consensus=0.6, freshness=0.7)

    @classmethod
    def high(cls) -> Confidence:
        """Create a high confidence instance."""
        return cls(score=0.85, evidence_count=15, consensus=0.8, freshness=0.9)

    def is_high(self) -> bool:
        """Check if confidence is high (>0.7)."""
        return self.score >= 0.7

    def is_low(self) -> bool:
        """Check if confidence is low (<0.5)."""
        return self.score < 0.5


@dataclass(frozen=True)
class AuditInfo(ValueObject):
    """Audit trail information for domain entities."""

    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None

    def __post_init__(self) -> None:
        if not self.created_by:
            msg = "created_by cannot be empty"
            raise ValueError(msg)

    @classmethod
    def create(cls, created_by: str) -> AuditInfo:
        """Create new audit info for entity creation."""
        now = datetime.now(UTC)
        return cls(
            created_by=created_by,
            created_at=now,
            updated_by=None,
            updated_at=None,
        )

    def update(self, updated_by: str) -> AuditInfo:
        """Create updated audit info."""
        return AuditInfo(
            created_by=self.created_by,
            created_at=self.created_at,
            updated_by=updated_by,
            updated_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class TenantInfo(ValueObject):
    """Tenant information for multi-tenancy support."""

    tenant_id: str
    organization_id: str | None

    def __post_init__(self) -> None:
        if not self.tenant_id:
            msg = "tenant_id cannot be empty"
            raise ValueError(msg)
