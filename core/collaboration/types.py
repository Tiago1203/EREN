"""Collaboration types for EREN Multi-Agent Collaboration Engine.

Types for multi-agent collaboration.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Collaboration Types
# =============================================================================


class MessageType(str, Enum):
    """Types of collaboration messages."""

    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    EVENT = "event"
    PROPOSAL = "proposal"
    VOTE = "vote"
    CONSENSUS = "consensus"
    CANCEL = "cancel"
    RETRY = "retry"
    ESCALATION = "escalation"


class MessageStatus(str, Enum):
    """Status of a message."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    FAILED = "failed"


class CollaborationStatus(str, Enum):
    """Status of a collaboration session."""

    CREATED = "created"
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsensusState(str, Enum):
    """State of consensus."""

    PENDING = "pending"
    VOTING = "voting"
    AGREED = "agreed"
    DISAGREED = "disagreed"
    TIMEOUT = "timeout"


class VoteValue(str, Enum):
    """Vote values."""

    ACCEPT = "accept"
    REJECT = "reject"
    ABSTAIN = "abstain"


# =============================================================================
# Collaboration Messages
# =============================================================================


@dataclass
class CollaborationMessage:
    """A message in collaboration."""

    message_id: str
    session_id: str
    sender_id: str
    message_type: MessageType
    content: Any

    # Routing
    receiver_ids: list[str] = field(default_factory=list)
    reply_to: str = ""

    # Status
    status: MessageStatus = MessageStatus.PENDING

    # Metadata
    correlation_id: str = ""
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    delivered_at: datetime | None = None

    @classmethod
    def create(
        cls,
        session_id: str,
        sender_id: str,
        message_type: MessageType,
        content: Any,
        receiver_ids: list[str] | None = None,
    ) -> CollaborationMessage:
        """Create a new message."""
        return cls(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            receiver_ids=receiver_ids or [],
        )


# =============================================================================
# Collaboration Session
# =============================================================================


@dataclass
class CollaborationSession:
    """A collaboration session between agents."""

    session_id: str
    goal: str
    description: str

    # Participants
    initiator_id: str
    participant_ids: list[str] = field(default_factory=list)

    # Status
    status: CollaborationStatus = CollaborationStatus.CREATED

    # Messages
    messages: list[CollaborationMessage] = field(default_factory=list)

    # Results
    partial_results: dict[str, Any] = field(default_factory=dict)
    final_result: Any = None

    # Decisions
    decisions: list[dict] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Configuration
    timeout_seconds: float = 300.0
    consensus_required: bool = True

    # Metadata
    metadata: dict = field(default_factory=dict)

    def add_participant(self, agent_id: str) -> None:
        """Add a participant."""
        if agent_id not in self.participant_ids:
            self.participant_ids.append(agent_id)

    def remove_participant(self, agent_id: str) -> None:
        """Remove a participant."""
        if agent_id in self.participant_ids:
            self.participant_ids.remove(agent_id)

    def add_message(self, message: CollaborationMessage) -> None:
        """Add a message to the session."""
        self.messages.append(message)

    def add_result(self, agent_id: str, result: Any) -> None:
        """Add a partial result."""
        self.partial_results[agent_id] = result

    @property
    def is_complete(self) -> bool:
        """Check if session is complete."""
        return self.status in [
            CollaborationStatus.COMPLETED,
            CollaborationStatus.FAILED,
            CollaborationStatus.CANCELLED,
        ]


# =============================================================================
# Task Assignment
# =============================================================================


@dataclass
class TaskAssignment:
    """A task assigned to an agent."""

    assignment_id: str
    session_id: str
    task_id: str
    agent_id: str
    description: str

    # Status
    status: str = "pending"  # pending, accepted, declined, completed, failed
    priority: int = 5

    # Result
    result: Any = None
    error: str = ""

    # Dependencies
    depends_on: list[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    accepted_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        session_id: str,
        task_id: str,
        agent_id: str,
        description: str,
        priority: int = 5,
        depends_on: list[str] | None = None,
    ) -> TaskAssignment:
        """Create a new task assignment."""
        return cls(
            assignment_id=str(uuid.uuid4()),
            session_id=session_id,
            task_id=task_id,
            agent_id=agent_id,
            description=description,
            priority=priority,
            depends_on=depends_on or [],
        )


# =============================================================================
# Proposal and Vote
# =============================================================================


@dataclass
class Proposal:
    """A proposal for consensus."""

    proposal_id: str
    session_id: str
    proposer_id: str
    title: str
    description: str
    content: Any

    # Voting
    votes: dict[str, VoteValue] = field(default_factory=dict)  # agent_id -> vote
    required_votes: int = 0

    # State
    state: ConsensusState = ConsensusState.PENDING
    deadline: datetime | None = None

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        session_id: str,
        proposer_id: str,
        title: str,
        description: str,
        content: Any,
        required_votes: int = 0,
        deadline_seconds: float = 60.0,
    ) -> Proposal:
        """Create a new proposal."""
        return cls(
            proposal_id=str(uuid.uuid4()),
            session_id=session_id,
            proposer_id=proposer_id,
            title=title,
            description=description,
            content=content,
            required_votes=required_votes,
            deadline=datetime.now(UTC).timestamp() + deadline_seconds,
        )

    def vote(self, agent_id: str, value: VoteValue) -> None:
        """Record a vote."""
        self.votes[agent_id] = value
        self._update_state()

    def _update_state(self) -> None:
        """Update proposal state based on votes."""
        if not self.votes:
            return

        accepts = sum(1 for v in self.votes.values() if v == VoteValue.ACCEPT)
        rejects = sum(1 for v in self.votes.values() if v == VoteValue.REJECT)

        if rejects > 0:
            self.state = ConsensusState.DISAGREED
        elif accepts >= self.required_votes:
            self.state = ConsensusState.AGREED
        else:
            self.state = ConsensusState.VOTING


# =============================================================================
# Collaboration Metrics
# =============================================================================


@dataclass
class CollaborationMetrics:
    """Metrics for collaboration."""

    sessions_created: int = 0
    sessions_completed: int = 0
    sessions_failed: int = 0
    messages_sent: int = 0
    proposals_created: int = 0
    consensus_achieved: int = 0
    consensus_failed: int = 0
    avg_session_duration_seconds: float = 0.0

    # By type
    by_type: dict[str, int] = field(default_factory=dict)
