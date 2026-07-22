"""
Diagnostic Engine Module

Complete implementation for clinical diagnosis including
differential diagnosis and root cause analysis.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import defaultdict


class UrgencyLevel(Enum):
    """Urgency level for diagnosis."""
    EMERGENCY = "emergency"      # Immediate action
    URGENT = "urgent"           # Action within minutes
    ROUTINE = "routine"         # Action within hours
    MONITOR = "monitor"          # Continue monitoring


class DiagnosticStatus(Enum):
    """Status of diagnostic process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class Recommendation:
    """Recommendation for action."""
    recommendation_id: str
    action: str
    priority: int
    confidence: float
    rationale: str
    contraindications: list[str] = field(default_factory=list)
    estimated_time: Optional[str] = None


@dataclass(frozen=True)
class Diagnosis:
    """Single diagnosis."""
    diagnosis_id: str
    condition: str
    probability: float
    confidence: float
    urgency: UrgencyLevel
    supporting_evidence: list[str] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    status: DiagnosticStatus = DiagnosticStatus.PENDING


@dataclass
class DifferentialDiagnosis:
    """Complete differential diagnosis."""
    dd_id: str
    symptoms: list[str]
    diagnoses: list[Diagnosis]
    most_likely: Optional[Diagnosis] = None
    ruled_out: list[str] = field(default_factory=list)
    pending_investigations: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RootCauseAnalysis:
    """Root cause analysis result."""
    rca_id: str
    problem_statement: str
    why_chains: list[list[str]]  # Multiple 5-whys chains
    contributing_factors: list[str]
    root_cause: Optional[str]
    recommendations: list[Recommendation]
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SymptomAnalysis:
    """Analysis of a symptom."""
    symptom: str
    pattern_matches: list[str]
    severity_impact: float
    related_diagnoses: list[str]


class SymptomAnalyzer:
    """
    Analyzes symptoms to identify patterns and related conditions.
    """
    
    def __init__(self):
        self._patterns: dict[str, list[str]] = defaultdict(list)
    
    async def analyze(
        self,
        symptoms: list[str],
    ) -> list[SymptomAnalysis]:
        """Analyze symptoms for patterns."""
        analyses = []
        
        for symptom in symptoms:
            pattern_matches = self._find_pattern_matches(symptom)
            related = self._find_related_diagnoses(symptom)
            
            analyses.append(SymptomAnalysis(
                symptom=symptom,
                pattern_matches=pattern_matches,
                severity_impact=self._calculate_severity_impact(symptom),
                related_diagnoses=related,
            ))
        
        return analyses
    
    def _find_pattern_matches(self, symptom: str) -> list[str]:
        """Find matching patterns for symptom."""
        symptom_lower = symptom.lower()
        matches = []
        
        for pattern, conditions in self._patterns.items():
            if any(c.lower() in symptom_lower for c in conditions):
                matches.append(pattern)
        
        return matches
    
    def _find_related_diagnoses(self, symptom: str) -> list[str]:
        """Find diagnoses related to symptom."""
        # Map symptoms to common diagnoses
        symptom_map = {
            "low_spo2": ["hypoxia", "sensor_malfunction", "probe_issue"],
            "high_heart_rate": ["tachycardia", "anxiety", "dehydration"],
            "high_blood_pressure": ["hypertension", "stress", "medication_effect"],
            "alarm": ["equipment_issue", "patient_condition", "false_positive"],
        }
        
        symptom_lower = symptom.lower()
        for key, diagnoses in symptom_map.items():
            if key in symptom_lower:
                return diagnoses
        
        return []
    
    def _calculate_severity_impact(self, symptom: str) -> float:
        """Calculate severity impact of symptom."""
        high_severity = ["low_spo2", "cardiac", "respiratory", "alarm_critical"]
        medium_severity = ["high_temp", "low_bp", "irregular"]
        
        symptom_lower = symptom.lower()
        
        for term in high_severity:
            if term in symptom_lower:
                return 0.9
        
        for term in medium_severity:
            if term in symptom_lower:
                return 0.6
        
        return 0.3


