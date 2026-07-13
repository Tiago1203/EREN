"""Runtime events for the Cognitive Operating System.

Defines all events published by the Cognitive Runtime during its lifecycle.
Events are immutable and published via the global Event Bus.

Event Flow:
RuntimeStarted -> RuntimeInitialized -> SessionCreated -> PlanningStarted
-> KnowledgeRequested -> MemoryRequested -> ReasoningStarted -> DecisionCreated
-> ActionGenerated -> ContextUpdated -> SessionCompleted -> RuntimeCompleted

On failure:
RuntimeFailed
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> str:
    """Return the current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """Return a fresh unique event identifier."""
    return uuid4().hex


class RuntimeEventType(str, Enum):
    """Catalog of runtime event types.

    These events track the complete lifecycle of the Cognitive Runtime,
    from initialization through the first cognitive cycle to completion.
    """

    # Lifecycle Events
    RUNTIME_STARTED = "runtime_started"
    RUNTIME_INITIALIZED = "runtime_initialized"
    RUNTIME_BOOT_STARTED = "runtime_boot_started"
    RUNTIME_BOOT_COMPLETED = "runtime_boot_completed"
    RUNTIME_VALIDATION_STARTED = "runtime_validation_started"
    RUNTIME_VALIDATION_COMPLETED = "runtime_validation_completed"

    # Session Events
    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"

    # Cognitive Cycle Events
    COGNITIVE_CYCLE_STARTED = "cognitive_cycle_started"
    COGNITIVE_CYCLE_COMPLETED = "cognitive_cycle_completed"
    COGNITIVE_CYCLE_FAILED = "cognitive_cycle_failed"

    # Planning Events
    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"
    PLANNING_FAILED = "planning_failed"

    # Knowledge Events
    KNOWLEDGE_REQUESTED = "knowledge_requested"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    KNOWLEDGE_FAILED = "knowledge_failed"

    # Memory Events
    MEMORY_REQUESTED = "memory_requested"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_FAILED = "memory_failed"

    # Reasoning Events
    REASONING_STARTED = "reasoning_started"
    REASONING_COMPLETED = "reasoning_completed"
    REASONING_FAILED = "reasoning_failed"

    # Decision Events
    DECISION_CREATED = "decision_created"
    DECISION_APPLIED = "decision_applied"
    DECISION_FAILED = "decision_failed"

    # Tool Events
    ACTION_GENERATED = "action_generated"
    ACTION_EXECUTED = "action_executed"
    ACTION_FAILED = "action_failed"

    # Context Events
    CONTEXT_UPDATED = "context_updated"
    CONTEXT_SNAPSHOT = "context_snapshot"

    # Completion Events
    RUNTIME_COMPLETED = "runtime_completed"
    RUNTIME_FAILED = "runtime_failed"
    RUNTIME_SHUTDOWN = "runtime_shutdown"


class RuntimeEvent(BaseModel):
    """Base class for all runtime events.

    Events are immutable (frozen=True) and carry metadata for
    correlation and tracing across the cognitive cycle.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(default_factory=_new_id, description="Unique event identifier")
    event_type: RuntimeEventType = Field(description="Type of the event")
    timestamp: str = Field(default_factory=_utcnow, description="Event timestamp (UTC)")
    correlation_id: str = Field(default="", description="Correlation ID for tracing")
    session_id: str = Field(default="", description="Session ID")
    runtime_id: str = Field(default="", description="Runtime instance ID")
    source: str = Field(default="runtime", description="Event source component")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload")

    def with_context(
        self,
        correlation_id: str | None = None,
        session_id: str | None = None,
        runtime_id: str | None = None,
    ) -> "RuntimeEvent":
        """Return a copy with updated context fields."""
        updates: dict[str, Any] = {}
        if correlation_id is not None:
            updates["correlation_id"] = correlation_id
        if session_id is not None:
            updates["session_id"] = session_id
        if runtime_id is not None:
            updates["runtime_id"] = runtime_id
        return self.model_copy(update=updates)


# =============================================================================
# Lifecycle Events
# =============================================================================


class RuntimeStarted(RuntimeEvent):
    """Runtime has started initialization.

    Payload:
    - runtime_id: Runtime instance ID
    - version: Runtime version
    - start_time: Start timestamp
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_STARTED


