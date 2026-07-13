"""Decision trace for the Cognitive Decision Engine.

Maintains complete audit trail of decision process.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Trace Events
# =============================================================================


@dataclass(frozen=True)
class DecisionTraceEvent:
    """A single event in the decision trace."""

    event_id: str
    event_type: str  # candidate_created, evaluated, selected, etc.
    timestamp: str
    details: dict = field(default_factory=dict)


# =============================================================================
# Trace Builder
# =============================================================================


class DecisionTraceBuilder:
    """Builds decision traces."""

    def __init__(self) -> None:
        """Initialize the trace builder."""
        self._events: list[DecisionTraceEvent] = []
        self._current_trace: dict | None = None

    def add_event(
        self,
        event_type: str,
        **details: Any,
    ) -> None:
        """Add an event to the trace.

        Args:
            event_type: Type of event.
            **details: Event details.
        """
        event = DecisionTraceEvent(
            event_id=f"evt_{uuid.uuid4().hex[:16]}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details,
        )
        self._events.append(event)

    def build_trace(
        self,
        decision_id: str,
        candidates: list,
        selected: Any,
        context: Any,
    ) -> dict:
        """Build a complete trace.

        Args:
            decision_id: The final decision ID.
            candidates: All considered candidates.
            selected: The selected candidate.
            context: Decision context.

        Returns:
            Complete trace dictionary.
        """
        self._current_trace = {
            "trace_id": f"trace_{uuid.uuid4().hex[:16]}",
            "decision_id": decision_id,
            "candidates_considered": [c.candidate_id for c in candidates],
            "candidates_rejected": [c.candidate_id for c in candidates if c.candidate_id != selected.candidate_id],
            "selected_candidate": selected.candidate_id,
            "events": [(e.event_id, e.event_type, e.timestamp) for e in self._events],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return self._current_trace

    def build(self) -> dict:
        """Build current trace.

        Returns:
            The current trace or empty dict.
        """
        return self._current_trace or {}

    def clear(self) -> None:
        """Clear the trace."""
        self._events.clear()
        self._current_trace = None