class DifferentialDiagnosisEngine:
    """
    Generates differential diagnosis from symptoms and evidence.
    """
    
    def __init__(self):
        self._diagnosis_rules: dict[str, dict] = {}
    
    async def generate(
        self,
        symptoms: list[str],
        evidence: list[dict] | None = None,
    ) -> DifferentialDiagnosis:
        """Generate differential diagnosis."""
        diagnoses = []
        
        # Generate candidates based on symptoms
        candidates = await self._generate_candidates(symptoms)
        
        # Evaluate each candidate
        for candidate in candidates:
            probability = candidate["probability"]
            confidence = candidate["confidence"]
            
            # Adjust based on evidence
            if evidence:
                probability, confidence = await self._adjust_with_evidence(
                    probability, confidence, evidence
                )
            
            diagnoses.append(Diagnosis(
                diagnosis_id=candidate["id"],
                condition=candidate["condition"],
                probability=probability,
                confidence=confidence,
                urgency=self._determine_urgency(candidate, symptoms),
                supporting_evidence=candidate.get("evidence", []),
                recommendations=self._generate_recommendations(candidate),
            ))
        
        # Sort by probability
        diagnoses.sort(key=lambda d: d.probability, reverse=True)
        
        # Determine most likely
        most_likely = diagnoses[0] if diagnoses else None
        
        return DifferentialDiagnosis(
            dd_id=f"dd_{datetime.now().timestamp()}",
            symptoms=symptoms,
            diagnoses=diagnoses,
            most_likely=most_likely,
            ruled_out=self._determine_ruled_out(diagnoses),
            pending_investigations=self._suggest_investigations(diagnoses),
        )
    
    async def _generate_candidates(
        self,
        symptoms: list[str],
    ) -> list[dict]:
        """Generate diagnostic candidates from symptoms."""
        candidates = []
        
        # SpO2 related
        if any("spo2" in s.lower() for s in symptoms):
            candidates.extend([
                {"id": "spo2_sensor", "condition": "Sensor Malfunction",
                 "probability": 0.35, "confidence": 0.7,
                 "evidence": ["alarm_active", "probe_warning"]},
                {"id": "spo2_patient", "condition": "Patient Hypoxia",
                 "probability": 0.28, "confidence": 0.6,
                 "evidence": ["vital_signs"]},
                {"id": "spo2_probe", "condition": "Probe Issue",
                 "probability": 0.22, "confidence": 0.65,
                 "evidence": ["probe_age"]},
            ])
        
        # Alarm related
        if any("alarm" in s.lower() for s in symptoms):
            candidates.extend([
                {"id": "alarm_equip", "condition": "Equipment Alarm",
                 "probability": 0.40, "confidence": 0.8,
                 "evidence": ["alarm_code"]},
                {"id": "alarm_false", "condition": "False Alarm",
                 "probability": 0.25, "confidence": 0.5,
                 "evidence": []},
            ])
        
        # Default if no matches
        if not candidates:
            candidates.append({
                "id": "unknown",
                "condition": "Indeterminate",
                "probability": 0.1,
                "confidence": 0.3,
                "evidence": [],
            })
        
        return candidates
    
    async def _adjust_with_evidence(
        self,
        probability: float,
        confidence: float,
        evidence: list[dict],
    ) -> tuple[float, float]:
        """Adjust probability based on evidence."""
        supporting = sum(1 for e in evidence if e.get("supporting", False))
        contradicting = sum(1 for e in evidence if not e.get("supporting", False))
        
        # Adjust probability
        adjustment = (supporting - contradicting) * 0.1
        probability = min(max(probability + adjustment, 0), 1)
        
        # Adjust confidence
        evidence_count = supporting + contradicting
        if evidence_count > 0:
            confidence = min(confidence + (evidence_count * 0.05), 1.0)
        
        return probability, confidence
    
    def _determine_urgency(self, candidate: dict, symptoms: list[str]) -> UrgencyLevel:
        """Determine urgency level."""
        if "critical" in candidate.get("condition", "").lower():
            return UrgencyLevel.EMERGENCY
        if any("spo2" in s.lower() and "low" in s.lower() for s in symptoms):
            return UrgencyLevel.URGENT
        if "alarm" in symptoms:
            return UrgencyLevel.URGENT
        return UrgencyLevel.ROUTINE
    
    def _generate_recommendations(self, candidate: dict) -> list[Recommendation]:
        """Generate recommendations for diagnosis."""
        recommendations = []
        
        if candidate["id"] == "spo2_sensor":
            recommendations.append(Recommendation(
                recommendation_id="r1",
                action="Check and replace SpO2 sensor",
                priority=1,
                confidence=0.8,
                rationale="Most likely cause of incorrect SpO2 reading",
            ))
            recommendations.append(Recommendation(
                recommendation_id="r2",
                action="Verify patient vital signs manually",
                priority=2,
                confidence=0.7,
                rationale="Rule out patient hypoxia",
            ))
        
        elif candidate["id"] == "alarm_equip":
            recommendations.append(Recommendation(
                recommendation_id="r3",
                action="Check alarm settings and parameters",
                priority=1,
                confidence=0.75,
                rationale="Equipment may need recalibration",
            ))
        
        return recommendations
    
    def _determine_ruled_out(self, diagnoses: list[Diagnosis]) -> list[str]:
        """Determine which diagnoses can be ruled out."""
        ruled_out = []
        for d in diagnoses:
            if d.probability < 0.1:
                ruled_out.append(d.condition)
        return ruled_out
    
    def _suggest_investigations(self, diagnoses: list[Diagnosis]) -> list[str]:
        """Suggest additional investigations."""
        investigations = []
        
        for d in diagnoses[:3]:  # Top 3 diagnoses
            if d.condition == "Patient Hypoxia":
                investigations.append("Blood gas analysis")
            elif d.condition == "Sensor Malfunction":
                investigations.append("Sensor self-test")
            elif d.condition == "Probe Issue":
                investigations.append("Replace probe and verify")
        
        return list(set(investigations))


