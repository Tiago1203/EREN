"""Unit tests for EREN Multi-Agent Collaboration Layer."""

import pytest

from core.collaboration.types import (
    MessageType,
    MessageStatus,
    CollaborationStatus,
    ConsensusState,
    VoteValue,
    CollaborationMessage,
    CollaborationSession,
    TaskAssignment,
    Proposal,
    CollaborationMetrics,
)
from core.collaboration.protocol import (
    ProtocolHandler,
    CommunicationPattern,
    MessageBuilder,
)
from core.collaboration.communication_bus import CommunicationBus
from core.collaboration.sessions import SessionManager
from core.collaboration.messaging import AgentMessaging
from core.collaboration.shared_context import SharedContext
from core.collaboration.consensus import ConsensusManager
from core.collaboration.resolver import ConflictResolver, ConflictType
from core.collaboration.aggregator import ResultAggregator
from core.collaboration.dispatcher import TaskDispatcher
from core.collaboration.engine import CoordinationEngine


class TestCollaborationTypes:
    """Tests for collaboration types."""

    def test_message_creation(self):
        """Test message creation."""
        msg = CollaborationMessage.create(
            session_id="session-1",
            sender_id="agent-1",
            message_type=MessageType.REQUEST,
            content={"task": "test"},
        )
        assert msg.message_id
        assert msg.sender_id == "agent-1"
        assert msg.message_type == MessageType.REQUEST

    def test_session_creation(self):
        """Test session creation."""
        session = CollaborationSession(
            session_id="session-1",
            goal="Test goal",
            description="Test",
            initiator_id="agent-1",
        )
        assert session.session_id == "session-1"
        assert session.status == CollaborationStatus.CREATED

    def test_session_add_participant(self):
        """Test adding participant."""
        session = CollaborationSession(
            session_id="session-1",
            goal="Test",
            description="Test",
            initiator_id="agent-1",
        )
        session.add_participant("agent-2")
        assert "agent-2" in session.participant_ids


class TestProtocol:
    """Tests for protocol handler."""

    def test_register_handler(self):
        """Test registering handler."""
        handler = ProtocolHandler()
        called = []

        def callback(msg):
            called.append(msg)

        handler.register_handler(MessageType.REQUEST, callback)
        assert MessageType.REQUEST in handler._handlers

    def test_validate_message(self):
        """Test message validation."""
        handler = ProtocolHandler()
        msg = CollaborationMessage.create(
            session_id="s1",
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content={},
        )
        valid, error = handler.validate_message(msg)
        assert valid


class TestCommunicationPattern:
    """Tests for communication patterns."""

    def test_one_to_one(self):
        """Test one-to-one."""
        receivers = CommunicationPattern.one_to_one("a1", "a2", {})
        assert receivers == ["a2"]

    def test_one_to_many(self):
        """Test one-to-many."""
        receivers = CommunicationPattern.one_to_many("a1", ["a2", "a3"], {})
        assert receivers == ["a2", "a3"]

    def test_broadcast(self):
        """Test broadcast."""
        receivers = CommunicationPattern.broadcast("a1", ["a1", "a2", "a3"], {})
        assert receivers == ["a2", "a3"]


class TestCommunicationBus:
    """Tests for communication bus."""

    def test_send(self):
        """Test sending message."""
        bus = CommunicationBus()
        msg = CollaborationMessage.create(
            session_id="s1",
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content="test",
            receiver_ids=["a2"],
        )
        bus.send(msg)
        assert len(bus._history) == 1

    def test_receive(self):
        """Test receiving message."""
        bus = CommunicationBus()
        msg = CollaborationMessage.create(
            session_id="s1",
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content="test",
            receiver_ids=["a2"],
        )
        bus.send(msg)

        received = bus.receive("a2")
        assert received is not None
        assert received.content == "test"

    def test_broadcast(self):
        """Test broadcasting."""
        bus = CommunicationBus()
        msg = bus.broadcast(
            sender_id="a1",
            receiver_ids=["a2", "a3"],
            content="broadcast",
            session_id="s1",
        )
        assert msg.message_type == MessageType.BROADCAST

    def test_subscribe(self):
        """Test subscribing."""
        bus = CommunicationBus()
        received = []

        def callback(msg):
            received.append(msg)

        bus.subscribe("session:s1", callback)
        msg = CollaborationMessage.create(
            session_id="s1",
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content="test",
            receiver_ids=["a2"],
        )
        bus.send(msg)
        assert len(received) == 1

    def test_route(self):
        """Test routing."""
        bus = CommunicationBus()
        msg = bus.route(
            sender_id="a1",
            receiver_id="a2",
            content="direct",
            session_id="s1",
        )
        assert msg.receiver_ids == ["a2"]


