"""Conversation domain value objects."""
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass(frozen=True)
class ConfidenceScore:
    """Confidence score with breakdown."""
    overall: float
    evidence_score: float = 0.0
    consistency_score: float = 0.0
    coverage_score: float = 0.0
    recency_score: float = 0.0
    low_evidence: bool = False
    conflicting_sources: bool = False
    outdated_information: bool = False
    summary: str = ""

    @property
    def level(self) -> ConfidenceLevel:
        if self.overall >= 0.9:
            return ConfidenceLevel.HIGH
        elif self.overall >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif self.overall >= 0.5:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW


@dataclass(frozen=True)
class MessageContent:
    """Message content value object."""
    text: str
    format: str = "text"
    citations: list[str] = None

    def __post_init__(self):
        if self.citations is None:
            object.__setattr__(self, 'citations', [])
