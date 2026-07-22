"""Event models for EREN's internal event system.

Defines the immutable :class:`Event` base, the :class:`EventType` catalog, and
one declarative model per cognitive lifecycle event (VoiceReceived …
ResponseGenerated).

Architecture only. These are **declarative Pydantic v2 models** — no business
logic, no AI, no dispatching. Events are *facts that happened*; producing and
consuming them belongs to the engines and the event bus, not to the models.

Design:

- Events are **immutable** (`frozen=True`): once emitted, a fact does not change.
- Every event carries common metadata (id, type, timestamp, correlation) so any
  subscriber can trace, order and correlate it without coupling to the producer.
- The domain-specific payload is kept **generic** (`payload: dict[str, object]`)
  so events stay decoupled from other engines' concrete types. Each specific
  event documents the payload keys it is expected to carry.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    """Return the current UTC timestamp (timezone-aware)."""
    return datetime.now(UTC)


def _new_id() -> str:
    """Return a fresh unique event identifier."""
    return uuid4().hex


class EventType(str, Enum):
    """Catalog of internal event types across the cognitive lifecycle.

    Events are organized in categories:
    - Input/Output: Voice and response events
    - Intent: Intent detection and processing
    - Planning: Plan creation and management
    - Knowledge: Knowledge retrieval operations
    - Memory: Memory operations
    - Reasoning: Reasoning engine events
    - Diagnostic: Diagnostic engine events
    - Workflow: Workflow management events
    - System: Error and system events
    """

    # Input/Output
    VOICE_INPUT_RECEIVED = "voice_input_received"
    VOICE_OUTPUT_GENERATED = "voice_output_generated"

    # Intent
    INTENT_RECEIVED = "intent_received"
    INTENT_DETECTED = "intent_detected"

    # Planning
    PLAN_CREATED = "plan_created"
    PLAN_UPDATED = "plan_updated"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"

    # Knowledge
    KNOWLEDGE_REQUESTED = "knowledge_requested"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    KNOWLEDGE_SEARCH_FAILED = "knowledge_search_failed"

    # Memory
    MEMORY_REQUESTED = "memory_requested"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_STORED = "memory_stored"

    # Reasoning
    REASONING_STARTED = "reasoning_started"
    REASONING_FINISHED = "reasoning_finished"
    HYPOTHESIS_GENERATED = "hypothesis_generated"
    HYPOTHESIS_EVALUATED = "hypothesis_evaluated"

    # Diagnostic
    DIAGNOSTIC_STARTED = "diagnostic_started"
    DIAGNOSTIC_FINISHED = "diagnostic_finished"
    DIAGNOSTIC_COMPLETED = "diagnostic_completed"

    # Workflow
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_FINISHED = "workflow_finished"
    WORKFLOW_COMPLETED = "workflow_completed"
    STEP_EXECUTED = "step_executed"

    # Tools
    TOOL_REQUESTED = "tool_requested"
    TOOL_EXECUTED = "tool_executed"
    TOOL_FAILED = "tool_failed"

    # Response
    RESPONSE_READY = "response_ready"
    RESPONSE_GENERATED = "response_generated"

    # System
    ENGINE_ERROR = "engine_error"
    ENGINE_INITIALIZED = "engine_initialized"
    ENGINE_SHUTDOWN = "engine_shutdown"


class Event(BaseModel):
    """Base class for every internal event.

    An event is an immutable record that *something happened*. Subscribers react
    to events without knowing which component produced them, keeping producers
    and consumers fully decoupled.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(
        default_factory=_new_id, description="Unique id of this event."
    )
    type: EventType = Field(description="Discriminator identifying the event kind.")
    timestamp: datetime = Field(
        default_factory=_utcnow, description="When the event occurred (UTC)."
    )
    correlation_id: str = Field(
        default="", description="Request id tying the event to one interaction."
    )
    session_id: str = Field(
        default="", description="Session id grouping events of a conversation."
    )
    source: str = Field(
        default="", description="Name of the engine/component that emitted the event."
    )
    payload: dict[str, object] = Field(
        default_factory=dict,
        description="Opaque, event-specific data (see each event's docs).",
    )

    def with_context(
        self,
        correlation_id: str | None = None,
        session_id: str | None = None,
        source: str | None = None,
    ) -> Event:
        """Return a copy with updated context fields."""
        updates: dict[str, object] = {}
        if correlation_id is not None:
            updates["correlation_id"] = correlation_id
        if session_id is not None:
            updates["session_id"] = session_id
        if source is not None:
            updates["source"] = source
        return self.model_copy(update=updates)


