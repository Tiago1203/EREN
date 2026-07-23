"""
PHASE 5 - Multi-Agent Cognitive System

Sistema cognitivo distribuido de agentes especializados.
"""

from __future__ import annotations

__version__ = "1.0.0"
__phase__ = "PHASE_5"
__epic__ = "Multi-Agent System"


# =============================================================================
# EPIC 0 - Foundation (exports)
# =============================================================================

from core.PHASE_5.foundation import (
    # Version
    __version__,
    # Enums
    AgentState,
    AgentType,
    AgentCapability,
    AgentPriority,
    MessageType,
    MessageError,
    # Value Objects
    AgentCapabilityVO,
    AgentVersion,
    AgentMetrics,
    AgentConfig,
    # Domain
    Agent,
    AgentTask,
    TaskStatus,
    AgentMessage,
    AgentContext,
    AgentSession,
    SessionStatus,
    AgentResult,
    ConfidenceLevel,
    # Contracts
    IAgent,
    IAgentRegistry,
    IMessageBroker,
    ILifecycleManager,
    IAgentOrchestrator,
    IAgentFactory,
    IEventBus,
    AgentEvent,
    # Events
    AgentEventType,
    EventSeverity,
    EventSubscriber,
    EventBus,
    EventFactory,
    # Messaging
    MessageBroker,
    MessageBuilder,
    # Lifecycle
    AgentLifecycleManager,
    StateValidator,
    VALID_TRANSITIONS,
    # Registry
    AgentRegistry,
    AgentLookup,
    # Context
    ContextManager,
    SessionManager,
    # Base
    BaseAgent,
    # Gateways
    PHASE1Gateway,
    PHASE2Gateway,
    PHASE3Gateway,
    PHASE4Gateway,
    MultiPhaseGateway,
)


# =============================================================================
# PHASE CONSTANTS
# =============================================================================

PHASE_5_DEPENDENCIES = {
    "FASE_1": ["Device", "Incident", "Knowledge", "Asset", "Hospital"],
    "FASE_2": ["AI Kernel", "Memory", "Context", "Retrieval", "RAG"],
    "FASE_3": ["Reasoning", "Evidence", "Decision", "Learning"],
    "FASE_4": [
        "Document Processing",
        "Knowledge Extraction",
        "Clinical Embeddings",
        "Vector Indexing",
        "Hybrid Retrieval",
        "Clinical RAG",
        "Citations",
        "Quality",
        "Repository",
        "Sync",
        "Governance",
    ],
}

EPICS = {
    "EPIC_0": "Multi-Agent Architecture Foundation",
    "EPIC_1": "Agent Orchestrator",
    "EPIC_2": "Biomedical Agent",
    "EPIC_3": "Diagnostic Agent",
    "EPIC_4": "Knowledge Agent",
    "EPIC_5": "Research Agent",
    "EPIC_6": "Planning Agent",
    "EPIC_7": "Collaboration Engine",
    "EPIC_8": "Consensus Engine",
    "EPIC_9": "Agent Memory Engine",
    "EPIC_10": "Agent Learning & Optimization",
    "EPIC_11": "Multi-Agent Governance",
}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__phase__",
    "__epic__",
    # Foundation exports
    "AgentState",
    "AgentType",
    "AgentCapability",
    "AgentPriority",
    "MessageType",
    "Agent",
    "AgentTask",
    "AgentMessage",
    "AgentContext",
    "AgentSession",
    "AgentResult",
    "BaseAgent",
    "AgentRegistry",
    "AgentLifecycleManager",
    "MessageBroker",
    "EventBus",
    "EventFactory",
    "ContextManager",
    "SessionManager",
    "AgentLookup",
    "MultiPhaseGateway",
    # Constants
    "PHASE_5_DEPENDENCIES",
    "EPICS",
]
