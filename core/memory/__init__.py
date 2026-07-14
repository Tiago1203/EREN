"""Cognitive Memory System (CMS).

EREN's memory system inspired by human cognitive memory architecture.
Not a database — a cognitive system for storing, retrieving, and forgetting.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

# =============================================================================
# Canonical Sources
# =============================================================================
# MemoryEntry, MemoryQuery -> core/memory/memory_models.py (models)
# MemoryType (detailed) -> core/memory/memory_types.py (types for engine)
# MemoryType (simple), MemoryState, etc. -> core/memory/types.py (types for coordinator)
# =============================================================================

# =============================================================================
# Canonical Imports (Single source per type)
# =============================================================================

# Types from types.py (Coordinator) - canonical source for coordinator types
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

# Types from memory_types.py (Engine) - canonical source for engine types
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
    RelationshipType,
    RetrievalContext,
    RetrievalMode,
    RetrievalPolicy,
    RetentionPolicy,
    SearchOptions,
)

# Models from memory_models.py
from core.memory.memory_models import (
    MemoryGraph,
    MemoryNode,
    MemoryQueryResult,
    MemorySnapshot,
    MemoryTemplates,
)

# Exceptions
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

# Engine
from core.memory.memory_engine import CognitiveMemoryEngine

# Stores
from core.memory.memory_stores import (
    LongTermMemoryStore,
    MemoryStore,
    ShortTermMemoryStore,
    WorkingMemoryStore,
    create_memory_store,
)

# Coordinator modules
from core.memory.base import BaseMemoryInterface, MemoryInterface
from core.memory.registry import (
    MemoryRegistry,
    get_memory_registry,
    reset_memory_registry,
)
from core.memory.selector import MemorySelector
from core.memory.coordinator import (
    MemoryCoordinator,
    get_memory_coordinator,
    reset_memory_coordinator,
    # Backward compatibility
    MemoryOrchestrator,
    get_memory_orchestrator,
    reset_memory_orchestrator,
)

__all__ = [
    # =================================================================
    # Core Engine
    # =================================================================
    "CognitiveMemoryEngine",
    
    # =================================================================
    # Stores
    # =================================================================
    "MemoryStore",
    "WorkingMemoryStore",
    "ShortTermMemoryStore",
    "LongTermMemoryStore",
    "create_memory_store",
    
    # =================================================================
    # Models (Canonical: memory_models.py)
    # =================================================================
    "MemoryEntry",
    "MemoryQuery",
    "MemoryQueryResult",
    "MemorySnapshot",
    "MemoryGraph",
    "MemoryNode",
    "MemoryTemplates",
    
    # =================================================================
    # Types - Coordinator (Canonical: types.py)
    # =================================================================
    "MemoryType",
    "MemoryState",
    "MemoryAccessPolicy",
    "MemoryOperation",
    "MemoryResult",
    "MemoryResponse",
    "MemoryMetrics",
    
    # =================================================================
    # Types - Engine (Canonical: memory_types.py)
    # =================================================================
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
    
    # =================================================================
    # Coordinator Components
    # =================================================================
    "BaseMemoryInterface",
    "MemoryInterface",
    "MemoryRegistry",
    "get_memory_registry",
    "reset_memory_registry",
    "MemorySelector",
    "MemoryCoordinator",
    "get_memory_coordinator",
    "reset_memory_coordinator",
    
    # =================================================================
    # Backward Compatibility (deprecated aliases)
    # =================================================================
    "MemoryOrchestrator",
    "get_memory_orchestrator",
    "reset_memory_orchestrator",
    
    # =================================================================
    # Exceptions - Core
    # =================================================================
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
    
    # =================================================================
    # Exceptions - Coordinator
    # =================================================================
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
