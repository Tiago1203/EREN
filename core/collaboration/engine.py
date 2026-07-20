"""Coordination Engine for EREN Multi-Agent Collaboration Layer.

Main engine for coordinating multi-agent collaboration.
Separated from communication - this handles coordination logic only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.collaboration.aggregator import get_result_aggregator
from core.collaboration.communication_bus import (
    get_communication_bus,
)
from core.collaboration.consensus import get_consensus_manager
from core.collaboration.dispatcher import get_task_dispatcher
from core.collaboration.protocol import (
    CommunicationPattern,
    MessageBuilder,
)
from core.collaboration.resolver import get_conflict_resolver
from core.collaboration.sessions import (
    get_session_manager,
)
from core.collaboration.shared_context import get_shared_context
from core.collaboration.types import (
    CollaborationMessage,
    CollaborationMetrics,
    CollaborationSession,
    MessageType,
)

if TYPE_CHECKING:
    pass


class CoordinationEngine:
    """Coordination Engine for multi-agent collaboration.

    The Coordination Engine does NOT:
    - Handle message transport
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Creates teams/sessions
    - Assigns tasks
    - Waits for results
    - Coordinates execution
    - Resolves conflicts
    - Builds final response

    Philosophy:
        Communication and collaboration are distinct concepts.
        Agents can communicate without collaborating.
        Collaboration uses communication as infrastructure.
    """

    def __init__(self):
        """Initialize coordination engine."""
        # Communication layer (infrastructure)
        self._bus = get_communication_bus()

        # Session management
        self._sessions = get_session_manager()

        # Coordination components
        self._context = get_shared_context()
        self._consensus = get_consensus_manager()
        self._resolver = get_conflict_resolver()
        self._aggregator = get_result_aggregator()
        self._dispatcher = get_task_dispatcher()

        # Metrics
        self._metrics = CollaborationMetrics()

    # ========================================================================
    # Session Management (delegates to SessionManager)
    # ========================================================================

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
        session = self._sessions.create_session(
            initiator_id=initiator_id,
            goal=goal,
            description=description,
            participant_ids=participant_ids,
            timeout_seconds=timeout_seconds,
            consensus_required=consensus_required,
        )

        # Create shared context
        self._context.create_session_context(session.session_id)

        # Update metrics
        self._metrics.sessions_created += 1

        return session

    def start_session(self, session_id: str) -> bool:
        """Start a collaboration session.

        Args:
            session_id: Session ID.

        Returns:
            True if started.
        """
        return self._sessions.start_session(session_id)

    def join_session(self, session_id: str, agent_id: str) -> bool:
        """Join a collaboration session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if joined.
        """
        return self._sessions.join_session(session_id, agent_id)

    def leave_session(self, session_id: str, agent_id: str) -> bool:
        """Leave a collaboration session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if left.
        """
        return self._sessions.leave_session(session_id, agent_id)

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
        if self._sessions.complete_session(session_id, final_result):
            self._metrics.sessions_completed += 1
            return True
        return False

    def cancel_session(self, session_id: str, reason: str = "") -> bool:
        """Cancel a collaboration session.

        Args:
            session_id: Session ID.
            reason: Cancellation reason.

        Returns:
            True if cancelled.
        """
        return self._sessions.cancel_session(session_id, reason)

    def get_session(self, session_id: str) -> CollaborationSession | None:
        """Get a session.

        Args:
            session_id: Session ID.

        Returns:
            Session or None.
        """
        return self._sessions.get_session(session_id)

    def get_all_sessions(self) -> list[CollaborationSession]:
        """Get all sessions.

        Returns:
            List of sessions.
        """
        return self._sessions.get_all_sessions()

    # ========================================================================
    # Communication (delegates to Communication Bus)
    # ========================================================================

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
        session = self._sessions.get_session(session_id)
        if not session:
            return None

        # Determine receivers
        if message_type == MessageType.BROADCAST:
            receivers = CommunicationPattern.broadcast(
                sender_id,
                session.participant_ids + [session.initiator_id],
                content,
            )
        else:
            receivers = receiver_ids or session.participant_ids

        # Build message
        message = MessageBuilder.request(
            session_id=session_id,
            sender_id=sender_id,
            receiver_ids=receivers,
            content=content,
        )

        # Send via bus
        self._bus.send(message)

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

    def receive_message(self, agent_id: str) -> CollaborationMessage | None:
        """Receive a message for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            Message or None.
        """
        return self._bus.receive(agent_id)

    def receive_all_messages(self, agent_id: str) -> list[CollaborationMessage]:
        """Receive all messages for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of messages.
        """
        return self._bus.receive_all(agent_id)

    # ========================================================================
    # Shared Context
    # ========================================================================

    def put_context(
        self,
        session_id: str,
        key: str,
        value: Any,
        agent_id: str = "",
    ) -> None:
        """Put a value in shared context."""
        self._context.put(session_id, key, value, agent_id)

    def get_context(self, session_id: str, key: str) -> Any | None:
        """Get a value from shared context."""
        return self._context.get(session_id, key)

    def get_session_context(self, session_id: str) -> dict[str, Any]:
        """Get all shared context for a session."""
        return self._context.get_all(session_id)

    # ========================================================================
    # Consensus
    # ========================================================================

    def create_proposal(
        self,
        session_id: str,
        proposer_id: str,
        title: str,
        description: str,
        content: Any,
        required_votes: int = 0,
    ):
        """Create a proposal for consensus."""
        session = self._sessions.get_session(session_id)
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

        self._metrics.proposals_created += 1
        return proposal

    def vote(self, proposal_id: str, agent_id: str, vote: str) -> bool:
        """Vote on a proposal."""
        from core.collaboration.types import VoteValue
        return self._consensus.vote(proposal_id, agent_id, VoteValue(vote))

    # ========================================================================
    # Results
    # ========================================================================

    def add_result(
        self,
        session_id: str,
        agent_id: str,
        result: Any,
        priority: int = 5,
    ) -> None:
        """Add a result from an agent."""
        self._aggregator.add_result(session_id, agent_id, result, priority)
        self._sessions.add_result(session_id, agent_id, result)

    def aggregate_results(
        self,
        session_id: str,
        strategy: str = "priority",
    ) -> Any:
        """Aggregate all results."""
        return self._aggregator.aggregate(session_id, strategy)

    # ========================================================================
    # Metrics
    # ========================================================================

    def get_metrics(self) -> CollaborationMetrics:
        """Get collaboration metrics."""
        return self._metrics


# Global coordination engine
_global_engine: CoordinationEngine | None = None
_engine_lock = __import__("threading").Lock()


def get_collaboration_engine() -> CoordinationEngine:
    """Get the global collaboration/coordination engine.

    Returns:
        Global CoordinationEngine instance.
    """
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = CoordinationEngine()
        return _global_engine


def reset_collaboration_engine() -> None:
    """Reset the global collaboration engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None


# Alias for backwards compatibility
CollaborationEngine = CoordinationEngine
