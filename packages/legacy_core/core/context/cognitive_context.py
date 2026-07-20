"""Cognitive Context — the shared context for all motors.

The Cognitive Context is a single, shared context that all motors work with.
No motor creates copies. All motors enrich the same context.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .context_types import (
    BlackboardEntry,
    BlackboardEntryType,
    Confidence,
    ConfidenceLevel,
    ContextMetadata,
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
class CognitiveContext:
    """The shared cognitive context for EREN.

    This is the central data structure that all motors work with.
    No motor creates copies — all motors read from and write to this context.

    The context contains:
    - Identity information (IDs, timestamps)
    - User and environmental context
    - Processing results from each stage
    - Evidence and hypotheses
    - Final results
    - Confidence information
    - Processing metadata

    The context is IMMUTABLE — modifications create new versions.
    This enables versioning, history, and audit trails.
    """

    # Identity
    context_id: str
    version: int = 1
    created_at: str = ""
    updated_at: str = ""

    # Context
    user: UserContext = field(default_factory=UserContext)
    hospital: HospitalContext = field(default_factory=HospitalContext)
    device: DeviceContext = field(default_factory=DeviceContext)
    incident: IncidentContext = field(default_factory=IncidentContext)

    # Processing
    status: ContextStatus = ContextStatus.INITIALIZING
    current_stage: ProcessingStage = ProcessingStage.INTENTION
    processing: ProcessingMetadata = field(default_factory=ProcessingMetadata)

    # Intent and Plan
    intent: IntentResult = field(default_factory=IntentResult)
    plan: PlanResult = field(default_factory=PlanResult)

    # Memory and Knowledge
    retrieved_memories: tuple[str, ...] = field(default_factory=tuple)  # Memory IDs
    retrieved_knowledge: tuple[str, ...] = field(default_factory=tuple)  # Knowledge IDs

    # Evidence and Hypotheses
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    hypotheses: tuple[Hypothesis, ...] = field(default_factory=tuple)
    observations: tuple[Observation, ...] = field(default_factory=tuple)

    # Results
    diagnosis: DiagnosisResult = field(default_factory=DiagnosisResult)
    workflow: WorkflowResult = field(default_factory=WorkflowResult)
    tools_used: tuple[ToolUsage, ...] = field(default_factory=tuple)
    response: ResponseResult = field(default_factory=ResponseResult)

    # Confidence
    overall_confidence: Confidence = field(default_factory=Confidence)

    # Blackboard (shared workspace)
    blackboard: tuple[BlackboardEntry, ...] = field(default_factory=tuple)

    # Metadata
    metadata: ContextMetadata = field(default_factory=ContextMetadata)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        correlation_id: str = "",
        session_id: str = "",
        user: UserContext | None = None,
        hospital: HospitalContext | None = None,
        device: DeviceContext | None = None,
        incident: IncidentContext | None = None,
    ) -> CognitiveContext:
        """Create a new cognitive context.

        Args:
            correlation_id: Correlation ID for tracking
            session_id: Session ID
            user: User context
            hospital: Hospital context
            device: Device context
            incident: Incident context

        Returns:
            A new CognitiveContext instance.
        """
        now = datetime.now(UTC).isoformat()
        context_id = f"ctx_{uuid.uuid4().hex[:16]}"

        return cls(
            context_id=context_id,
            version=1,
            created_at=now,
            updated_at=now,
            user=user or UserContext(),
            hospital=hospital or HospitalContext(),
            device=device or DeviceContext(),
            incident=incident or IncidentContext(),
            processing=ProcessingMetadata(
                correlation_id=correlation_id,
                session_id=session_id,
                started_at=now,
                stage=ProcessingStage.INTENTION,
            ),
            metadata=ContextMetadata(created_at=now, updated_at=now),
        )

    # =========================================================================
    # Status Methods
    # =========================================================================

    def update_status(
        self,
        status: ContextStatus,
        stage: ProcessingStage | None = None,
    ) -> CognitiveContext:
        """Return new context with updated status."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            status=status,
            current_stage=stage or self.current_stage,
            updated_at=now,
            processing=replace(
                self.processing,
                stage=stage or self.processing.stage,
                updated_at=now,
            ),
        )

    def complete(
        self,
        response: ResponseResult,
        confidence: Confidence | None = None,
    ) -> CognitiveContext:
        """Return new context marked as completed."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            status=ContextStatus.COMPLETED,
            current_stage=ProcessingStage.RESPONSE,
            updated_at=now,
            completed_at=now,
            response=response,
            overall_confidence=confidence or self.overall_confidence,
        )

    def fail(self, error: dict) -> CognitiveContext:
        """Return new context marked as failed."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        new_errors = self.processing.errors + (error,)
        return replace(
            self,
            status=ContextStatus.FAILED,
            updated_at=now,
            processing=replace(
                self.processing,
                errors=new_errors,
            ),
        )

    # =========================================================================
    # Intent and Plan Methods
    # =========================================================================

    def set_intent(
        self,
        intent: IntentResult,
    ) -> CognitiveContext:
        """Return new context with intent result."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            intent=intent,
            current_stage=ProcessingStage.CONTEXT_BUILDING,
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.CONTEXT_BUILDING,
            ),
        )

    def set_plan(
        self,
        plan: PlanResult,
    ) -> CognitiveContext:
        """Return new context with plan result."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            plan=plan,
            current_stage=ProcessingStage.KNOWLEDGE_RETRIEVAL,
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.KNOWLEDGE_RETRIEVAL,
            ),
        )

    # =========================================================================
    # Evidence and Hypothesis Methods
    # =========================================================================

    def add_evidence(
        self,
        evidence: Evidence,
    ) -> CognitiveContext:
        """Return new context with added evidence."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            evidence=self.evidence + (evidence,),
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.EVIDENCE_COLLECTION,
            ),
        )

    def add_hypothesis(
        self,
        hypothesis: Hypothesis,
    ) -> CognitiveContext:
        """Return new context with added hypothesis."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            hypotheses=self.hypotheses + (hypothesis,),
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.HYPOTHESIS_GENERATION,
            ),
        )

    def add_observation(
        self,
        observation: Observation,
    ) -> CognitiveContext:
        """Return new context with added observation."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            observations=self.observations + (observation,),
            updated_at=now,
        )

    def update_hypothesis(
        self,
        hypothesis_id: str,
        updates: dict,
    ) -> CognitiveContext:
        """Return new context with updated hypothesis."""
        from dataclasses import replace
        new_hypotheses = []
        for h in self.hypotheses:
            if h.hypothesis_id == hypothesis_id:
                new_hypotheses.append(replace(h, **updates))
            else:
                new_hypotheses.append(h)
        return replace(
            self,
            hypotheses=tuple(new_hypotheses),
            updated_at=datetime.now(UTC).isoformat(),
        )

    def rank_hypotheses(self) -> CognitiveContext:
        """Return new context with ranked hypotheses."""
        from dataclasses import replace
        sorted_hypotheses = sorted(
            self.hypotheses,
            key=lambda h: (h.probability * (h.confidence.score if h.confidence else 0.5)),
            reverse=True,
        )
        ranked = []
        for i, h in enumerate(sorted_hypotheses):
            ranked.append(replace(h, rank=i + 1))
        return replace(self, hypotheses=tuple(ranked))

    # =========================================================================
    # Memory and Knowledge Methods
    # =========================================================================

    def add_retrieved_memories(
        self,
        memory_ids: list[str],
    ) -> CognitiveContext:
        """Return new context with added memory IDs."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            retrieved_memories=self.retrieved_memories + tuple(memory_ids),
            updated_at=now,
        )

    def add_retrieved_knowledge(
        self,
        knowledge_ids: list[str],
    ) -> CognitiveContext:
        """Return new context with added knowledge IDs."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            retrieved_knowledge=self.retrieved_knowledge + tuple(knowledge_ids),
            updated_at=now,
        )

    # =========================================================================
    # Result Methods
    # =========================================================================

    def set_diagnosis(
        self,
        diagnosis: DiagnosisResult,
    ) -> CognitiveContext:
        """Return new context with diagnosis result."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            diagnosis=diagnosis,
            current_stage=ProcessingStage.WORKFLOW_SELECTION,
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.WORKFLOW_SELECTION,
            ),
        )

    def set_workflow(
        self,
        workflow: WorkflowResult,
    ) -> CognitiveContext:
        """Return new context with workflow result."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            workflow=workflow,
            current_stage=ProcessingStage.EXECUTION,
            updated_at=now,
            processing=replace(
                self.processing,
                stage=ProcessingStage.EXECUTION,
            ),
        )

    def add_tool_usage(
        self,
        tool_usage: ToolUsage,
    ) -> CognitiveContext:
        """Return new context with added tool usage."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            tools_used=self.tools_used + (tool_usage,),
            updated_at=now,
        )

    # =========================================================================
    # Blackboard Methods
    # =========================================================================

    def add_blackboard_entry(
        self,
        entry: BlackboardEntry,
    ) -> CognitiveContext:
        """Return new context with added blackboard entry."""
        now = datetime.now(UTC).isoformat()
        from dataclasses import replace
        return replace(
            self,
            blackboard=self.blackboard + (entry,),
            updated_at=now,
        )

    def get_active_entries(
        self,
        entry_type: BlackboardEntryType | None = None,
    ) -> list[BlackboardEntry]:
        """Get active blackboard entries."""
        entries = [e for e in self.blackboard if e.is_active()]
        if entry_type:
            entries = [e for e in entries if e.entry_type == entry_type]
        return entries

    def get_entries_by_author(
        self,
        author_engine: str,
    ) -> list[BlackboardEntry]:
        """Get blackboard entries by author engine."""
        return [e for e in self.blackboard if e.author_engine == author_engine]

    # =========================================================================
    # Confidence Methods
    # =========================================================================

    def recalculate_confidence(self) -> CognitiveContext:
        """Recalculate overall confidence from all components."""
        scores: list[float] = []
        reasons: list[str] = []

        # From evidence
        for e in self.evidence:
            if e.confidence and e.confidence.score > 0:
                scores.append(e.confidence.score)
                reasons.extend(list(e.confidence.reasons))

        # From hypotheses
        for h in self.hypotheses:
            if h.probability > 0:
                scores.append(h.probability)
            if h.confidence and h.confidence.score > 0:
                scores.append(h.confidence.score)

        # From diagnosis
        if self.diagnosis.confidence and self.diagnosis.confidence.score > 0:
            scores.append(self.diagnosis.confidence.score)

        # Calculate average
        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 0.0

        # Determine level
        if avg_score >= 0.9:
            level = ConfidenceLevel.CERTAIN
        elif avg_score >= 0.75:
            level = ConfidenceLevel.VERY_HIGH
        elif avg_score >= 0.5:
            level = ConfidenceLevel.HIGH
        elif avg_score >= 0.25:
            level = ConfidenceLevel.MODERATE
        elif avg_score >= 0.1:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.VERY_LOW

        from dataclasses import replace
        return replace(
            self,
            overall_confidence=Confidence(
                level=level,
                score=avg_score,
                reasons=tuple(reasons),
            ),
        )

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_highest_ranked_hypothesis(self) -> Hypothesis | None:
        """Get the highest ranked hypothesis."""
        if not self.hypotheses:
            return None
        return min(self.hypotheses, key=lambda h: h.rank)

    def get_confirmed_hypotheses(self) -> list[Hypothesis]:
        """Get confirmed hypotheses."""
        return [h for h in self.hypotheses if h.status == "confirmed"]

    def get_active_hypotheses(self) -> list[Hypothesis]:
        """Get active (non-rejected) hypotheses."""
        return [h for h in self.hypotheses if h.status != "rejected"]

    def get_evidence_by_source(self, source: str) -> list[Evidence]:
        """Get evidence by source."""
        return [e for e in self.evidence if e.source.value == source]

    # =========================================================================
    # String Representation
    # =========================================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"CognitiveContext("
            f"id={self.context_id[:12]}..., "
            f"status={self.status.name}, "
            f"stage={self.current_stage.name}, "
            f"evidence={len(self.evidence)}, "
            f"hypotheses={len(self.hypotheses)})"
        )
