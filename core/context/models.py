"""Cognitive context models for EREN core.

This module defines :class:`CognitiveContext` — the single object that travels
through every cognitive engine during one interaction. It is the shared,
serializable "state of the conversation" that the orchestrator hands to each
engine and enriches step by step.

Architecture only. This module contains **no business logic, no AI, and no
LLM calls** — just declarative Pydantic v2 models that fix the *shape* of the
context. Behaviour (how the context is populated, validated against a hospital,
or persisted) belongs to the engines and services that consume it, not here.

The model is organized into cohesive sub-models (identity, user, clinical,
conversation, cognitive state, memory, knowledge, result, metadata) that are
composed into :class:`CognitiveContext`. All fields have safe, empty defaults
so a context can be created incrementally as it flows through the pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    """Return the current UTC timestamp (timezone-aware)."""
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    """Coarse role of the actor driving the interaction.

    Kept intentionally small; fine-grained permissions are a separate concern
    handled outside the context object.
    """

    ADMIN = "admin"
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    ESTABLISHMENT = "establishment"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    """Author of a single conversation turn."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationTurn(BaseModel):
    """A single message exchanged during the conversation."""

    model_config = ConfigDict(extra="forbid")

    role: MessageRole = Field(description="Who authored this turn.")
    content: str = Field(default="", description="Text content of the turn.")
    timestamp: datetime = Field(
        default_factory=_utcnow, description="When the turn was recorded (UTC)."
    )


class MemoryRecord(BaseModel):
    """A single remembered item (short- or long-term).

    The payload is intentionally opaque at this layer; the Memory engine owns
    its interpretation and storage.
    """

    model_config = ConfigDict(extra="forbid")

    key: str = Field(default="", description="Stable identifier for the record.")
    content: str = Field(default="", description="Human-readable memory content.")
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Opaque metadata attached by the Memory engine.",
    )


class RetrievedDocument(BaseModel):
    """A knowledge document surfaced by the Knowledge engine."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        default="", description="Document identifier in the knowledge base."
    )
    title: str = Field(default="", description="Human-readable title.")
    source: str = Field(default="", description="Origin (manual, KB entry, URL, …).")
    score: float | None = Field(
        default=None, description="Relevance score assigned during retrieval."
    )
    snippet: str = Field(default="", description="Relevant excerpt of the document.")


class RetrievedCase(BaseModel):
    """A prior case surfaced from the case base."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default="", description="Case identifier in the case base.")
    summary: str = Field(default="", description="Short description of the case.")
    score: float | None = Field(
        default=None, description="Similarity score to the current interaction."
    )


class Regulation(BaseModel):
    """A normative/regulatory reference relevant to the interaction."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default="", description="Regulation identifier.")
    name: str = Field(default="", description="Human-readable name of the norm.")
    reference: str = Field(
        default="", description="Citable reference (article, clause, standard code)."
    )


class Citation(BaseModel):
    """A traceable citation backing part of the response (explainability)."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(
        default="", description="What is being cited (document, case, norm)."
    )
    reference: str = Field(default="", description="Precise locator within the source.")
    snippet: str = Field(default="", description="Quoted text supporting the claim.")


class Identity(BaseModel):
    """Correlation identity and timing of the interaction."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        default="", description="Unique id for this single request."
    )
    session_id: str = Field(
        default="", description="Id grouping requests of the same conversation/session."
    )
    timestamp: datetime = Field(
        default_factory=_utcnow, description="When the interaction started (UTC)."
    )


class UserInfo(BaseModel):
    """Who is interacting and under which organization."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(default="", description="Identifier of the acting user.")
    user_role: UserRole = Field(
        default=UserRole.UNKNOWN, description="Coarse role of the acting user."
    )
    organization_id: str = Field(
        default="", description="Tenant/organization the user belongs to."
    )


class ClinicalContext(BaseModel):
    """Clinical-engineering context: where and about which device."""

    model_config = ConfigDict(extra="forbid")

    hospital_id: str = Field(
        default="", description="Hospital/establishment identifier."
    )
    department: str = Field(
        default="", description="Department or area within the hospital."
    )
    device_id: str = Field(default="", description="Identifier of the medical device.")
    device_type: str = Field(default="", description="Type/category of the device.")
    manufacturer: str = Field(default="", description="Device manufacturer.")
    model: str = Field(default="", description="Device model.")


