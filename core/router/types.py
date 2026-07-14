"""Router types and enums for EREN OS Cognitive Capability Router.

Defines all types, enums, and value objects used by the router system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Router States
# =============================================================================


class RouterState(str, Enum):
    """States for the router lifecycle."""

    CREATED = "created"
    ANALYZING = "analyzing"
    MATCHING = "matching"
    SELECTING = "selecting"
    READY = "ready"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal(cls, state: "RouterState") -> bool:
        """Check if state is terminal."""
        return state in (cls.READY, cls.FAILED, cls.CANCELLED)

    @classmethod
    def can_route(cls, state: "RouterState") -> bool:
        """Check if router can route from this state."""
        return state in (cls.READY, cls.CREATED)


# =============================================================================
# Routing Policies
# =============================================================================


class RoutingPolicy(str, Enum):
    """Policies for pipeline selection."""

    FIRST_MATCH = "first_match"
    HIGHEST_SCORE = "highest_score"
    PRIORITY = "priority"
    FALLBACK = "fallback"
    STRICT = "strict"
    WEIGHTED = "weighted"


# =============================================================================
# Match Results
# =============================================================================


class MatchResult(str, Enum):
    """Result of matching intent to pipeline."""

    EXACT = "exact"
    PARTIAL = "partial"
    POTENTIAL = "potential"
    NO_MATCH = "no_match"


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True, slots=True)
class PipelineMetadata:
    """Metadata for a routable pipeline."""

    pipeline_name: str
    pipeline_id: str
    description: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 0
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    required_context: tuple[str, ...] = field(default_factory=tuple)
    intent_types: tuple[str, ...] = field(default_factory=tuple)
    excluded_intent_types: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pipeline_name": self.pipeline_name,
            "pipeline_id": self.pipeline_id,
            "description": self.description,
            "tags": list(self.tags),
            "priority": self.priority,
            "required_capabilities": list(self.required_capabilities),
            "required_context": list(self.required_context),
            "intent_types": list(self.intent_types),
            "excluded_intent_types": list(self.excluded_intent_types),
            "metadata": self.metadata,
        }


@dataclass
class CandidatePipeline:
    """A pipeline candidate for selection."""

    metadata: PipelineMetadata
    score: float = 0.0
    match_result: MatchResult = MatchResult.NO_MATCH
    match_reasons: list[str] = field(default_factory=list)
    is_eligible: bool = True
    eligibility_reason: str = ""
    matched_rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pipeline_name": self.metadata.pipeline_name,
            "score": self.score,
            "match_result": self.match_result.value,
            "match_reasons": self.match_reasons,
            "is_eligible": self.is_eligible,
            "eligibility_reason": self.eligibility_reason,
            "matched_rules": self.matched_rules,
        }


@dataclass
class RoutingResult:
    """Result of routing operation."""

    state: RouterState
    selected_pipeline: PipelineMetadata | None = None
    candidate_pipelines: list[CandidatePipeline] = field(default_factory=list)
    reason: str = ""
    policy_used: RoutingPolicy = RoutingPolicy.FIRST_MATCH
    duration_ms: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if routing succeeded."""
        return self.state == RouterState.READY and self.selected_pipeline is not None

    @property
    def is_failure(self) -> bool:
        """Check if routing failed."""
        return self.state == RouterState.FAILED

    @property
    def was_cancelled(self) -> bool:
        """Check if routing was cancelled."""
        return self.state == RouterState.CANCELLED

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "state": self.state.value,
            "selected_pipeline": self.selected_pipeline.to_dict() if self.selected_pipeline else None,
            "candidate_pipelines": [c.to_dict() for c in self.candidate_pipelines],
            "reason": self.reason,
            "policy_used": self.policy_used.value,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


@dataclass
class RoutingRule:
    """A routing rule for matching intents to pipelines."""

    rule_id: str
    name: str
    description: str = ""
    intent_type: str = ""
    tags: list[str] = field(default_factory=list)
    priority: int = 0
    weight: float = 1.0
    pipeline_name: str = ""
    conditions: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "intent_type": self.intent_type,
            "tags": self.tags,
            "priority": self.priority,
            "weight": self.weight,
            "pipeline_name": self.pipeline_name,
            "conditions": self.conditions,
            "metadata": self.metadata,
        }


# =============================================================================
# Context Types
# =============================================================================


@dataclass
class RoutingContext:
    """Context for routing decision."""

    intent_type: str
    intent_data: dict = field(default_factory=dict)
    session_id: str = ""
    correlation_id: str = ""
    user_id: str = ""
    tenant_id: str = ""
    hospital_id: str = ""
    priority: int = 0
    available_capabilities: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    context_data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "intent_type": self.intent_type,
            "intent_data": self.intent_data,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "hospital_id": self.hospital_id,
            "priority": self.priority,
            "available_capabilities": self.available_capabilities,
            "required_capabilities": self.required_capabilities,
            "context_data": self.context_data,
            "metadata": self.metadata,
        }