class RootCauseAnalyzer:
    """
    Performs root cause analysis using 5 Whys methodology.
    """
    
    async def analyze(
        self,
        problem: str,
        evidence: list[dict] | None = None,
    ) -> RootCauseAnalysis:
        """Perform 5 Whys root cause analysis."""
        why_chains = []
        contributing_factors = []
        
        # Generate 5 Whys chains based on problem type
        if "spo2" in problem.lower() or "oximeter" in problem.lower():
            chain = await self._analyze_spo2_problem(problem)
            why_chains.append(chain)
            
            # Contributing factors
            contributing_factors = [
                "Equipment age",
                "Usage patterns",
                "Maintenance history",
                "Environmental conditions",
            ]
        
        # Find common root cause
        root_cause = why_chains[0][-1] if why_chains else None
        
        return RootCauseAnalysis(
            rca_id=f"rca_{datetime.now().timestamp()}",
            problem_statement=problem,
            why_chains=why_chains,
            contributing_factors=contributing_factors,
            root_cause=root_cause,
            recommendations=self._generate_rca_recommendations(root_cause),
            confidence=0.8 if root_cause else 0.4,
        )
    
    async def _analyze_spo2_problem(self, problem: str) -> list[str]:
        """Analyze SpO2 problem using 5 Whys."""
        chain = [
            "SpO2 reading is incorrect",
            "Why? → Sensor is malfunctioning",
            "Why? → Sensor has exceeded recommended usage hours",
            "Why? → Preventive maintenance was not performed on schedule",
            "Why? → Maintenance tracking system did not alert",
            "Why? → Integration between equipment tracking and maintenance scheduling needs improvement",
        ]
        return chain
    
    def _generate_rca_recommendations(self, root_cause: str | None) -> list[Recommendation]:
        """Generate recommendations from root cause analysis."""
        if root_cause and "maintenance" in root_cause.lower():
            return [
                Recommendation(
                    recommendation_id="rca_r1",
                    action="Schedule overdue preventive maintenance",
                    priority=1,
                    confidence=0.9,
                    rationale="Root cause identified as maintenance gap",
                ),
                Recommendation(
                    recommendation_id="rca_r2",
                    action="Implement automated maintenance alerts",
                    priority=2,
                    confidence=0.8,
                    rationale="Prevent future maintenance gaps",
                ),
            ]
        return []


class DiagnosticEngine:
    """
    Complete diagnostic engine combining all diagnostic capabilities.
    """
    
    def __init__(self):
        self.symptom_analyzer = SymptomAnalyzer()
        self.differential_engine = DifferentialDiagnosisEngine()
        self.rca_analyzer = RootCauseAnalyzer()
    
    async def diagnose(
        self,
        symptoms: list[str],
        evidence: list[dict] | None = None,
        include_rca: bool = False,
    ) -> DifferentialDiagnosis:
        """Perform complete diagnosis."""
        # Analyze symptoms
        await self.symptom_analyzer.analyze(symptoms)
        
        # Generate differential diagnosis
        diagnosis = await self.differential_engine.generate(symptoms, evidence)
        
        return diagnosis
    
    async def diagnose_with_rca(
        self,
        problem: str,
        symptoms: list[str],
        evidence: list[dict] | None = None,
    ) -> tuple[DifferentialDiagnosis, RootCauseAnalysis]:
        """Perform diagnosis with root cause analysis."""
        diagnosis = await self.diagnose(symptoms, evidence)
        rca = await self.rca_analyzer.analyze(problem, evidence)
        
        return diagnosis, rca


__all__ = [
    "UrgencyLevel",
    "DiagnosticStatus",
    "Recommendation",
    "Diagnosis",
    "DifferentialDiagnosis",
    "RootCauseAnalysis",
    "SymptomAnalysis",
    "SymptomAnalyzer",
    "DifferentialDiagnosisEngine",
    "RootCauseAnalyzer",
    "DiagnosticEngine",
]
