"""Context History — tracks changes to contexts.

The Context History maintains a complete audit trail of all
changes made to contexts.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .context_types import ContextStatus

if TYPE_CHECKING:
    pass


@dataclass
class HistoryRecord:
    """A single record in the context history."""

    record_id: str
    context_id: str
    timestamp: str
    action: str  # created, updated, status_changed, completed, failed
    from_status: ContextStatus | None = None
    to_status: ContextStatus | None = None
    details: dict = field(default_factory=dict)


class ContextHistory:
    """Maintains history of all context changes.

    Provides an immutable audit trail of:
    - Context creation
    - Status transitions
    - Content updates
    - Engine contributions
    - Completion and failure
    """

    def __init__(self, max_records_per_context: int = 1000) -> None:
        """Initialize the history.

        Args:
            max_records_per_context: Maximum records to keep per context
        """
        self._records: dict[str, list[HistoryRecord]] = defaultdict(list)
        self._lock = threading.RLock()
        self._max_records = max_records_per_context

    def record_creation(self, context_id: str) -> None:
        """Record context creation.

        Args:
            context_id: The created context ID
        """
        record = HistoryRecord(
            record_id=f"hist_{datetime.now(UTC).isoformat()}",
            context_id=context_id,
            timestamp=datetime.now(UTC).isoformat(),
            action="created",
        )
        self._add_record(context_id, record)

    def record_transition(
        self,
        context_id: str,
        from_status: ContextStatus,
        to_status: ContextStatus,
        details: dict | None = None,
    ) -> None:
        """Record a status transition.

        Args:
            context_id: The context ID
            from_status: Previous status
            to_status: New status
            details: Optional additional details
        """
        record = HistoryRecord(
            record_id=f"hist_{datetime.now(UTC).isoformat()}",
            context_id=context_id,
            timestamp=datetime.now(UTC).isoformat(),
            action="status_changed",
            from_status=from_status,
            to_status=to_status,
            details=details or {},
        )
        self._add_record(context_id, record)

    def record_update(
        self,
        context_id: str,
        updates: dict,
        engine_id: str = "",
    ) -> None:
        """Record a context update.

        Args:
            context_id: The context ID
            updates: Dictionary of updates made
            engine_id: Engine that made the update
        """
        record = HistoryRecord(
            record_id=f"hist_{datetime.now(UTC).isoformat()}",
            context_id=context_id,
            timestamp=datetime.now(UTC).isoformat(),
            action="updated",
            details={"updates": updates, "engine_id": engine_id},
        )
        self._add_record(context_id, record)

    def record_engine_contribution(
        self,
        context_id: str,
        engine_id: str,
        contribution_type: str,
        details: dict,
    ) -> None:
        """Record an engine's contribution to a context.

        Args:
            context_id: The context ID
            engine_id: The contributing engine
            contribution_type: Type of contribution (evidence, hypothesis, etc.)
            details: Contribution details
        """
        record = HistoryRecord(
            record_id=f"hist_{datetime.now(UTC).isoformat()}",
            context_id=context_id,
            timestamp=datetime.now(UTC).isoformat(),
            action="engine_contribution",
            details={
                "engine_id": engine_id,
                "contribution_type": contribution_type,
                **details,
            },
        )
        self._add_record(context_id, record)

    def record_final_state(
        self,
        context_id: str,
        context: CognitiveContext,
    ) -> None:
        """Record the final state of a context.

        Args:
            context_id: The context ID
            context: The final context state
        """
        record = HistoryRecord(
            record_id=f"hist_{datetime.now(UTC).isoformat()}",
            context_id=context_id,
            timestamp=datetime.now(UTC).isoformat(),
            action="finalized",
            to_status=context.status,
            details={
                "duration_ms": context.processing.duration_ms,
                "evidence_count": len(context.evidence),
                "hypothesis_count": len(context.hypotheses),
                "confidence": context.overall_confidence.score if context.overall_confidence else 0,
            },
        )
        self._add_record(context_id, record)

    def get_history(
        self,
        context_id: str,
        limit: int | None = None,
    ) -> list[HistoryRecord]:
        """Get the history for a context.

        Args:
            context_id: The context ID
            limit: Optional limit on number of records

        Returns:
            List of history records, newest first.
        """
        with self._lock:
            records = list(self._records.get(context_id, []))
            records.sort(key=lambda r: r.timestamp, reverse=True)
            if limit:
                records = records[:limit]
            return records

    def get_status_timeline(
        self,
        context_id: str,
    ) -> list[tuple[str, ContextStatus]]:
        """Get the status transition timeline.

        Args:
            context_id: The context ID

        Returns:
            List of (timestamp, status) tuples.
        """
        with self._lock:
            records = self._records.get(context_id, [])
            timeline = []

            for record in records:
                if record.action == "created":
                    timeline.append((record.timestamp, ContextStatus.INITIALIZING))
                elif record.action == "status_changed" and record.to_status:
                    timeline.append((record.timestamp, record.to_status))
                elif record.action == "finalized" and record.to_status:
                    timeline.append((record.timestamp, record.to_status))

            return timeline

    def get_engine_contributions(
        self,
        context_id: str,
    ) -> dict[str, list[HistoryRecord]]:
        """Get all engine contributions to a context.

        Args:
            context_id: The context ID

        Returns:
            Dictionary of engine_id -> list of contribution records.
        """
        with self._lock:
            records = self._records.get(context_id, [])
            contributions: dict[str, list[HistoryRecord]] = defaultdict(list)

            for record in records:
                if record.action == "engine_contribution":
                    engine_id = record.details.get("engine_id", "unknown")
                    contributions[engine_id].append(record)

            return dict(contributions)

    def get_statistics(self) -> dict:
        """Get history statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            total_records = sum(len(r) for r in self._records.values())
            return {
                "total_contexts_tracked": len(self._records),
                "total_records": total_records,
                "avg_records_per_context": (
                    total_records / len(self._records) if self._records else 0
                ),
            }

    def clear_history(self, context_id: str) -> None:
        """Clear history for a context.

        Args:
            context_id: The context ID
        """
        with self._lock:
            if context_id in self._records:
                del self._records[context_id]

    def _add_record(self, context_id: str, record: HistoryRecord) -> None:
        """Add a record to the history.

        Args:
            context_id: The context ID
            record: The history record
        """
        with self._lock:
            self._records[context_id].append(record)

            # Trim if over limit
            if len(self._records[context_id]) > self._max_records:
                self._records[context_id] = self._records[context_id][-self._max_records:]
