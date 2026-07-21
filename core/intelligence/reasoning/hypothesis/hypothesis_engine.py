"""
Hypothesis Engine Module

Complete implementation for generating, evaluating, and prioritizing
clinical hypotheses from symptoms and evidence.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import defaultdict


class SeverityLevel(Enum):
    """Severity level for hypotheses."""
    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"            # Action needed soon
    MEDIUM = "medium"        # Monitor closely
    LOW = "low"             # Document and monitor


class HypothesisStatus(Enum):
    """Status of a hypothesis."""
    GENERATED = "generated"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    PENDING = "pending"


@dataclass(frozen=True)
class Symptom:
    """Clinical symptom."""
    symptom_id: str
    name: str
    description: str
    value: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.MEDIUM
    observed_at: datetime = field(default_factory=datetime.now)
    equipment_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Evidence:
    """Evidence supporting or contradicting a hypothesis."""
    evidence_id: str
    evidence_type: str
    description: str
    source: str
    weight: float = 1.0  # 0.0 - 1.0
    supporting: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Hypothesis:
    """
    Clinical hypothesis with probability and confidence.
    """
    hypothesis_id: str
    name: str
    description: str
    probability: float = 0.0  # 0.0 - 1.0
    confidence: float = 0.0  # 0.0 - 1.0
    severity: SeverityLevel = SeverityLevel.MEDIUM
    status: HypothesisStatus = HypothesisStatus.GENERATED
    supporting_evidence: list[Evidence] = field(default_factory=list)
    contradicting_evidence: list[Evidence] = field(default_factory=list)
    related_symptoms: list[str] = field(default_factory=list)
    equipment_category: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.severity, str):
            object.__setattr__(self, 'severity', SeverityLevel(self.severity))
        if isinstance(self.status, str):
            object.__setattr__(self, 'status', HypothesisStatus(self.status))


@dataclass(frozen=True)
class HypothesisSet:
    """Set of related hypotheses."""
    set_id: str
    hypotheses: list[Hypothesis]
    primary_hypothesis: Optional[Hypothesis] = None
    differential_diagnosis: list[Hypothesis] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HypothesisEvaluation:
    """Evaluation result for a hypothesis."""
    hypothesis: Hypothesis
    prior_probability: float
    likelihood: float
    posterior_probability: float
    evidence_weight: float
    confidence_score: float
    consistency_score: float


class HypothesisGenerator:
    """
    Generates hypotheses from symptoms and context.
    """
    
    def __init__(self):
        self._pattern_rules: list[dict] = []
    
    async def generate_from_symptoms(
        self,
        symptoms: list[Symptom],
        equipment_type: Optional[str] = None,
    ) -> list[Hypothesis]:
        """Generate hypotheses from symptoms."""
        hypotheses = []
        
        symptom_names = {s.name.lower() for s in symptoms}
        
        # Rule-based generation
        for rule in self._pattern_rules:
            if self._matches_pattern(symptom_names, rule.get("pattern", [])):
                hypothesis = self._create_hypothesis_from_rule(rule, symptoms)
                hypotheses.append(hypothesis)
        
        # Equipment-specific generation
        if equipment_type:
            equipment_hypotheses = await self._generate_for_equipment(
                symptoms, equipment_type
            )
            hypotheses.extend(equipment_hypotheses)
        
        # Default hypothesis if none generated
        if not hypotheses:
            hypotheses.append(Hypothesis(
                hypothesis_id="h_unknown",
                name="Unknown Condition",
                description="Unable to determine specific hypothesis from available symptoms",
                probability=0.1,
                confidence=0.3,
                severity=SeverityLevel.MEDIUM,
                related_symptoms=[s.symptom_id for s in symptoms],
            ))
        
        return hypotheses
    
    async def _generate_for_equipment(
        self,
        symptoms: list[Symptom],
        equipment_type: str,
    ) -> list[Hypothesis]:
        """Generate equipment-specific hypotheses."""
        # Common failure modes by equipment type
        failure_modes = {
            "pulse_oximeter": [
                {"id": "spo2_sensor_malfunction", "name": "SpO2 Sensor Malfunction",
                 "probability": 0.35, "severity": SeverityLevel.HIGH},
                {"id": "spo2_calibration_drift", "name": "Calibration Drift",
                 "probability": 0.25, "severity": SeverityLevel.MEDIUM},
                {"id": "spo2_probe_issue", "name": "Probe Issue",
                 "probability": 0.20, "severity": SeverityLevel.HIGH},
            ],
            "infusion_pump": [
                {"id": "occlusion", "name": "Tubing Occlusion",
                 "probability": 0.30, "severity": SeverityLevel.HIGH},
                {"id": "flow_rate_error", "name": "Flow Rate Error",
                 "probability": 0.25, "severity": SeverityLevel.MEDIUM},
            ],
        }
        
        modes = failure_modes.get(equipment_type, [])
        hypotheses = []
        
        for mode in modes:
            hypothesis = Hypothesis(
                hypothesis_id=f"h_{mode['id']}",
                name=mode["name"],
                description=f"Likely {mode['name']} based on observed symptoms",
                probability=mode["probability"],
                confidence=0.6,
                severity=mode["severity"],
                equipment_category=equipment_type,
                related_symptoms=[s.symptom_id for s in symptoms],
                metadata={"source": "equipment_model"},
            )
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _matches_pattern(
        self,
        symptoms: set[str],
        pattern: list[str],
    ) -> bool:
        """Check if symptoms match a pattern."""
        return all(s in symptoms for s in pattern)
    
    def _create_hypothesis_from_rule(
        self,
        rule: dict,
        symptoms: list[Symptom],
    ) -> Hypothesis:
        """Create hypothesis from a rule."""
        return Hypothesis(
            hypothesis_id=f"h_{rule.get('id', 'rule')}",
            name=rule.get("name", "Pattern Match"),
            description=rule.get("description", ""),
            probability=rule.get("probability", 0.5),
            confidence=rule.get("confidence", 0.5),
            severity=SeverityLevel(rule.get("severity", "medium")),
            related_symptoms=[s.symptom_id for s in symptoms],
            metadata={"source": "pattern_rule", "rule_id": rule.get("id")},
        )


class HypothesisEvaluator:
    """
    Evaluates hypotheses using Bayesian inference and evidence assessment.
    """
    
    async def evaluate(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> HypothesisEvaluation:
        """Evaluate a hypothesis with evidence."""
        # Separate supporting and contradicting evidence
        supporting = [e for e in evidence if e.supporting]
        contradicting = [e for e in evidence if not e.supporting]
        
        # Calculate evidence weight
        supporting_weight = sum(e.weight * e.confidence for e in supporting)
        contradicting_weight = sum(e.weight * e.confidence for e in contradicting)
        evidence_weight = (supporting_weight - contradicting_weight) / max(supporting_weight + contradicting_weight, 1)
        
        # Bayesian update
        prior = hypothesis.probability
        likelihood = await self._calculate_likelihood(supporting, contradicting)
        
        # P(H|E) = P(E|H) * P(H) / P(E)
        posterior = (likelihood * prior)
        posterior = min(max(posterior, 0.0), 1.0)
        
        # Consistency check
        consistency = await self._check_consistency(hypothesis, evidence)
        
        # Confidence calculation
        confidence = self._calculate_confidence(
            len(supporting) + len(contradicting),
            evidence_weight,
            consistency,
        )
        
        return HypothesisEvaluation(
            hypothesis=hypothesis,
            prior_probability=prior,
            likelihood=likelihood,
            posterior_probability=posterior,
            evidence_weight=evidence_weight,
            confidence_score=confidence,
            consistency_score=consistency,
        )
    
    async def _calculate_likelihood(
        self,
        supporting: list[Evidence],
        contradicting: list[Evidence],
    ) -> float:
        """Calculate likelihood P(E|H)."""
        if not supporting and not contradicting:
            return 0.5
        
        likelihood = 0.5
        for e in supporting:
            likelihood *= e.weight * e.confidence
        for e in contradicting:
            likelihood *= (1 - e.weight) * e.confidence
        
        return min(max(likelihood, 0.0), 1.0)
    
    async def _check_consistency(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> float:
        """Check consistency between hypothesis and evidence."""
        if not evidence:
            return 0.5
        
        consistent_count = 0
        for e in evidence:
            if e.supporting and hypothesis.probability > 0.3:
                consistent_count += 1
            elif not e.supporting and hypothesis.probability < 0.3:
                consistent_count += 1
        
        return consistent_count / len(evidence)
    
    def _calculate_confidence(
        self,
        evidence_count: int,
        evidence_weight: float,
        consistency: float,
    ) -> float:
        """Calculate overall confidence score."""
        # More evidence = higher confidence (diminishing returns)
        evidence_factor = min(evidence_count / 5, 1.0) * 0.4
        
        # Weight of evidence
        weight_factor = abs(evidence_weight) * 0.3
        
        # Consistency
        consistency_factor = consistency * 0.3
        
        return min(evidence_factor + weight_factor + consistency_factor, 1.0)


class HypothesisPrioritizer:
    """
    Prioritizes hypotheses based on severity, probability, and confidence.
    """
    
    async def prioritize(
        self,
        hypotheses: list[Hypothesis],
    ) -> list[Hypothesis]:
        """Prioritize hypotheses."""
        # Sort by composite score
        scored = []
        for h in hypotheses:
            score = self._calculate_priority_score(h)
            scored.append((score, h))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [h for _, h in scored]
    
    def _calculate_priority_score(self, hypothesis: Hypothesis) -> float:
        """Calculate priority score."""
        # Severity weight
        severity_weights = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.LOW: 0.3,
        }
        severity_score = severity_weights.get(hypothesis.severity, 0.5)
        
        # Probability weight
        probability_score = hypothesis.probability
        
        # Confidence weight
        confidence_score = hypothesis.confidence
        
        # Composite score
        return (
            severity_score * 0.4 +
            probability_score * 0.3 +
            confidence_score * 0.3
        )


class HypothesisEngine:
    """
    Complete hypothesis engine for clinical reasoning.
    """
    
    def __init__(self):
        self.generator = HypothesisGenerator()
        self.evaluator = HypothesisEvaluator()
        self.prioritizer = HypothesisPrioritizer()
    
    async def generate_hypotheses(
        self,
        symptoms: list[Symptom],
        equipment_type: Optional[str] = None,
        existing_evidence: list[Evidence] | None = None,
    ) -> HypothesisSet:
        """Generate and evaluate hypotheses from symptoms."""
        # Generate candidates
        candidates = await self.generator.generate_from_symptoms(symptoms, equipment_type)
        
        # Evaluate with evidence
        evaluated = []
        for hypothesis in candidates:
            evidence = existing_evidence or []
            evaluation = await self.evaluator.evaluate(hypothesis, evidence)
            
            # Update hypothesis with evaluation
            updated = Hypothesis(
                hypothesis_id=hypothesis.hypothesis_id,
                name=hypothesis.name,
                description=hypothesis.description,
                probability=evaluation.posterior_probability,
                confidence=evaluation.confidence_score,
                severity=hypothesis.severity,
                status=HypothesisStatus.EVALUATED,
                supporting_evidence=hypothesis.supporting_evidence,
                contradicting_evidence=hypothesis.contradicting_evidence,
                related_symptoms=hypothesis.related_symptoms,
                equipment_category=hypothesis.equipment_category,
                created_at=hypothesis.created_at,
                updated_at=datetime.now(),
                metadata=hypothesis.metadata,
            )
            evaluated.append(updated)
        
        # Prioritize
        prioritized = await self.prioritizer.prioritize(evaluated)
        
        # Create set
        set_id = f"hs_{datetime.now().timestamp()}"
        primary = prioritized[0] if prioritized else None
        differential = prioritized[:5]  # Top 5 for differential
        
        return HypothesisSet(
            set_id=set_id,
            hypotheses=prioritized,
            primary_hypothesis=primary,
            differential_diagnosis=differential,
        )
    
    async def update_with_evidence(
        self,
        hypothesis: Hypothesis,
        new_evidence: list[Evidence],
    ) -> Hypothesis:
        """Update hypothesis with new evidence."""
        evaluation = await self.evaluator.evaluate(hypothesis, new_evidence)
        
        # Update evidence lists
        supporting = list(hypothesis.supporting_evidence)
        contradicting = list(hypothesis.contradicting_evidence)
        
        for e in new_evidence:
            if e.supporting:
                supporting.append(e)
            else:
                contradicting.append(e)
        
        return Hypothesis(
            hypothesis_id=hypothesis.hypothesis_id,
            name=hypothesis.name,
            description=hypothesis.description,
            probability=evaluation.posterior_probability,
            confidence=evaluation.confidence_score,
            severity=hypothesis.severity,
            status=HypothesisStatus.EVALUATED,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            related_symptoms=hypothesis.related_symptoms,
            equipment_category=hypothesis.equipment_category,
            created_at=hypothesis.created_at,
            updated_at=datetime.now(),
            metadata=hypothesis.metadata,
        )


__all__ = [
    "SeverityLevel",
    "HypothesisStatus",
    "Symptom",
    "Evidence",
    "Hypothesis",
    "HypothesisSet",
    "HypothesisEvaluation",
    "HypothesisGenerator",
    "HypothesisEvaluator",
    "HypothesisPrioritizer",
    "HypothesisEngine",
]
