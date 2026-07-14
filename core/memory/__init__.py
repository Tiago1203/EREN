"""Cognitive Memory System (CMS).

EREN's memory system inspired by human cognitive memory architecture.
Not a database — a cognitive system for storing, retrieving, and forgetting.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from core.memory.exceptions import (
    MemoryAlreadyExistsError,
    MemoryCapacityError,
    MemoryConsolidationError,
    MemoryDecayError,
    MemoryError,
    MemoryNotFoundError,
    MemoryRelationshipError,
    MemoryRetrievalError,
    MemorySnapshotError,
    MemoryValidationError,
    # Orchestrator exceptions
    MemoryOrchestratorException,
    MemoryNotRegisteredError,
    MemoryUnavailableError,
    MemoryOperationError,
    MemoryReadError,
    MemoryWriteError,
    MemorySearchError,
    MemorySelectionError,
    MemoryNoResultsError,
    MemoryPolicyError,
)
from core.memory.memory_engine import CognitiveMemoryEngine
from core.memory.memory_models import (
    MemoryEntry,
    MemoryGraph,
    MemoryNode,
    MemoryQuery,
    MemoryQueryResult,
    MemorySnapshot,
    MemoryTemplates,
)
from core.memory.memory_stores import (
    LongTermMemoryStore,
    MemoryStore,
    ShortTermMemoryStore,
    WorkingMemoryStore,
    create_memory_store,
)
from core.memory.memory_types import (
    AccessPattern,
    ConsolidationContext,
    ConsolidationPolicy,
    ContentType,
    IndexingPolicy,
    MemoryAccess,
    MemoryContent,
    MemoryFilter,
    MemoryMetadata,
    MemoryRelationship,
    MemoryStatistics,
    MemoryStatus,
    MemoryStrength,
    MemoryType,
    RelationshipType,
    RetrievalContext,
    RetrievalMode,
    RetrievalPolicy,
    RetentionPolicy,
    SearchOptions,
)

# Orchestrator modules
from core.memory.base import BaseMemoryInterface, MemoryInterface
from core.memory.registry import (
    MemoryRegistry,
    get_memory_registry,
    reset_memory_registry,
)
from core.memory.selector import MemorySelector
from core.memory.orchestrator import (
    MemoryOrchestrator,
    get_memory_orchestrator,
    reset_memory_orchestrator,
)
from core.memory.types import (
    MemoryType,
    MemoryState,
    MemoryAccessPolicy,
    MemoryOperation,
    MemoryQuery,
    MemoryResult,
    MemoryResponse,
    MemoryEntry,
    MemoryMetrics,
)

__all__ = [
    # Core Engine
    "CognitiveMemoryEngine",
    # Stores
    "MemoryStore",
    "WorkingMemoryStore",
    "ShortTermMemoryStore",
    "LongTermMemoryStore",
    "create_memory_store",
    # Models
    "MemoryEntry",
    "MemoryQuery",
    "MemoryQueryResult",
    "MemorySnapshot",
    "MemoryGraph",
    "MemoryNode",
    "MemoryTemplates",
    # Types
    "MemoryType",
    "MemoryStatus",
    "MemoryStrength",
    "ContentType",
    "RelationshipType",
    "AccessPattern",
    "RetrievalMode",
    "MemoryAccess",
    "MemoryContent",
    "MemoryMetadata",
    "MemoryRelationship",
    "MemoryFilter",
    "SearchOptions",
    "RetrievalContext",
    "ConsolidationContext",
    "RetentionPolicy",
    "IndexingPolicy",
    "RetrievalPolicy",
    "ConsolidationPolicy",
    "MemoryStatistics",
    # Orchestrator Types
    "MemoryState",
    "MemoryAccessPolicy",
    "MemoryOperation",
    "MemoryResult",
    "MemoryResponse",
    "MemoryMetrics",
    # Orchestrator Components
    "BaseMemoryInterface",
    "MemoryInterface",
    "MemoryRegistry",
    "get_memory_registry",
    "reset_memory_registry",
    "MemorySelector",
    "MemoryOrchestrator",
    "get_memory_orchestrator",
    "reset_memory_orchestrator",
    # Exceptions
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryAlreadyExistsError",
    "MemoryCapacityError",
    "MemoryConsolidationError",
    "MemoryDecayError",
    "MemoryRetrievalError",
    "MemoryRelationshipError",
    "MemoryValidationError",
    "MemorySnapshotError",
    # Orchestrator Exceptions
    "MemoryOrchestratorException",
    "MemoryNotRegisteredError",
    "MemoryUnavailableError",
    "MemoryOperationError",
    "MemoryReadError",
    "MemoryWriteError",
    "MemorySearchError",
    "MemorySelectionError",
    "MemoryNoResultsError",
    "MemoryPolicyError",
]
