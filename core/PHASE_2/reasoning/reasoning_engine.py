"""Cognitive Reasoning Engine.

The logical brain of EREN. Transforms evidence into hypotheses
and then into justified decisions.

Architecture only -- no AI, no LLM, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .adapters import ReasoningContextAdapter, ReasoningMemoryAdapter
from .capabilities import get_reasoning_capabilities
from .confidence_model import ConfidenceCalculatorFactory
from .evidence_manager import EvidenceManager
from .hypothesis_manager import HypothesisManager
from .reasoning_chain import ReasoningChainManager
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
    InferenceType,
    ReasoningChain,
    ReasoningMetrics,
    ReasoningStage,
    ReasoningState,
    ReasoningStrategy,
    ReasoningTrace,
    StrategyConfig,
)

# EventBus integration (optional)
try:
    from core.PHASE_1.infrastructure.events import Event, get_global_bus
    _HAS_EVENT_BUS = True
except ImportError:
    _HAS_EVENT_BUS = False

# CapabilityRegistry integration (optional)
try:
    from core.PHASE_2.capabilities import Capability, CapabilityRegistry
    _HAS_CAPABILITIES = True
except ImportError:
    _HAS_CAPABILITIES = False

if TYPE_CHECKING:
    pass


# =============================================================================
# Session (Immutable)
# =============================================================================


@dataclass(frozen=True)
class ReasoningSession:
    """A reasoning session (immutable)."""

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
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


# =============================================================================
# Event Publisher (Uses Global EventBus)
# =============================================================================


class ReasoningEventPublisher:
    """Publishes events to the global EventBus.
    
    CRITICAL: Uses ONLY the global EventBus. No internal bus.
    """

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._enabled = _HAS_EVENT_BUS

    def publish(self, event_type: str, **data: Any) -> None:
        """Publish an event to the global EventBus.
        
        Args:
            event_type: Type of event.
            **data: Event data.
        """
        if not self._enabled:
            return

        try:
            bus = get_global_bus()
            if bus:
                event = Event(
                    event_type=event_type,
                    data=data,
                )
                bus.publish(event)
        except Exception:
            pass

    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False

    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = _HAS_EVENT_BUS


# =============================================================================
# Capability Registration
# =============================================================================


class ReasoningCapabilityRegistrar:
    """Handles automatic capability registration."""

    def __init__(self) -> None:
        """Initialize the registrar."""
        self._registered = False
        self._enabled = _HAS_CAPABILITIES

    def register(self, registry: Any | None = None) -> None:
        """Register reasoning capabilities.
        
        Args:
            registry: Optional CapabilityRegistry instance.
        """
        if not self._enabled or self._registered:
            return

        try:
            if registry is None:
                return

            for cap_def in get_reasoning_capabilities():
                capability = Capability(
                    capability_id=cap_def["id"],
                    name=cap_def["name"],
                    description=cap_def["description"],
                    category=cap_def["category"],
                )
                registry.register(capability)

            self._registered = True
        except Exception:
            pass

    @property
    def is_registered(self) -> bool:
        """Check if capabilities are registered."""
        return self._registered


# =============================================================================
# Main Engine
# =============================================================================


class CognitiveReasoningEngine:
    """The main reasoning engine.

    Transforms evidence into hypotheses and then into justified decisions.
    """

    def __init__(
        self,
        strategy: ReasoningStrategy = ReasoningStrategy.EXHAUSTIVE,
        max_hypotheses: int = 10,
        confidence_algorithm: str = "default",
        context_adapter: ReasoningContextAdapter | None = None,
        memory_adapter: ReasoningMemoryAdapter | None = None,
    ) -> None:
        """Initialize the reasoning engine."""
        # Managers
        self._hypothesis_manager = HypothesisManager(max_hypotheses=max_hypotheses)
        self._evidence_manager = EvidenceManager()
        self._chain_manager = ReasoningChainManager()
        self._trace_builder = ReasoningTraceBuilder()
        self._strategy_executor = ReasoningStrategyExecutor()
        self._metrics_collector = ReasoningMetricsCollector()

        # Event publisher (uses global EventBus)
        self._event_publisher = ReasoningEventPublisher()

        # Capability registrar
        self._capability_registrar = ReasoningCapabilityRegistrar()

        # Configuration
        self._strategy_config = StrategyConfig(
            strategy=strategy,
            max_hypotheses=max_hypotheses,
        )
        self._confidence_algorithm = confidence_algorithm

        # Adapters
        self._context_adapter = context_adapter or ReasoningContextAdapter()
        self._memory_adapter = memory_adapter or ReasoningMemoryAdapter()

        # Session state
        self._session: ReasoningSession | None = None
        self._decisions: dict[str, Decision] = {}
        self._lock = threading.RLock()

    def register_capabilities(self, registry: Any | None = None) -> None:
        """Register reasoning capabilities to the Capability Registry."""
        self._capability_registrar.register(registry)

    @property
    def capabilities_registered(self) -> bool:
        """Check if capabilities are registered."""
        return self._capability_registrar.is_registered

    def start_session(
        self,
        session_id: str = "",
        context: dict | None = None,
    ) -> ReasoningSession:
        """Start a new reasoning session."""
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:16]}"

        session = ReasoningSession(
            session_id=session_id,
            started_at=datetime.now(UTC).isoformat(),
            stage=ReasoningStage.INITIAL,
        )

        with self._lock:
            self._session = session
            self._decisions = {}

            self._hypothesis_manager = HypothesisManager(
                max_hypotheses=self._strategy_config.max_hypotheses
            )
            self._evidence_manager = EvidenceManager()
            self._chain_manager = ReasoningChainManager()
            self._trace_builder = ReasoningTraceBuilder(session_id)
            self._metrics_collector = ReasoningMetricsCollector(session_id)

            session_with_state = ReasoningSession(
                session_id=session_id,
                created_at=session.created_at,
                started_at=session.started_at,
                stage=ReasoningStage.INITIAL,
                state=ReasoningState(
                    session_id=session_id,
                    started_at=session.started_at,
                ),
            )
            self._session = session_with_state

            if context:
                self._trace_builder.add_metadata("context", context)

        self._publish("session_started", session_id=session_id)

        return self._session

    def end_session(self) -> ReasoningSession | None:
        """End the current session."""
        with self._lock:
            if not self._session:
                return None

            session = self._session
            completed_session = ReasoningSession(
                session_id=session.session_id,
                created_at=session.created_at,
                started_at=session.started_at,
                completed_at=datetime.now(UTC).isoformat(),
                stage=ReasoningStage.COMPLETED,
                state=session.state,
                trace=self._trace_builder.build(),
            )

            self._session = completed_session

        self._publish("session_completed", session_id=completed_session.session_id)

        return completed_session

    def get_session(self) -> ReasoningSession | None:
        """Get the current session."""
        return self._session

    def _publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish an event to the global EventBus."""
        self._event_publisher.publish(event_type, **kwargs)

    def generate_hypotheses(
        self,
        descriptions: list[str],
        initial_probabilities: list[float] | None = None,
        tags: tuple[str, ...] | None = None,
    ) -> list[Hypothesis]:
        """Generate hypotheses from descriptions."""
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

        self._update_state()

        return hypotheses

    def update_hypothesis(
        self,
        hypothesis_id: str,
        confidence: ConfidenceScore,
    ) -> Hypothesis | None:
        """Update hypothesis confidence."""
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
        """Rank all active hypotheses."""
        ranked = self._hypothesis_manager.rank_hypotheses()

        self._trace_builder.add_event(
            "hypotheses_ranked",
            count=len(ranked),
            best_id=ranked[0].hypothesis_id if ranked else None,
        )

        self._update_state()

        return ranked

    def get_best_hypothesis(self) -> Hypothesis | None:
        """Get the highest ranked hypothesis."""
        return self._hypothesis_manager.get_best()

    def confirm_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Mark a hypothesis as confirmed."""
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
        """Mark a hypothesis as rejected."""
        hyp = self._hypothesis_manager.reject(hypothesis_id)
        if hyp:
            self._trace_builder.add_event(
                "hypothesis_rejected",
                hypothesis_id=hypothesis_id,
            )
            self._publish("hypothesis_rejected", hypothesis_id=hypothesis_id)
            self._update_state()

        return hyp

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        content: str | dict,
        source: EvidenceSource,
        confidence: float = 0.5,
        hypothesis_id: str = "",
        relation: EvidenceRelation = EvidenceRelation.NEUTRAL,
    ) -> Evidence:
        """Add evidence to the reasoning process."""
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

        if hypothesis_id:
            self._relate_evidence_to_hypothesis(evidence, hypothesis_id, relation)

        self._update_state()

        return evidence

    def add_observation(self, observation: str) -> Evidence:
        """Add evidence from user observation."""
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
        """Add evidence from measurement."""
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
        """Incorporate evidence into hypothesis evaluation."""
        self._evidence_manager.set_relation(evidence_id, hypothesis_id, relation)

        hyp = self._hypothesis_manager.add_evidence(
            hypothesis_id, evidence_id, relation
        )

        if hyp:
            self._recalculate_hypothesis_confidence(hyp)

            self._trace_builder.add_event(
                "evidence_incorporated",
                evidence_id=evidence_id,
                hypothesis_id=hypothesis_id,
                relation=relation.value,
            )

        self._update_state()

        return hyp

    def make_decision(
        self,
        decision_type: DecisionType,
        based_on_hypothesis_id: str,
        justification: list[str],
    ) -> Decision:
        """Generate a decision based on reasoning."""
        if not self._session:
            raise RuntimeError("No active session")

        self._transition_to(ReasoningStage.DECISION_MAKING)

        hypothesis = self._hypothesis_manager.get(based_on_hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {based_on_hypothesis_id} not found")

        alternatives = [
            h.hypothesis_id
            for h in self._hypothesis_manager.get_active()
            if h.hypothesis_id != based_on_hypothesis_id
        ]

        confidence = ConfidenceScore(
            value=hypothesis.confidence_score * hypothesis.probability,
            reasons=(
                f"Based on hypothesis: {hypothesis.description}",
                f"Hypothesis confidence: {hypothesis.confidence_score:.2f}",
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

        if self._session and self._session.state:
            self._session.state.decisions_count = len(self._decisions)

        return decision

    def get_decision(self, decision_id: str) -> Decision | None:
        """Get a decision by ID."""
        return self._decisions.get(decision_id)

    def get_all_decisions(self) -> list[Decision]:
        """Get all decisions."""
        return list(self._decisions.values())

    def build_reasoning_chain(
        self,
        hypothesis_id: str,
        inference_type: InferenceType = InferenceType.ABDUCTIVE,
    ) -> ReasoningChain:
        """Build a reasoning chain for a hypothesis."""
        hypothesis = self._hypothesis_manager.get(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        chain = self._chain_manager.build_chain(
            hypothesis_id=hypothesis_id,
            evidence_ids=list(hypothesis.supporting_evidence) + list(hypothesis.contradicting_evidence),
            inference_type=inference_type,
        )

        self._trace_builder.add_chain(chain)
        self._publish("chain_built", hypothesis_id=hypothesis_id)

        return chain

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

    def _transition_to(self, stage: ReasoningStage) -> None:
        """Transition to a new reasoning stage."""
        if self._session and self._session.state:
            new_state = ReasoningState(
                session_id=self._session.state.session_id,
                stage=stage,
                active_hypotheses=self._session.state.active_hypotheses,
                total_hypotheses=self._session.state.total_hypotheses,
                active_evidence=self._session.state.active_evidence,
                total_evidence=self._session.state.total_evidence,
                best_hypothesis_id=self._session.state.best_hypothesis_id,
                best_hypothesis_confidence=self._session.state.best_hypothesis_confidence,
                decisions_count=self._session.state.decisions_count,
                reasoning_steps=self._session.state.reasoning_steps,
                started_at=self._session.state.started_at,
                updated_at=datetime.now(UTC).isoformat(),
            )

            self._trace_builder.add_event(
                "stage_changed",
                previous_stage=self._session.stage,
                new_stage=stage,
            )

            self._session = ReasoningSession(
                session_id=self._session.session_id,
                created_at=self._session.created_at,
                started_at=self._session.started_at,
                completed_at=self._session.completed_at,
                stage=stage,
                state=new_state,
                trace=self._session.trace,
            )

    def _update_state(self) -> None:
        """Update session state."""
        if not self._session or not self._session.state:
            return

        state = self._session.state
        new_state = ReasoningState(
            session_id=state.session_id,
            stage=state.stage,
            active_hypotheses=len(self._hypothesis_manager.get_active()),
            total_hypotheses=len(self._hypothesis_manager.get_all()),
            active_evidence=len(self._evidence_manager.get_all()),
            total_evidence=state.total_evidence,
            best_hypothesis_id=self._hypothesis_manager.get_best().hypothesis_id if self._hypothesis_manager.get_best() else "",
            best_hypothesis_confidence=self._hypothesis_manager.get_best().confidence_score if self._hypothesis_manager.get_best() else 0.0,
            decisions_count=len(self._decisions),
            reasoning_steps=self._chain_manager.get_step_count(),
            started_at=state.started_at,
            updated_at=datetime.now(UTC).isoformat(),
        )

        self._session = ReasoningSession(
            session_id=self._session.session_id,
            created_at=self._session.created_at,
            started_at=self._session.started_at,
            completed_at=self._session.completed_at,
            stage=self._session.stage,
            state=new_state,
            trace=self._session.trace,
        )

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

        hyp = self._hypothesis_manager.get(hypothesis_id)
        if hyp:
            self._recalculate_hypothesis_confidence(hyp)

    def _recalculate_hypothesis_confidence(self, hypothesis: Hypothesis) -> None:
        """Recalculate hypothesis confidence."""
        supporting, contradicting = self._hypothesis_manager.get_evidence_for(hypothesis.hypothesis_id)

        supporting_ev = [self._evidence_manager.get(e) for e in supporting]
        contradicting_ev = [self._evidence_manager.get(e) for e in contradicting]
        supporting_ev = [e for e in supporting_ev if e]
        contradicting_ev = [e for e in contradicting_ev if e]

        calculator = ConfidenceCalculatorFactory.create(self._confidence_algorithm)
        new_confidence = calculator.calculate(
            hypothesis=hypothesis,
            supporting_evidence=supporting_ev,
            contradicting_evidence=contradicting_ev,
        )

        self._hypothesis_manager.update_confidence(hypothesis.hypothesis_id, new_confidence)
