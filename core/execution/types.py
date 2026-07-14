"""Execution types and enums for EREN OS Cognitive Execution Coordinator.

Defines all types, enums, and value objects used by the execution system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Execution States
# =============================================================================


class ExecutionState(str, Enum):
    """States for the execution lifecycle."""

    CREATED = "created"
    INITIALIZING = "initializing"
    CREATING_SESSION = "creating_session"
    ROUTING = "routing"
    PIPELINE_EXECUTION = "pipeline_execution"
    UPDATING_CONTEXT = "updating_context"
    COMPLETING_SESSION = "completing_session"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal(cls, state: ExecutionState) -> bool:
        """Check if state is terminal."""
        return state in (cls.COMPLETED, cls.FAILED, cls.CANCELLED)

    @classmethod
    def can_start(cls, state: ExecutionState) -> bool:
        """Check if execution can start from this state."""
        return state in (cls.CREATED,)

    @classmethod
    def can_cancel(cls, state: ExecutionState) -> bool:
        """Check if execution can cancel from this state."""
        return state not in (cls.COMPLETED, cls.FAILED, cls.CANCELLED)


# =============================================================================
# Execution Policies
# =============================================================================


class ExecutionPolicy(str, Enum):
    """Policies for execution behavior."""

    STRICT = "strict"
    GRACEFUL = "graceful"
    RESILIENT = "resilient"
    PARALLEL = "parallel"


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True, slots=True)
class ExecutionMetadata:
    """Metadata for an execution."""

    execution_id: str
    intent_type: str
    intent_data: dict
    user_id: str = ""
    tenant_id: str = ""
    hospital_id: str = ""
    priority: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "intent_type": self.intent_type,
            "intent_data": self.intent_data,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "hospital_id": self.hospital_id,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ExecutionResult:
    """Result of a complete execution cycle."""

    execution_id: str
    session_id: str
    status: ExecutionState
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_ms: int = 0

    # Sub-results
    routing_result: dict | None = None
    pipeline_result: dict | None = None
    context_updates: dict = field(default_factory=dict)

    # Timing
    routing_time_ms: int = 0
    pipeline_time_ms: int = 0
    context_update_time_ms: int = 0

    # Errors
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Events
    events: list[dict] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)

    # Metadata
    metadata: dict = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == ExecutionState.COMPLETED

    @property
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status == ExecutionState.FAILED

    @property
    def was_cancelled(self) -> bool:
        """Check if execution was cancelled."""
        return self.status == ExecutionState.CANCELLED

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "routing_result": self.routing_result,
            "pipeline_result": self.pipeline_result,
            "context_updates": self.context_updates,
            "routing_time_ms": self.routing_time_ms,
            "pipeline_time_ms": self.pipeline_time_ms,
            "context_update_time_ms": self.context_update_time_ms,
            "errors": self.errors,
            "warnings": self.warnings,
            "events": self.events,
            "trace": self.trace,
            "metadata": self.metadata,
        }


@dataclass
class ComponentStatus:
    """Status of a registered component."""

    name: str
    available: bool = False
    healthy: bool = False
    last_check: datetime = field(default_factory=lambda: datetime.now(UTC))
    error: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "available": self.available,
            "healthy": self.healthy,
            "last_check": self.last_check.isoformat(),
            "error": self.error,
        }


@dataclass
class ValidationResult:
    """Result of execution validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    component_statuses: list[ComponentStatus] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "component_statuses": [s.to_dict() for s in self.component_statuses],
        }