# =============================================================================
# Voice Events
# =============================================================================


class VoiceInputReceived(Event):
    """A voice input was received from the user.

    Payload may carry:
    - ``text``: transcribed text
    - ``language``: detected language
    - ``duration``: audio duration in seconds
    - ``format``: audio format (e.g., "wav", "mp3")
    """

    type: EventType = EventType.VOICE_INPUT_RECEIVED


class VoiceOutputGenerated(Event):
    """A voice output was generated for the user.

    Payload may carry:
    - ``text``: text to be spoken
    - ``language``: output language
    - ``engine``: TTS engine used
    """

    type: EventType = EventType.VOICE_OUTPUT_GENERATED


# =============================================================================
# Intent Events
# =============================================================================


class IntentReceived(Event):
    """An intent was received for processing.

    Payload may carry:
    - ``raw_text``: original user input
    - ``entities``: extracted entities
    - ``urgency``: detected urgency level
    """

    type: EventType = EventType.INTENT_RECEIVED


class IntentDetected(Event):
    """An intent was inferred from the input.

    Payload may carry:
    - ``intent``: detected intent type
    - ``confidence``: confidence score (0-1)
    - ``entities``: structured entities
    """

    type: EventType = EventType.INTENT_DETECTED


# =============================================================================
# Plan Events
# =============================================================================


class PlanCreated(Event):
    """The planner produced a plan.

    Payload may carry:
    - ``step_count``: number of steps in the plan
    - ``priority``: task priority
    - ``estimated_duration``: estimated execution time
    """

    type: EventType = EventType.PLAN_CREATED


class PlanUpdated(Event):
    """An existing plan was updated.

    Payload may carry:
    - ``previous_steps``: previous step count
    - ``new_steps``: updated step count
    - ``reason``: reason for update
    """

    type: EventType = EventType.PLAN_UPDATED


class PlanCompleted(Event):
    """A plan was completed successfully.

    Payload may carry:
    - ``actual_steps``: actual steps executed
    - ``duration``: total execution time
    - ``outcome``: execution outcome
    """

    type: EventType = EventType.PLAN_COMPLETED


class PlanFailed(Event):
    """A plan failed during execution.

    Payload may carry:
    - ``failed_step``: step that failed
    - ``error``: error message
    - ``can_retry``: whether the plan can be retried
    """

    type: EventType = EventType.PLAN_FAILED


# =============================================================================
# Knowledge Events
# =============================================================================


class KnowledgeRequested(Event):
    """A knowledge retrieval was requested.

    Payload may carry:
    - ``query``: search query
    - ``sources``: requested sources
    - ``filters``: search filters
    """

    type: EventType = EventType.KNOWLEDGE_REQUESTED


class KnowledgeRetrieved(Event):
    """Knowledge was retrieved.

    Payload may carry:
    - ``document_count``: number of documents retrieved
    - ``source_types``: types of sources consulted
    - ``relevance_scores``: relevance scores for results
    """

    type: EventType = EventType.KNOWLEDGE_RETRIEVED


class KnowledgeSearchFailed(Event):
    """A knowledge search failed.

    Payload may carry:
    - ``query``: failed query
    - ``error``: error message
    - ``fallback_used``: whether a fallback was used
    """

    type: EventType = EventType.KNOWLEDGE_SEARCH_FAILED


# =============================================================================
# Memory Events
# =============================================================================


class MemoryRequested(Event):
    """A memory retrieval was requested.

    Payload may carry:
    - ``query``: search query
    - ``memory_type``: type of memory (short/long term)
    - ``filters``: retrieval filters
    """

    type: EventType = EventType.MEMORY_REQUESTED


class MemoryRetrieved(Event):
    """Memory was retrieved.

    Payload may carry:
    - ``entries``: retrieved memory entries
    - ``memory_type``: type of memory accessed
    - ``age``: age of retrieved memories
    """

    type: EventType = EventType.MEMORY_RETRIEVED


class MemoryStored(Event):
    """Information was stored in memory.

    Payload may carry:
    - ``memory_type``: type of memory
    - ``importance``: importance score
    - ``ttl``: time to live (if applicable)
    """

    type: EventType = EventType.MEMORY_STORED


# =============================================================================
# Reasoning Events
# =============================================================================


