"""Differential Diagnosis Engine for Biomedical Devices."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.PHASE_1.clinical.diagnosis import (
    DifferentialDiagnosisResult,
    DiagnosisHypothesis,
    HypothesisStatus,
)


class HypothesisStatus(str, Enum):
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    PENDING = "pending"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DiagnosisHypothesis:
    """Represents a possible diagnosis."""
    id: str
    name: str
    probability: float
    severity: SeverityLevel
    supporting_evidence: list[str]
    ruling_out_tests: list[str]
    status: HypothesisStatus = HypothesisStatus.PENDING


@dataclass
class DifferentialDiagnosisResult:
    """Result of differential diagnosis analysis."""
    hypotheses: list[DiagnosisHypothesis]
    recommended_tests: list[str]
    most_likely: str | None
    confidence: float


class DiagnosisEngine:
    """
    Differential Diagnosis Engine for biomedical engineering.
    
    Analyzes symptoms and device data to generate ranked differential diagnoses.
    """

    def __init__(self):
        self._diagnosis_rules: dict[str, dict[str, Any]] = {}
        self._symptom_diagnosis_map: dict[str, list[str]] = {}
        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """Initialize the diagnosis rules database."""
        # Power-related diagnoses
        self._diagnosis_rules["power_failure"] = {
            "symptoms": ["no_power", "intermittent_power", "power_fluctuation"],
            "causes": [
                "Failed power supply unit",
                "Damaged power cable",
                "Faulty outlet",
                "UPS failure",
            ],
            "severity": SeverityLevel.CRITICAL,
            "tests": [
                "Check power cable continuity",
                "Measure output voltage",
                "Test with known-good outlet",
                "Verify UPS functionality",
            ],
        }

        # Calibration drift diagnoses
        self._diagnosis_rules["calibration_drift"] = {
            "symptoms": ["inaccurate_readings", "drift_detected", "quality_control_fail"],
            "causes": [
                "Sensor degradation",
                "Component aging",
                "Environmental factors",
                "Software error",
            ],
            "severity": SeverityLevel.HIGH,
            "tests": [
                "Run calibration verification",
                "Check environmental conditions",
                "Compare with reference device",
                "Review error logs",
            ],
        }

        # Communication failures
        self._diagnosis_rules["communication_failure"] = {
            "symptoms": ["data_loss", "timeout_errors", "connection_failed"],
            "causes": [
                "Network issues",
                "Protocol mismatch",
                "Port configuration error",
                "Firewall blocking",
            ],
            "severity": SeverityLevel.MEDIUM,
            "tests": [
                "Ping network connection",
                "Verify protocol settings",
                "Check firewall rules",
                "Test with direct connection",
            ],
        }

        # Display issues
        self._diagnosis_rules["display_failure"] = {
            "symptoms": ["blank_screen", "flickering", "color_distortion", "dead_pixels"],
            "causes": [
                "Backlight failure",
                "LCD panel damage",
                "Connection ribbon fault",
                "Inverter failure",
            ],
            "severity": SeverityLevel.HIGH,
            "tests": [
                "Check with external monitor",
                "Inspect ribbon cables",
                "Test backlight voltage",
                "Verify inverter output",
            ],
        }

        # Sensor failures
        self._diagnosis_rules["sensor_failure"] = {
            "symptoms": ["erratic_readings", "stuck_values", "no_response"],
            "causes": [
                "Sensor element failure",
                "Wiring damage",
                "Electromagnetic interference",
                "Contamination",
            ],
            "severity": SeverityLevel.CRITICAL,
            "tests": [
                "Test sensor with simulator",
                "Check wiring continuity",
                "Shield from EMI sources",
                "Clean or replace sensor",
            ],
        }

        # Build symptom to diagnosis mapping
        for diagnosis, config in self._diagnosis_rules.items():
            for symptom in config["symptoms"]:
                if symptom not in self._symptom_diagnosis_map:
                    self._symptom_diagnosis_map[symptom] = []
                self._symptom_diagnosis_map[symptom].append(diagnosis)

    def analyze(
        self,
        symptoms: list[str],
        device_type: str | None = None,
        device_history: dict[str, Any] | None = None,
    ) -> DifferentialDiagnosisResult:
        """
        Perform differential diagnosis based on symptoms.
        
        Args:
            symptoms: List of observed symptoms
            device_type: Optional device type for context
            device_history: Optional device history for pattern analysis
            
        Returns:
            DifferentialDiagnosisResult with ranked hypotheses
        """
        hypothesis_scores: dict[str, float] = {}
        supporting_evidence: dict[str, list[str]] = {}
        recommended_tests: set[str] = set()

        # Score each possible diagnosis
        for symptom in symptoms:
            if symptom in self._symptom_diagnosis_map:
                for diagnosis_id in self._symptom_diagnosis_map[symptom]:
                    if diagnosis_id not in hypothesis_scores:
                        hypothesis_scores[diagnosis_id] = 0.0
                        supporting_evidence[diagnosis_id] = []

                    # Base score from symptom match
                    hypothesis_scores[diagnosis_id] += 1.0
                    supporting_evidence[diagnosis_id].append(f"Symptom: {symptom}")

                    # Add recommended tests
                    for test in self._diagnosis_rules[diagnosis_id]["tests"]:
                        recommended_tests.add(test)

        # Adjust scores based on severity and prior probability
        adjusted_scores = {}
        for diagnosis_id, score in hypothesis_scores.items():
            config = self._diagnosis_rules[diagnosis_id]
            
            # Apply severity multiplier
            severity_multiplier = {
                SeverityLevel.CRITICAL: 1.3,
                SeverityLevel.HIGH: 1.1,
                SeverityLevel.MEDIUM: 1.0,
                SeverityLevel.LOW: 0.9,
            }
            
            multiplier = severity_multiplier.get(config["severity"], 1.0)
            
            # Apply device history adjustment
            if device_history:
                age_factor = self._calculate_age_factor(device_history)
                multiplier *= age_factor

            adjusted_scores[diagnosis_id] = score * multiplier

        # Normalize to probabilities
        total_score = sum(adjusted_scores.values()) if adjusted_scores else 1.0
        hypotheses = []
        
        for diagnosis_id, raw_score in adjusted_scores.items():
            probability = raw_score / total_score if total_score > 0 else 0.0
            config = self._diagnosis_rules[diagnosis_id]

            hypothesis = DiagnosisHypothesis(
                id=f"diag-{diagnosis_id}",
                name=self._format_diagnosis_name(diagnosis_id),
                probability=probability,
                severity=config["severity"],
                supporting_evidence=supporting_evidence.get(diagnosis_id, []),
                ruling_out_tests=config["tests"][:2] if config["tests"] else [],
                status=HypothesisStatus.PENDING,
            )
            hypotheses.append(hypothesis)

        # Sort by probability
        hypotheses.sort(key=lambda h: h.probability, reverse=True)

        # Determine most likely diagnosis
        most_likely = hypotheses[0].id if hypotheses else None
        
        # Calculate confidence
        confidence = hypotheses[0].probability if hypotheses else 0.0
        if len(hypotheses) > 1:
            # Confidence is higher when there's a clear leader
            confidence = hypotheses[0].probability - hypotheses[1].probability
            confidence = min(1.0, confidence + 0.5)

        return DifferentialDiagnosisResult(
            hypotheses=hypotheses,
            recommended_tests=list(recommended_tests),
            most_likely=most_likely,
            confidence=confidence,
        )

    def _calculate_age_factor(self, device_history: dict[str, Any]) -> float:
        """Calculate probability adjustment based on device age."""
        age_years = device_history.get("age_years", 0)
        usage_hours = device_history.get("usage_hours", 0)
        
        factor = 1.0
        
        # Older devices more likely to have component failures
        if age_years > 10:
            factor *= 1.2
        elif age_years > 7:
            factor *= 1.1
        
        # High usage increases failure probability
        if usage_hours > 20000:
            factor *= 1.15
        elif usage_hours > 15000:
            factor *= 1.05
        
        return factor

    def _format_diagnosis_name(self, diagnosis_id: str) -> str:
        """Format diagnosis ID into human-readable name."""
        return diagnosis_id.replace("_", " ").title()

    def confirm_diagnosis(
        self,
        hypothesis_id: str,
        result: DifferentialDiagnosisResult,
    ) -> DifferentialDiagnosisResult:
        """
        Mark a hypothesis as confirmed and rule out others.
        
        Args:
            hypothesis_id: ID of the confirmed hypothesis
            result: The diagnosis result to update
            
        Returns:
            Updated diagnosis result
        """
        for hypothesis in result.hypotheses:
            if hypothesis.id == hypothesis_id:
                hypothesis.status = HypothesisStatus.CONFIRMED
            else:
                hypothesis.status = HypothesisStatus.RULED_OUT
        
        return result


# Global instance
_engine: DiagnosisEngine | None = None


def get_diagnosis_engine() -> DiagnosisEngine:
    """Get or create the global diagnosis engine instance."""
    global _engine
    if _engine is None:
        _engine = DiagnosisEngine()
    return _engine
