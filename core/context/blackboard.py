"""Cognitive Blackboard — shared workspace for all motors.

The Blackboard is a shared workspace where all motors can:
- Read entries from other motors
- Write their own entries
- Add evidence and hypotheses
- Add observations

Entries are immutable once written. Motor should never modify
another motor's work directly.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .context_types import (
    BlackboardEntry,
    BlackboardEntryType,
    Evidence,
    EvidenceType,
    Hypothesis,
    Observation,
)

if TYPE_CHECKING:
    pass


@dataclass
class BlackboardState:
    """Current state of the blackboard."""

    entries: dict[str, BlackboardEntry] = field(default_factory=dict)
    evidence_by_hypothesis: dict[str, list[str]] = field(default_factory=dict)
    entries_by_engine: dict[str, list[str]] = field(default_factory=dict)
    entries_by_type: dict[str, list[str]] = field(default_factory=dict)


class CognitiveBlackboard:
    """The shared cognitive blackboard.

    The blackboard is a shared workspace that enables all motors to
    collaborate on solving problems without direct coupling.

    Key principles:
    - All entries are immutable once written
    - Motors can only write their own entries
    - Any motor can read any entry
    - Entries can supersede previous entries (versioning)
    - All operations are thread-safe

    Example:
        blackboard = CognitiveBlackboard()

        # Engine A writes evidence
        blackboard.write_evidence(
            engine_id="diagnostic_engine",
            evidence=Evidence(...),
        )

        # Engine B reads evidence
        evidence = blackboard.read_evidence()

        # Engine B adds hypothesis
        blackboard.write_hypothesis(
            engine_id="reasoning_engine",
            hypothesis=Hypothesis(...),
        )
    """

    def __init__(self) -> None:
        """Initialize the blackboard."""
        self._state = BlackboardState()
        self._lock = threading.RLock()
        self._subscribers: list[callable] = []

    # =========================================================================
    # Write Operations (All motors can write)
    # =========================================================================

    def write_entry(
        self,
        engine_id: str,
        entry: BlackboardEntry,
    ) -> str:
        """Write an entry to the blackboard.

        Args:
            engine_id: ID of the engine writing the entry
            entry: The entry to write

        Returns:
            The entry ID.
        """
        with self._lock:
            # Store entry
            self._state.entries[entry.entry_id] = entry

            # Update indexes
            self._index_entry(entry, engine_id)

            # Notify subscribers
            self._notify_subscribers(entry)

            return entry.entry_id

    def write_evidence(
        self,
        engine_id: str,
        evidence: Evidence,
        supersedes: str = "",
    ) -> str:
        """Write evidence to the blackboard.

        Args:
            engine_id: Engine writing the evidence
            evidence: Evidence to write
            supersedes: Optional entry ID this supersedes

        Returns:
            The entry ID.
        """
        entry = BlackboardEntry(
            entry_id=f"entry_{uuid.uuid4().hex[:16]}",
            entry_type=BlackboardEntryType.EVIDENCE,
            content=evidence,
            author_engine=engine_id,
            superseded_by=supersedes,
            confidence=evidence.confidence,
            metadata={"evidence_id": evidence.evidence_id},
        )

        return self.write_entry(engine_id, entry)

    def write_hypothesis(
        self,
        engine_id: str,
        hypothesis: Hypothesis,
        supersedes: str = "",
    ) -> str:
        """Write a hypothesis to the blackboard.

        Args:
            engine_id: Engine writing the hypothesis
            hypothesis: Hypothesis to write
            supersedes: Optional entry ID this supersedes

        Returns:
            The entry ID.
        """
        entry = BlackboardEntry(
            entry_id=f"entry_{uuid.uuid4().hex[:16]}",
            entry_type=BlackboardEntryType.HYPOTHESIS,
            content=hypothesis,
            author_engine=engine_id,
            superseded_by=supersedes,
            confidence=hypothesis.confidence,
            metadata={
                "hypothesis_id": hypothesis.hypothesis_id,
                "probability": hypothesis.probability,
            },
        )

        return self.write_entry(engine_id, entry)

    def write_observation(
        self,
        engine_id: str,
        observation: Observation,
        supersedes: str = "",
    ) -> str:
        """Write an observation to the blackboard.

        Args:
            engine_id: Engine writing the observation
            observation: Observation to write
            supersedes: Optional entry ID this supersedes

        Returns:
            The entry ID.
        """
        entry = BlackboardEntry(
            entry_id=f"entry_{uuid.uuid4().hex[:16]}",
            entry_type=BlackboardEntryType.OBSERVATION,
            content=observation,
            author_engine=engine_id,
            superseded_by=supersedes,
            confidence=observation.confidence,
            metadata={
                "observation_id": observation.observation_id,
                "observation_type": observation.observation_type,
            },
        )

        return self.write_entry(engine_id, entry)

    def supersede_entry(
        self,
        entry_id: str,
        new_entry_id: str,
    ) -> bool:
        """Mark an entry as superseded by a new entry.

        Args:
            entry_id: The entry to supersede
            new_entry_id: The new entry that supersedes it

        Returns:
            True if successful, False if entry not found.
        """
        with self._lock:
            if entry_id not in self._state.entries:
                return False

            entry = self._state.entries[entry_id]
            self._state.entries[entry_id] = entry.model_copy(
                update={"superseded_by": new_entry_id}
            )
            return True

    # =========================================================================
    # Read Operations (All motors can read)
    # =========================================================================

    def read_entry(self, entry_id: str) -> BlackboardEntry | None:
        """Read a specific entry.

        Args:
            entry_id: The entry ID

        Returns:
            The entry if found, None otherwise.
        """
        with self._lock:
            return self._state.entries.get(entry_id)

    def read_all_entries(
        self,
        entry_type: BlackboardEntryType | None = None,
        include_superseded: bool = False,
    ) -> list[BlackboardEntry]:
        """Read all entries, optionally filtered.

        Args:
            entry_type: Optional filter by entry type
            include_superseded: Whether to include superseded entries

        Returns:
            List of entries.
        """
        with self._lock:
            entries = list(self._state.entries.values())

            if not include_superseded:
                entries = [e for e in entries if e.is_active()]

            if entry_type:
                entries = [e for e in entries if e.entry_type == entry_type]

            return entries

    def read_evidence(
        self,
        engine_id: str | None = None,
        evidence_type: EvidenceType | None = None,
    ) -> list[Evidence]:
        """Read evidence entries.

        Args:
            engine_id: Optional filter by source engine
            evidence_type: Optional filter by evidence type

        Returns:
            List of evidence.
        """
        entries = self.read_all_entries(BlackboardEntryType.EVIDENCE)
        evidence_list: list[Evidence] = []

        for entry in entries:
            ev = entry.content
            if not isinstance(ev, Evidence):
                continue
            if engine_id and ev.engine_id != engine_id:
                continue
            if evidence_type and ev.evidence_type != evidence_type:
                continue
            evidence_list.append(ev)

        return evidence_list

    def read_hypotheses(
        self,
        engine_id: str | None = None,
        status: str | None = None,
    ) -> list[Hypothesis]:
        """Read hypothesis entries.

        Args:
            engine_id: Optional filter by source engine
            status: Optional filter by status (active, confirmed, rejected)

        Returns:
            List of hypotheses.
        """
        entries = self.read_all_entries(BlackboardEntryType.HYPOTHESIS)
        hypotheses: list[Hypothesis] = []

        for entry in entries:
            hyp = entry.content
            if not isinstance(hyp, Hypothesis):
                continue
            if engine_id and hyp.engine_id != engine_id:
                continue
            if status and hyp.status != status:
                continue
            hypotheses.append(hyp)

        return hypotheses

    def read_observations(
        self,
        engine_id: str | None = None,
        observation_type: str | None = None,
    ) -> list[Observation]:
        """Read observation entries.

        Args:
            engine_id: Optional filter by source engine
            observation_type: Optional filter by type

        Returns:
            List of observations.
        """
        entries = self.read_all_entries(BlackboardEntryType.OBSERVATION)
        observations: list[Observation] = []

        for entry in entries:
            obs = entry.content
            if not isinstance(obs, Observation):
                continue
            if engine_id and obs.engine_id != engine_id:
                continue
            if observation_type and obs.observation_type != observation_type:
                continue
            observations.append(obs)

        return observations

    def read_by_engine(self, engine_id: str) -> list[BlackboardEntry]:
        """Read all entries by a specific engine.

        Args:
            engine_id: The engine ID

        Returns:
            List of entries.
        """
        with self._lock:
            entry_ids = self._state.entries_by_engine.get(engine_id, [])
            return [
                self._state.entries[eid]
                for eid in entry_ids
                if eid in self._state.entries
            ]

    # =========================================================================
    # Query Operations
    # =========================================================================

    def get_hypothesis_evidence(
        self,
        hypothesis_id: str,
    ) -> list[Evidence]:
        """Get evidence supporting a hypothesis.

        Args:
            hypothesis_id: The hypothesis ID

        Returns:
            List of supporting evidence.
        """
        entry_ids = self._state.evidence_by_hypothesis.get(hypothesis_id, [])
        evidence: list[Evidence] = []

        for entry in self._state.entries.values():
            if entry.entry_id in entry_ids:
                if isinstance(entry.content, Evidence):
                    evidence.append(entry.content)

        return evidence

    def get_active_count(self) -> dict[str, int]:
        """Get count of active entries by type."""
        with self._lock:
            counts: dict[str, int] = {}
            for entry in self._state.entries.values():
                if entry.is_active():
                    type_name = entry.entry_type.value
                    counts[type_name] = counts.get(type_name, 0) + 1
            return counts

    # =========================================================================
    # Subscription Operations
    # =========================================================================

    def subscribe(self, callback: callable) -> None:
        """Subscribe to blackboard changes.

        Args:
            callback: Function called when entries are added
        """
        with self._lock:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from blackboard changes.

        Args:
            callback: The callback to remove
        """
        with self._lock:
            self._subscribers = [s for s in self._subscribers if s != callback]

    def _notify_subscribers(self, entry: BlackboardEntry) -> None:
        """Notify subscribers of a new entry."""
        for callback in self._subscribers:
            try:
                callback(entry)
            except Exception:
                pass

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def clear(self) -> None:
        """Clear all entries from the blackboard."""
        with self._lock:
            self._state = BlackboardState()

    def snapshot(self) -> dict:
        """Create a snapshot of the blackboard state."""
        with self._lock:
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "total_entries": len(self._state.entries),
                "by_type": self.get_active_count(),
                "by_engine": {
                    engine: len(ids)
                    for engine, ids in self._state.entries_by_engine.items()
                },
            }

    def _index_entry(self, entry: BlackboardEntry, engine_id: str) -> None:
        """Index an entry for fast lookup."""
        # By engine
        if engine_id not in self._state.entries_by_engine:
            self._state.entries_by_engine[engine_id] = []
        self._state.entries_by_engine[engine_id].append(entry.entry_id)

        # By type
        type_name = entry.entry_type.value
        if type_name not in self._state.entries_by_type:
            self._state.entries_by_type[type_name] = []
        self._state.entries_by_type[type_name].append(entry.entry_id)

        # Index evidence by hypothesis
        if isinstance(entry.content, Evidence):
            for hyp_id in getattr(entry.content, "supporting_hypotheses", []):
                if hyp_id not in self._state.evidence_by_hypothesis:
                    self._state.evidence_by_hypothesis[hyp_id] = []
                self._state.evidence_by_hypothesis[hyp_id].append(entry.entry_id)