class ReasoningStarted(Event):
    """Reasoning began.

    Payload may carry:
    - ``question``: question being reasoned about
    - ``context``: reasoning context
    """

    type: EventType = EventType.REASONING_STARTED


class ReasoningFinished(Event):
    """Reasoning finished.

    Payload may carry:
    - ``confidence``: overall confidence
    - ``citation_count``: number of citations
    - ``conclusions``: reasoning conclusions
    """

    type: EventType = EventType.REASONING_FINISHED


class HypothesisGenerated(Event):
    """A hypothesis was generated.

    Payload may carry:
    - ``hypothesis``: hypothesis text
    - ``evidence``: supporting evidence
    - ``confidence``: hypothesis confidence
    """

    type: EventType = EventType.HYPOTHESIS_GENERATED


class HypothesisEvaluated(Event):
    """A hypothesis was evaluated.

    Payload may carry:
    - ``hypothesis``: evaluated hypothesis
    - ``score``: evaluation score
    - ``decision``: accept/reject decision
    """

    type: EventType = EventType.HYPOTHESIS_EVALUATED


# =============================================================================
# Diagnostic Events
# =============================================================================


class DiagnosticStarted(Event):
    """A diagnostic process started.

    Payload may carry:
    - ``device_id``: device being diagnosed
    - ``symptoms``: reported symptoms
    """

    type: EventType = EventType.DIAGNOSTIC_STARTED


class DiagnosticFinished(Event):
    """A diagnostic process finished.

    Payload may carry:
    - ``findings``: diagnostic findings
    - ``confidence``: diagnostic confidence
    """

    type: EventType = EventType.DIAGNOSTIC_FINISHED


class DiagnosticCompleted(Event):
    """A diagnostic completed.

    Payload may carry:
    - ``diagnosis``: final diagnosis
    - ``recommendations``: recommended actions
    - ``confidence``: overall confidence
    """

    type: EventType = EventType.DIAGNOSTIC_COMPLETED


# =============================================================================
# Workflow Events
# =============================================================================


class WorkflowStarted(Event):
    """A workflow started.

    Payload may carry:
    - ``workflow_id``: workflow identifier
    - ``workflow_type``: type of workflow
    - ``initial_state``: starting state
    """

    type: EventType = EventType.WORKFLOW_STARTED


class WorkflowFinished(Event):
    """A workflow finished.

    Payload may carry:
    - ``workflow_id``: workflow identifier
    - ``final_state``: final state
    - ``duration``: total duration
    """

    type: EventType = EventType.WORKFLOW_FINISHED


class WorkflowCompleted(Event):
    """A workflow completed successfully.

    Payload may carry:
    - ``workflow_id``: workflow identifier
    - ``outcome``: workflow outcome
    - ``steps_completed``: number of steps completed
    """

    type: EventType = EventType.WORKFLOW_COMPLETED


class StepExecuted(Event):
    """A workflow step was executed.

    Payload may carry:
    - ``workflow_id``: parent workflow
    - ``step_id``: step identifier
    - ``status``: execution status
    - ``duration``: step duration
    """

    type: EventType = EventType.STEP_EXECUTED


# =============================================================================
# Tool Events
# =============================================================================


class ToolRequested(Event):
    """A tool was requested.

    Payload may carry:
    - ``tool_name``: name of the tool
    - ``parameters``: tool parameters
    """

    type: EventType = EventType.TOOL_REQUESTED


class ToolExecuted(Event):
    """A tool was invoked.

    Payload may carry:
    - ``tool_name``: name of the tool
    - ``status``: execution status
    - ``result``: tool result (if successful)
    - ``duration``: execution duration
    """

    type: EventType = EventType.TOOL_EXECUTED


class ToolFailed(Event):
    """A tool execution failed.

    Payload may carry:
    - ``tool_name``: name of the tool
    - ``error``: error message
    - ``can_retry``: whether the tool can be retried
    """

    type: EventType = EventType.TOOL_FAILED


# =============================================================================
# Response Events
# =============================================================================


class ResponseReady(Event):
    """A response is ready to be delivered.

    Payload may carry:
    - ``response_type``: type of response
    - ``confidence``: response confidence
    - ``needs_confirmation``: whether user confirmation is needed
    """

    type: EventType = EventType.RESPONSE_READY


