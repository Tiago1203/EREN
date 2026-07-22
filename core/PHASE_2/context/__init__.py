"""Cognitive Context & Blackboard System (CCBS).

The shared cognitive context for all motors in EREN.
No motor creates copies. All motors enrich the same context.

Architecture only — no AI, no implementations.
"""

from __future__ import annotations

# Import new CCBS components
from core.PHASE_2.context.blackboard import CognitiveBlackboard
from core.PHASE_2.context.cognitive_context import CognitiveContext
from core.PHASE_2.context.context_history import ContextHistory, HistoryRecord
from core.PHASE_2.context.context_manager import ContextManager, ContextStats
from core.PHASE_2.context.context_snapshot import (
    ContextSnapshot,
    SnapshotDiff,
    SnapshotRegistry,
)
from core.PHASE_2.context.context_types import (
    BlackboardEntry,
    BlackboardEntryType,
    BlackboardFilter,
    Confidence,
    ConfidenceLevel,
    ContextFilter,
    ContextMetadata,
    ContextStatus,
    DeviceContext,
    DiagnosisResult,
    Evidence,
    EvidenceSource,
    EvidenceType,
    HospitalContext,
    Hypothesis,
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
from core.PHASE_2.context.exceptions import (
    BlackboardEntryNotFoundError,
    BlackboardError,
    BlackboardWriteError,
    ConfidenceError,
    ContextAlreadyExistsError,
    ContextCapacityError,
    ContextError,
    ContextExpiredError,
    ContextImmutableError,
    ContextMergeError,
    ContextNotFoundError,
    ContextSnapshotError,
    ContextStatusError,
    ContextValidationError,
)

# Import from models.py (existing Pydantic models)
from core.PHASE_2.context.models import (
    Citation,
    ClinicalContext,
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
    # Core Context (new implementation)
    "CognitiveContext",
    # Blackboard
    "CognitiveBlackboard",
    "BlackboardEntry",
    "BlackboardEntryType",
    # Manager
    "ContextManager",
    "ContextStats",
    # History
    "ContextHistory",
    "HistoryRecord",
    # Snapshot
    "ContextSnapshot",
    "SnapshotDiff",
    "SnapshotRegistry",
    # Types
    "ContextStatus",
    "ProcessingStage",
    "ConfidenceLevel",
    "Confidence",
    "Evidence",
    "EvidenceType",
    "EvidenceSource",
    "Hypothesis",
    "Observation",
    "UserContext",
    "HospitalContext",
    "DeviceContext",
    "IncidentContext",
    "IntentResult",
    "PlanResult",
    "DiagnosisResult",
    "WorkflowResult",
    "ToolUsage",
    "ResponseResult",
    "ProcessingMetadata",
    "ContextMetadata",
    "ContextFilter",
    "BlackboardFilter",
    # Exceptions
    "ContextError",
    "ContextNotFoundError",
    "ContextAlreadyExistsError",
    "ContextImmutableError",
    "ContextStatusError",
    "ContextValidationError",
    "ContextMergeError",
    "ContextSnapshotError",
    "ContextExpiredError",
    "ContextCapacityError",
    "ConfidenceError",
    "BlackboardError",
    "BlackboardEntryNotFoundError",
    "BlackboardWriteError",
    # Legacy models (Pydantic)
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
