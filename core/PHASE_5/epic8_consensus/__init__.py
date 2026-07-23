"""
PHASE 5 - EPIC 8: Consensus Engine

Motor de consenso para resolver conflictos entre agentes.
Combina respuestas y genera una única respuesta validada.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_8"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic8_consensus.domain import (
    # Consensus Decision
    ConsensusDecision,
    ConsensusLevel,
    # Agent Vote
    AgentVote,
    VoteOption,
    # Conflict Case
    ConflictCase,
    ConflictType,
    ResolutionStrategy,
)

# Engines
from core.PHASE_5.epic8_consensus.engines import (
    # Voting Engine
    VotingEngine,
    VotingResult,
    # Conflict Resolver
    ConflictResolver,
    ResolutionResult,
    # Ranking Engine
    RankingEngine,
    RankingResult,
    # Consensus Builder
    ConsensusBuilder,
    ConsensusResult,
)

# Agent
from core.PHASE_5.epic8_consensus.agent import (
    ConsensusEngine,
    ConsensusEngineConfig,
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
    "ConsensusDecision",
    "ConsensusLevel",
    "AgentVote",
    "VoteOption",
    "ConflictCase",
    "ConflictType",
    "ResolutionStrategy",
    # Engines
    "VotingEngine",
    "VotingResult",
    "ConflictResolver",
    "ResolutionResult",
    "RankingEngine",
    "RankingResult",
    "ConsensusBuilder",
    "ConsensusResult",
    # Agent
    "ConsensusEngine",
    "ConsensusEngineConfig",
]
