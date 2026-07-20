"""Clinical Decision Support System."""
from dataclasses import dataclass
from enum import Enum


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceLevel(str, Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"


@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    priority: RecommendationPriority
    evidence_level: EvidenceLevel
    confidence: float
    actions: list[str]


@dataclass
class CDSSResult:
    recommendations: list[Recommendation]
    confidence: float
    summary: str