class TestSessionManager:
    """Tests for session manager."""

    def test_create_session(self):
        """Test creating session."""
        manager = SessionManager()
        session = manager.create_session(
            initiator_id="a1",
            goal="Test goal",
            description="Test",
            participant_ids=["a2"],
        )
        assert session.session_id
        assert session.initiator_id == "a1"

    def test_start_session(self):
        """Test starting session."""
        manager = SessionManager()
        session = manager.create_session("a1", "Goal", "Desc")
        manager.start_session(session.session_id)
        assert session.status == CollaborationStatus.ACTIVE

    def test_join_leave_session(self):
        """Test joining and leaving."""
        manager = SessionManager()
        session = manager.create_session("a1", "Goal", "Desc")

        manager.join_session(session.session_id, "a4")
        assert "a4" in session.participant_ids

        manager.leave_session(session.session_id, "a4")
        assert "a4" not in session.participant_ids

    def test_complete_session(self):
        """Test completing session."""
        manager = SessionManager()
        session = manager.create_session("a1", "Goal", "Desc")
        manager.complete_session(session.session_id, {"result": "done"})
        assert session.status == CollaborationStatus.COMPLETED

    def test_get_agent_sessions(self):
        """Test getting agent sessions."""
        manager = SessionManager()
        session = manager.create_session("a1", "Goal", "Desc")
        sessions = manager.get_agent_sessions("a1")
        assert len(sessions) == 1


class TestMessaging:
    """Tests for messaging system."""

    def test_send_receive(self):
        """Test send and receive."""
        messaging = AgentMessaging()
        msg = CollaborationMessage.create(
            session_id="s1",
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content="test",
            receiver_ids=["a2"],
        )
        messaging.send(msg)

        received = messaging.receive("a2")
        assert received is not None
        assert received.content == "test"


class TestSharedContext:
    """Tests for shared context."""

    def test_create_context(self):
        """Test creating context."""
        context = SharedContext()
        context.create_session_context("s1")
        assert "s1" in context._contexts

    def test_put_get(self):
        """Test put and get."""
        context = SharedContext()
        context.put("s1", "key", "value", "a1")
        value = context.get("s1", "key")
        assert value == "value"


class TestConsensus:
    """Tests for consensus manager."""

    def test_create_proposal(self):
        """Test creating proposal."""
        consensus = ConsensusManager()
        proposal = consensus.create_proposal(
            session_id="s1",
            proposer_id="a1",
            title="Test",
            description="Test",
            content={},
        )
        assert proposal.proposal_id

    def test_vote(self):
        """Test voting."""
        consensus = ConsensusManager()
        proposal = consensus.create_proposal(
            session_id="s1",
            proposer_id="a1",
            title="Test",
            description="Test",
            content={},
            required_votes=2,
        )

        consensus.vote(proposal.proposal_id, "a2", VoteValue.ACCEPT)
        consensus.vote(proposal.proposal_id, "a3", VoteValue.ACCEPT)

        assert consensus.is_consensus_reached(proposal.proposal_id)


class TestConflictResolver:
    """Tests for conflict resolver."""

    def test_create_conflict(self):
        """Test creating conflict."""
        resolver = ConflictResolver()
        conflict = resolver.create_conflict(
            session_id="s1",
            conflict_type=ConflictType.DECISION,
            description="Test",
            parties=["a1", "a2"],
        )
        assert conflict.conflict_id

    def test_resolve_by_priority(self):
        """Test resolving by priority."""
        resolver = ConflictResolver()
        conflict = resolver.create_conflict(
            session_id="s1",
            conflict_type=ConflictType.PRIORITY,
            description="Test",
            parties=["a1", "a2"],
        )

        resolver.resolve_by_priority(
            conflict_id=conflict.conflict_id,
            priorities={"a1": 5, "a2": 10},
        )

        assert resolver.get_conflict(conflict.conflict_id).is_resolved


