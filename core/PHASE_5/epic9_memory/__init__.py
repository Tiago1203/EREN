"""
PHASE 5 - EPIC 9: Agent Memory Engine

Motor de memoria para dar memoria individual y colectiva a los agentes.
Persiste experiencias, contexto y conversaciones.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_9"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic9_memory.domain import (
    # Memory Record
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    # Conversation Context
    ConversationContext,
    Message,
    # Agent Experience
    AgentExperience,
    ExperienceOutcome,
)

# Engines
from core.PHASE_5.epic9_memory.engines import (
    # Episodic Memory
    EpisodicMemory,
    EpisodicResult,
    # Shared Memory
    SharedMemory,
    SharedResult,
    # Long-term Memory
    LongTermMemory,
    LongTermResult,
    # Conversation Memory
    ConversationMemory,
    ConversationResult,
    # Memory Synchronizer
    MemorySynchronizer,
    SyncResult,
)

# Agent
from core.PHASE_5.epic9_memory.agent import (
    AgentMemory,
    AgentMemoryConfig,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain
    "MemoryRecord",
    "MemoryType",
    "MemoryImportance",
    "ConversationContext",
    "Message",
    "AgentExperience",
    "ExperienceOutcome",
    # Engines
    "EpisodicMemory",
    "EpisodicResult",
    "SharedMemory",
    "SharedResult",
    "LongTermMemory",
    "LongTermResult",
    "ConversationMemory",
    "ConversationResult",
    "MemorySynchronizer",
    "SyncResult",
    # Agent
    "AgentMemory",
    "AgentMemoryConfig",
]
