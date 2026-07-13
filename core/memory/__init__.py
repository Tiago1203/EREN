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
]
