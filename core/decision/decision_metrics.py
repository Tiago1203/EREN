"""Decision metrics for the Cognitive Decision Engine.

Collects and calculates decision operation metrics.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .decision_types import DecisionMetrics, DecisionStatus, DecisionType

if TYPE_CHECKING:
    pass


class DecisionMetricsCollector:
    """Collects decision metrics."""

    def __init__(self) -> None:
        """Initialize the metrics collector."""
        self._decisions_created = 0
        self._decisions_evaluated = 0
        self._decisions_approved = 0
        self._decisions_rejected = 0
        self._decisions_executed = 0
        self._escalations = 0
        self._scores: list[float] = []
        self._risk_scores: list[float] = []
        self._by_type: dict[str, int] = {}
        self._by_category: dict[str, int] = {}

    def record_created(self, decision_type: DecisionType) -> None:
        """Record a decision creation."""
        self._decisions_created += 1
        self._by_type[decision_type.value] = self._by_type.get(decision_type.value, 0) + 1

    def record_evaluated(self, score: float, risk_score: float) -> None:
        """Record a decision evaluation."""
        self._decisions_evaluated += 1
        self._scores.append(score)
        self._risk_scores.append(risk_score)

    def record_approved(self) -> None:
        """Record a decision approval."""
        self._decisions_approved += 1

    def record_rejected(self) -> None:
        """Record a decision rejection."""
        self._decisions_rejected += 1

    def record_executed(self) -> None:
        """Record a decision execution."""
        self._decisions_executed += 1

    def record_escalation(self) -> None:
        """Record an escalation."""
        self._escalations += 1

    def calculate(self) -> DecisionMetrics:
        """Calculate final metrics."""
        avg_score = sum(self._scores) / len(self._scores) if self._scores else 0.0
        avg_risk = sum(self._risk_scores) / len(self._risk_scores) if self._risk_scores else 0.0

        return DecisionMetrics(
            decisions_created=self._decisions_created,
            decisions_evaluated=self._decisions_evaluated,
            decisions_approved=self._decisions_approved,
            decisions_rejected=self._decisions_rejected,
            decisions_executed=self._decisions_executed,
            escalations=self._escalations,
            average_score=avg_score,
            average_risk_score=avg_risk,
            by_type=self._by_type.copy(),
            by_category=self._by_category.copy(),
        )


@dataclass
class DecisionHealthCheck:
    """Health check for decision engine."""

    is_healthy: bool = True
    pending_decisions: int = 0
    rejected_rate: float = 0.0
    escalation_rate: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(timezone.utc).isoformat())
