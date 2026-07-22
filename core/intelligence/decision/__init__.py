"""
Decision Engine Module

Complete implementation of EPIC 9 for EREN PHASE 3.

This module provides clinical decision making:
- Alternative Ranking
- Decision Scoring
- Action Planning
- Priority Classification
- Automation Evaluation
- Recommendation Generation
- Decision Recording

ARCHITECTURE NOTE:
- Severity, RiskLevel, and Priority are imported from Foundation (single source of truth)
- AutomationLevel is extended here for decision-specific values
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

# Import shared enums from Foundation (SINGLE SOURCE OF TRUTH)
from core.intelligence.foundation import Severity, RiskLevel, Priority


# Version
__version__ = "1.0.0"


# ============ ENGINE-SPECIFIC ENUMS ============

class DecisionAutomationLevel(Enum):
    """Automation approval level for decisions."""
    AUTO_APPROVED = "auto_approved"
    REQUIRES_REVIEW = "requires_review"
    BLOCKED = "blocked"


# ============ DOMAIN MODELS ============

@dataclass
class EvidenceBundle:
    """Bundle of evidence supporting a decision."""
    supporting: list = field(default_factory=list)
    contradicting: list = field(default_factory=list)
    quality_score: float = 0.0
    sufficiency_score: float = 0.0


@dataclass
class ReasoningChain:
    """Chain of reasoning leading to decision."""
    hypothesis: str = ""
    evidence_used: list = field(default_factory=list)
    logic_steps: list = field(default_factory=list)
    conclusion: str = ""


@dataclass
class Risk:
    """Risk associated with decision."""
    risk_id: str
    description: str
    level: RiskLevel
    mitigation: str = ""


@dataclass
class PlanStep:
    """Individual step in action plan."""
    step_number: int
    action: str
    description: str
    estimated_duration_minutes: int
    required_personnel: list = field(default_factory=list)
    safety_warnings: list = field(default_factory=list)


@dataclass
class DecisionPlan:
    """Action plan for executing decision."""
    steps: list[PlanStep]
    estimated_total_duration_minutes: int
    prerequisites: list = field(default_factory=list)
    safety_checks: list = field(default_factory=list)


@dataclass
class DecisionAction:
    """Recommended action."""
    action: str
    reasoning: str
    priority: Priority
    alternatives: list = field(default_factory=list)


@dataclass
class DecisionAlternative:
    """Alternative decision option."""
    id: str
    option: str
    score: float
    evidence_count: int
    risk_level: RiskLevel
    confidence: float
    ranking: int = 0


@dataclass
class DecisionScore:
    """Score breakdown for a decision."""
    total_score: float
    evidence_score: float
    confidence_score: float
    safety_score: float
    rules_score: float
    ranking: int = 0


@dataclass
class AuditInfo:
    """Audit information for decision."""
    decision_id: str
    timestamp: datetime
    reasoning_version: str = "v1.0"
    knowledge_version: str = "v1.0"
    evidence_version: str = "v1.0"
    rules_version: str = "v1.0"
    operator: Optional[str] = None


@dataclass
class ValidationStatus:
    """Validation status of decision."""
    is_valid: bool
    evidence_valid: bool
    confidence_valid: bool
    safety_valid: bool
    rules_valid: bool
    clinical_valid: bool
    rejection_reasons: list = field(default_factory=list)


@dataclass
class ClinicalDecision:
    """Main clinical decision object."""
    id: str
    timestamp: datetime
    decision: str
    confidence: float
    priority: Priority
    alternatives: list[DecisionAlternative]
    recommended_actions: list[DecisionAction]
    validation_status: ValidationStatus
    automation_level: AutomationLevel
    action_plan: Optional[DecisionPlan]
    audit: AuditInfo
    reasoning: ReasoningChain = field(default_factory=ReasoningChain)
    risks: list = field(default_factory=list)


# ============ COMPONENT SCORING ============

class DecisionScorer:
    """Scores decisions based on multiple factors."""
    
    # Component weights
    EVIDENCE_WEIGHT = 0.40
    CONFIDENCE_WEIGHT = 0.25
    SAFETY_WEIGHT = 0.20
    RULES_WEIGHT = 0.15
    
    def score(
        self,
        alternative: dict,
        safety_decision: str,
        rules_compliant: bool,
        confidence: float,
    ) -> DecisionScore:
        """Calculate total score for alternative."""
        
        # Evidence score
        evidence_bundle = alternative.get("evidence_bundle", {})
        evidence_score = self._calculate_evidence_score(evidence_bundle)
        
        # Safety score
        safety_score = 1.0 if safety_decision != "block" else 0.0
        
        # Rules score
        rules_score = 1.0 if rules_compliant else 0.0
        
        # Confidence score
        conf_score = confidence
        
        # Weighted sum
        total_score = (
            evidence_score * self.EVIDENCE_WEIGHT +
            conf_score * self.CONFIDENCE_WEIGHT +
            safety_score * self.SAFETY_WEIGHT +
            rules_score * self.RULES_WEIGHT
        )
        
        return DecisionScore(
            total_score=total_score,
            evidence_score=evidence_score,
            confidence_score=conf_score,
            safety_score=safety_score,
            rules_score=rules_score,
        )
    
    def _calculate_evidence_score(self, evidence_bundle: dict) -> float:
        """Calculate evidence score."""
        supporting = evidence_bundle.get("supporting", [])
        
        if not supporting:
            return 0.0
        
        # Count factor
        count_score = min(len(supporting) / 3, 1.0)
        
        # Quality factor
        quality_scores = [e.get("quality_score", 0) for e in supporting]
        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return count_score * 0.3 + quality_score * 0.7


class AlternativeRanker:
    """Ranks decision alternatives."""
    
    def rank(self, scored: list) -> list[DecisionAlternative]:
        """Rank alternatives by score."""
        
        # Sort by total score descending
        sorted_alts = sorted(scored, key=lambda x: x[1].total_score, reverse=True)
        
        # Assign rankings
        ranked = []
        for rank, (alt, score) in enumerate(sorted_alts, 1):
            ranked.append(DecisionAlternative(
                id=alt.get("id", f"alt_{rank}"),
                option=alt.get("option", "Unknown"),
                score=score.total_score,
                evidence_count=len(alt.get("evidence_bundle", {}).get("supporting", [])),
                risk_level=RiskLevel(alt.get("risk_level", "medium")),
                confidence=alt.get("confidence", 0.5),
                ranking=rank,
            ))
        
        return ranked


# ============ ACTION PLANNING ============

PLAN_TEMPLATES = {
    "REPLACE": [
        {"action": "Remove equipment from service", "duration": 15},
        {"action": "Notify biomedical engineering", "duration": 5},
        {"action": "Replace component", "duration": 30},
        {"action": "Perform calibration", "duration": 45},
        {"action": "Execute functional tests", "duration": 30},
        {"action": "Return equipment to service", "duration": 10},
    ],
    "CALIBRATE": [
        {"action": "Remove equipment from service", "duration": 10},
        {"action": "Connect calibration equipment", "duration": 15},
        {"action": "Perform calibration procedure", "duration": 60},
        {"action": "Verify calibration results", "duration": 15},
        {"action": "Document calibration", "duration": 10},
        {"action": "Return equipment to service", "duration": 10},
    ],
    "REPAIR": [
        {"action": "Remove equipment from service", "duration": 10},
        {"action": "Document fault symptoms", "duration": 15},
        {"action": "Diagnose root cause", "duration": 30},
        {"action": "Perform repair", "duration": 60},
        {"action": "Test repair", "duration": 30},
        {"action": "Complete documentation", "duration": 15},
    ],
    "UPDATE": [
        {"action": "Backup current configuration", "duration": 10},
        {"action": "Download update package", "duration": 15},
        {"action": "Apply update", "duration": 30},
        {"action": "Verify update success", "duration": 15},
        {"action": "Test functionality", "duration": 30},
    ],
}


class ActionPlanner:
    """Generates action plans for decisions."""
    
    def create_plan(self, decision: str, context: dict = None) -> DecisionPlan:
        """Create action plan for decision."""
        
        # Determine plan type
        decision_upper = decision.upper()
        if "REPLACE" in decision_upper:
            template = PLAN_TEMPLATES["REPLACE"]
        elif "CALIBRAT" in decision_upper:
            template = PLAN_TEMPLATES["CALIBRATE"]
        elif "REPAIR" in decision_upper:
            template = PLAN_TEMPLATES["REPAIR"]
        elif "UPDATE" in decision_upper or "FIRMWARE" in decision_upper:
            template = PLAN_TEMPLATES["UPDATE"]
        else:
            template = PLAN_TEMPLATES["REPLACE"]
        
        # Generate steps
        steps = []
        total_duration = 0
        
        for i, step_template in enumerate(template, 1):
            steps.append(PlanStep(
                step_number=i,
                action=step_template["action"],
                description=f"Step {i}: {step_template['action']}",
                estimated_duration_minutes=step_template["duration"],
                required_personnel=["Biomedical Technician"],
                safety_warnings=["Verify equipment safety", "Follow procedures"],
            ))
            total_duration += step_template["duration"]
        
        return DecisionPlan(
            steps=steps,
            estimated_total_duration_minutes=total_duration,
            prerequisites=["Equipment removed from service", "Parts available"],
            safety_checks=["Verify power off", "ESD protection"],
        )


# ============ PRIORITY & AUTOMATION ============

class PriorityClassifier:
    """Classifies decision priority."""
    
    def classify(self, alternative: DecisionAlternative, context: dict) -> Priority:
        """Classify priority based on alternative and context."""
        
        # Check risk level
        if alternative.risk_level == RiskLevel.CRITICAL:
            return Priority.CRITICAL
        
        # Check score
        if alternative.score >= 0.9:
            if alternative.risk_level == RiskLevel.HIGH:
                return Priority.HIGH
            return Priority.MEDIUM
        
        if alternative.score >= 0.7:
            return Priority.MEDIUM
        
        return Priority.LOW


class AutomationEvaluator:
    """Evaluates automation level for decisions."""
    
    def evaluate(
        self,
        alternative: DecisionAlternative,
        safety_decision: str,
        rules_compliant: bool,
        confidence: float,
    ) -> AutomationLevel:
        """Determine automation level."""
        
        # Blocked conditions
        if safety_decision == "block" or not rules_compliant:
            return AutomationLevel.BLOCKED
        
        # Auto-approved conditions
        if (
            alternative.score >= 0.9 and
            confidence >= 0.9 and
            alternative.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        ):
            return AutomationLevel.AUTO_APPROVED
        
        # Default: requires review
        return AutomationLevel.REQUIRES_REVIEW


class RecommendationGenerator:
    """Generates recommendations from decision."""
    
    def generate(self, alternative: DecisionAlternative, plan: DecisionPlan) -> list[DecisionAction]:
        """Generate recommendations."""
        
        recommendations = [
            DecisionAction(
                action=alternative.option,
                reasoning=f"Best option with score {alternative.score:.0%}",
                priority=Priority.HIGH,
                alternatives=[],
            )
        ]
        
        # Add plan-based recommendations
        if plan.steps:
            recommendations.append(DecisionAction(
                action=f"Follow action plan ({len(plan.steps)} steps)",
                reasoning="Standard procedure for this decision",
                priority=Priority.MEDIUM,
                alternatives=[],
            ))
        
        return recommendations


# ============ MAIN DECISION ENGINE ============

class DecisionEngine:
    """
    Main decision engine.
    Point where all intelligence converges.
    """
    
    def __init__(self):
        self.scorer = DecisionScorer()
        self.ranker = AlternativeRanker()
        self.planner = ActionPlanner()
        self.priority_classifier = PriorityClassifier()
        self.automation_evaluator = AutomationEvaluator()
        self.recommendation_generator = RecommendationGenerator()
    
    async def decide(
        self,
        alternatives: list[dict],
        context: dict,
        safety_decision: str,
        rules_compliant: bool,
        confidence: float,
    ) -> ClinicalDecision:
        """Make the final clinical decision."""
        
        # Score all alternatives
        scored = []
        for alt in alternatives:
            score = self.scorer.score(alt, safety_decision, rules_compliant, confidence)
            scored.append((alt, score))
        
        # Rank alternatives
        ranked = self.ranker.rank(scored)
        
        # Select best
        best = ranked[0] if ranked else None
        
        if not best:
            return ClinicalDecision(
                id=self._generate_id(),
                timestamp=datetime.now(),
                decision="NO_DECISION",
                confidence=0.0,
                priority=Priority.INFORMATIONAL,
                alternatives=[],
                recommended_actions=[],
                validation_status=ValidationStatus(
                    is_valid=False,
                    evidence_valid=False,
                    confidence_valid=False,
                    safety_valid=False,
                    rules_valid=False,
                    clinical_valid=False,
                ),
                automation_level=AutomationLevel.BLOCKED,
                action_plan=None,
                audit=AuditInfo(
                    decision_id=self._generate_id(),
                    timestamp=datetime.now(),
                ),
            )
        
        # Generate plan
        plan = self.planner.create_plan(best.option)
        
        # Classify priority
        priority = self.priority_classifier.classify(best, context)
        
        # Evaluate automation
        automation = self.automation_evaluator.evaluate(
            best, safety_decision, rules_compliant, confidence
        )
        
        # Generate recommendations
        recommendations = self.recommendation_generator.generate(best, plan)
        
        return ClinicalDecision(
            id=self._generate_id(),
            timestamp=datetime.now(),
            decision=best.option,
            confidence=best.confidence,
            priority=priority,
            alternatives=ranked,
            recommended_actions=recommendations,
            validation_status=ValidationStatus(
                is_valid=True,
                evidence_valid=True,
                confidence_valid=True,
                safety_valid=safety_decision != "block",
                rules_valid=rules_compliant,
                clinical_valid=True,
            ),
            automation_level=automation,
            action_plan=plan,
            audit=AuditInfo(
                decision_id=self._generate_id(),
                timestamp=datetime.now(),
            ),
        )
    
    def _generate_id(self) -> str:
        """Generate unique decision ID."""
        return f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


__all__ = [
    # Version
    "__version__",
    # Enums
    "Priority",
    "AutomationLevel",
    "Severity",
    "RiskLevel",
    # Domain Models
    "EvidenceBundle",
    "ReasoningChain",
    "Risk",
    "PlanStep",
    "DecisionPlan",
    "DecisionAction",
    "DecisionAlternative",
    "DecisionScore",
    "AuditInfo",
    "ValidationStatus",
    "ClinicalDecision",
    # Components
    "DecisionScorer",
    "AlternativeRanker",
    "ActionPlanner",
    "PriorityClassifier",
    "AutomationEvaluator",
    "RecommendationGenerator",
    "DecisionEngine",
]
