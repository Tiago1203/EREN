"""Context Snapshot — point-in-time captures of contexts.

Snapshots provide point-in-time captures of context state for:
- Debugging
- Rollback
- Audit compliance
- Distributed sync

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .cognitive_context import CognitiveContext
from .context_types import (
    Confidence,
    ContextStatus,
    DeviceContext,
    DiagnosisResult,
    Evidence,
    HospitalContext,
    IncidentContext,
    IntentResult,
    Observation,
    PlanResult,
    ProcessingMetadata,
    ProcessingStage,
    ResponseResult,
    ToolUsage,
    UserContext,
    WorkflowResult,
)

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Immutable point-in-time snapshot of a CognitiveContext.

    Snapshots capture the complete state of a context at a specific
    moment in time. They are used for:
    - Audit trails
    - Debugging
    - Rollback
    - Distributed synchronization
    """

    # Identity
    snapshot_id: str
    context_id: str
    version: int
    timestamp: str

    # Context
    user: UserContext
    hospital: HospitalContext
    device: DeviceContext
    incident: IncidentContext

    # Processing
    status: ContextStatus
    current_stage: ProcessingStage
    processing: ProcessingMetadata

    # Results
    intent: IntentResult
    plan: PlanResult
    retrieved_memories: tuple[str, ...]
    retrieved_knowledge: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    hypotheses: tuple[Observation, ...]  # Note: Using Observation for simplicity
    diagnosis: DiagnosisResult
    workflow: WorkflowResult
    tools_used: tuple[ToolUsage, ...]
    response: ResponseResult

    # Confidence
    overall_confidence: Confidence

    # Statistics
    evidence_count: int
    hypothesis_count: int
    observation_count: int
    blackboard_entry_count: int

    @classmethod
    def from_context(
        cls,
        context: CognitiveContext,
        snapshot_id: str = "",
    ) -> ContextSnapshot:
        """Create a snapshot from a context.

        Args:
            context: The context to snapshot
            snapshot_id: Optional snapshot ID (auto-generated if not provided)

        Returns:
            A new ContextSnapshot.
        """
        import uuid

        if not snapshot_id:
            snapshot_id = f"snap_{uuid.uuid4().hex[:16]}"

        return cls(
            snapshot_id=snapshot_id,
            context_id=context.context_id,
            version=context.version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user=context.user,
            hospital=context.hospital,
            device=context.device,
            incident=context.incident,
            status=context.status,
            current_stage=context.current_stage,
            processing=context.processing,
            intent=context.intent,
            plan=context.plan,
            retrieved_memories=context.retrieved_memories,
            retrieved_knowledge=context.retrieved_knowledge,
            evidence=context.evidence,
            hypotheses=context.hypotheses,
            diagnosis=context.diagnosis,
            workflow=context.workflow,
            tools_used=context.tools_used,
            response=context.response,
            overall_confidence=context.overall_confidence,
            evidence_count=len(context.evidence),
            hypothesis_count=len(context.hypotheses),
            observation_count=len(context.observations),
            blackboard_entry_count=len(context.blackboard),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "snapshot_id": self.snapshot_id,
            "context_id": self.context_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "status": self.status.name if self.status else None,
            "current_stage": self.current_stage.name if self.current_stage else None,
            "evidence_count": self.evidence_count,
            "hypothesis_count": self.hypothesis_count,
            "confidence_score": (
                self.overall_confidence.score
                if self.overall_confidence else 0
            ),
        }

    def summary(self) -> str:
        """Get a human-readable summary.

        Returns:
            Summary string.
        """
        conf = self.overall_confidence.score if self.overall_confidence else 0
        return (
            f"Snapshot({self.snapshot_id[:12]}... "
            f"ctx={self.context_id[:12]}... "
            f"status={self.status.name} "
            f"evidence={self.evidence_count} "
            f"hypotheses={self.hypothesis_count} "
            f"confidence={conf:.2f})"
        )


