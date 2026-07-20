"""Routing Result for EREN OS Cognitive Capability Router.

Represents the result of a routing operation.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.router.types import (
    CandidatePipeline,
    PipelineMetadata,
    RouterState,
    RoutingPolicy,
)
from core.router.types import (
    RoutingResult as RoutingResultType,
)

if TYPE_CHECKING:
    pass


@dataclass
class RoutingResult:
    """Result of routing operation.

    Contains the selected pipeline and all candidate information.
    """

    # State
    state: RouterState = RouterState.CREATED
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_ms: int = 0

    # Selection result
    selected_pipeline: PipelineMetadata | None = None
    candidate_pipelines: list[CandidatePipeline] = field(default_factory=list)

    # Selection info
    reason: str = ""
    policy_used: RoutingPolicy = RoutingPolicy.FIRST_MATCH

    # Errors and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Trace
    trace_entries: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        if self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_success(self) -> bool:
        """Check if routing succeeded."""
        with self._lock:
            return self.state == RouterState.READY and self.selected_pipeline is not None

    @property
    def is_failure(self) -> bool:
        """Check if routing failed."""
        with self._lock:
            return self.state == RouterState.FAILED

    @property
    def was_cancelled(self) -> bool:
        """Check if routing was cancelled."""
        with self._lock:
            return self.state == RouterState.CANCELLED

    @property
    def candidate_count(self) -> int:
        """Get number of candidates."""
        with self._lock:
            return len(self.candidate_pipelines)

    @property
    def eligible_candidates(self) -> list[CandidatePipeline]:
        """Get eligible candidates."""
        with self._lock:
            return [c for c in self.candidate_pipelines if c.is_eligible]

    @property
    def top_candidates(self) -> list[CandidatePipeline]:
        """Get top candidates sorted by score."""
        with self._lock:
            sorted_candidates = sorted(
                self.candidate_pipelines,
                key=lambda c: c.score,
                reverse=True,
            )
            return sorted_candidates

    # =========================================================================
    # State Management
    # =========================================================================

    def set_state(self, state: RouterState) -> None:
        """Set router state.

        Args:
            state: New state.
        """
        with self._lock:
            self.state = state

    def start(self) -> None:
        """Mark routing as started."""
        with self._lock:
            self.started_at = datetime.now(UTC)
            self.state = RouterState.ANALYZING

    def complete(self) -> None:
        """Mark routing as completed."""
        with self._lock:
            self.finished_at = datetime.now(UTC)
            self.duration_ms = int(
                (self.finished_at - self.started_at).total_seconds() * 1000
            )
            if self.selected_pipeline:
                self.state = RouterState.READY
            else:
                self.state = RouterState.FAILED

    def fail(self, error: str) -> None:
        """Mark routing as failed.

        Args:
            error: Error message.
        """
        with self._lock:
            self.finished_at = datetime.now(UTC)
            self.duration_ms = int(
                (self.finished_at - self.started_at).total_seconds() * 1000
            )
            self.errors.append(error)
            self.state = RouterState.FAILED

    def cancel(self) -> None:
        """Mark routing as cancelled."""
        with self._lock:
            self.finished_at = datetime.now(UTC)
            self.duration_ms = int(
                (self.finished_at - self.started_at).total_seconds() * 1000
            )
            self.state = RouterState.CANCELLED

    # =========================================================================
    # Selection Management
    # =========================================================================

    def set_selected_pipeline(
        self,
        pipeline: PipelineMetadata,
        reason: str = "",
    ) -> None:
        """Set the selected pipeline.

        Args:
            pipeline: Selected pipeline metadata.
            reason: Selection reason.
        """
        with self._lock:
            self.selected_pipeline = pipeline
            self.reason = reason

    def add_candidate(self, candidate: CandidatePipeline) -> None:
        """Add a candidate pipeline.

        Args:
            candidate: Candidate pipeline.
        """
        with self._lock:
            self.candidate_pipelines.append(candidate)

    def set_policy(self, policy: RoutingPolicy) -> None:
        """Set the routing policy used.

        Args:
            policy: Routing policy.
        """
        with self._lock:
            self.policy_used = policy

    # =========================================================================
    # Trace and Events
    # =========================================================================

    def add_trace_entry(
        self,
        operation: str,
        details: dict | None = None,
    ) -> None:
        """Add a trace entry.

        Args:
            operation: Operation name.
            details: Operation details.
        """
        with self._lock:
            self.trace_entries.append({
                "timestamp": datetime.now(UTC).isoformat(),
                "operation": operation,
                "details": details or {},
            })

    def add_event(
        self,
        event_type: str,
        data: dict | None = None,
    ) -> None:
        """Add an event.

        Args:
            event_type: Event type.
            data: Event data.
        """
        with self._lock:
            self.events.append({
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                "data": data or {},
            })

    def add_warning(self, warning: str) -> None:
        """Add a warning.

        Args:
            warning: Warning message.
        """
        with self._lock:
            self.warnings.append(warning)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "state": self.state.value,
                "started_at": self.started_at.isoformat(),
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "duration_ms": self.duration_ms,
                "selected_pipeline": self.selected_pipeline.to_dict() if self.selected_pipeline else None,
                "candidate_pipelines": [c.to_dict() for c in self.candidate_pipelines],
                "reason": self.reason,
                "policy_used": self.policy_used.value,
                "errors": list(self.errors),
                "warnings": list(self.warnings),
                "trace_entries": list(self.trace_entries),
                "events": list(self.events),
                "metadata": dict(self.metadata),
                "candidate_count": len(self.candidate_pipelines),
                "eligible_count": len(self.eligible_candidates),
            }

    def to_routing_result_type(self) -> RoutingResultType:
        """Convert to RoutingResult type.

        Returns:
            RoutingResultType instance.
        """
        with self._lock:
            return RoutingResultType(
                state=self.state,
                selected_pipeline=self.selected_pipeline,
                candidate_pipelines=list(self.candidate_pipelines),
                reason=self.reason,
                policy_used=self.policy_used,
                duration_ms=self.duration_ms,
                started_at=self.started_at,
                finished_at=self.finished_at,
                errors=list(self.errors),
                warnings=list(self.warnings),
                trace=list(self.trace_entries),
                events=list(self.events),
                metadata=dict(self.metadata),
            )

    def get_summary(self) -> str:
        """Get a summary string.

        Returns:
            Summary string.
        """
        with self._lock:
            lines = [
                "==================================================",
                "EREN OS ROUTING RESULT",
                "==================================================",
                f"State: {self.state.value}",
                f"Policy: {self.policy_used.value}",
                f"Duration: {self.duration_ms}ms",
                f"Candidates: {len(self.candidate_pipelines)}",
            ]

            if self.selected_pipeline:
                lines.append(f"Selected: {self.selected_pipeline.pipeline_name}")
                lines.append(f"Reason: {self.reason}")

            if self.errors:
                lines.append(f"Errors: {len(self.errors)}")
                for error in self.errors[:3]:
                    lines.append(f"  - {error}")

            lines.append("==================================================")
            return "\n".join(lines)
