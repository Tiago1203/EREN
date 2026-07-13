"""EREN cognitive context package.

Defines :class:`CognitiveContext`, the object shared across all cognitive
engines during a single interaction, plus its composing sub-models.

Architecture only — declarative Pydantic v2 models, no business logic or AI.
"""

from __future__ import annotations

from core.context.models import (
    Citation,
    ClinicalContext,
    CognitiveContext,
    CognitiveState,
    Conversation,
    ConversationTurn,
    ExecutionMetadata,
    Identity,
    KnowledgeState,
    MemoryRecord,
    MemoryState,
    MessageRole,
    Regulation,
    ResultState,
    RetrievedCase,
    RetrievedDocument,
    UserInfo,
    UserRole,
)

__all__ = [
    "CognitiveContext",
    "Identity",
    "UserInfo",
    "ClinicalContext",
    "Conversation",
    "ConversationTurn",
    "CognitiveState",
    "MemoryState",
    "MemoryRecord",
    "KnowledgeState",
    "RetrievedDocument",
    "RetrievedCase",
    "Regulation",
    "ResultState",
    "ExecutionMetadata",
    "Citation",
    "UserRole",
    "MessageRole",
]
