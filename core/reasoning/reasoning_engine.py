"""Cognitive Reasoning Engine.

The logical brain of EREN. Transforms evidence into hypotheses
and then into justified decisions.

Architecture only — no AI, no LLM, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable

from .confidence_model import ConfidenceCalculatorFactory
from .evidence_manager import EvidenceManager
from .hypothesis_manager import HypothesisManager
from .reasoning_chain import ReasoningChainBuilder, ReasoningChainManager
from .reasoning_events import ReasoningEventPublisher
from .reasoning_metrics import ReasoningMetricsCollector
from .reasoning_strategy import ReasoningStrategyExecutor
from .reasoning_trace import ReasoningTraceBuilder
from .reasoning_types import (
    ConfidenceScore,
    Decision,
    DecisionStatus,
    DecisionType,
    Evidence,
    EvidenceRelation,
    EvidenceSource,
    EvidenceType,
    Hypothesis,
    HypothesisStatus,
    InferenceType,
    ReasoningChain,
    ReasoningMetrics,
    ReasoningStage,
    ReasoningState,
    ReasoningStrategy,
    ReasoningTrace,
    StrategyConfig,
)

if TYPE_CHECKING:
    pass


@dataclass
class ReasoningSession:
    """A reasoning session."""

    session_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    stage: ReasoningStage = ReasoningStage.INITIAL
    state: ReasoningState | None = None
    trace: ReasoningTrace | None = None

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(timezone.utc).isoformat())


class CognitiveReasoningEngine:
    """The main reasoning engine.

    Transforms evidence into hypotheses and then into justified decisions.

    Responsibilities:
    - Generate and maintain hypotheses
    - Collect and analyze evidence
    - Calculate confidence scores
    - Build reasoning chains
    - Generate decisions
    - Maintain complete trace
    - Publish events
    """

    def __init__(
        self,
        strategy: ReasoningStrategy = ReasoningStrategy.EXHAUSTIVE,
        max_hypotheses: int = 10,
        confidence_algorithm: str = "default",
    ) -> None:
        """Initialize the reasoning engine.

        Args:
            strategy: Reasoning strategy.
            max_hypotheses: Maximum hypotheses to maintain.
            confidence_algorithm: Algorithm for confidence calculation.
        """
        # Managers
        self._hypothesis_manager = HypothesisManager(max_hypotheses=max_hypotheses)
        self._evidence_manager = EvidenceManager()
        self._chain_manager = ReasoningChainManager()
        self._trace_builder = ReasoningTraceBuilder()
        self._strategy_executor = ReasoningStrategyExecutor()
        self._metrics_collector = ReasoningMetricsCollector()
        self._event_publisher = ReasoningEventPublisher()

        # Configuration
        self._strategy_config = StrategyConfig(
            strategy=strategy,
            max_hypotheses=max_hypotheses,
        )
        self._confidence_algorithm = confidence_algorithm

        # Session state
        self._session: ReasoningSession | None = None
        self._decisions: dict[str, Decision] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Session Management
    # =========================================================================

    def start_session(
        self,
        session_id: str = "",
        context: dict | None = None,
    ) -> ReasoningSession:
        """Start a new reasoning session.

        Args:
            session_id: Optional session ID.
            context: Optional context data.

        Returns:
            The created session.
        """
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:16]}"

        session = ReasoningSession(
            session_id=session_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            stage=ReasoningStage.INITIAL,
        )

        with self._lock:
            self._session = session
            self._decisions = {}

            # Reset managers
            self._hypothesis_manager = HypothesisManager(
                max_hypotheses=self._strategy_config.max_hypotheses
            )
            self._evidence_manager = EvidenceManager()
            self._chain_manager = ReasoningChainManager()
            self._trace_builder = ReasoningTraceBuilder(session_id)
            self._metrics_collector = ReasoningMetricsCollector(session_id)

            # Initialize state
            session.state = ReasoningState(
                session_id=session_id,
                stage=ReasoningStage.INITIAL,
                started_at=session.started_at,
            )

            # Add context to trace
            if context:
                self._trace_builder.add_metadata("context", context)

        self._publish("session_started", session_id=session_id)

        return session

    def end_session(self) -> ReasoningSession | None:
        """End the current session.

        Returns:
            The completed session.
        """
        with self._lock:
            if not self._session:
                return None

            session = self._session
            session.completed_at = datetime.now(timezone.utc).isoformat()
            session.stage = ReasoningStage.COMPLETED

            if session.state:
                session.state.stage = ReasoningStage.COMPLETED

            session.trace = self._trace_builder.build()

            # Collect final metrics
            metrics = self._metrics_collector.calculate()
            session.trace.metadata["metrics"] = metrics

        self._publish("session_completed", session_id=session.session_id)

        return session

    def get_session(self) -> ReasoningSession | None:
        """Get the current session."""
        return self._session

    # =========================================================================
    # Hypothesis Management
    # =========================================================================

    def generate_hypotheses(
        self,
        descriptions: list[str],
        initial_probabilities: list[float] | None = None,
        tags: tuple[str, ...] | None = None,
    ) -> list[Hypothesis]:
        """Generate hypotheses from descriptions.

        Args:
            descriptions: List of hypothesis descriptions.
            initial_probabilities: Optional initial probabilities.
            tags: Optional tags for all hypotheses.

        Returns:
            List of created hypotheses.
        """
        if not self._session:
            raise RuntimeError("No active session")

        self._transition_to(ReasoningStage.HYPOTHESIS_GENERATION)

        hypotheses = []
        for i, description in enumerate(descriptions):
            prob = (
                initial_probabilities[i]
                if initial_probabilities and i < len(initial_probabilities)
                else 1.0 / len(descriptions)
            )

            hyp = self._hypothesis_manager.create(
                description=description,
                initial_probability=prob,
                tags=tags,
            )

            hypotheses.append(hyp)
            self._trace_builder.add_hypothesis(hyp)
            self._publish("hypothesis_created", hypothesis_id=hyp.hypothesis_id)

        # Update state
        self._update_state()

        return hypotheses

    def update_hypothesis(
        self,
        hypothesis_id: str,
        confidence: ConfidenceScore,
    ) -> Hypothesis | None:
        """Update hypothesis confidence.

        Args:
            hypothesis_id: The hypothesis ID.
            confidence: New confidence score.

        Returns:
            Updated hypothesis.
        """
        hyp = self._hypothesis_manager.update_confidence(hypothesis_id, confidence)
        if hyp:
            self._trace_builder.add_event(
                "hypothesis_confidence_updated",
                hypothesis_id=hypothesis_id,
                confidence=confidence.value,
            )
            self._publish("confidence_updated", hypothesis_id=hypothesis_id)
            self._update_state()

        return hyp

    def rank_hypotheses(self) -> list[Hypothesis]:
        """Rank all active hypotheses.

        Returns:
            Ranked list of hypotheses.
        """
        ranked = self._hypothesis_manager.rank_hypotheses()

        self._trace_builder.add_event(
            "hypotheses_ranked",
            count=len(ranked),
            best_id=ranked[0].hypothesis_id if ranked else None,
        )

        self._update_state()

        return ranked

    def get_best_hypothesis(self) -> Hypothesis | None:
        """Get the highest ranked hypothesis.

        Returns:
            The best hypothesis or None.
        """
        return self._hypothesis_manager.get_best()

    def confirm_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Mark a hypothesis as confirmed.

        Args:
            hypothesis_id: The hypothesis ID.

        Returns:
            Updated hypothesis.
        """
        hyp = self._hypothesis_manager.confirm(hypothesis_id)
        if hyp:
            self._trace_builder.add_event(
                "hypothesis_confirmed",
                hypothesis_id=hypothesis_id,
            )
            self._publish("hypothesis_confirmed", hypothesis_id=hypothesis_id)
            self._update_state()

        return hyp

    def reject_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Mark a hypothesis as rejected.

        Args:
            hypothesis_id: The hypothesis ID.

        Returns:
            Updated hypothesis.
        """
        hyp = self._hypothesis_manager.reject(hypothesis_id)
        if hyp:
            self._trace_builder.add_event(
                "hypothesis_rejected",
                hypothesis_id=hypothesis_id,
            )
            self._publish("hypothesis_rejected", hypothesis_id=hypothesis_id)
            self._update_state()

        return hyp

    # =========================================================================
    # Evidence Management
    # =========================================================================

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        content: str | dict,
        source: EvidenceSource,
        confidence: float = 0.5,
        hypothesis_id: str = "",
        relation: EvidenceRelation = EvidenceRelation.NEUTRAL,
    ) -> Evidence:
        """Add evidence to the reasoning process.

        Args:
            evidence_type: Type of evidence.
            content: Evidence content.
            source: Evidence source.
            confidence: Evidence confidence.
            hypothesis_id: Optional hypothesis to relate.
            relation: Relation to hypothesis.

        Returns:
            The added evidence.
        """
        if not self._session:
            raise RuntimeError("No active session")

        self._transition_to(ReasoningStage.EVIDENCE_COLLECTION)

        evidence = self._evidence_manager.add(
            evidence_type=evidence_type,
            source=source,
            content=content,
            confidence=confidence,
            hypothesis_id=hypothesis_id,
            relation=relation,
        )

        self._trace_builder.add_evidence(evidence)
        self._publish("evidence_added", evidence_id=evidence.evidence_id)

        # If relates to hypothesis, update hypothesis
        if hypothesis_id:
            self._relate_evidence_to_hypothesis(evidence, hypothesis_id, relation)

        self._update_state()

        return evidence

    def add_observation(self, observation: str) -> Evidence:
        """Add evidence from user observation.

        Args:
            observation: The observation text.

        Returns:
            The added evidence.
        """
        return self.add_evidence(
            evidence_type=EvidenceType.OBSERVATION,
            content=observation,
            source=EvidenceSource.USER,
            confidence=0.8,
        )

    def add_measurement(
        self,
        value: float,
        unit: str,
        normal_range: tuple[float, float] | None = None,
    ) -> Evidence:
        """Add evidence from measurement.

        Args:
            value: The measurement value.
            unit: Unit of measurement.
            normal_range: Normal range.

        Returns:
            The added evidence.
        """
        return self.add_evidence(
            evidence_type=EvidenceType.MEASUREMENT,
            content={"value": value, "unit": unit, "normal_range": normal_range},
            source=EvidenceSource.SENSOR,
            confidence=0.95,
        )

    def incorporate_evidence(
        self,
        evidence_id: str,
        hypothesis_id: str,
        relation: EvidenceRelation,
    ) -> Hypothesis | None:
        """Incorporate evidence into hypothesis evaluation.

        Args:
            evidence_id: The evidence ID.
            hypothesis_id: The hypothesis ID.
            relation: How evidence relates.

        Returns:
            Updated hypothesis.
        """
        # Add relation
        self._evidence_manager.set_relation(evidence_id, hypothesis_id, relation)

        # Update hypothesis
        hyp = self._hypothesis_manager.add_evidence(
            hypothesis_id, evidence_id, relation
        )

        if hyp:
            # Recalculate confidence
            self._recalculate_hypothesis_confidence(hyp)

            self._trace_builder.add_event(
                "evidence_incorporated",
                evidence_id=evidence_id,
                hypothesis_id=hypothesis_id,
                relation=relation.value,
            )

        self._update_state()

        return hyp

    # =========================================================================
    # Decision Making
    # =========================================================================

    def make_decision(
        self,
        decision_type: DecisionType,
        based_on_hypothesis_id: str,
        justification: list[str],
    ) -> Decision:
        """Generate a decision based on reasoning.

        Args:
            decision_type: Type of decision.
            based_on_hypothesis_id: Hypothesis the decision is based on.
            justification: Justification text.

        Returns:
            The generated decision.
        """
        if not self._session:
            raise RuntimeError("No active session")

        self._transition_to(ReasoningStage.DECISION_MAKING)

        # Get hypothesis
        hypothesis = self._hypothesis_manager.get(based_on_hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {based_on_hypothesis_id} not found")

        # Get alternatives
        alternatives = [
            h.hypothesis_id
            for h in self._hypothesis_manager.get_active()
            if h.hypothesis_id != based_on_hypothesis_id
        ]

        # Calculate decision confidence
        confidence = ConfidenceScore(
            value=hypothesis.confidence_score * hypothesis.probability,
            level=self._level_from_prob(hypothesis.confidence_score * hypothesis.probability),
            reasons=(
                f"Based on hypothesis: {hypothesis.description}",
                f"Hypothesis confidence: {hypothesis.confidence_score:.2f}",
                f"Probability: {hypothesis.probability:.2f}",
            ),
        )

        decision = Decision(
            decision_id=f"dec_{uuid.uuid4().hex[:16]}",
            decision_type=decision_type,
            description=f"Decision based on: {hypothesis.description}",
            status=DecisionStatus.PROPOSED,
            based_on_hypothesis=based_on_hypothesis_id,
            confidence=confidence,
            justification=tuple(justification),
            alternatives=tuple(alternatives),
            selected_reason=f"Highest ranked hypothesis (confidence: {hypothesis.confidence_score:.2f})",
        )

        with self._lock:
            self._decisions[decision.decision_id] = decision

        self._trace_builder.add_decision(decision)
        self._publish("decision_generated", decision_id=decision.decision_id)

        # Update state
        if self._session.state:
            self._session.state.decisions_count = len(self._decisions)

        return decision

    def get_decision(self, decision_id: str) -> Decision | None:
        """Get a decision by ID."""
        return self._decisions.get(decision_id)

    def get_all_decisions(self) -> list[Decision]:
        """Get all decisions."""
        return list(self._decisions.values())

    # =========================================================================
    # Reasoning Chains
    # =========================================================================

    def build_reasoning_chain(
        self,
        hypothesis_id: str,
        inference_type: InferenceType = InferenceType.ABDUCTIVE,
    ) -> ReasoningChain:
        """Build a reasoning chain for a hypothesis.

        Args:
            hypothesis_id: The hypothesis ID.
            inference_type: Type of inference.

        Returns:
            The built reasoning chain.
        """
        hypothesis = self._hypothesis_manager.get(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        # Build chain
        chain = self._chain_manager.build_chain(
            hypothesis_id=hypothesis_id,
            evidence_ids=list(hypothesis.supporting_evidence) + list(hypothesis.contradicting_evidence),
            inference_type=inference_type,
        )

        self._trace_builder.add_chain(chain)
        self._publish("chain_built", hypothesis_id=hypothesis_id)

        return chain

    # =========================================================================
    # Trace and Metrics
    # =========================================================================

    def get_trace(self) -> ReasoningTrace | None:
        """Get the reasoning trace."""
        if self._session:
            return self._trace_builder.build()
        return None

    def get_metrics(self) -> ReasoningMetrics | None:
        """Get reasoning metrics."""
        if self._session:
            return self._metrics_collector.calculate()
        return None

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _transition_to(self, stage: ReasoningStage) -> None:
        """Transition to a new reasoning stage."""
        if self._session and self._session.state:
            self._session.state.stage = stage
            self._trace_builder.add_event("stage_changed", previous_stage=self._session.stage, new_stage=stage)
            self._session.stage = stage

    def _update_state(self) -> None:
        """Update session state."""
        if not self._session or not self._session.state:
            return

        state = self._session.state
        state.active_hypotheses = len(self._hypothesis_manager.get_active())
        state.total_hypotheses = len(self._hypothesis_manager.get_all())
        state.active_evidence = len(self._evidence_manager.get_all())
        state.total_evidence = state.active_evidence

        best = self._hypothesis_manager.get_best()
        if best:
            state.best_hypothesis_id = best.hypothesis_id
            state.best_hypothesis_confidence = best.confidence_score

        state.reasoning_steps = self._chain_manager.get_step_count()
        state.decisions_count = len(self._decisions)
        state.updated_at = datetime.now(timezone.utc).isoformat()

    def _relate_evidence_to_hypothesis(
        self,
        evidence: Evidence,
        hypothesis_id: str,
        relation: EvidenceRelation,
    ) -> None:
        """Relate evidence to hypothesis and recalculate."""
        self._hypothesis_manager.add_evidence(
            hypothesis_id=hypothesis_id,
            evidence_id=evidence.evidence_id,
            relation=relation,
        )

        # Recalculate confidence
        hyp = self._hypothesis_manager.get(hypothesis_id)
        if hyp:
            self._recalculate_hypothesis_confidence(hyp)

    def _recalculate_hypothesis_confidence(self, hypothesis: Hypothesis) -> None:
        """Recalculate hypothesis confidence."""
        supporting, contradicting = self._hypothesis_manager.get_evidence_for(hypothesis.hypothesis_id)

        # Get evidence objects
        supporting_ev = [self._evidence_manager.get(e) for e in supporting]
        contradicting_ev = [self._evidence_manager.get(e) for e in contradicting]
        supporting_ev = [e for e in supporting_ev if e]
        contradicting_ev = [e for e in contradicting_ev if e]

        # Calculate new confidence
        calculator = ConfidenceCalculatorFactory.create(self._confidence_algorithm)
        new_confidence = calculator.calculate(
            hypothesis=hypothesis,
            supporting_evidence=supporting_ev,
            contradicting_evidence=contradicting_ev,
        )

        # Update hypothesis
        self._hypothesis_manager.update_confidence(hypothesis.hypothesis_id, new_confidence)

    def _publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish a reasoning event."""
        self._event_publisher.publish(event_type, session_id=self._session.session_id if self._session else "", **kwargs)

    @staticmethod
    def _level_from_prob(prob: float) -> ConfidenceScore:
        """Get confidence level from probability."""
        if prob >= 0.95:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=6).level)
        elif prob >= 0.8:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=5).level)
        elif prob >= 0.6:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=4).level)
        elif prob >= 0.4:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=3).level)
        elif prob >= 0.2:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=2).level)
        else:
            return ConfidenceScore(value=prob, level=ConfidenceScore(level=1).level)
