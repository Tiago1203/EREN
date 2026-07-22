"""Differential Diagnosis Engine."""
from dataclasses import dataclass
from enum import Enum


class HypothesisStatus(str, Enum):
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    PENDING = "pending"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RCAMethodology(str, Enum):
    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"


@dataclass
class DiagnosisHypothesis:
    """Represents a possible diagnosis."""
    id: str
    name: str
    probability: float
    severity: SeverityLevel
    supporting_evidence: list[str]
    ruling_out_tests: list[str]
    status: HypothesisStatus


@dataclass
class DifferentialDiagnosisResult:
    """Result of differential diagnosis analysis."""
    hypotheses: list[DiagnosisHypothesis]
    recommended_tests: list[str]
    most_likely: str | None
    confidence: float


@dataclass
class DiagnosisResult:
    cause: str
    probability: float
    confidence: str
    evidence: list[str]


@dataclass
class RootCauseResult:
    root_cause: str
    evidence_chain: list[str]
    methodology: RCAMethodology
    confidence: float


# Import engine for convenience
from core.PHASE_1.clinical.diagnosis.engine import DiagnosisEngine, get_diagnosis_engine

__all__ = [
    "HypothesisStatus",
    "SeverityLevel",
    "RCAMethodology",
    "DiagnosisHypothesis",
    "DifferentialDiagnosisResult",
    "DiagnosisResult",
    "RootCauseResult",
    "DiagnosisEngine",
    "get_diagnosis_engine",
]
