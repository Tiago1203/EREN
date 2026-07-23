"""
PHASE 5 - EPIC 7: Collaboration Engine

Motor de colaboración entre agentes.
Gestiona colaboración, intercambio de contexto y sincronización.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_7"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic7_collaboration.domain import (
    # Shared Context
    SharedContext,
    ContextEntry,
    ContextType,
    # Collaboration Session
    CollaborationSession,
    SessionStatus,
    Participant,
    # Agent Conversation
    AgentConversation,
    Message,
    MessageType,
)

# Engines
from core.PHASE_5.epic7_collaboration.engines import (
    # Context Sharing
    ContextSharing,
    SharingResult,
    # Agent Messaging
    AgentMessaging,
    MessageResult,
    # Collaboration Bus
    CollaborationBus,
    BusMessage,
    # Shared Workspace
    SharedWorkspace,
    WorkspaceResult,
)

# Agent (for EPIC integration)
from core.PHASE_5.epic7_collaboration.agent import (
    CollaborationEngine,
    CollaborationEngineConfig,
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
    "SharedContext",
    "ContextEntry",
    "ContextType",
    "CollaborationSession",
    "SessionStatus",
    "Participant",
    "AgentConversation",
    "Message",
    "MessageType",
    # Engines
    "ContextSharing",
    "SharingResult",
    "AgentMessaging",
    "MessageResult",
    "CollaborationBus",
    "BusMessage",
    "SharedWorkspace",
    "WorkspaceResult",
    # Agent
    "CollaborationEngine",
    "CollaborationEngineConfig",
]
