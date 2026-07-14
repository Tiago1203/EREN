"""Evidence management for the Reasoning Engine.

Handles evidence lifecycle: collection, validation, and relationship management.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .reasoning_types import Evidence, EvidenceRelation, EvidenceSource, EvidenceType

if TYPE_CHECKING:
    pass


@dataclass
class EvidenceManagerState:
    """State of the evidence manager."""

    evidence: dict[str, Evidence] = field(default_factory=dict)
    by_type: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_source: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_hypothesis: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    relations: dict[str, dict[str, EvidenceRelation]] = field(default_factory=dict)


class EvidenceManager:
    """Manages evidence in the reasoning process.

    Responsibilities:
    - Collect and store evidence
    - Validate evidence
    - Manage evidence-hypothesis relationships
    - Track evidence provenance
    """

    def __init__(self) -> None:
        """Initialize the evidence manager."""
        self._state = EvidenceManagerState()
        self._lock = threading.RLock()
        self._subscribers: list[Callable] = []

    # =========================================================================
    # Creation
    # =========================================================================

    def add(
        self,
        evidence_type: EvidenceType,
        source: EvidenceSource,
        content: str | dict,
        confidence: float = 0.5,
        hypothesis_id: str = "",
        relation: EvidenceRelation = EvidenceRelation.NEUTRAL,
        weight: float = 1.0,
        is_temporary: bool = False,
        parent_evidence_id: str = "",
        metadata: dict | None = None,
    ) -> Evidence:
        """Add new evidence.

        Args:
            evidence_type: Type of evidence.
            source: Source of evidence.
            content: Evidence content.
            confidence: Confidence (0.0 to 1.0).
            hypothesis_id: Related hypothesis ID.
            relation: Relation to hypothesis.
            weight: Evidence weight.
            is_temporary: If evidence is temporary.
            parent_evidence_id: Parent evidence ID for derived evidence.
            metadata: Optional metadata.

        Returns:
            The added evidence.
        """
        evidence_id = f"ev_{uuid.uuid4().hex[:16]}"

        evidence = Evidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source=source,
            content=content,
            confidence=confidence,
            related_hypotheses=(hypothesis_id,) if hypothesis_id else (),
            relation=relation,
            weight=weight,
            is_temporary=is_temporary,
            parent_evidence_id=parent_evidence_id,
            metadata=metadata or {},
        )

        with self._lock:
            self._state.evidence[evidence_id] = evidence
            self._state.by_type[evidence_type.value].add(evidence_id)
            self._state.by_source[source.value].add(evidence_id)
            self._state.relations[evidence_id] = {}

            if hypothesis_id:
                self._state.by_hypothesis[hypothesis_id].add(evidence_id)

        self._notify_subscribers("evidence_added", evidence)

        return evidence

    def add_from_observation(
        self,
        observation: str,
        confidence: float = 0.8,
        source: EvidenceSource = EvidenceSource.USER,
    ) -> Evidence:
        """Add evidence from a user observation.

        Args:
            observation: The observation text.
            confidence: Confidence level.
            source: Evidence source.

        Returns:
            The added evidence.
        """
        return self.add(
            evidence_type=EvidenceType.OBSERVATION,
            source=source,
            content=observation,
            confidence=confidence,
        )

    def add_measurement(
        self,
        value: float,
        unit: str,
        normal_range: tuple[float, float] | None = None,
        source: EvidenceSource = EvidenceSource.SENSOR,
    ) -> Evidence:
        """Add evidence from a measurement.

        Args:
            value: The measurement value.
            unit: Unit of measurement.
            normal_range: Normal range (min, max).
            source: Evidence source.

        Returns:
            The added evidence.
        """
        content = {
            "value": value,
            "unit": unit,
            "normal_range": normal_range,
            "is_normal": normal_range is not None and normal_range[0] <= value <= normal_range[1],
        }

        return self.add(
            evidence_type=EvidenceType.MEASUREMENT,
            source=source,
            content=content,
            confidence=0.95 if normal_range else 0.7,
            weight=1.5,  # Measurements have higher weight
        )

    def add_from_knowledge(
        self,
        knowledge_id: str,
        content: str,
        confidence: float = 0.8,
    ) -> Evidence:
        """Add evidence from knowledge base.

        Args:
            knowledge_id: ID from knowledge base.
            content: Knowledge content.
            confidence: Confidence level.

        Returns:
            The added evidence.
        """
        return self.add(
            evidence_type=EvidenceType.DOCUMENTED,
            source=EvidenceSource.KNOWLEDGE_BASE,
            content={"knowledge_id": knowledge_id, "content": content},
            confidence=confidence,
        )

    def derive(
        self,
        parent_evidence_id: str,
        derived_content: str | dict,
        confidence: float = 0.5,
    ) -> Evidence | None:
        """Create derived evidence from existing evidence.

        Args:
            parent_evidence_id: Parent evidence ID.
            derived_content: Derived content.
            confidence: Derived evidence confidence.

        Returns:
            The derived evidence or None if parent not found.
        """
        with self._lock:
            parent = self._state.evidence.get(parent_evidence_id)
            if not parent:
                return None

        return self.add(
            evidence_type=EvidenceType.DERIVED,
            source=EvidenceSource.ENGINE,
            content=derived_content,
            confidence=confidence * parent.confidence,  # Inherit some confidence
            parent_evidence_id=parent_evidence_id,
            is_temporary=True,
        )

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, evidence_id: str) -> Evidence | None:
        """Get evidence by ID."""
        with self._lock:
            return self._state.evidence.get(evidence_id)

    def get_all(self) -> list[Evidence]:
        """Get all evidence."""
        with self._lock:
            return list(self._state.evidence.values())

    def get_by_type(self, evidence_type: EvidenceType) -> list[Evidence]:
        """Get evidence by type."""
        with self._lock:
            ids = self._state.by_type.get(evidence_type.value, set())
            return [self._state.evidence[e] for e in ids if e in self._state.evidence]

    def get_by_source(self, source: EvidenceSource) -> list[Evidence]:
        """Get evidence by source."""
        with self._lock:
            ids = self._state.by_source.get(source.value, set())
            return [self._state.evidence[e] for e in ids if e in self._state.evidence]

    def get_for_hypothesis(self, hypothesis_id: str) -> list[Evidence]:
        """Get all evidence for a hypothesis."""
        with self._lock:
            ids = self._state.by_hypothesis.get(hypothesis_id, set())
            return [self._state.evidence[e] for e in ids if e in self._state.evidence]

    def get_relation(self, evidence_id: str, hypothesis_id: str) -> EvidenceRelation | None:
        """Get relation between evidence and hypothesis."""
        with self._lock:
            if evidence_id in self._state.relations:
                return self._state.relations[evidence_id].get(hypothesis_id)
            return None

    def set_relation(
        self,
        evidence_id: str,
        hypothesis_id: str,
        relation: EvidenceRelation,
    ) -> bool:
        """Set relation between evidence and hypothesis.

        Args:
            evidence_id: The evidence ID.
            hypothesis_id: The hypothesis ID.
            relation: The relation type.

        Returns:
            True if successful.
        """
        with self._lock:
            if evidence_id not in self._state.evidence:
                return False

            self._state.relations[evidence_id][hypothesis_id] = relation

            # Update evidence
            evidence = self._state.evidence[evidence_id]
            related = list(evidence.related_hypotheses)
            if hypothesis_id not in related:
                related.append(hypothesis_id)

            from dataclasses import replace
            self._state.evidence[evidence_id] = replace(
                evidence,
                related_hypotheses=tuple(related),
                relation=relation,
            )

            # Update hypothesis index
            self._state.by_hypothesis[hypothesis_id].add(evidence_id)

            self._notify_subscribers("relation_changed", evidence, hypothesis_id, relation)

            return True

    # =========================================================================
    # Update
    # =========================================================================

    def update_confidence(
        self,
        evidence_id: str,
        confidence: float,
    ) -> Evidence | None:
        """Update evidence confidence.

        Args:
            evidence_id: The evidence ID.
            confidence: New confidence (0.0 to 1.0).

        Returns:
            Updated evidence or None.
        """
        with self._lock:
            evidence = self._state.evidence.get(evidence_id)
            if not evidence:
                return None

            from dataclasses import replace
            updated = replace(
                evidence,
                confidence=max(0.0, min(1.0, confidence)),
            )

            self._state.evidence[evidence_id] = updated
            self._notify_subscribers("confidence_updated", updated)

            return updated

    def verify(self, evidence_id: str) -> Evidence | None:
        """Mark evidence as verified."""
        with self._lock:
            evidence = self._state.evidence.get(evidence_id)
            if not evidence:
                return None

            from dataclasses import replace
            updated = replace(
                evidence,
                is_verified=True,
                is_temporary=False,  # Verified evidence is not temporary
            )

            self._state.evidence[evidence_id] = updated
            return updated

    # =========================================================================
    # Deletion
    # =========================================================================

    def remove(self, evidence_id: str) -> bool:
        """Remove evidence.

        Args:
            evidence_id: The evidence ID.

        Returns:
            True if removed.
        """
        with self._lock:
            evidence = self._state.evidence.get(evidence_id)
            if not evidence:
                return False

            # Remove from indexes
            self._state.by_type[evidence.evidence_type.value].discard(evidence_id)
            self._state.by_source[evidence.source.value].discard(evidence_id)

            for hyp_id in evidence.related_hypotheses:
                self._state.by_hypothesis[hyp_id].discard(evidence_id)

            # Remove relations
            self._state.relations.pop(evidence_id, None)

            # Remove evidence
            del self._state.evidence[evidence_id]

            self._notify_subscribers("evidence_removed", evidence)

            return True

    def remove_temporary(self) -> int:
        """Remove all temporary evidence.

        Returns:
            Number of evidence removed.
        """
        with self._lock:
            temp_ids = [
                e.evidence_id
                for e in self._state.evidence.values()
                if e.is_temporary
            ]

            for evidence_id in temp_ids:
                self.remove(evidence_id)

            return len(temp_ids)

    # =========================================================================
    # Analysis
    # =========================================================================

    def analyze_evidence_quality(self) -> dict:
        """Analyze overall evidence quality.

        Returns:
            Quality metrics.
        """
        with self._lock:
            total = len(self._state.evidence)
            if total == 0:
                return {
                    "total": 0,
                    "average_confidence": 0.0,
                    "verified_count": 0,
                    "by_type": {},
                    "by_source": {},
                }

            total_confidence = sum(e.confidence for e in self._state.evidence.values())
            verified = sum(1 for e in self._state.evidence.values() if e.is_verified)

            by_type = {
                t: len(ids)
                for t, ids in self._state.by_type.items()
            }

            by_source = {
                s: len(ids)
                for s, ids in self._state.by_source.items()
            }

            return {
                "total": total,
                "average_confidence": total_confidence / total,
                "verified_count": verified,
                "verification_rate": verified / total,
                "by_type": by_type,
                "by_source": by_source,
            }

    # =========================================================================
    # Utility
    # =========================================================================

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to evidence changes."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from changes."""
        self._subscribers = [s for s in self._subscribers if s != callback]

    def _notify_subscribers(
        self,
        event_type: str,
        evidence: Evidence,
        *args,
    ) -> None:
        """Notify subscribers of changes."""
        for callback in self._subscribers:
            try:
                callback(event_type, evidence, *args)
            except Exception:
                pass
