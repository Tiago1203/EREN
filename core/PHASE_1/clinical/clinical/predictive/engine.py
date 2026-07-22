"""Predictive Maintenance and Risk Assessment Engine."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from core.PHASE_1.clinical.predictive import (
    FailurePrediction,
    MaintenanceSuggestion,
    MaintenanceType,
    RiskLevel,
)


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


class PredictiveEngine:
    """
    Predictive Maintenance and Risk Assessment Engine.
    
    Analyzes device data to predict failures and recommend maintenance actions.
    """

    def __init__(self):
        # Risk factor weights
        self._weights = {
            "age": 0.20,
            "usage_hours": 0.25,
            "maintenance_history": 0.20,
            "failure_history": 0.15,
            "environmental": 0.10,
            "usage_pattern": 0.10,
        }

        # Thresholds
        self._risk_thresholds = {
            RiskLevel.CRITICAL: 0.80,
            RiskLevel.HIGH: 0.60,
            RiskLevel.MEDIUM: 0.40,
            RiskLevel.LOW: 0.0,
        }

        # Typical lifecycles by device type (in years)
        self._typical_lifecycles = {
            "monitor": 7,
            "infusion_pump": 10,
            "ventilator": 12,
            "defibrillator": 8,
            "anesthesia": 15,
            "xray": 20,
            "ultrasound": 10,
            "ecg": 10,
            "default": 10,
        }

    def predict_failure(
        self,
        device_id: str,
        device_type: str,
        device_data: dict[str, Any],
    ) -> FailurePrediction:
        """
        Predict device failure probability based on various factors.
        
        Args:
            device_id: Device identifier
            device_type: Type of device
            device_data: Dictionary containing:
                - age_years: Device age
                - usage_hours: Total usage hours
                - maintenance_count: Number of maintenance events
                - days_since_last_maintenance: Days since last PM
                - failure_count: Historical failures
                - environment: Operating environment
                - usage_pattern: Typical usage pattern
                
        Returns:
            FailurePrediction with risk assessment
        """
        factors = []
        
        # Age factor
        age_years = device_data.get("age_years", 0)
        typical_life = self._typical_lifecycles.get(device_type.lower(), self._typical_lifecycles["default"])
        age_factor = min(1.0, age_years / typical_life)
        if age_factor > 0.8:
            factors.append(f"Device age ({age_years} years) exceeds 80% of typical lifecycle")
        age_score = age_factor * self._weights["age"]

        # Usage hours factor
        usage_hours = device_data.get("usage_hours", 0)
        expected_hours = typical_life * 365 * 8  # Assume 8 hours/day average
        usage_factor = min(1.0, usage_hours / expected_hours)
        if usage_factor > 0.8:
            factors.append(f"High usage hours ({usage_hours})")
        usage_score = usage_factor * self._weights["usage_hours"]

        # Maintenance history factor
        maintenance_count = device_data.get("maintenance_count", 0)
        days_since_maintenance = device_data.get("days_since_last_maintenance", 0)
        maintenance_factor = self._calculate_maintenance_factor(
            maintenance_count, days_since_maintenance, typical_life
        )
        if maintenance_factor > 0.5:
            factors.append("Maintenance overdue or insufficient maintenance history")
        maintenance_score = maintenance_factor * self._weights["maintenance_history"]

        # Failure history factor
        failure_count = device_data.get("failure_count", 0)
        failure_factor = min(1.0, failure_count * 0.15)
        if failure_count >= 3:
            factors.append(f"Multiple past failures ({failure_count})")
        failure_score = failure_factor * self._weights["failure_history"]

        # Environmental factor
        environment = device_data.get("environment", "standard")
        env_factor = self._calculate_environment_factor(environment)
        if env_factor > 0.5:
            factors.append(f"Harsh environment: {environment}")
        env_score = env_factor * self._weights["environmental"]

        # Usage pattern factor
        usage_pattern = device_data.get("usage_pattern", "standard")
        pattern_factor = self._calculate_pattern_factor(usage_pattern)
        pattern_score = pattern_factor * self._weights["usage_pattern"]

        # Calculate total risk score
        risk_score = (
            age_score
            + usage_score
            + maintenance_score
            + failure_score
            + env_score
            + pattern_score
        )
        risk_score = min(1.0, risk_score)

        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)

        # Calculate probability of failure
        probability_of_failure = risk_score

        # Estimate time to failure
        time_to_failure = self._estimate_time_to_failure(
            risk_score, age_years, typical_life
        )

        return FailurePrediction(
            device_id=device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            probability_of_failure=probability_of_failure,
            estimated_time_to_failure=time_to_failure,
            factors=factors,
        )

    def _calculate_maintenance_factor(
        self,
        maintenance_count: int,
        days_since_maintenance: int,
        device_life_years: int,
    ) -> float:
        """Calculate maintenance factor score."""
        expected_maintenance = device_life_years * 2  # Expect 2 PMs per year
        
        # Factor based on maintenance frequency
        frequency_factor = min(1.0, maintenance_count / expected_maintenance)
        
        # Factor based on time since last maintenance
        # Typical PM interval is 6 months (180 days)
        overdue_factor = min(1.0, days_since_maintenance / 180)
        
        return (frequency_factor + overdue_factor) / 2

    def _calculate_environment_factor(self, environment: str) -> float:
        """Calculate environmental risk factor."""
        env_scores = {
            "icu": 0.3,
            "standard": 0.4,
            "operating_room": 0.5,
            "emergency": 0.6,
            "laboratory": 0.7,
            "sterile": 0.3,
            "outdoor": 0.8,
        }
        return env_scores.get(environment.lower(), 0.4)

    def _calculate_pattern_factor(self, pattern: str) -> float:
        """Calculate usage pattern risk factor."""
        pattern_scores = {
            "light": 0.3,
            "standard": 0.5,
            "heavy": 0.7,
            "continuous": 0.9,
        }
        return pattern_scores.get(pattern.lower(), 0.5)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score."""
        if risk_score >= self._risk_thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif risk_score >= self._risk_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif risk_score >= self._risk_thresholds[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _estimate_time_to_failure(
        self,
        risk_score: float,
        age_years: int,
        typical_life: int,
    ) -> str:
        """Estimate time to failure based on risk factors."""
        if risk_score >= 0.8:
            return "< 30 days"
        elif risk_score >= 0.6:
            remaining_life = typical_life - age_years
            if remaining_life <= 1:
                return f"{remaining_life * 30} days"
            return f"1-3 months"
        elif risk_score >= 0.4:
            remaining_life = typical_life - age_years
            if remaining_life <= 1:
                return "1-3 months"
            return f"{remaining_life // 2} months"
        else:
            remaining_life = typical_life - age_years
            if remaining_life <= 0:
                return "Schedule replacement planning"
            return f"{remaining_life} years"

    def suggest_maintenance(
        self,
        device_id: str,
        device_type: str,
        failure_prediction: FailurePrediction,
    ) -> MaintenanceSuggestion:
        """
        Generate maintenance suggestion based on failure prediction.
        
        Args:
            device_id: Device identifier
            device_type: Type of device
            failure_prediction: Predicted failure data
            
        Returns:
            MaintenanceSuggestion with recommended action
        """
        risk_level = failure_prediction.risk_level
        
        # Determine maintenance type based on risk
        if risk_level == RiskLevel.CRITICAL:
            maintenance_type = MaintenanceType.EMERGENCY
            description = "Immediate inspection and potential replacement required"
            duration = "2-4 hours"
        elif risk_level == RiskLevel.HIGH:
            maintenance_type = MaintenanceType.PREDICTIVE
            description = "Schedule predictive maintenance within 2 weeks"
            duration = "1-2 hours"
        elif risk_level == RiskLevel.MEDIUM:
            maintenance_type = MaintenanceType.PREVENTIVE
            description = "Include in next preventive maintenance cycle"
            duration = "30-60 minutes"
        else:
            maintenance_type = MaintenanceType.PREVENTIVE
            description = "Continue regular maintenance schedule"
            duration = "30 minutes"

        # Calculate recommended date
        recommended_date = self._calculate_recommended_date(risk_level)

        return MaintenanceSuggestion(
            device_id=device_id,
            maintenance_type=maintenance_type,
            priority=risk_level,
            description=description,
            estimated_duration=duration,
            recommended_date=recommended_date,
        )

    def _calculate_recommended_date(self, risk_level: RiskLevel) -> str:
        """Calculate recommended maintenance date."""
        today = datetime.now()
        
        if risk_level == RiskLevel.CRITICAL:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif risk_level == RiskLevel.HIGH:
            return (today + timedelta(weeks=2)).strftime("%Y-%m-%d")
        elif risk_level == RiskLevel.MEDIUM:
            return (today + timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            return (today + timedelta(days=90)).strftime("%Y-%m-%d")

    def batch_predict(
        self,
        devices: list[dict[str, Any]],
    ) -> list[FailurePrediction]:
        """
        Run failure prediction on multiple devices.
        
        Args:
            devices: List of device dictionaries with id, type, and data
            
        Returns:
            List of FailurePrediction results
        """
        predictions = []
        for device in devices:
            prediction = self.predict_failure(
                device_id=device["id"],
                device_type=device["type"],
                device_data=device.get("data", {}),
            )
            predictions.append(prediction)
        
        # Sort by risk score descending
        predictions.sort(key=lambda p: p.risk_score, reverse=True)
        return predictions


# Global instance
_engine: PredictiveEngine | None = None


def get_predictive_engine() -> PredictiveEngine:
    """Get or create the global predictive engine instance."""
    global _engine
    if _engine is None:
        _engine = PredictiveEngine()
    return _engine
