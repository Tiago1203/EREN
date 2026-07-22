"""Reasoning engine for EREN core.

Evidence-based, explainable reasoning engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ReasoningStrategy(str, Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "very_high"  # > 0.9
    HIGH = "high"            # > 0.7
    MEDIUM = "medium"        # > 0.5
    LOW = "low"             # > 0.3
    VERY_LOW = "very_low"   # <= 0.3


@dataclass
class Evidence:
    """Represents a piece of evidence for reasoning."""
    id: str
    content: str
    source: str
    source_type: str  # "document", "sensor", "user", "llm"
    timestamp: datetime
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain."""
    step_id: str
    description: str
    strategy: ReasoningStrategy
    evidence_used: list[str]  # Evidence IDs
    inference: str
    confidence: float
    timestamp: datetime


@dataclass
class Conclusion:
    """A conclusion reached through reasoning."""
    statement: str
    confidence: float
    confidence_level: ConfidenceLevel
    supporting_evidence: list[str]
    reasoning_chain: list[ReasoningStep]
    alternative_conclusions: list[str]
    timestamp: datetime


@dataclass
class Explanation:
    """Human-readable explanation of reasoning."""
    summary: str
    chain_description: str
    evidence_summary: str
    confidence_explanation: str
    alternative_explanation: str | None = None