class Conversation(BaseModel):
    """Raw and normalized input plus the conversation history."""

    model_config = ConfigDict(extra="forbid")

    original_input: str = Field(default="", description="Verbatim user input.")
    normalized_input: str = Field(
        default="", description="Cleaned/normalized version of the input."
    )
    detected_language: str = Field(
        default="", description="Detected language code (e.g. 'es', 'en')."
    )
    conversation_history: list[ConversationTurn] = Field(
        default_factory=list, description="Ordered prior turns of the conversation."
    )


class CognitiveState(BaseModel):
    """The evolving cognitive state as the pipeline advances."""

    model_config = ConfigDict(extra="forbid")

    detected_intent: str = Field(
        default="", description="Intent inferred from the input."
    )
    confidence: float | None = Field(
        default=None, description="Confidence in the detected intent (0.0–1.0)."
    )
    current_plan: list[str] = Field(
        default_factory=list,
        description="Ordered step descriptions of the current plan (decoupled from Planner types).",
    )
    current_step: int | None = Field(
        default=None, description="Index of the step currently being executed."
    )
    executed_engines: list[str] = Field(
        default_factory=list, description="Names of engines already invoked, in order."
    )
    executed_tools: list[str] = Field(
        default_factory=list, description="Names of tools already invoked, in order."
    )


class MemoryState(BaseModel):
    """Memory made available to the engines for this interaction."""

    model_config = ConfigDict(extra="forbid")

    short_term_memory: list[MemoryRecord] = Field(
        default_factory=list, description="Working memory scoped to the session."
    )
    long_term_memory: list[MemoryRecord] = Field(
        default_factory=list,
        description="Persistent institutional memory recalled for this request.",
    )


class KnowledgeState(BaseModel):
    """Knowledge retrieved to ground the interaction."""

    model_config = ConfigDict(extra="forbid")

    retrieved_documents: list[RetrievedDocument] = Field(
        default_factory=list,
        description="Knowledge documents surfaced for this request.",
    )
    retrieved_cases: list[RetrievedCase] = Field(
        default_factory=list,
        description="Similar prior cases surfaced for this request.",
    )
    regulations: list[Regulation] = Field(
        default_factory=list, description="Applicable normative/regulatory references."
    )


class ResultState(BaseModel):
    """Intermediate and final products of the interaction."""

    model_config = ConfigDict(extra="forbid")

    intermediate_results: dict[str, object] = Field(
        default_factory=dict,
        description="Per-engine intermediate outputs keyed by engine/tool name.",
    )
    final_response: str = Field(
        default="", description="The response returned to the caller."
    )


class ExecutionMetadata(BaseModel):
    """Cross-cutting metadata for observability and explainability."""

    model_config = ConfigDict(extra="forbid")

    execution_time: float | None = Field(
        default=None, description="Total execution time in seconds."
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings accumulated during execution.",
    )
    citations: list[Citation] = Field(
        default_factory=list, description="Traceable citations backing the response."
    )


class CognitiveContext(BaseModel):
    """The object that travels through every cognitive engine of EREN.

    A single :class:`CognitiveContext` represents one full interaction. The
    orchestrator creates it, and each engine reads what it needs and writes
    back its contribution (retrieved knowledge, memory, plan progress,
    intermediate results, citations, …). By the end of the pipeline the context
    carries both the ``final_response`` and the complete, auditable trail of how
    it was produced.

    Sub-models group related fields so the context stays cohesive as it grows.
    Every field has an empty default, allowing the context to be populated
    incrementally instead of all at once.

    This is a declarative model only — it holds state, it does not act on it.
    """

    model_config = ConfigDict(extra="forbid")

    # Identity & timing
    identity: Identity = Field(
        default_factory=Identity, description="Correlation ids and timing."
    )

    # Actor
    user: UserInfo = Field(default_factory=UserInfo, description="Who is interacting.")

    # Clinical-engineering context
    clinical: ClinicalContext = Field(
        default_factory=ClinicalContext, description="Hospital and device context."
    )

    # Conversation
    conversation: Conversation = Field(
        default_factory=Conversation, description="Input and conversation history."
    )

    # Evolving cognitive state
    cognitive_state: CognitiveState = Field(
        default_factory=CognitiveState,
        description="Intent, plan and execution progress.",
    )

    # Memory
    memory: MemoryState = Field(
        default_factory=MemoryState,
        description="Short- and long-term memory for this request.",
    )

    # Knowledge
    knowledge: KnowledgeState = Field(
        default_factory=KnowledgeState,
        description="Retrieved knowledge, cases and regulations.",
    )

    # Result
    result: ResultState = Field(
        default_factory=ResultState, description="Intermediate and final outputs."
    )

    # Metadata
    metadata: ExecutionMetadata = Field(
        default_factory=ExecutionMetadata,
        description="Observability and explainability metadata.",
    )
