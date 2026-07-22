"""EREN Multi-Agent Collaboration Layer.

The official system for multi-agent collaboration in EREN.
Allows multiple specialized agents to work together on shared objectives.

Philosophy:
    Communication and collaboration are distinct concepts.
    Agents can communicate without collaborating.
    Collaboration uses communication as infrastructure.

Architecture:
    Decision Engine
            │
            ▼
    Agent Platform
            │
            ▼
    Collaboration Layer
            │
            ├── Communication Bus
            ├── Coordination Engine
            ├── Session Manager
            ├── Shared Context
            ├── Consensus Manager
            ├── Conflict Resolver
            └── Result Aggregator
"""

from __future__ import annotations

from core.LEGACY.collaboration.aggregator import (
    ResultAggregator,
    get_result_aggregator,
    reset_result_aggregator,
)

# Communication Layer
from core.LEGACY.collaboration.communication_bus import (
    CommunicationBus,
    get_communication_bus,
    reset_communication_bus,
)
from core.LEGACY.collaboration.consensus import (
    ConsensusManager,
    get_consensus_manager,
    reset_consensus_manager,
)
from core.LEGACY.collaboration.dispatcher import (
    TaskDispatcher,
    get_task_dispatcher,
    reset_task_dispatcher,
)

# Coordination Engine (main engine)
from core.LEGACY.collaboration.engine import (
    CollaborationEngine,  # Alias for backwards compatibility
    CoordinationEngine,
    get_collaboration_engine,
    reset_collaboration_engine,
)
from core.LEGACY.collaboration.events import (
    CollaborationEvent,
    CollaborationEventBus,
    CollaborationEventType,
    get_event_bus,
    reset_event_bus,
)
from core.LEGACY.collaboration.messaging import (
    AgentMessaging,
    get_messaging,
    reset_messaging,
)

# Components
from core.LEGACY.collaboration.protocol import (
    CommunicationPattern,
    MessageBuilder,
    ProtocolHandler,
)
from core.LEGACY.collaboration.resolver import (
    Conflict,
    ConflictResolver,
    ConflictType,
    Resolution,
    get_conflict_resolver,
    reset_conflict_resolver,
)

# Sessions
from core.LEGACY.collaboration.sessions import (
    SessionManager,
    get_session_manager,
    reset_session_manager,
)
from core.LEGACY.collaboration.shared_context import (
    SharedContext,
    get_shared_context,
    reset_shared_context,
)

# Types
from core.LEGACY.collaboration.types import (
    # Classes
    CollaborationMessage,
    CollaborationMetrics,
    CollaborationSession,
    CollaborationStatus,
    ConsensusState,
    MessageStatus,
    # Enums
    MessageType,
    Proposal,
    TaskAssignment,
    VoteValue,
)

__all__ = [
    # Types
    "MessageType",
    "MessageStatus",
    "CollaborationStatus",
    "ConsensusState",
    "VoteValue",
    "CollaborationMessage",
    "CollaborationSession",
    "TaskAssignment",
    "Proposal",
    "CollaborationMetrics",
    # Communication Layer
    "CommunicationBus",
    "get_communication_bus",
    "reset_communication_bus",
    # Sessions
    "SessionManager",
    "get_session_manager",
    "reset_session_manager",
    # Components
    "ProtocolHandler",
    "CommunicationPattern",
    "MessageBuilder",
    "AgentMessaging",
    "get_messaging",
    "reset_messaging",
    "SharedContext",
    "get_shared_context",
    "reset_shared_context",
    "ConsensusManager",
    "get_consensus_manager",
    "reset_consensus_manager",
    "ConflictType",
    "Conflict",
    "Resolution",
    "ConflictResolver",
    "get_conflict_resolver",
    "reset_conflict_resolver",
    "ResultAggregator",
    "get_result_aggregator",
    "reset_result_aggregator",
    "TaskDispatcher",
    "get_task_dispatcher",
    "reset_task_dispatcher",
    "CollaborationEventType",
    "CollaborationEvent",
    "CollaborationEventBus",
    "get_event_bus",
    "reset_event_bus",
    # Main Engine
    "CoordinationEngine",
    "CollaborationEngine",
    "get_collaboration_engine",
    "reset_collaboration_engine",
]