class ReasoningEngine:
    """
    Evidence-based, explainable reasoning engine.

    Applies reasoning strategies over evidence to reach conclusions
    with full auditability and explainability.
    """

    def __init__(self):
        self._evidence_store: dict[str, Evidence] = {}
        self._strategies: dict[ReasoningStrategy, Any] = {}
        self._confidence_threshold = 0.5
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize available reasoning strategies."""
        self._strategies = {
            ReasoningStrategy.DEDUCTIVE: self._deductive_reason,
            ReasoningStrategy.INDUCTIVE: self._inductive_reason,
            ReasoningStrategy.ABDUCTIVE: self._abductive_reason,
            ReasoningStrategy.ANALOGICAL: self._analogical_reason,
            ReasoningStrategy.CAUSAL: self._causal_reason,
        }

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the evidence store."""
        self._evidence_store[evidence.id] = evidence

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        """Retrieve evidence by ID."""
        return self._evidence_store.get(evidence_id)

    def get_evidence_by_source(self, source: str) -> list[Evidence]:
        """Get all evidence from a specific source."""
        return [e for e in self._evidence_store.values() if e.source == source]

    async def reason(
        self,
        question: str,
        evidence_ids: list[str],
        strategy: ReasoningStrategy = ReasoningStrategy.DEDUCTIVE,
        context: dict[str, Any] | None = None,
    ) -> tuple[Conclusion, Explanation]:
        """
        Apply reasoning to reach a conclusion.

        Args:
            question: The question or claim to reason about
            evidence_ids: List of evidence IDs to use
            strategy: The reasoning strategy to apply
            context: Optional context for reasoning

        Returns:
            Tuple of (Conclusion, Explanation)
        """
        # Collect evidence
        evidence_list = [
            self._evidence_store[eid]
            for eid in evidence_ids
            if eid in self._evidence_store
        ]

        if not evidence_list:
            return self._no_evidence_conclusion(question)

        # Apply reasoning strategy
        reasoning_func = self._strategies.get(strategy, self._deductive_reason)
        conclusion = await reasoning_func(question, evidence_list, context or {})

        # Generate explanation
        explanation = self._generate_explanation(question, conclusion, evidence_list)

        return conclusion, explanation

    async def _deductive_reason(
        self,
        question: str,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> Conclusion:
        """Apply deductive reasoning: General → Specific."""
        steps = []

        # Calculate overall confidence from evidence
        confidences = [e.confidence for e in evidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Apply deductive chain
        step = ReasoningStep(
            step_id=f"ded-{datetime.now().timestamp()}",
            description=f"Applying deductive reasoning from {len(evidence)} premises",
            strategy=ReasoningStrategy.DEDUCTIVE,
            evidence_used=[e.id for e in evidence],
            inference=f"Based on {len(evidence)} premises with average confidence {avg_confidence:.2f}",
            confidence=avg_confidence,
            timestamp=datetime.now(),
        )
        steps.append(step)

        # Determine conclusion
        if avg_confidence >= 0.8:
            statement = f"High confidence conclusion for: {question}"
        elif avg_confidence >= 0.5:
            statement = f"Moderate confidence conclusion for: {question}"
        else:
            statement = f"Uncertain conclusion for: {question}"

        return Conclusion(
            statement=statement,
            confidence=avg_confidence,
            confidence_level=self._confidence_to_level(avg_confidence),
            supporting_evidence=[e.id for e in evidence],
            reasoning_chain=steps,
            alternative_conclusions=[],
            timestamp=datetime.now(),
        )

    async def _inductive_reason(
        self,
        question: str,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> Conclusion:
        """Apply inductive reasoning: Specific → General."""
        steps = []

        # Inductive reasoning builds general rules from specific cases
        observation_count = len(evidence)
        consistency = self._calculate_consistency(evidence)

        step = ReasoningStep(
            step_id=f"ind-{datetime.now().timestamp()}",
            description=f"Building generalization from {observation_count} observations",
            strategy=ReasoningStrategy.INDUCTIVE,
            evidence_used=[e.id for e in evidence],
            inference=f"Pattern identified with {consistency:.0%} consistency",
            confidence=consistency * 0.9,  # Inductive is always less certain
            timestamp=datetime.now(),
        )
        steps.append(step)

        confidence = consistency * 0.9

        return Conclusion(
            statement=f"Inductive generalization: {question}",
            confidence=confidence,
            confidence_level=self._confidence_to_level(confidence),
            supporting_evidence=[e.id for e in evidence],
            reasoning_chain=steps,
            alternative_conclusions=[f"Alternative pattern: {q}" for q in ["Possibly different cause", "Consider edge cases"]],
            timestamp=datetime.now(),
        )

    async def _abductive_reason(
        self,
        question: str,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> Conclusion:
        """Apply abductive reasoning: Observation → Best explanation."""
        steps = []

        # Find best explanation for observations
        best_explanation = self._find_best_explanation(evidence, context)

        step = ReasoningStep(
            step_id=f"abd-{datetime.now().timestamp()}",
            description=f"Finding best explanation for {len(evidence)} observations",
            strategy=ReasoningStrategy.ABDUCTIVE,
            evidence_used=[e.id for e in evidence],
            inference=f"Most likely explanation: {best_explanation}",
            confidence=0.7,
            timestamp=datetime.now(),
        )
        steps.append(step)

        return Conclusion(
            statement=f"Most likely explanation: {best_explanation}",
            confidence=0.7,
            confidence_level=ConfidenceLevel.HIGH,
            supporting_evidence=[e.id for e in evidence],
            reasoning_chain=steps,
            alternative_conclusions=["Alternative explanation 1", "Alternative explanation 2"],
            timestamp=datetime.now(),
        )

    async def _analogical_reason(
        self,
        question: str,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> Conclusion:
        """Apply analogical reasoning: Similarity-based."""
        steps = []

        # Find similar past cases
        similar_cases = context.get("similar_cases", [])

        step = ReasoningStep(
            step_id=f"ana-{datetime.now().timestamp()}",
            description=f"Reasoning by analogy from {len(similar_cases)} similar cases",
            strategy=ReasoningStrategy.ANALOGICAL,
            evidence_used=[e.id for e in evidence],
            inference=f"Found {len(similar_cases)} similar past situations",
            confidence=0.65 if similar_cases else 0.4,
            timestamp=datetime.now(),
        )
        steps.append(step)

        return Conclusion(
            statement=f"Based on analogous situations: {question}",
            confidence=0.65 if similar_cases else 0.4,
            confidence_level=ConfidenceLevel.MEDIUM if similar_cases else ConfidenceLevel.LOW,
            supporting_evidence=[e.id for e in evidence],
            reasoning_chain=steps,
            alternative_conclusions=[],
            timestamp=datetime.now(),
        )

    async def _causal_reason(
        self,
        question: str,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> Conclusion:
        """Apply causal reasoning: Cause → Effect."""
        steps = []

        # Identify causal relationships
        causes = context.get("causes", [])
        effects = context.get("effects", [])

        step = ReasoningStep(
            step_id=f"cau-{datetime.now().timestamp()}",
            description=f"Tracing causal chain: {len(causes)} causes → {len(effects)} effects",
            strategy=ReasoningStrategy.CAUSAL,
            evidence_used=[e.id for e in evidence],
            inference=f"Causal relationship identified between causes and effects",
            confidence=0.8,
            timestamp=datetime.now(),
        )
        steps.append(step)

        return Conclusion(
            statement=f"Causal conclusion for: {question}",
            confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            supporting_evidence=[e.id for e in evidence],
            reasoning_chain=steps,
            alternative_conclusions=[],
            timestamp=datetime.now(),
        )

    def _calculate_consistency(self, evidence: list[Evidence]) -> float:
        """Calculate consistency score among evidence."""
        if len(evidence) < 2:
            return 1.0

        # Simple consistency: all evidence agree on key points
        confidences = [e.confidence for e in evidence]
        variance = sum((c - sum(confidences) / len(confidences)) ** 2 for c in confidences) / len(confidences)

        # Low variance = high consistency
        consistency = 1.0 - min(1.0, variance)
        return consistency

    def _find_best_explanation(
        self,
        evidence: list[Evidence],
        context: dict[str, Any],
    ) -> str:
        """Find the best explanation given evidence."""
        hypotheses = context.get("hypotheses", [])

        if not hypotheses:
            return "Insufficient data for explanation"

        # Score hypotheses by evidence support
        scores = {}
        for hyp in hypotheses:
            scores[hyp] = sum(e.confidence for e in evidence if hyp.lower() in e.content.lower())

        if scores:
            return max(scores, key=scores.get)
        return "No clear explanation"

    def _confidence_to_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to confidence level."""
        if confidence > 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence > 0.7:
            return ConfidenceLevel.HIGH
        elif confidence > 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence > 0.3:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW

    def _no_evidence_conclusion(self, question: str) -> tuple[Conclusion, Explanation]:
        """Return a conclusion when no evidence is available."""
        conclusion = Conclusion(
            statement=f"Cannot determine: {question}",
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            supporting_evidence=[],
            reasoning_chain=[],
            alternative_conclusions=[],
            timestamp=datetime.now(),
        )

        explanation = Explanation(
            summary="No evidence available for reasoning",
            chain_description="No reasoning chain could be constructed",
            evidence_summary="No evidence provided",
            confidence_explanation="Zero confidence due to lack of evidence",
            alternative_explanation=None,
        )

        return conclusion, explanation

    def _generate_explanation(
        self,
        question: str,
        conclusion: Conclusion,
        evidence: list[Evidence],
    ) -> Explanation:
        """Generate human-readable explanation."""
        chain_desc = " → ".join([s.description for s in conclusion.reasoning_chain])

        evidence_summary = "\n".join([
            f"- {e.content[:100]}... (confidence: {e.confidence:.2f})"
            for e in evidence[:3]
        ])

        alt_explanation = None
        if conclusion.alternative_conclusions:
            alt_explanation = "Alternative conclusions considered:\n" + "\n".join(
                f"- {alt}" for alt in conclusion.alternative_conclusions[:2]
            )

        return Explanation(
            summary=f"Reasoned about: {question}",
            chain_description=chain_desc or "No reasoning steps",
            evidence_summary=evidence_summary or "No evidence",
            confidence_explanation=f"Confidence: {conclusion.confidence:.2f} ({conclusion.confidence_level.value})",
            alternative_explanation=alt_explanation,
        )

    def get_supported_strategies(self) -> list[ReasoningStrategy]:
        """Get list of supported reasoning strategies."""
        return list(self._strategies.keys())


# Global instance
_engine: ReasoningEngine | None = None


def get_reasoning_engine() -> ReasoningEngine:
    """Get or create the global reasoning engine instance."""
    global _engine
    if _engine is None:
        _engine = ReasoningEngine()
    return _engine
