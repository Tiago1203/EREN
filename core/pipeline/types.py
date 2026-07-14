"""Pipeline types and enums for EREN OS Cognitive Capability Pipeline.

Defines all types, enums, and value objects used by the pipeline system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Pipeline States
# =============================================================================


class PipelineState(str, Enum):
    """States for the overall pipeline lifecycle."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal(cls, state: PipelineState) -> bool:
        """Check if state is terminal (no further transitions)."""
        return state in (cls.COMPLETED, cls.FAILED, cls.CANCELLED)

    @classmethod
    def can_start(cls, state: PipelineState) -> bool:
        """Check if pipeline can start from this state."""
        return state in (cls.READY,)

    @classmethod
    def can_pause(cls, state: PipelineState) -> bool:
        """Check if pipeline can pause from this state."""
        return state in (cls.RUNNING, cls.WAITING)

    @classmethod
    def can_resume(cls, state: PipelineState) -> bool:
        """Check if pipeline can resume from this state."""
        return state in (cls.PAUSED,)

    @classmethod
    def can_cancel(cls, state: PipelineState) -> bool:
        """Check if pipeline can cancel from this state."""
        return state in (cls.CREATED, cls.READY, cls.RUNNING, cls.WAITING, cls.PAUSED)


class StageState(str, Enum):
    """States for individual pipeline stages."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SKIPPED = "skipped"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal(cls, state: StageState) -> bool:
        """Check if state is terminal."""
        return state in (cls.SKIPPED, cls.FAILED, cls.COMPLETED, cls.CANCELLED)


# =============================================================================
# Stage Types
# =============================================================================


class StageType(str, Enum):
    """Types of pipeline stages."""

    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    REASONING = "reasoning"
    DECISION = "decision"
    TOOL = "tool"
    CONTEXT_UPDATE = "context_update"
    CUSTOM = "custom"


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True, slots=True)
class StageMetadata:
    """Metadata for a pipeline stage."""

    stage_name: str
    stage_type: StageType
    description: str = ""
    required: bool = True
    optional: bool = False
    retry_count: int = 0
    timeout_seconds: float = 30.0
    tags: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "stage_type": self.stage_type.value,
            "description": self.description,
            "required": self.required,
            "optional": self.optional,
            "retry_count": self.retry_count,
            "timeout_seconds": self.timeout_seconds,
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
        }


@dataclass
class StageResult:
    """Result of a single stage execution."""

    stage_name: str
    stage_type: StageType
    status: StageState
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_ms: int = 0
    output: Any = None
    metadata: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    retry_attempts: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "metadata": self.metadata,
            "errors": self.errors,
            "warnings": self.warnings,
            "retry_attempts": self.retry_attempts,
        }

    @property
    def is_success(self) -> bool:
        """Check if stage completed successfully."""
        return self.status == StageState.COMPLETED

    @property
    def is_failure(self) -> bool:
        """Check if stage failed."""
        return self.status == StageState.FAILED

    @property
    def is_skipped(self) -> bool:
        """Check if stage was skipped."""
        return self.status == StageState.SKIPPED


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""

    pipeline_id: str
    pipeline_name: str
    status: PipelineState
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_ms: int = 0
    completed_stages: list[str] = field(default_factory=list)
    failed_stage: str | None = None
    stage_results: list[StageResult] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    correlation_id: str = ""
    session_id: str = ""
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_name": self.pipeline_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "completed_stages": self.completed_stages,
            "failed_stage": self.failed_stage,
            "stage_results": [r.to_dict() for r in self.stage_results],
            "metrics": self.metrics,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "errors": self.errors,
            "metadata": self.metadata,
        }

    @property
    def is_success(self) -> bool:
        """Check if pipeline completed successfully."""
        return self.status == PipelineState.COMPLETED

    @property
    def is_failure(self) -> bool:
        """Check if pipeline failed."""
        return self.status == PipelineState.FAILED

    @property
    def was_cancelled(self) -> bool:
        """Check if pipeline was cancelled."""
        return self.status == PipelineState.CANCELLED

    @property
    def success_rate(self) -> float:
        """Calculate stage success rate."""
        if not self.stage_results:
            return 0.0
        successful = sum(1 for r in self.stage_results if r.is_success)
        return successful / len(self.stage_results) * 100


# =============================================================================
# Configuration Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for pipeline execution."""

    pipeline_name: str
    pipeline_id: str
    stage_timeout_seconds: float = 30.0
    pipeline_timeout_seconds: float = 300.0
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_events: bool = True
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pipeline_name": self.pipeline_name,
            "pipeline_id": self.pipeline_id,
            "stage_timeout_seconds": self.stage_timeout_seconds,
            "pipeline_timeout_seconds": self.pipeline_timeout_seconds,
            "enable_metrics": self.enable_metrics,
            "enable_tracing": self.enable_tracing,
            "enable_events": self.enable_events,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
        }


# =============================================================================
# Policy Types
# =============================================================================


class ExecutionPolicy(str, Enum):
    """Policies for pipeline execution."""

    STOP_ON_FAILURE = "stop_on_failure"
    CONTINUE_ON_FAILURE = "continue_on_failure"
    RETRY_STAGE = "retry_stage"
    STRICT_EXECUTION = "strict_execution"
    SKIP_OPTIONAL = "skip_optional"


# =============================================================================
# Intent Types
# =============================================================================


@dataclass
class PipelineIntent:
    """Intent that triggers pipeline execution."""

    intent_id: str
    intent_type: str
    intent_data: dict = field(default_factory=dict)
    priority: int = 0
    correlation_id: str = ""
    session_id: str = ""
    user_id: str = ""
    hospital_id: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type,
            "intent_data": self.intent_data,
            "priority": self.priority,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "hospital_id": self.hospital_id,
            "metadata": self.metadata,
        }
