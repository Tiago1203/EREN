"""Failure Prediction and Risk Assessment."""
from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MaintenanceType(str, Enum):
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"


@dataclass
class FailurePrediction:
    device_id: str
    risk_score: float
    risk_level: RiskLevel
    probability_of_failure: float
    estimated_time_to_failure: str
    factors: list[str]


@dataclass
class MaintenanceSuggestion:
    device_id: str
    maintenance_type: MaintenanceType
    priority: RiskLevel
    description: str
    estimated_duration: str
    recommended_date: str


# Import engine for convenience
from core.PHASE_1.clinical.predictive.engine import (
    PredictiveEngine,
    get_predictive_engine,
    FailurePrediction,
    MaintenanceSuggestion,
    RiskLevel,
    MaintenanceType,
)

__all__ = [
    "RiskLevel",
    "MaintenanceType",
    "FailurePrediction",
    "MaintenanceSuggestion",
    "PredictiveEngine",
    "get_predictive_engine",
]
