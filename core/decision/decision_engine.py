"""Cognitive Decision Engine.

The decision component of EREN. Transforms hypotheses and evidence
into structured decisions.

Philosophy:
- Reasoning = Think
- Decision = Decide

The Decision Engine does NOT:
- Reason (that's the Reasoning Engine)
- Execute tools (that's the Tool Engine)
- Respond to users (that's the Voice Engine)

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .decision_evaluator import DecisionEvaluatorComponent
from .decision_metrics import DecisionMetricsCollector
from .decision_policies import ConservativePolicy, DecisionPolicyComponent
from .decision_strategy import DecisionStrategy, BalancedStrategy
from .decision_trace import DecisionTraceBuilder
from .decision_types import (
    Decision,
    DecisionCandidate,
    DecisionCategory,
    DecisionContext,
    DecisionPriority,
    DecisionStatus,
    DecisionStrategyType,
    DecisionType,
    RiskLevel,
)

# EventBus integration (optional)
try:
    from core.events import get_global_bus, Event
    _HAS_EVENT_BUS = True
except ImportError:
    _HAS_EVENT_BUS = False

# CapabilityRegistry integration (optional)
try:
    from core.capabilities import Capability, CapabilityRegistry
    _HAS_CAPABILITIES = True
except ImportError:
    _HAS_CAPABILITIES = False

if TYPE_CHECKING:
    pass


# =============================================================================
# Capability Registration
# =============================================================================


class DecisionCapabilityRegistrar:
    """Handles automatic capability registration for decisions."""

    def __init__(self) -> None:
        """Initialize the registrar."""
        self._registered = False
        self._enabled = _HAS_CAPABILITIES

    def register(self, registry: Any | None = None) -> None:
        """Register decision capabilities."""
        if not self._enabled or self._registered:
            return

        try:
            if registry is None:
                return

            capabilities = [
                ("decision.evaluate", "Decision Evaluation", "Evaluate decision candidates"),
                ("decision.select", "Decision Selection", "Select best decision"),
                ("decision.prioritize", "Decision Prioritization", "Prioritize decisions"),
                ("decision.escalate", "Escalate Decision", "Escalate to human"),
                ("decision.stop", "Stop Decision", "Stop decision process"),
                ("decision.workflow", "Decision Workflow", "Create workflow from decision"),
            ]

            for cap_id, name, desc in capabilities:
                capability = Capability(
                    capability_id=cap_id,
                    name=name,
                    description=desc,
                    category="decision",
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
# Event Publisher (Uses Global EventBus)
# =============================================================================


class DecisionEventPublisher:
    """Publishes events to the global EventBus."""

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._enabled = _HAS_EVENT_BUS

    def publish(self, event_type: str, **data: Any) -> None:
        """Publish an event to the global EventBus."""
        if not self._enabled:
            return

        try:
            bus = get_global_bus()
            if bus:
                event = Event(event_type=event_type, data=data)
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
# Main Decision Engine
# =============================================================================


class CognitiveDecisionEngine:
    """The main decision engine.

    Responsibilities:
    - Create decision candidates from reasoning results
    - Evaluate and rank candidates
    - Select the best decision
    - Apply decision policies
    - Handle escalation to humans
    - Maintain decision traces
    - Publish decision events

    The engine does NOT:
    - Reason (use ReasoningEngine)
    - Execute tools (use ToolEngine)
    - Respond to users (use VoiceEngine)
    """

    def __init__(
        self,
        strategy: DecisionStrategyType = DecisionStrategyType.BALANCED,
        require_human_approval: bool = False,
    ) -> None:
        """Initialize the decision engine.

        Args:
            strategy: Decision strategy to use.
            require_human_approval: Whether to require human approval.
        """
        # Core components
        self._evaluator = DecisionEvaluatorComponent()
        self._policy = ConservativePolicy()
        self._strategy = self._create_strategy(strategy)

        # Trace and metrics
        self._trace_builder = DecisionTraceBuilder()
        self._metrics = DecisionMetricsCollector()

        # Event publisher
        self._event_publisher = DecisionEventPublisher()

        # Capability registrar
        self._capability_registrar = DecisionCapabilityRegistrar()

        # State
        self._decisions: dict[str, Decision] = {}
        self._candidates: dict[str, DecisionCandidate] = {}
        self._require_human_approval = require_human_approval
        self._lock = threading.RLock()

    def _create_strategy(self, strategy_type: DecisionStrategyType) -> DecisionStrategy:
        """Create a decision strategy."""
        strategies = {
            DecisionStrategyType.CONSERVATIVE: BalancedStrategy(),
            DecisionStrategyType.SAFETY_FIRST: BalancedStrategy(),
            DecisionStrategyType.EFFICIENCY: BalancedStrategy(),
            DecisionStrategyType.SPEED: BalancedStrategy(),
            DecisionStrategyType.BALANCED: BalancedStrategy(),
            DecisionStrategyType.CONFIDENCE_BASED: BalancedStrategy(),
            DecisionStrategyType.HUMAN_IN_LOOP: BalancedStrategy(),
            DecisionStrategyType.FULLY_AUTOMATED: BalancedStrategy(),
        }
        return strategies.get(strategy_type, BalancedStrategy())

    # =========================================================================
    # Capability Registration
    # =========================================================================

    def register_capabilities(self, registry: Any | None = None) -> None:
        """Register decision capabilities to the Capability Registry."""
        self._capability_registrar.register(registry)

    @property
    def capabilities_registered(self) -> bool:
        """Check if capabilities are registered."""
        return self._capability_registrar.is_registered

    # =========================================================================
    # Candidate Creation
    # =========================================================================

    def create_candidate(
        self,
        decision_type: DecisionType,
        description: str,
        based_on_hypothesis: str = "",
        based_on_evidence: list[str] | None = None,
        confidence: float = 0.5,
        metadata: dict | None = None,
    ) -> DecisionCandidate:
        """Create a decision candidate.

        Args:
            decision_type: Type of decision.
            description: Human-readable description.
            based_on_hypothesis: Hypothesis this decision is based on.
            based_on_evidence: Evidence supporting this decision.
            confidence: Confidence level (0.0 to 1.0).
            metadata: Additional metadata.

        Returns:
            The created candidate.
        """
        from .decision_types import DECISION_CATEGORY_MAP, DECISION_PRIORITY_MAP, DECISION_RISK_MAP

        candidate = DecisionCandidate(
            candidate_id=f"cand_{uuid.uuid4().hex[:16]}",
            decision_type=decision_type,
            description=description,
            category=DECISION_CATEGORY_MAP.get(decision_type, DecisionCategory.ACTION),
            priority=DECISION_PRIORITY_MAP.get(decision_type, DecisionPriority.MEDIUM),
            confidence=confidence,
            risk_level=DECISION_RISK_MAP.get(decision_type, RiskLevel.MEDIUM),
            risk_score=0.5,
            based_on_hypothesis=based_on_hypothesis,
            based_on_evidence=tuple(based_on_evidence or []),
            metadata=metadata or {},
        )

        with self._lock:
            self._candidates[candidate.candidate_id] = candidate

        self._publish("DecisionCreated", candidate_id=candidate.candidate_id)

        return candidate

    def create_candidates_from_reasoning(
        self,
        hypothesis_id: str,
        hypothesis_confidence: float,
        context: DecisionContext,
    ) -> list[DecisionCandidate]:
        """Create decision candidates from reasoning results.

        Args:
            hypothesis_id: The hypothesis ID.
            hypothesis_confidence: Confidence in the hypothesis.
            context: Decision context.

        Returns:
            List of decision candidates.
        """
        candidates = []

        # High confidence hypothesis -> Continue or Execute
        if hypothesis_confidence >= 0.8:
            candidates.append(
                self.create_candidate(
                    decision_type=DecisionType.CONTINUE_ANALYSIS,
                    description=f"Continue analysis with confidence {hypothesis_confidence:.2f}",
                    based_on_hypothesis=hypothesis_id,
                    confidence=hypothesis_confidence,
                )
            )

        # Medium confidence -> Consult Knowledge
        elif hypothesis_confidence >= 0.5:
            candidates.append(
                self.create_candidate(
                    decision_type=DecisionType.CONSULT_KNOWLEDGE,
                    description=f"Consult knowledge base for more evidence",
                    based_on_hypothesis=hypothesis_id,
                    confidence=hypothesis_confidence,
                )
            )

        # Low confidence -> Need more evidence
        else:
            candidates.append(
                self.create_candidate(
                    decision_type=DecisionType.REQUEST_MORE_EVIDENCE,
                    description="Request more evidence for hypothesis",
                    based_on_hypothesis=hypothesis_id,
                    confidence=hypothesis_confidence,
                )
            )

        return candidates

    # =========================================================================
    # Decision Evaluation
    # =========================================================================

    def evaluate_candidates(
        self,
        candidate_ids: list[str],
        context: DecisionContext,
    ) -> list[DecisionCandidate]:
        """Evaluate and rank decision candidates.

        Args:
            candidate_ids: IDs of candidates to evaluate.
            context: Decision context.

        Returns:
            Evaluated and ranked candidates.
        """
        with self._lock:
            candidates = [
                self._candidates[cand_id]
                for cand_id in candidate_ids
                if cand_id in self._candidates
            ]

        # Evaluate using strategy
        evaluated = self._evaluator.evaluate(candidates, context, self._strategy)

        # Update candidates
        with self._lock:
            for cand in evaluated:
                self._candidates[cand.candidate_id] = cand

        self._publish(
            "DecisionEvaluated",
            candidate_count=len(evaluated),
            best_id=evaluated[0].candidate_id if evaluated else None,
        )

        return evaluated

    def evaluate_single(
        self,
        candidate_id: str,
        context: DecisionContext,
    ) -> DecisionCandidate | None:
        """Evaluate a single candidate.

        Args:
            candidate_id: The candidate ID.
            context: Decision context.

        Returns:
            The evaluated candidate.
        """
        candidates = self.evaluate_candidates([candidate_id], context)
        return candidates[0] if candidates else None

    # =========================================================================
    # Decision Selection
    # =========================================================================

    def select_decision(
        self,
        candidate_ids: list[str],
        context: DecisionContext,
    ) -> Decision | None:
        """Select the best decision from candidates.

        Args:
            candidate_ids: IDs of candidates to consider.
            context: Decision context.

        Returns:
            The selected decision or None.
        """
        # Evaluate candidates
        evaluated = self.evaluate_candidates(candidate_ids, context)

        if not evaluated:
            return None

        # Select best candidate
        best = evaluated[0]  # Already ranked

        # Check if human approval required
        requires_approval = (
            self._require_human_approval
            or best.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
            or best.decision_type == DecisionType.ESCALATE_TO_HUMAN
        )

        # Create decision
        decision = Decision(
            decision_id=f"dec_{uuid.uuid4().hex[:16]}",
            candidate_id=best.candidate_id,
            decision_type=best.decision_type,
            description=best.description,
            category=best.category,
            priority=best.priority,
            status=DecisionStatus.APPROVED if not requires_approval else DecisionStatus.PENDING,
            confidence=best.confidence,
            risk_level=best.risk_level,
            risk_score=best.risk_score,
            score=best.risk_score * (1 - best.confidence),  # Lower is better
            justification=(f"Selected via {self._strategy.name()} strategy",),
            based_on_hypothesis=best.based_on_hypothesis,
            based_on_evidence=best.based_on_evidence,
            alternatives_considered=tuple(c.candidate_id for c in evaluated[1:]),
            requires_human_approval=requires_approval,
            metadata=best.metadata,
        )

        with self._lock:
            self._decisions[decision.decision_id] = decision

        # Build trace
        self._trace_builder.build_trace(
            decision_id=decision.decision_id,
            candidates=candidates,
            selected=best,
            context=context,
        )

        self._publish("ActionSelected", decision_id=decision.decision_id)

        if requires_approval:
            self._publish("EscalationRequested", decision_id=decision.decision_id)

        return decision

    # =========================================================================
    # Decision Actions
    # =========================================================================

    def approve_decision(self, decision_id: str) -> Decision | None:
        """Approve a pending decision.

        Args:
            decision_id: The decision ID.

        Returns:
            The approved decision.
        """
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                return None

            from dataclasses import replace
            approved = replace(
                decision,
                status=DecisionStatus.APPROVED,
                approved_at=datetime.now(timezone.utc).isoformat(),
            )
            self._decisions[decision_id] = approved

        self._publish("DecisionApproved", decision_id=decision_id)

        return approved

    def reject_decision(self, decision_id: str, reason: str = "") -> Decision | None:
        """Reject a decision.

        Args:
            decision_id: The decision ID.
            reason: Rejection reason.

        Returns:
            The rejected decision.
        """
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                return None

            from dataclasses import replace
            rejected = replace(
                decision,
                status=DecisionStatus.REJECTED,
                justification=decision.justification + (f"Rejected: {reason}",),
            )
            self._decisions[decision_id] = rejected

        self._publish("DecisionRejected", decision_id=decision_id, reason=reason)

        return rejected

    def mark_executed(self, decision_id: str) -> Decision | None:
        """Mark a decision as executed.

        Args:
            decision_id: The decision ID.

        Returns:
            The executed decision.
        """
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision or decision.status != DecisionStatus.APPROVED:
                return None

            from dataclasses import replace
            executed = replace(
                decision,
                status=DecisionStatus.EXECUTED,
            )
            self._decisions[decision_id] = executed

        return executed

    # =========================================================================
    # Getters
    # =========================================================================

    def get_decision(self, decision_id: str) -> Decision | None:
        """Get a decision by ID."""
        return self._decisions.get(decision_id)

    def get_candidate(self, candidate_id: str) -> DecisionCandidate | None:
        """Get a candidate by ID."""
        return self._candidates.get(candidate_id)

    def get_all_decisions(self) -> list[Decision]:
        """Get all decisions."""
        return list(self._decisions.values())

    def get_all_candidates(self) -> list[DecisionCandidate]:
        """Get all candidates."""
        return list(self._candidates.values())

    def get_pending_decisions(self) -> list[Decision]:
        """Get all pending decisions."""
        return [
            d for d in self._decisions.values()
            if d.status == DecisionStatus.PENDING
        ]

    # =========================================================================
    # Trace and Metrics
    # =========================================================================

    def get_trace(self) -> Any:
        """Get the current decision trace."""
        return self._trace_builder.build()

    def get_metrics(self) -> DecisionMetricsCollector:
        """Get decision metrics."""
        return self._metrics

    # =========================================================================
    # Event Publishing
    # =========================================================================

    def _publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish an event to the global EventBus."""
        self._event_publisher.publish(event_type, **kwargs)
