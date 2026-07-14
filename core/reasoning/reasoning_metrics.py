"""Reasoning metrics collection.

Collects and calculates reasoning metrics.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .reasoning_types import ReasoningMetrics

if TYPE_CHECKING:
    pass


class ReasoningMetricsCollector:
    """Collects reasoning metrics."""

    def __init__(self, session_id: str = "") -> None:
        """Initialize the metrics collector.

        Args:
            session_id: The session ID.
        """
        self._session_id = session_id
        self._start_time: float | None = None
        self._hypotheses_generated = 0
        self._hypotheses_confirmed = 0
        self._hypotheses_rejected = 0
        self._evidence_collected = 0
        self._reasoning_steps = 0
        self._decisions_generated = 0
        self._chains_created = 0
        self._confidence_scores: list[float] = []
        self._inference_counts: dict[str, int] = {}

    def record_start(self) -> None:
        """Record reasoning start."""
        import time
        self._start_time = time.time()

    def record_hypothesis_created(self) -> None:
        """Record hypothesis creation."""
        self._hypotheses_generated += 1

    def record_hypothesis_confirmed(self) -> None:
        """Record hypothesis confirmation."""
        self._hypotheses_confirmed += 1

    def record_hypothesis_rejected(self) -> None:
        """Record hypothesis rejection."""
        self._hypotheses_rejected += 1

    def record_evidence_collected(self) -> None:
        """Record evidence collection."""
        self._evidence_collected += 1

    def record_reasoning_step(self) -> None:
        """Record reasoning step."""
        self._reasoning_steps += 1

    def record_decision(self) -> None:
        """Record decision generation."""
        self._decisions_generated += 1

    def record_chain_created(self) -> None:
        """Record chain creation."""
        self._chains_created += 1

    def record_confidence(self, score: float) -> None:
        """Record a confidence score.

        Args:
            score: The confidence score.
        """
        self._confidence_scores.append(score)

    def record_inference(self, inference_type: str) -> None:
        """Record an inference type usage.

        Args:
            inference_type: The inference type.
        """
        self._inference_counts[inference_type] = self._inference_counts.get(inference_type, 0) + 1

    def calculate(self) -> ReasoningMetrics:
        """Calculate final metrics.

        Returns:
            Reasoning metrics.
        """
        import time

        total_time = 0.0
        if self._start_time:
            total_time = (time.time() - self._start_time) * 1000

        avg_confidence = sum(self._confidence_scores) / len(self._confidence_scores) if self._confidence_scores else 0.0

        return ReasoningMetrics(
            session_id=self._session_id,
            hypotheses_generated=self._hypotheses_generated,
            hypotheses_confirmed=self._hypotheses_confirmed,
            hypotheses_rejected=self._hypotheses_rejected,
            evidence_collected=self._evidence_collected,
            reasoning_steps=self._reasoning_steps,
            decisions_generated=self._decisions_generated,
            average_confidence=avg_confidence,
            total_reasoning_time_ms=total_time,
            chains_created=self._chains_created,
            inferences_deductive=self._inference_counts.get("deductive", 0),
            inferences_inductive=self._inference_counts.get("inductive", 0),
            inferences_abductive=self._inference_counts.get("abductive", 0),
        )


@dataclass
class ReasoningHealthCheck:
    """Health check for reasoning engine."""

    session_id: str
    is_healthy: bool = True
    active_hypotheses: int = 0
    pending_evidence: int = 0
    has_conclusion: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(UTC).isoformat())