class ResponseGenerated(Event):
    """The final response was produced.

    Payload may carry:
    - ``length``: response length
    - ``citation_count``: number of citations
    - ``format``: response format
    """

    type: EventType = EventType.RESPONSE_GENERATED


# =============================================================================
# System Events
# =============================================================================


class EngineError(Event):
    """An engine encountered an error.

    Payload may carry:
    - ``engine``: name of the engine
    - ``error_type``: type of error
    - ``message``: error message
    - ``can_recover``: whether the engine can recover
    """

    type: EventType = EventType.ENGINE_ERROR


class EngineInitialized(Event):
    """An engine was initialized.

    Payload may carry:
    - ``engine``: name of the engine
    - ``config``: engine configuration
    """

    type: EventType = EventType.ENGINE_INITIALIZED


class EngineShutdown(Event):
    """An engine was shut down.

    Payload may carry:
    - ``engine``: name of the engine
    - ``reason``: shutdown reason
    """

    type: EventType = EventType.ENGINE_SHUTDOWN


# =============================================================================
# Event type registry for runtime discovery
# =============================================================================


EVENT_TYPE_TO_CLASS: dict[EventType, type[Event]] = {
    # Voice
    EventType.VOICE_INPUT_RECEIVED: VoiceInputReceived,
    EventType.VOICE_OUTPUT_GENERATED: VoiceOutputGenerated,
    # Intent
    EventType.INTENT_RECEIVED: IntentReceived,
    EventType.INTENT_DETECTED: IntentDetected,
    # Plan
    EventType.PLAN_CREATED: PlanCreated,
    EventType.PLAN_UPDATED: PlanUpdated,
    EventType.PLAN_COMPLETED: PlanCompleted,
    EventType.PLAN_FAILED: PlanFailed,
    # Knowledge
    EventType.KNOWLEDGE_REQUESTED: KnowledgeRequested,
    EventType.KNOWLEDGE_RETRIEVED: KnowledgeRetrieved,
    EventType.KNOWLEDGE_SEARCH_FAILED: KnowledgeSearchFailed,
    # Memory
    EventType.MEMORY_REQUESTED: MemoryRequested,
    EventType.MEMORY_RETRIEVED: MemoryRetrieved,
    EventType.MEMORY_STORED: MemoryStored,
    # Reasoning
    EventType.REASONING_STARTED: ReasoningStarted,
    EventType.REASONING_FINISHED: ReasoningFinished,
    EventType.HYPOTHESIS_GENERATED: HypothesisGenerated,
    EventType.HYPOTHESIS_EVALUATED: HypothesisEvaluated,
    # Diagnostic
    EventType.DIAGNOSTIC_STARTED: DiagnosticStarted,
    EventType.DIAGNOSTIC_FINISHED: DiagnosticFinished,
    EventType.DIAGNOSTIC_COMPLETED: DiagnosticCompleted,
    # Workflow
    EventType.WORKFLOW_STARTED: WorkflowStarted,
    EventType.WORKFLOW_FINISHED: WorkflowFinished,
    EventType.WORKFLOW_COMPLETED: WorkflowCompleted,
    EventType.STEP_EXECUTED: StepExecuted,
    # Tools
    EventType.TOOL_REQUESTED: ToolRequested,
    EventType.TOOL_EXECUTED: ToolExecuted,
    EventType.TOOL_FAILED: ToolFailed,
    # Response
    EventType.RESPONSE_READY: ResponseReady,
    EventType.RESPONSE_GENERATED: ResponseGenerated,
    # System
    EventType.ENGINE_ERROR: EngineError,
    EventType.ENGINE_INITIALIZED: EngineInitialized,
    EventType.ENGINE_SHUTDOWN: EngineShutdown,
}


def create_event(
    event_type: EventType,
    source: str = "",
    correlation_id: str = "",
    session_id: str = "",
    **payload: object,
) -> Event:
    """Factory function to create events by type.

    Args:
        event_type: The type of event to create.
        source: The engine/component emitting the event.
        correlation_id: Request correlation ID.
        session_id: Session ID.
        **payload: Additional payload fields.

    Returns:
        An instance of the appropriate Event subclass.

    Raises:
        ValueError: If event_type is not recognized.
    """
    event_class = EVENT_TYPE_TO_CLASS.get(event_type)
    if event_class is None:
        raise ValueError(f"Unknown event type: {event_type}")

    return event_class(
        source=source,
        correlation_id=correlation_id,
        session_id=session_id,
        payload=payload,
    )
