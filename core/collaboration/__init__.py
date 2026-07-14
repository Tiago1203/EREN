"""EREN Multi-Agent Collaboration Engine (MACE).

The official system for multi-agent collaboration in EREN.
Allows multiple specialized agents to work together on shared objectives.

Philosophy:
    Agents don't work in isolation.
    They collaborate.
    They negotiate.
    They share knowledge.
    They build solutions together.

Architecture:
    Decision Engine
            │
            ▼
    Agent Platform
            │
            ▼
    Collaboration Engine
            │
            ├── Task Distributor
            ├── Shared Context
            ├── Agent Messaging
            ├── Consensus Manager
            ├── Conflict Resolver
            └── Result Aggregator

Responsibilities:
- Divide objectives among agents
- Create dynamic teams
- Share context
- Send messages
- Receive responses
- Merge results
- Resolve conflicts
- Build final response
"""

from __future__ import annotations

# Types
from core.collaboration.types import (
    # Enums
    MessageType,
    MessageStatus,
    CollaborationStatus,
    ConsensusState,
    VoteValue,
    # Classes
    CollaborationMessage,
    CollaborationSession,
    TaskAssignment,
    Proposal,
    CollaborationMetrics,
)

# Components
from core.collaboration.protocol import (
    ProtocolHandler,
    CommunicationPattern,
    MessageBuilder,
)
from core.collaboration.messaging import (
    AgentMessaging,
    get_messaging,
    reset_messaging,
)
from core.collaboration.shared_context import (
    SharedContext,
    get_shared_context,
    reset_shared_context,
)
from core.collaboration.consensus import (
    ConsensusManager,
    get_consensus_manager,
    reset_consensus_manager,
)
from core.collaboration.resolver import (
    ConflictType,
    Conflict,
    Resolution,
    ConflictResolver,
    get_conflict_resolver,
    reset_conflict_resolver,
)
from core.collaboration.aggregator import (
    ResultAggregator,
    get_result_aggregator,
    reset_result_aggregator,
)
from core.collaboration.dispatcher import (
    TaskDispatcher,
    get_task_dispatcher,
    reset_task_dispatcher,
)
from core.collaboration.events import (
    CollaborationEventType,
    CollaborationEvent,
    CollaborationEventBus,
    get_event_bus,
    reset_event_bus,
)

# Main engine
from core.collaboration.engine import (
    CollaborationEngine,
    get_collaboration_engine,
    reset_collaboration_engine,
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
    # Main engine
    "CollaborationEngine",
    "get_collaboration_engine",
    "reset_collaboration_engine",
]
