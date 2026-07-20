"""Differential Diagnosis Engine."""
from dataclasses import dataclass


class RCAMethodology(str, Enum):
    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"


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