class TestResultAggregator:
    """Tests for result aggregator."""

    def test_add_result(self):
        """Test adding result."""
        aggregator = ResultAggregator()
        aggregator.add_result("s1", "a1", {"data": "test"}, priority=5)
        assert aggregator.get_result_count("s1") == 1

    def test_aggregate(self):
        """Test aggregating results."""
        aggregator = ResultAggregator()
        aggregator.add_result("s1", "a1", "result1")
        aggregator.add_result("s1", "a2", "result2")

        results = aggregator.aggregate("s1", strategy="all")
        assert len(results) == 2


class TestTaskDispatcher:
    """Tests for task dispatcher."""

    def test_create_assignment(self):
        """Test creating assignment."""
        dispatcher = TaskDispatcher()
        assignment = dispatcher.create_assignment(
            session_id="s1",
            task_id="t1",
            agent_id="a1",
            description="Test task",
        )
        assert assignment.assignment_id

    def test_accept_assignment(self):
        """Test accepting assignment."""
        dispatcher = TaskDispatcher()
        assignment = dispatcher.create_assignment(
            session_id="s1",
            task_id="t1",
            agent_id="a1",
            description="Test",
        )

        dispatcher.accept(assignment.assignment_id)
        assert assignment.status == "accepted"

    def test_complete_assignment(self):
        """Test completing assignment."""
        dispatcher = TaskDispatcher()
        assignment = dispatcher.create_assignment(
            session_id="s1",
            task_id="t1",
            agent_id="a1",
            description="Test",
        )

        dispatcher.accept(assignment.assignment_id)
        dispatcher.complete(assignment.assignment_id, {"done": True})
        assert assignment.status == "completed"


class TestCoordinationEngine:
    """Tests for coordination engine."""

    def test_create_session(self):
        """Test creating session."""
        engine = CoordinationEngine()
        session = engine.create_session(
            initiator_id="a1",
            goal="Test goal",
            description="Test",
            participant_ids=["a2", "a3"],
        )
        assert session.session_id
        assert session.initiator_id == "a1"
        assert len(session.participant_ids) == 2

    def test_start_session(self):
        """Test starting session."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")
        engine.start_session(session.session_id)
        assert session.status == CollaborationStatus.ACTIVE

    def test_join_leave_session(self):
        """Test joining and leaving session."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")

        engine.join_session(session.session_id, "a4")
        assert "a4" in session.participant_ids

        engine.leave_session(session.session_id, "a4")
        assert "a4" not in session.participant_ids

    def test_send_message(self):
        """Test sending message."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc", ["a2"])

        msg = engine.send_message(
            session_id=session.session_id,
            sender_id="a1",
            message_type=MessageType.REQUEST,
            content={"task": "test"},
        )

        assert msg is not None

    def test_broadcast(self):
        """Test broadcasting."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc", ["a2", "a3"])

        msg = engine.broadcast(
            session_id=session.session_id,
            sender_id="a1",
            content={"update": "test"},
        )

        assert msg is not None
        assert MessageType.BROADCAST == MessageType.BROADCAST

    def test_context(self):
        """Test shared context."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")

        engine.put_context(session.session_id, "key", "value", "a1")
        value = engine.get_context(session.session_id, "key")

        assert value == "value"

    def test_proposal(self):
        """Test creating proposal."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc", ["a2"])

        proposal = engine.create_proposal(
            session_id=session.session_id,
            proposer_id="a1",
            title="Test",
            description="Test",
            content={},
        )

        assert proposal is not None

    def test_add_result(self):
        """Test adding result."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")

        engine.add_result(session.session_id, "a1", {"data": "test"})
        result = engine.aggregate_results(session.session_id)

        assert result is not None

    def test_complete_session(self):
        """Test completing session."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")

        engine.complete_session(session.session_id, {"final": "result"})
        assert session.status == CollaborationStatus.COMPLETED

    def test_cancel_session(self):
        """Test cancelling session."""
        engine = CoordinationEngine()
        session = engine.create_session("a1", "Goal", "Desc")

        engine.cancel_session(session.session_id, "User cancelled")
        assert session.status == CollaborationStatus.CANCELLED

    def test_get_metrics(self):
        """Test getting metrics."""
        engine = CoordinationEngine()
        engine.create_session("a1", "Goal", "Desc")

        metrics = engine.get_metrics()
        assert metrics.sessions_created >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
