"""Hypothesis management for the Reasoning Engine.

Handles hypothesis lifecycle: creation, update, ranking, and archiving.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .reasoning_types import (
    ConfidenceScore,
    EvidenceRelation,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
)

if TYPE_CHECKING:
    pass


@dataclass
class HypothesisManagerState:
    """State of the hypothesis manager."""

    hypotheses: dict[str, Hypothesis] = field(default_factory=dict)
    by_status: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_priority: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    evidence_to_hypotheses: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    hypothesis_evidence: dict[str, dict[str, EvidenceRelation]] = field(default_factory=dict)


class HypothesisManager:
    """Manages hypotheses in the reasoning process.

    Responsibilities:
    - Create and store hypotheses
    - Update hypothesis status
    - Manage evidence-hypothesis relationships
    - Rank hypotheses by confidence
    - Discard hypotheses
    """

    def __init__(self, max_hypotheses: int = 10) -> None:
        """Initialize the hypothesis manager.

        Args:
            max_hypotheses: Maximum number of active hypotheses.
        """
        self._state = HypothesisManagerState()
        self._lock = threading.RLock()
        self._max_hypotheses = max_hypotheses
        self._subscribers: list[Callable] = []

    # =========================================================================
    # Creation
    # =========================================================================

    def create(
        self,
        description: str,
        initial_probability: float = 0.5,
        priority: HypothesisPriority = HypothesisPriority.MEDIUM,
        tags: tuple[str, ...] | None = None,
        metadata: dict | None = None,
    ) -> Hypothesis:
        """Create a new hypothesis.

        Args:
            description: The hypothesis description.
            initial_probability: Initial probability (0.0 to 1.0).
            priority: Priority level.
            tags: Optional tags.
            metadata: Optional metadata.

        Returns:
            The created hypothesis.
        """
        hypothesis_id = f"hyp_{uuid.uuid4().hex[:16]}"

        hypothesis = Hypothesis(
            hypothesis_id=hypothesis_id,
            description=description,
            probability=initial_probability,
            priority=priority,
            tags=tags or (),
            metadata=metadata or {},
        )

        with self._lock:
            self._state.hypotheses[hypothesis_id] = hypothesis
            self._state.by_status[HypothesisStatus.ACTIVE.name].add(hypothesis_id)
            self._state.by_priority[priority.name].add(hypothesis_id)
            self._state.hypothesis_evidence[hypothesis_id] = {}

        self._notify_subscribers("hypothesis_created", hypothesis)

        return hypothesis

    def create_from_observation(
        self,
        observation: str,
        possible_causes: list[str],
    ) -> list[Hypothesis]:
        """Create multiple hypotheses from an observation.

        Args:
            observation: The observed phenomenon.
            possible_causes: List of possible causes.

        Returns:
            List of created hypotheses.
        """
        hypotheses = []

        for i, cause in enumerate(possible_causes):
            # Initial probability based on position (can be adjusted later)
            prob = 1.0 / (i + 1)  # First is most likely

            hyp = self.create(
                description=f"{observation}: {cause}",
                initial_probability=prob,
            )
            hypotheses.append(hyp)

        return hypotheses

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, hypothesis_id: str) -> Hypothesis | None:
        """Get a hypothesis by ID."""
        with self._lock:
            return self._state.hypotheses.get(hypothesis_id)

    def get_all(self) -> list[Hypothesis]:
        """Get all hypotheses."""
        with self._lock:
            return list(self._state.hypotheses.values())

    def get_active(self) -> list[Hypothesis]:
        """Get all active hypotheses."""
        with self._lock:
            active_ids = self._state.by_status.get(HypothesisStatus.ACTIVE.name, set())
            return [self._state.hypotheses[h] for h in active_ids if h in self._state.hypotheses]

    def get_by_status(self, status: HypothesisStatus) -> list[Hypothesis]:
        """Get hypotheses by status."""
        with self._lock:
            ids = self._state.by_status.get(status.name, set())
            return [self._state.hypotheses[h] for h in ids if h in self._state.hypotheses]

    def get_ranked(self) -> list[Hypothesis]:
        """Get hypotheses ranked by probability."""
        with self._lock:
            return sorted(
                self._state.hypotheses.values(),
                key=lambda h: (h.probability * h.confidence_score, -h.priority.value),
                reverse=True,
            )

    def get_best(self) -> Hypothesis | None:
        """Get the highest ranked hypothesis."""
        ranked = self.get_ranked()
        return ranked[0] if ranked else None

    # =========================================================================
    # Evidence Management
    # =========================================================================

    def add_evidence(
        self,
        hypothesis_id: str,
        evidence_id: str,
        relation: EvidenceRelation,
    ) -> Hypothesis | None:
        """Add evidence to a hypothesis.

        Args:
            hypothesis_id: The hypothesis ID.
            evidence_id: The evidence ID.
            relation: How the evidence relates.

        Returns:
            Updated hypothesis or None if not found.
        """
        with self._lock:
            hypothesis = self._state.hypotheses.get(hypothesis_id)
            if not hypothesis:
                return None

            # Add to evidence mapping
            self._state.hypothesis_evidence[hypothesis_id][evidence_id] = relation
            self._state.evidence_to_hypotheses[evidence_id].add(hypothesis_id)

            # Update hypothesis evidence lists
            supporting = list(hypothesis.supporting_evidence)
            contradicting = list(hypothesis.contradicting_evidence)

            if relation == EvidenceRelation.SUPPORTS:
                if evidence_id not in supporting:
                    supporting.append(evidence_id)
                    contradicting = [e for e in contradicting if e != evidence_id]
            elif relation == EvidenceRelation.CONTRADICTS:
                if evidence_id not in contradicting:
                    contradicting.append(evidence_id)
                    supporting = [e for e in supporting if e != evidence_id]

            # Update status
            new_status = hypothesis.status
            if supporting and not contradicting:
                new_status = HypothesisStatus.SUPPORTED
            elif contradicting and not supporting:
                new_status = HypothesisStatus.CONTRADICTED
            elif contradicting and supporting:
                new_status = HypothesisStatus.ACTIVE

            # Create updated hypothesis
            from dataclasses import replace
            updated = replace(
                hypothesis,
                supporting_evidence=tuple(supporting),
                contradicting_evidence=tuple(contradicting),
                status=new_status,
                updated_at=datetime.now(UTC).isoformat(),
            )

            self._state.hypotheses[hypothesis_id] = updated
            self._notify_subscribers("evidence_added", updated, evidence_id)

            return updated

    def remove_evidence(
        self,
        hypothesis_id: str,
        evidence_id: str,
    ) -> Hypothesis | None:
        """Remove evidence from a hypothesis.

        Args:
            hypothesis_id: The hypothesis ID.
            evidence_id: The evidence ID.

        Returns:
            Updated hypothesis or None.
        """
        with self._lock:
            hypothesis = self._state.hypotheses.get(hypothesis_id)
            if not hypothesis:
                return None

            # Remove from mappings
            if hypothesis_id in self._state.hypothesis_evidence:
                self._state.hypothesis_evidence[hypothesis_id].pop(evidence_id, None)

            if evidence_id in self._state.evidence_to_hypotheses:
                self._state.evidence_to_hypotheses[evidence_id].discard(hypothesis_id)

            # Update lists
            supporting = [e for e in hypothesis.supporting_evidence if e != evidence_id]
            contradicting = [e for e in hypothesis.contradicting_evidence if e != evidence_id]

            from dataclasses import replace
            updated = replace(
                hypothesis,
                supporting_evidence=tuple(supporting),
                contradicting_evidence=tuple(contradicting),
                updated_at=datetime.now(UTC).isoformat(),
            )

            self._state.hypotheses[hypothesis_id] = updated
            return updated

    def get_evidence_for(self, hypothesis_id: str) -> tuple[list[str], list[str]]:
        """Get supporting and contradicting evidence IDs."""
        with self._lock:
            hypothesis = self._state.hypotheses.get(hypothesis_id)
            if not hypothesis:
                return [], []
            return (
                list(hypothesis.supporting_evidence),
                list(hypothesis.contradicting_evidence),
            )

    # =========================================================================
    # Status Updates
    # =========================================================================

    def update_status(
        self,
        hypothesis_id: str,
        status: HypothesisStatus,
    ) -> Hypothesis | None:
        """Update hypothesis status."""
        with self._lock:
            hypothesis = self._state.hypotheses.get(hypothesis_id)
            if not hypothesis:
                return None

            # Remove from old status index
            self._state.by_status[hypothesis.status.name].discard(hypothesis_id)

            # Add to new status index
            self._state.by_status[status.name].add(hypothesis_id)

            from dataclasses import replace
            updated = replace(
                hypothesis,
                status=status,
                updated_at=datetime.now(UTC).isoformat(),
            )

            self._state.hypotheses[hypothesis_id] = updated
            self._notify_subscribers("status_updated", updated)

            return updated

    def confirm(self, hypothesis_id: str) -> Hypothesis | None:
        """Mark hypothesis as confirmed."""
        return self.update_status(hypothesis_id, HypothesisStatus.CONFIRMED)

    def reject(self, hypothesis_id: str) -> Hypothesis | None:
        """Mark hypothesis as rejected."""
        return self.update_status(hypothesis_id, HypothesisStatus.REJECTED)

    def archive(self, hypothesis_id: str) -> Hypothesis | None:
        """Archive a hypothesis."""
        return self.update_status(hypothesis_id, HypothesisStatus.ARCHIVED)

    # =========================================================================
    # Confidence Updates
    # =========================================================================

    def update_confidence(
        self,
        hypothesis_id: str,
        confidence: ConfidenceScore,
    ) -> Hypothesis | None:
        """Update hypothesis confidence.

        Args:
            hypothesis_id: The hypothesis ID.
            confidence: The new confidence score.

        Returns:
            Updated hypothesis or None.
        """
        with self._lock:
            hypothesis = self._state.hypotheses.get(hypothesis_id)
            if not hypothesis:
                return None

            from dataclasses import replace
            updated = replace(
                hypothesis,
                confidence_score=confidence.value,
                confidence_reasons=confidence.reasons,
                updated_at=datetime.now(UTC).isoformat(),
            )

            self._state.hypotheses[hypothesis_id] = updated
            self._notify_subscribers("confidence_updated", updated)

            return updated

    # =========================================================================
    # Ranking
    # =========================================================================

    def rank_hypotheses(self) -> list[Hypothesis]:
        """Rank hypotheses by confidence and probability."""
        with self._lock:
            ranked = []
            for h in self._state.hypotheses.values():
                if h.is_active():
                    # Calculate composite score
                    score = h.probability * h.confidence_score
                    ranked.append((h, score))

            # Sort by score, then by priority
            ranked.sort(key=lambda x: (x[1], -x[0].priority.value), reverse=True)

            # Assign ranks
            result = []
            for i, (h, _) in enumerate(ranked):
                from dataclasses import replace
                updated = replace(h, rank=i + 1)
                self._state.hypotheses[h.hypothesis_id] = updated
                result.append(updated)

            return result

    # =========================================================================
    # Utility
    # =========================================================================

    def get_statistics(self) -> dict:
        """Get hypothesis statistics."""
        with self._lock:
            return {
                "total": len(self._state.hypotheses),
                "active": len(self._state.by_status.get(HypothesisStatus.ACTIVE.name, set())),
                "confirmed": len(self._state.by_status.get(HypothesisStatus.CONFIRMED.name, set())),
                "rejected": len(self._state.by_status.get(HypothesisStatus.REJECTED.name, set())),
                "by_priority": {
                    p.name: len(ids)
                    for p, ids in self._state.by_priority.items()
                },
            }

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to hypothesis changes."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from changes."""
        self._subscribers = [s for s in self._subscribers if s != callback]

    def _notify_subscribers(
        self,
        event_type: str,
        hypothesis: Hypothesis,
        evidence_id: str = "",
    ) -> None:
        """Notify subscribers of changes."""
        for callback in self._subscribers:
            try:
                callback(event_type, hypothesis, evidence_id)
            except Exception:
                pass
