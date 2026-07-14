"""Multi-Agent Collaboration Engine (MACE) for EREN OS.

Main engine for multi-agent collaboration.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.collaboration.types import (
    CollaborationSession,
    CollaborationStatus,
    CollaborationMessage,
    MessageType,
    CollaborationMetrics,
)
from core.collaboration.protocol import (
    ProtocolHandler,
    MessageBuilder,
    CommunicationPattern,
)
from core.collaboration.messaging import AgentMessaging, get_messaging
from core.collaboration.shared_context import SharedContext, get_shared_context
from core.collaboration.consensus import ConsensusManager, get_consensus_manager
from core.collaboration.resolver import ConflictResolver, get_conflict_resolver
from core.collaboration.aggregator import ResultAggregator, get_result_aggregator
from core.collaboration.dispatcher import TaskDispatcher, get_task_dispatcher

if TYPE_CHECKING:
    pass


class CollaborationEngine:
    """Multi-Agent Collaboration Engine.

    The Collaboration Engine does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Creates collaboration sessions
    - Manages agents
    - Coordinates communication
    - Builds consensus
    - Resolves conflicts
    - Aggregates results

    Philosophy:
        Agents don't work in isolation.
        They collaborate.
        They negotiate.
        They share knowledge.
        They build solutions together.
    """

    def __init__(self):
        """Initialize collaboration engine."""
        # Core components
        self._messaging = get_messaging()
        self._context = get_shared_context()
        self._consensus = get_consensus_manager()
        self._resolver = get_conflict_resolver()
        self._aggregator = get_result_aggregator()
        self._dispatcher = get_task_dispatcher()
        self._protocol = ProtocolHandler()

        # Sessions
        self._sessions: dict[str, CollaborationSession] = {}

        # Metrics
        self._metrics = CollaborationMetrics()

    def create_session(
        self,
        initiator_id: str,
        goal: str,
        description: str,
        participant_ids: list[str] | None = None,
        timeout_seconds: float = 300.0,
        consensus_required: bool = True,
    ) -> CollaborationSession:
        """Create a new collaboration session.

        Args:
            initiator_id: Initiating agent ID.
            goal: Collaboration goal.
            description: Session description.
            participant_ids: Initial participant IDs.
            timeout_seconds: Session timeout.
            consensus_required: Whether consensus is required.

        Returns:
            Created session.
        """
        session_id = str(uuid.uuid4())

        session = CollaborationSession(
            session_id=session_id,
            goal=goal,
            description=description,
            initiator_id=initiator_id,
            participant_ids=participant_ids or [],
            status=CollaborationStatus.CREATED,
            timeout_seconds=timeout_seconds,
            consensus_required=consensus_required,
        )

        self._sessions[session_id] = session
        self._context.create_session_context(session_id)

        # Update metrics
        self._metrics.sessions_created += 1

        return session

    def start_session(
        self,
        session_id: str,
    ) -> bool:
        """Start a collaboration session.

        Args:
            session_id: Session ID.

        Returns:
            True if started.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.ACTIVE
        session.started_at = datetime.now(timezone.utc)

        return True

    def join_session(
        self,
        session_id: str,
        agent_id: str,
    ) -> bool:
        """Join a collaboration session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if joined.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.add_participant(agent_id)
        return True

    def leave_session(
        self,
        session_id: str,
        agent_id: str,
    ) -> bool:
        """Leave a collaboration session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if left.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.remove_participant(agent_id)
        return True

    def send_message(
        self,
        session_id: str,
        sender_id: str,
        message_type: MessageType,
        content: Any,
        receiver_ids: list[str] | None = None,
    ) -> CollaborationMessage | None:
        """Send a message in a session.

        Args:
            session_id: Session ID.
            sender_id: Sender agent ID.
            message_type: Type of message.
            content: Message content.
            receiver_ids: Receiver agent IDs.

        Returns:
            Sent message or None.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        # Build message
        if message_type == MessageType.BROADCAST:
            receivers = CommunicationPattern.broadcast(
                sender_id,
                session.participant_ids + [session.initiator_id],
                content,
            )
        else:
            receivers = receiver_ids or session.participant_ids

        message = MessageBuilder.request(
            session_id=session_id,
            sender_id=sender_id,
            receiver_ids=receivers,
            content=content,
        )

        # Send via messaging
        self._messaging.send(message)

        # Add to session
        session.add_message(message)

        # Update metrics
        self._metrics.messages_sent += 1

        return message

    def broadcast(
        self,
        session_id: str,
        sender_id: str,
        content: Any,
    ) -> CollaborationMessage | None:
        """Broadcast to all participants.

        Args:
            session_id: Session ID.
            sender_id: Sender agent ID.
            content: Broadcast content.

        Returns:
            Broadcast message or None.
        """
        return self.send_message(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.BROADCAST,
            content=content,
        )

    def receive_message(
        self,
        agent_id: str,
    ) -> CollaborationMessage | None:
        """Receive a message for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            Message or None.
        """
        return self._messaging.receive(agent_id)

    def receive_all_messages(
        self,
        agent_id: str,
    ) -> list[CollaborationMessage]:
        """Receive all messages for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of messages.
        """
        return self._messaging.receive_all(agent_id)

    def put_context(
        self,
        session_id: str,
        key: str,
        value: Any,
        agent_id: str = "",
    ) -> None:
        """Put a value in shared context.

        Args:
            session_id: Session ID.
            key: Key.
            value: Value.
            agent_id: Contributing agent ID.
        """
        self._context.put(session_id, key, value, agent_id)

    def get_context(
        self,
        session_id: str,
        key: str,
    ) -> Any | None:
        """Get a value from shared context.

        Args:
            session_id: Session ID.
            key: Key.

        Returns:
            Value or None.
        """
        return self._context.get(session_id, key)

    def get_session_context(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get all shared context for a session.

        Args:
            session_id: Session ID.

        Returns:
            All context values.
        """
        return self._context.get_all(session_id)

    def create_proposal(
        self,
        session_id: str,
        proposer_id: str,
        title: str,
        description: str,
        content: Any,
        required_votes: int = 0,
    ):
        """Create a proposal for consensus.

        Args:
            session_id: Session ID.
            proposer_id: Proposer agent ID.
            title: Proposal title.
            description: Proposal description.
            content: Proposal content.
            required_votes: Required votes for consensus.

        Returns:
            Created proposal.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        proposal = self._consensus.create_proposal(
            session_id=session_id,
            proposer_id=proposer_id,
            title=title,
            description=description,
            content=content,
            required_votes=required_votes or len(session.participant_ids) // 2 + 1,
        )

        # Update metrics
        self._metrics.proposals_created += 1

        return proposal

    def vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: str,
    ) -> bool:
        """Vote on a proposal.

        Args:
            proposal_id: Proposal ID.
            agent_id: Voting agent ID.
            vote: Vote value.

        Returns:
            True if vote recorded.
        """
        from core.collaboration.types import VoteValue
        return self._consensus.vote(proposal_id, agent_id, VoteValue(vote))

    def add_result(
        self,
        session_id: str,
        agent_id: str,
        result: Any,
        priority: int = 5,
    ) -> None:
        """Add a result from an agent.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.
            result: Result value.
            priority: Agent priority.
        """
        self._aggregator.add_result(session_id, agent_id, result, priority)

    def aggregate_results(
        self,
        session_id: str,
        strategy: str = "priority",
    ) -> Any:
        """Aggregate all results.

        Args:
            session_id: Session ID.
            strategy: Aggregation strategy.

        Returns:
            Aggregated result.
        """
        return self._aggregator.aggregate(session_id, strategy)

    def complete_session(
        self,
        session_id: str,
        final_result: Any = None,
    ) -> bool:
        """Complete a collaboration session.

        Args:
            session_id: Session ID.
            final_result: Final aggregated result.

        Returns:
            True if completed.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.final_result = final_result

        # Update metrics
        self._metrics.sessions_completed += 1

        return True

    def cancel_session(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Cancel a collaboration session.

        Args:
            session_id: Session ID.
            reason: Cancellation reason.

        Returns:
            True if cancelled.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.CANCELLED
        session.completed_at = datetime.now(timezone.utc)
        session.metadata["cancellation_reason"] = reason

        return True

    def get_session(
        self,
        session_id: str,
    ) -> CollaborationSession | None:
        """Get a session.

        Args:
            session_id: Session ID.

        Returns:
            Session or None.
        """
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> list[CollaborationSession]:
        """Get all sessions.

        Returns:
            List of sessions.
        """
        return list(self._sessions.values())

    def get_metrics(self) -> CollaborationMetrics:
        """Get collaboration metrics.

        Returns:
            Metrics.
        """
        return self._metrics


# Global collaboration engine
_global_engine: CollaborationEngine | None = None
_engine_lock = __import__("threading").Lock()


def get_collaboration_engine() -> CollaborationEngine:
    """Get the global collaboration engine.

    Returns:
        Global CollaborationEngine instance.
    """
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = CollaborationEngine()
        return _global_engine


def reset_collaboration_engine() -> None:
    """Reset the global collaboration engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
