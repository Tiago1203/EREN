# Multi-Agent Collaboration Engine (MACE)

## Overview

The official system for multi-agent collaboration in EREN. Allows multiple specialized agents to work together on shared objectives.

## Philosophy

> **Agents don't work in isolation.**
> **They collaborate.**
> **They negotiate.**
> **They share knowledge.**
> **They build solutions together.**

**The Engine NEVER:**
- Knows about OpenAI
- Knows about models
- Knows about retrieval
- Knows about databases

**It ONLY:**
- Creates collaboration sessions
- Manages agents
- Coordinates communication
- Builds consensus
- Resolves conflicts
- Aggregates results

## Architecture

```
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
```

## Communication Patterns

- **One-to-One**: Direct communication between two agents
- **One-to-Many**: One agent to multiple agents
- **Many-to-One**: Multiple agents to one agent
- **Many-to-Many**: Multiple agents to multiple agents
- **Broadcast**: One agent to all participants
- **Hierarchical**: Nested communication
- **Peer-to-Peer**: Direct agent-to-agent

## Protocols

- **REQUEST**: Request for action
- **RESPONSE**: Response to request
- **BROADCAST**: Broadcast to all
- **EVENT**: Event notification
- **PROPOSAL**: Proposal for consensus
- **VOTE**: Vote on proposal
- **CONSENSUS**: Consensus reached
- **CANCEL**: Cancel action
- **RETRY**: Retry request
- **ESCALATION**: Escalate issue

## Components

| Component | Responsibility |
|-----------|----------------|
| `engine.py` | Main collaboration engine |
| `dispatcher.py` | Task distribution |
| `messaging.py` | Agent messaging |
| `consensus.py` | Consensus building |
| `resolver.py` | Conflict resolution |
| `aggregator.py` | Result aggregation |
| `shared_context.py` | Shared context management |
| `protocol.py` | Communication protocols |
| `events.py` | Event publishing |
| `types.py` | Type definitions |

## Usage

```python
from core.collaboration import (
    CollaborationEngine,
    get_collaboration_engine,
    MessageType,
)

# Get engine
engine = get_collaboration_engine()

# Create session
session = engine.create_session(
    initiator_id="agent-1",
    goal="Solve complex problem",
    description="Multi-agent collaboration",
    participant_ids=["agent-2", "agent-3"],
)

# Start session
engine.start_session(session.session_id)

# Send message
message = engine.send_message(
    session_id=session.session_id,
    sender_id="agent-1",
    message_type=MessageType.REQUEST,
    content={"task": "Analyze data"},
    receiver_ids=["agent-2"],
)

# Broadcast
engine.broadcast(
    session_id=session.session_id,
    sender_id="agent-1",
    content={"update": "Progress update"},
)

# Add shared context
engine.put_context(
    session_id=session.session_id,
    key="shared_data",
    value={"key": "value"},
    agent_id="agent-1",
)

# Create proposal
proposal = engine.create_proposal(
    session_id=session.session_id,
    proposer_id="agent-1",
    title="Solution approach",
    description="Proposed solution",
    content={"approach": "A"},
)

# Vote
engine.vote(proposal.proposal_id, "agent-2", "accept")

# Add results
engine.add_result(session.session_id, "agent-1", {"result": "partial"})
engine.add_result(session.session_id, "agent-2", {"result": "partial"})

# Aggregate
final = engine.aggregate_results(session.session_id, strategy="priority")

# Complete
engine.complete_session(session.session_id, final)
```

## Consensus Building

```python
from core.collaboration import get_consensus_manager

consensus = get_consensus_manager()

# Create proposal
proposal = consensus.create_proposal(
    session_id="session-1",
    proposer_id="agent-1",
    title="Approve solution",
    description="Vote for solution",
    content={"solution": "A"},
    required_votes=2,
)

# Vote
consensus.vote(proposal.proposal_id, "agent-2", VoteValue.ACCEPT)
consensus.vote(proposal.proposal_id, "agent-3", VoteValue.ACCEPT)

# Check consensus
if consensus.is_consensus_reached(proposal.proposal_id):
    print("Consensus reached!")
```

## Conflict Resolution

```python
from core.collaboration import get_conflict_resolver, ConflictType

resolver = get_conflict_resolver()

# Create conflict
conflict = resolver.create_conflict(
    session_id="session-1",
    conflict_type=ConflictType.DECISION,
    description="Agents disagree on approach",
    parties=["agent-1", "agent-2"],
)

# Resolve by priority
resolver.resolve_by_priority(
    conflict_id=conflict.conflict_id,
    priorities={"agent-1": 5, "agent-2": 8},
)

# Or resolve with custom result
resolver.resolve(
    conflict_id=conflict.conflict_id,
    resolution={"chosen": "agent-2"},
    resolved_by="system",
    strategy="priority",
)
```

## Task Distribution

```python
from core.collaboration import get_task_dispatcher

dispatcher = get_task_dispatcher()

# Create assignment
assignment = dispatcher.create_assignment(
    session_id="session-1",
    task_id="task-1",
    agent_id="agent-1",
    description="Analyze data",
    priority=5,
    depends_on=[],
)

# Accept
dispatcher.accept(assignment.assignment_id)

# Complete
dispatcher.complete(assignment.assignment_id, {"analysis": "done"})
```

## Shared Context

```python
from core.collaboration import get_shared_context

context = get_shared_context()

# Create session context
context.create_session_context("session-1")

# Put values
context.put("session-1", "key1", "value1", agent_id="agent-1")
context.put("session-1", "key2", "value2", agent_id="agent-2")

# Get all
all_values = context.get_all("session-1")

# Merge contributions
merged = context.merge("session-1", "agent-1", "agent-2")
```

---

*Agents don't work in isolation. They collaborate.*
