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

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    """Return the current UTC timestamp (timezone-aware)."""
    return datetime.now(timezone.utc)


def _new_id() -> str:
    """Return a fresh unique event identifier."""
    return uuid4().hex


class EventType(str, Enum):
    """Catalog of internal event types across the cognitive lifecycle."""

    VOICE_RECEIVED = "voice_received"
    INTENT_DETECTED = "intent_detected"
    PLAN_CREATED = "plan_created"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    REASONING_STARTED = "reasoning_started"
    REASONING_FINISHED = "reasoning_finished"
    TOOL_EXECUTED = "tool_executed"
    DIAGNOSTIC_COMPLETED = "diagnostic_completed"
    WORKFLOW_COMPLETED = "workflow_completed"
    RESPONSE_GENERATED = "response_generated"


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


class VoiceReceived(Event):
    """A voice input was received. Payload may carry: ``language``, ``duration``."""

    type: EventType = EventType.VOICE_RECEIVED


class IntentDetected(Event):
    """An intent was inferred from the input. Payload may carry: ``intent``, ``confidence``."""

    type: EventType = EventType.INTENT_DETECTED


class PlanCreated(Event):
    """The planner produced a plan. Payload may carry: ``step_count``, ``plan_id``."""

    type: EventType = EventType.PLAN_CREATED


class KnowledgeRetrieved(Event):
    """Knowledge was retrieved. Payload may carry: ``document_count``, ``case_count``."""

    type: EventType = EventType.KNOWLEDGE_RETRIEVED


class ReasoningStarted(Event):
    """Reasoning began. Payload may carry: ``question``."""

    type: EventType = EventType.REASONING_STARTED


class ReasoningFinished(Event):
    """Reasoning finished. Payload may carry: ``confidence``, ``citation_count``."""

    type: EventType = EventType.REASONING_FINISHED


class ToolExecuted(Event):
    """A tool was invoked. Payload may carry: ``tool_name``, ``status``."""

    type: EventType = EventType.TOOL_EXECUTED


class DiagnosticCompleted(Event):
    """A diagnostic finished. Payload may carry: ``diagnosis``, ``confidence``."""

    type: EventType = EventType.DIAGNOSTIC_COMPLETED


class WorkflowCompleted(Event):
    """A workflow instance completed. Payload may carry: ``workflow_id``, ``final_state``."""

    type: EventType = EventType.WORKFLOW_COMPLETED


class ResponseGenerated(Event):
    """The final response was produced. Payload may carry: ``length``, ``citation_count``."""

    type: EventType = EventType.RESPONSE_GENERATED