class RuntimeInitialized(RuntimeEvent):
    """Runtime has completed initialization.

    Payload:
    - runtime_id: Runtime instance ID
    - initialization_time_ms: Time taken to initialize
    - modules_loaded: Number of modules loaded
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_INITIALIZED


class RuntimeBootStarted(RuntimeEvent):
    """Runtime boot process has started.

    Payload:
    - runtime_id: Runtime instance ID
    - boot_sequence: Boot sequence being executed
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_BOOT_STARTED


class RuntimeBootCompleted(RuntimeEvent):
    """Runtime boot process has completed.

    Payload:
    - runtime_id: Runtime instance ID
    - boot_time_ms: Time taken to boot
    - components_ready: Number of components ready
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_BOOT_COMPLETED


class RuntimeValidationStarted(RuntimeEvent):
    """Runtime validation has started.

    Payload:
    - runtime_id: Runtime instance ID
    - validation_checks: List of checks to perform
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_VALIDATION_STARTED


class RuntimeValidationCompleted(RuntimeEvent):
    """Runtime validation has completed.

    Payload:
    - runtime_id: Runtime instance ID
    - validation_time_ms: Time taken to validate
    - valid: Whether validation passed
    - errors: List of validation errors (if any)
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_VALIDATION_COMPLETED


# =============================================================================
# Session Events
# =============================================================================


class SessionCreated(RuntimeEvent):
    """A new cognitive session has been created.

    Payload:
    - session_id: Session ID
    - user_id: User ID (if available)
    - session_type: Type of session
    - created_at: Creation timestamp
    """

    event_type: RuntimeEventType = RuntimeEventType.SESSION_CREATED


class SessionStarted(RuntimeEvent):
    """A cognitive session has started.

    Payload:
    - session_id: Session ID
    - started_at: Start timestamp
    - correlation_id: Correlation ID for this session
    """

    event_type: RuntimeEventType = RuntimeEventType.SESSION_STARTED


class SessionCompleted(RuntimeEvent):
    """A cognitive session has completed.

    Payload:
    - session_id: Session ID
    - completed_at: Completion timestamp
    - duration_ms: Session duration
    - final_stage: Final processing stage
    """

    event_type: RuntimeEventType = RuntimeEventType.SESSION_COMPLETED


class SessionFailed(RuntimeEvent):
    """A cognitive session has failed.

    Payload:
    - session_id: Session ID
    - error: Error message
    - failed_at: Failure timestamp
    - stage: Stage where failure occurred
    """

    event_type: RuntimeEventType = RuntimeEventType.SESSION_FAILED


# =============================================================================
# Cognitive Cycle Events
# =============================================================================


class CognitiveCycleStarted(RuntimeEvent):
    """A cognitive cycle has started.

    Payload:
    - session_id: Session ID
    - cycle_id: Cycle identifier
    - intent: Initial intent
    - context: Initial context summary
    """

    event_type: RuntimeEventType = RuntimeEventType.COGNITIVE_CYCLE_STARTED


class CognitiveCycleCompleted(RuntimeEvent):
    """A cognitive cycle has completed.

    Payload:
    - session_id: Session ID
    - cycle_id: Cycle identifier
    - duration_ms: Cycle duration
    - stages_completed: Number of stages completed
    - result: Cycle result summary
    """

    event_type: RuntimeEventType = RuntimeEventType.COGNITIVE_CYCLE_COMPLETED


class CognitiveCycleFailed(RuntimeEvent):
    """A cognitive cycle has failed.

    Payload:
    - session_id: Session ID
    - cycle_id: Cycle identifier
    - error: Error message
    - failed_stage: Stage where failure occurred
    """

    event_type: RuntimeEventType = RuntimeEventType.COGNITIVE_CYCLE_FAILED


# =============================================================================
# Planning Events
# =============================================================================


class PlanningStarted(RuntimeEvent):
    """Planning has started.

    Payload:
    - session_id: Session ID
    - planning_id: Planning session ID
    - input: Planning input summary
    """

    event_type: RuntimeEventType = RuntimeEventType.PLANNING_STARTED


class PlanningCompleted(RuntimeEvent):
    """Planning has completed.

    Payload:
    - session_id: Session ID
    - planning_id: Planning session ID
    - plan_steps: Number of steps in plan
    - duration_ms: Planning duration
    """

    event_type: RuntimeEventType = RuntimeEventType.PLANNING_COMPLETED


class PlanningFailed(RuntimeEvent):
    """Planning has failed.

    Payload:
    - session_id: Session ID
    - planning_id: Planning session ID
    - error: Error message
    """

    event_type: RuntimeEventType = RuntimeEventType.PLANNING_FAILED


# =============================================================================
# Knowledge Events
# =============================================================================


class KnowledgeRequested(RuntimeEvent):
    """Knowledge has been requested.

    Payload:
    - session_id: Session ID
    - query: Knowledge query
    - sources: Knowledge sources consulted
    """

    event_type: RuntimeEventType = RuntimeEventType.KNOWLEDGE_REQUESTED


class KnowledgeRetrieved(RuntimeEvent):
    """Knowledge has been retrieved.

    Payload:
    - session_id: Session ID
    - results_count: Number of results
    - relevance_scores: Relevance scores
    - duration_ms: Retrieval duration
    """

    event_type: RuntimeEventType = RuntimeEventType.KNOWLEDGE_RETRIEVED


class KnowledgeFailed(RuntimeEvent):
    """Knowledge retrieval has failed.

    Payload:
    - session_id: Session ID
    - error: Error message
    - query: Failed query
    """

    event_type: RuntimeEventType = RuntimeEventType.KNOWLEDGE_FAILED


# =============================================================================
# Memory Events
# =============================================================================


class MemoryRequested(RuntimeEvent):
    """Memory has been requested.

    Payload:
    - session_id: Session ID
    - query: Memory query
    - memory_types: Memory types searched
    """

    event_type: RuntimeEventType = RuntimeEventType.MEMORY_REQUESTED


class MemoryRetrieved(RuntimeEvent):
    """Memory has been retrieved.

    Payload:
    - session_id: Session ID
    - results_count: Number of results
    - memory_ids: Retrieved memory IDs
    - duration_ms: Retrieval duration
    """

    event_type: RuntimeEventType = RuntimeEventType.MEMORY_RETRIEVED


class MemoryFailed(RuntimeEvent):
    """Memory retrieval has failed.

    Payload:
    - session_id: Session ID
    - error: Error message
    - query: Failed query
    """

    event_type: RuntimeEventType = RuntimeEventType.MEMORY_FAILED


# =============================================================================
# Reasoning Events
# =============================================================================


class ReasoningStarted(RuntimeEvent):
    """Reasoning has started.

    Payload:
    - session_id: Session ID
    - evidence_count: Number of evidence items
    - strategy: Reasoning strategy used
    """

    event_type: RuntimeEventType = RuntimeEventType.REASONING_STARTED


class ReasoningCompleted(RuntimeEvent):
    """Reasoning has completed.

    Payload:
    - session_id: Session ID
    - hypotheses_count: Number of hypotheses generated
    - best_hypothesis: Best hypothesis ID
    - duration_ms: Reasoning duration
    """

    event_type: RuntimeEventType = RuntimeEventType.REASONING_COMPLETED


class ReasoningFailed(RuntimeEvent):
    """Reasoning has failed.

    Payload:
    - session_id: Session ID
    - error: Error message
    - evidence_ids: Evidence that was being processed
    """

    event_type: RuntimeEventType = RuntimeEventType.REASONING_FAILED


# =============================================================================
# Decision Events
# =============================================================================


class DecisionCreated(RuntimeEvent):
    """A decision has been created.

    Payload:
    - session_id: Session ID
    - decision_id: Decision ID
    - decision_type: Type of decision
    - based_on_hypothesis: Hypothesis ID used
    - confidence: Decision confidence
    """

    event_type: RuntimeEventType = RuntimeEventType.DECISION_CREATED


class DecisionApplied(RuntimeEvent):
    """A decision has been applied.

    Payload:
    - session_id: Session ID
    - decision_id: Decision ID
    - result: Application result
    """

    event_type: RuntimeEventType = RuntimeEventType.DECISION_APPLIED


class DecisionFailed(RuntimeEvent):
    """A decision has failed.

    Payload:
    - session_id: Session ID
    - decision_id: Decision ID
    - error: Error message
    """

    event_type: RuntimeEventType = RuntimeEventType.DECISION_FAILED


# =============================================================================
# Action Events
# =============================================================================


class ActionGenerated(RuntimeEvent):
    """An action has been generated.

    Payload:
    - session_id: Session ID
    - action_id: Action ID
    - action_type: Type of action
    - parameters: Action parameters
    """

    event_type: RuntimeEventType = RuntimeEventType.ACTION_GENERATED


class ActionExecuted(RuntimeEvent):
    """An action has been executed.

    Payload:
    - session_id: Session ID
    - action_id: Action ID
    - result: Execution result
    - duration_ms: Execution duration
    """

    event_type: RuntimeEventType = RuntimeEventType.ACTION_EXECUTED


class ActionFailed(RuntimeEvent):
    """An action has failed.

    Payload:
    - session_id: Session ID
    - action_id: Action ID
    - error: Error message
    """

    event_type: RuntimeEventType = RuntimeEventType.ACTION_FAILED


# =============================================================================
# Context Events
# =============================================================================


class ContextUpdated(RuntimeEvent):
    """The cognitive context has been updated.

    Payload:
    - session_id: Session ID
    - context_id: Context ID
    - updated_fields: Fields that were updated
    - version: New context version
    """

    event_type: RuntimeEventType = RuntimeEventType.CONTEXT_UPDATED


class ContextSnapshot(RuntimeEvent):
    """A context snapshot has been taken.

    Payload:
    - session_id: Session ID
    - context_id: Context ID
    - snapshot_data: Snapshot data
    """

    event_type: RuntimeEventType = RuntimeEventType.CONTEXT_SNAPSHOT


# =============================================================================
# Completion Events
# =============================================================================


class RuntimeCompleted(RuntimeEvent):
    """Runtime has completed successfully.

    Payload:
    - runtime_id: Runtime instance ID
    - completed_at: Completion timestamp
    - total_duration_ms: Total runtime duration
    - cycles_completed: Number of cognitive cycles
    - sessions_completed: Number of sessions completed
    - metrics: Final runtime metrics
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_COMPLETED


