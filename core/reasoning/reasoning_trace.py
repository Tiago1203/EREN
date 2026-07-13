"""Reasoning trace management.

Maintains complete audit trail of reasoning process.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .reasoning_types import Decision, Evidence, Hypothesis, ReasoningEvent, ReasoningTrace

if TYPE_CHECKING:
    pass


class ReasoningTraceBuilder:
    """Builds reasoning traces."""

    def __init__(self, session_id: str = "") -> None:
        """Initialize the trace builder.

        Args:
            session_id: The session ID.
        """
        self._trace_id = f"trace_{uuid.uuid4().hex[:16]}"
        self._session_id = session_id
        self._events: list[ReasoningEvent] = []
        self._hypotheses: list[Hypothesis] = []
        self._evidence: list[Evidence] = []
        self._decisions: list[Decision] = []
        self._chains: list[dict] = []
        self._metadata: dict = {}

    def add_event(
        self,
        event_type: str,
        actor: str = "reasoning_engine",
        **details: Any,
    ) -> None:
        """Add an event to the trace.

        Args:
            event_type: Type of event.
            actor: What triggered the event.
            **details: Additional details.
        """
        event = ReasoningEvent(
            event_id=f"evt_{uuid.uuid4().hex[:16]}",
            event_type=event_type,
            actor=actor,
            details=details,
        )
        self._events.append(event)

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Record a hypothesis in the trace.

        Args:
            hypothesis: The hypothesis.
        """
        self._hypotheses.append(hypothesis)
        self.add_event(
            "hypothesis_recorded",
            hypothesis_id=hypothesis.hypothesis_id,
            description=hypothesis.description,
        )

    def add_evidence(self, evidence: Evidence) -> None:
        """Record evidence in the trace.

        Args:
            evidence: The evidence.
        """
        self._evidence.append(evidence)
        self.add_event(
            "evidence_recorded",
            evidence_id=evidence.evidence_id,
            type=evidence.evidence_type.value,
        )

    def add_decision(self, decision: Decision) -> None:
        """Record a decision in the trace.

        Args:
            decision: The decision.
        """
        self._decisions.append(decision)
        self.add_event(
            "decision_recorded",
            decision_id=decision.decision_id,
            type=decision.decision_type.value,
        )

    def add_chain(self, chain: Any) -> None:
        """Record a reasoning chain.

        Args:
            chain: The chain.
        """
        self._chains.append({
            "chain_id": chain.chain_id,
            "hypothesis_id": chain.hypothesis_id,
            "step_count": len(chain.steps),
        })
        self.add_event(
            "chain_recorded",
            chain_id=chain.chain_id,
        )

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the trace.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self._metadata[key] = value

    def build(self) -> ReasoningTrace:
        """Build the final trace.

        Returns:
            The reasoning trace.
        """
        return ReasoningTrace(
            trace_id=self._trace_id,
            session_id=self._session_id,
            events=tuple(self._events),
            hypothesis_graph=self._build_hypothesis_graph(),
            evidence_graph=self._build_evidence_graph(),
            metadata=self._metadata,
        )

    def _build_hypothesis_graph(self) -> dict:
        """Build hypothesis relationship graph."""
        nodes = []
        edges = []

        for h in self._hypotheses:
            nodes.append({
                "id": h.hypothesis_id,
                "description": h.description,
                "probability": h.probability,
                "status": h.status.name,
            })

            for ev_id in h.supporting_evidence:
                edges.append({
                    "from": ev_id,
                    "to": h.hypothesis_id,
                    "type": "supports",
                })

            for ev_id in h.contradicting_evidence:
                edges.append({
                    "from": ev_id,
                    "to": h.hypothesis_id,
                    "type": "contradicts",
                })

        return {"nodes": nodes, "edges": edges}

    def _build_evidence_graph(self) -> dict:
        """Build evidence relationship graph."""
        nodes = []
        edges = []

        for e in self._evidence:
            nodes.append({
                "id": e.evidence_id,
                "type": e.evidence_type.value,
                "confidence": e.confidence,
            })

            if e.parent_evidence_id:
                edges.append({
                    "from": e.parent_evidence_id,
                    "to": e.evidence_id,
                    "type": "derived_from",
                })

        return {"nodes": nodes, "edges": edges}
