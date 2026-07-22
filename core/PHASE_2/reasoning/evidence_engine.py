"""Evidence Engine for EREN Cognitive Reasoning Platform.

Collects, ranks, and evaluates evidence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.reasoning.reasoning_types import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)

if TYPE_CHECKING:
    pass


class EvidenceEngine:
    """Manages evidence lifecycle.

    The Evidence Engine does NOT:
    - Perform inference
    - Make decisions
    - Generate hypotheses

    It ONLY:
    - Collects evidence
    - Ranks evidence
    - Removes duplicates
    - Evaluates quality
    """

    def __init__(self):
        """Initialize evidence engine."""
        self._evidence: dict[str, Evidence] = {}
        self._quality_scores: dict[str, float] = {}
        self._duplicates: dict[str, str] = {}  # duplicate_id -> original_id

    def collect(
        self,
        evidence: Evidence,
    ) -> str:
        """Collect evidence.

        Args:
            evidence: Evidence to collect.

        Returns:
            Evidence ID.
        """
        # Check for duplicates
        existing = self._find_duplicate(evidence)
        if existing:
            self._duplicates[evidence.evidence_id] = existing
            return existing

        self._evidence[evidence.evidence_id] = evidence
        return evidence.evidence_id

    def _find_duplicate(self, evidence: Evidence) -> str | None:
        """Find duplicate evidence.

        Args:
            evidence: Evidence to check.

        Returns:
            Original evidence ID or None.
        """
        for eid, existing in self._evidence.items():
            if self._is_duplicate(evidence, existing):
                return eid
        return None

    def _is_duplicate(self, e1: Evidence, e2: Evidence) -> bool:
        """Check if two evidence are duplicates.

        Args:
            e1: First evidence.
            e2: Second evidence.

        Returns:
            True if duplicates.
        """
        if e1.evidence_type != e2.evidence_type:
            return False
        if e1.source != e2.source:
            return False
        if e1.content == e2.content:
            return True
        return False

    def rank_evidence(
        self,
        evidence_ids: list[str],
        criteria: dict | None = None,
    ) -> list[str]:
        """Rank evidence by quality.

        Args:
            evidence_ids: Evidence IDs to rank.
            criteria: Optional ranking criteria.

        Returns:
            Ranked evidence IDs.
        """
        scored = []

        for eid in evidence_ids:
            evidence = self._evidence.get(eid)
            if not evidence:
                continue

            score = self._calculate_quality_score(evidence)
            self._quality_scores[eid] = score
            scored.append((eid, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [eid for eid, _ in scored]

    def _calculate_quality_score(self, evidence: Evidence) -> float:
        """Calculate evidence quality score.

        Args:
            evidence: Evidence to score.

        Returns:
            Quality score (0.0 to 1.0).
        """
        score = evidence.confidence * evidence.weight

        # Adjust by source reliability
        source_weights = {
            EvidenceSource.DEVICE: 0.9,
            EvidenceSource.SENSOR: 0.9,
            EvidenceSource.STANDARD: 0.95,
            EvidenceSource.KNOWLEDGE_BASE: 0.8,
            EvidenceSource.MANUAL: 0.85,
            EvidenceSource.USER: 0.5,
            EvidenceSource.MEMORY: 0.6,
            EvidenceSource.ENGINE: 0.4,
        }

        source_weight = source_weights.get(evidence.source, 0.5)
        score *= source_weight

        # Adjust by type
        if evidence.evidence_type == EvidenceType.MEASUREMENT:
            score *= 1.1
        elif evidence.evidence_type == EvidenceType.DERIVED:
            score *= 0.8

        return min(1.0, max(0.0, score))

    def evaluate_quality(self, evidence_id: str) -> float:
        """Evaluate evidence quality.

        Args:
            evidence_id: Evidence ID.

        Returns:
            Quality score.
        """
        return self._quality_scores.get(evidence_id, 0.5)

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        """Get evidence by ID.

        Args:
            evidence_id: Evidence ID.

        Returns:
            Evidence or None.
        """
        return self._evidence.get(evidence_id)

    def get_all_evidence(self) -> list[Evidence]:
        """Get all collected evidence.

        Returns:
            List of evidence.
        """
        return list(self._evidence.values())

    def remove_duplicates(self) -> int:
        """Remove duplicate evidence.

        Returns:
            Number of duplicates removed.
        """
        count = len(self._duplicates)
        self._duplicates.clear()
        return count


# Global evidence engine
_evidence_engine: EvidenceEngine | None = None
_evidence_lock = __import__("threading").Lock()


def get_evidence_engine() -> EvidenceEngine:
    """Get the global evidence engine."""
    global _evidence_engine
    with _evidence_lock:
        if _evidence_engine is None:
            _evidence_engine = EvidenceEngine()
        return _evidence_engine


def reset_evidence_engine() -> None:
    """Reset the global evidence engine."""
    global _evidence_engine
    with _evidence_lock:
        _evidence_engine = None