class RuntimeFailed(RuntimeEvent):
    """Runtime has failed.

    Payload:
    - runtime_id: Runtime instance ID
    - failed_at: Failure timestamp
    - error: Error message
    - stage: Stage where failure occurred
    - can_recover: Whether the failure is recoverable
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_FAILED


class RuntimeShutdown(RuntimeEvent):
    """Runtime has been shut down.

    Payload:
    - runtime_id: Runtime instance ID
    - shutdown_at: Shutdown timestamp
    - reason: Shutdown reason
    """

    event_type: RuntimeEventType = RuntimeEventType.RUNTIME_SHUTDOWN


# =============================================================================
# Event Registry
# =============================================================================


EVENT_TYPE_TO_CLASS: dict[RuntimeEventType, type[RuntimeEvent]] = {
    # Lifecycle
    RuntimeEventType.RUNTIME_STARTED: RuntimeStarted,
    RuntimeEventType.RUNTIME_INITIALIZED: RuntimeInitialized,
    RuntimeEventType.RUNTIME_BOOT_STARTED: RuntimeBootStarted,
    RuntimeEventType.RUNTIME_BOOT_COMPLETED: RuntimeBootCompleted,
    RuntimeEventType.RUNTIME_VALIDATION_STARTED: RuntimeValidationStarted,
    RuntimeEventType.RUNTIME_VALIDATION_COMPLETED: RuntimeValidationCompleted,
    # Session
    RuntimeEventType.SESSION_CREATED: SessionCreated,
    RuntimeEventType.SESSION_STARTED: SessionStarted,
    RuntimeEventType.SESSION_COMPLETED: SessionCompleted,
    RuntimeEventType.SESSION_FAILED: SessionFailed,
    # Cognitive Cycle
    RuntimeEventType.COGNITIVE_CYCLE_STARTED: CognitiveCycleStarted,
    RuntimeEventType.COGNITIVE_CYCLE_COMPLETED: CognitiveCycleCompleted,
    RuntimeEventType.COGNITIVE_CYCLE_FAILED: CognitiveCycleFailed,
    # Planning
    RuntimeEventType.PLANNING_STARTED: PlanningStarted,
    RuntimeEventType.PLANNING_COMPLETED: PlanningCompleted,
    RuntimeEventType.PLANNING_FAILED: PlanningFailed,
    # Knowledge
    RuntimeEventType.KNOWLEDGE_REQUESTED: KnowledgeRequested,
    RuntimeEventType.KNOWLEDGE_RETRIEVED: KnowledgeRetrieved,
    RuntimeEventType.KNOWLEDGE_FAILED: KnowledgeFailed,
    # Memory
    RuntimeEventType.MEMORY_REQUESTED: MemoryRequested,
    RuntimeEventType.MEMORY_RETRIEVED: MemoryRetrieved,
    RuntimeEventType.MEMORY_FAILED: MemoryFailed,
    # Reasoning
    RuntimeEventType.REASONING_STARTED: ReasoningStarted,
    RuntimeEventType.REASONING_COMPLETED: ReasoningCompleted,
    RuntimeEventType.REASONING_FAILED: ReasoningFailed,
    # Decision
    RuntimeEventType.DECISION_CREATED: DecisionCreated,
    RuntimeEventType.DECISION_APPLIED: DecisionApplied,
    RuntimeEventType.DECISION_FAILED: DecisionFailed,
    # Action
    RuntimeEventType.ACTION_GENERATED: ActionGenerated,
    RuntimeEventType.ACTION_EXECUTED: ActionExecuted,
    RuntimeEventType.ACTION_FAILED: ActionFailed,
    # Context
    RuntimeEventType.CONTEXT_UPDATED: ContextUpdated,
    RuntimeEventType.CONTEXT_SNAPSHOT: ContextSnapshot,
    # Completion
    RuntimeEventType.RUNTIME_COMPLETED: RuntimeCompleted,
    RuntimeEventType.RUNTIME_FAILED: RuntimeFailed,
    RuntimeEventType.RUNTIME_SHUTDOWN: RuntimeShutdown,
}


def create_runtime_event(
    event_type: RuntimeEventType,
    runtime_id: str = "",
    session_id: str = "",
    correlation_id: str = "",
    **payload: Any,
) -> RuntimeEvent:
    """Factory function to create runtime events by type.

    Args:
        event_type: The type of event to create.
        runtime_id: Runtime instance ID.
        session_id: Session ID.
        correlation_id: Correlation ID for tracing.
        **payload: Additional payload fields.

    Returns:
        An instance of the appropriate RuntimeEvent subclass.
    """
    event_class = EVENT_TYPE_TO_CLASS.get(event_type)
    if event_class is None:
        raise ValueError(f"Unknown runtime event type: {event_type}")

    return event_class(
        runtime_id=runtime_id,
        session_id=session_id,
        correlation_id=correlation_id,
        payload=payload,
    )
