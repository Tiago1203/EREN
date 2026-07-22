"""Reasoning strategy executor.

Executes different reasoning strategies.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from .reasoning_types import Evidence, Hypothesis, ReasoningStrategy

if TYPE_CHECKING:
    pass


class StrategyExecutor(Protocol):
    """Protocol for strategy executors."""

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Select hypotheses based on strategy."""
        ...

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Order evidence collection based on strategy."""
        ...


class ExhaustiveStrategyExecutor:
    """Exhaustive reasoning strategy.

    Considers all hypotheses and all evidence.
    """

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Select all hypotheses."""
        return list(hypotheses)

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Return evidence in original order."""
        return list(evidence)


class FocusedStrategyExecutor:
    """Focused reasoning strategy.

    Focuses on most likely hypotheses.
    """

    def __init__(self, top_n: int = 3) -> None:
        """Initialize.

        Args:
            top_n: Number of top hypotheses to consider.
        """
        self._top_n = top_n

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Select top hypotheses by probability."""
        sorted_hyps = sorted(
            hypotheses,
            key=lambda h: h.probability,
            reverse=True,
        )
        return sorted_hyps[:self._top_n]

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Order evidence by relevance to top hypotheses."""
        return list(evidence)


class EvidenceFirstStrategyExecutor:
    """Evidence-first reasoning strategy.

    Collects all evidence before generating hypotheses.
    """

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Return hypotheses sorted by supporting evidence."""
        def evidence_count(h: Hypothesis) -> int:
            return len([e for e in evidence if e.evidence_id in h.supporting_evidence])

        return sorted(hypotheses, key=evidence_count, reverse=True)

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Return evidence grouped by type."""
        return list(evidence)


class HypothesisFirstStrategyExecutor:
    """Hypothesis-first reasoning strategy.

    Generates hypotheses before collecting evidence.
    """

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Return hypotheses in original order."""
        return list(hypotheses)

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Order evidence by relevance to top hypothesis."""
        if not hypotheses:
            return list(evidence)

        top_hyp = max(hypotheses, key=lambda h: h.probability)

        def relevance(e: Evidence) -> int:
            if e.evidence_id in top_hyp.supporting_evidence:
                return 2
            elif e.evidence_id in top_hyp.contradicting_evidence:
                return 1
            return 0

        return sorted(evidence, key=relevance, reverse=True)


class ReasoningStrategyExecutor:
    """Executes reasoning strategies."""

    _executors: dict[ReasoningStrategy, type[StrategyExecutor]] = {
        ReasoningStrategy.EXHAUSTIVE: ExhaustiveStrategyExecutor,
        ReasoningStrategy.FOCUSED: FocusedStrategyExecutor,
        ReasoningStrategy.EVIDENCE_FIRST: EvidenceFirstStrategyExecutor,
        ReasoningStrategy.HYPOTHESIS_FIRST: HypothesisFirstStrategyExecutor,
    }

    def __init__(self) -> None:
        """Initialize the strategy executor."""
        self._current_strategy = ReasoningStrategy.EXHAUSTIVE
        self._executor: StrategyExecutor = ExhaustiveStrategyExecutor()

    def set_strategy(self, strategy: ReasoningStrategy, **kwargs: any) -> None:
        """Set the reasoning strategy.

        Args:
            strategy: The strategy to use.
            **kwargs: Strategy-specific parameters.
        """
        self._current_strategy = strategy
        executor_cls = self._executors.get(strategy, ExhaustiveStrategyExecutor)
        self._executor = executor_cls(**kwargs)

    def select_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[Hypothesis]:
        """Select hypotheses based on current strategy.

        Args:
            hypotheses: All hypotheses.
            evidence: Collected evidence.

        Returns:
            Selected hypotheses.
        """
        return self._executor.select_hypotheses(hypotheses, evidence)

    def order_evidence(
        self,
        evidence: list[Evidence],
        hypotheses: list[Hypothesis],
    ) -> list[Evidence]:
        """Order evidence based on current strategy.

        Args:
            evidence: All evidence.
            hypotheses: Relevant hypotheses.

        Returns:
            Ordered evidence.
        """
        return self._executor.order_evidence(evidence, hypotheses)