@dataclass
class SnapshotDiff:
    """Represents differences between two snapshots."""

    snapshot_a: str  # Earlier snapshot ID
    snapshot_b: str  # Later snapshot ID
    timestamp_a: str
    timestamp_b: str

    # Changes
    status_changed: bool = False
    from_status: ContextStatus | None = None
    to_status: ContextStatus | None = None

    new_evidence_count: int = 0
    new_hypothesis_count: int = 0
    new_observations: int = 0
    confidence_delta: float = 0.0

    stage_advanced: bool = False
    from_stage: ProcessingStage | None = None
    to_stage: ProcessingStage | None = None

    changes: list[str] = field(default_factory=list)

    @classmethod
    def compare(
        cls,
        snapshot_a: ContextSnapshot,
        snapshot_b: ContextSnapshot,
    ) -> SnapshotDiff:
        """Compare two snapshots and return differences.

        Args:
            snapshot_a: Earlier snapshot
            snapshot_b: Later snapshot

        Returns:
            SnapshotDiff with differences.
        """
        diff = cls(
            snapshot_a=snapshot_a.snapshot_id,
            snapshot_b=snapshot_b.snapshot_id,
            timestamp_a=snapshot_a.timestamp,
            timestamp_b=snapshot_b.timestamp,
        )

        # Status change
        if snapshot_a.status != snapshot_b.status:
            diff.status_changed = True
            diff.from_status = snapshot_a.status
            diff.to_status = snapshot_b.status
            diff.changes.append(f"Status: {snapshot_a.status.name} -> {snapshot_b.status.name}")

        # Evidence count
        diff.new_evidence_count = snapshot_b.evidence_count - snapshot_a.evidence_count
        if diff.new_evidence_count > 0:
            diff.changes.append(f"Added {diff.new_evidence_count} evidence")

        # Hypothesis count
        diff.new_hypothesis_count = snapshot_b.hypothesis_count - snapshot_a.hypothesis_count
        if diff.new_hypothesis_count > 0:
            diff.changes.append(f"Added {diff.new_hypothesis_count} hypotheses")

        # Observations
        diff.new_observations = snapshot_b.observation_count - snapshot_a.observation_count
        if diff.new_observations > 0:
            diff.changes.append(f"Added {diff.new_observations} observations")

        # Confidence delta
        conf_a = snapshot_a.overall_confidence.score if snapshot_a.overall_confidence else 0
        conf_b = snapshot_b.overall_confidence.score if snapshot_b.overall_confidence else 0
        diff.confidence_delta = conf_b - conf_a
        if abs(diff.confidence_delta) > 0.01:
            diff.changes.append(f"Confidence: {diff_a:.2f} -> {conf_b:.2f} ({diff.confidence_delta:+.2f})")

        # Stage advancement
        if snapshot_a.current_stage != snapshot_b.current_stage:
            diff.stage_advanced = True
            diff.from_stage = snapshot_a.current_stage
            diff.to_stage = snapshot_b.current_stage
            diff.changes.append(
                f"Stage: {snapshot_a.current_stage.name} -> {snapshot_b.current_stage.name}"
            )

        return diff


@dataclass
class SnapshotRegistry:
    """Registry for managing context snapshots."""

    snapshots: dict[str, list[ContextSnapshot]] = field(default_factory=dict)
    latest_snapshots: dict[str, ContextSnapshot] = field(default_factory=dict)

    def add_snapshot(self, snapshot: ContextSnapshot) -> None:
        """Add a snapshot to the registry.

        Args:
            snapshot: The snapshot to add
        """
        context_id = snapshot.context_id

        if context_id not in self.snapshots:
            self.snapshots[context_id] = []

        self.snapshots[context_id].append(snapshot)
        self.latest_snapshots[context_id] = snapshot

    def get_snapshots(self, context_id: str) -> list[ContextSnapshot]:
        """Get all snapshots for a context.

        Args:
            context_id: The context ID

        Returns:
            List of snapshots, oldest first.
        """
        return list(self.snapshots.get(context_id, []))

    def get_latest(self, context_id: str) -> ContextSnapshot | None:
        """Get the latest snapshot for a context.

        Args:
            context_id: The context ID

        Returns:
            The latest snapshot or None.
        """
        return self.latest_snapshots.get(context_id)

    def compare_versions(
        self,
        context_id: str,
        version_a: int,
        version_b: int,
    ) -> SnapshotDiff | None:
        """Compare two versions of a context.

        Args:
            context_id: The context ID
            version_a: Earlier version number
            version_b: Later version number

        Returns:
            SnapshotDiff or None if versions not found.
        """
        snapshots = self.snapshots.get(context_id, [])

        snap_a = None
        snap_b = None

        for snap in snapshots:
            if snap.version == version_a:
                snap_a = snap
            if snap.version == version_b:
                snap_b = snap

        if snap_a and snap_b:
            return SnapshotDiff.compare(snap_a, snap_b)

        return None
