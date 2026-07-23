"""
Tests for EPIC 7: Collaboration Engine

Test suite for the Collaboration Engine.
"""

import pytest
from datetime import UTC, datetime

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.foundation import (
    AgentType,
    AgentState,
    AgentTask,
)

from core.PHASE_5.epic7_collaboration import (
    CollaborationEngine,
    CollaborationEngineConfig,
)

from core.PHASE_5.epic7_collaboration.domain import (
    SharedContext,
    ContextEntry,
    ContextType,
    CollaborationSession,
    SessionStatus,
    Participant,
    AgentConversation,
    Message,
    MessageType,
)

from core.PHASE_5.epic7_collaboration.engines import (
    ContextSharing,
    AgentMessaging,
    CollaborationBus,
    SharedWorkspace,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def engine_config():
    """Create engine config."""
    return CollaborationEngineConfig(
        enable_context_sharing=True,
        enable_agent_messaging=True,
        enable_collaboration_bus=True,
        enable_shared_workspace=True,
    )


@pytest.fixture
def collaboration_engine(engine_config):
    """Create collaboration engine."""
    return CollaborationEngine(
        agent_id="collab_test_1",
        config=engine_config,
    )


# =============================================================================
# TEST COLLABORATION ENGINE
# =============================================================================

class TestCollaborationEngine:
    """Tests for CollaborationEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, collaboration_engine, engine_config):
        """Test engine initializes correctly."""
        assert collaboration_engine.agent_id == "collab_test_1"
        assert collaboration_engine.agent_type == AgentType.COLLABORATION
        assert collaboration_engine.config == engine_config
        
        # Engines should be initialized
        assert collaboration_engine._context_sharing is not None
        assert collaboration_engine._agent_messaging is not None
        assert collaboration_engine._collaboration_bus is not None
        assert collaboration_engine._shared_workspace is not None
    
    @pytest.mark.asyncio
    async def test_engine_initialize(self, collaboration_engine):
        """Test engine initialization method."""
        await collaboration_engine.initialize()
        assert collaboration_engine.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_create_session(self, collaboration_engine):
        """Test session creation."""
        task = AgentTask(
            task_id="task_1",
            agent_id="collab_test_1",
            task_type="collaboration",
            input_data={
                "action": "session",
                "operation": "create",
                "session_type": "parallel",
                "participants": ["agent_1", "agent_2"],
            },
        )
        
        result = await collaboration_engine.execute(task)
        
        assert result is not None
        assert result.success is True
        assert "session_id" in result.output
    
    @pytest.mark.asyncio
    async def test_share_context(self, collaboration_engine):
        """Test context sharing."""
        task = AgentTask(
            task_id="task_2",
            agent_id="collab_test_1",
            task_type="collaboration",
            input_data={
                "action": "context",
                "operation": "share",
                "session_id": "test_session",
                "agent_id": "agent_1",
                "entries": [
                    ("key1", "value1", "task"),
                ],
            },
        )
        
        result = await collaboration_engine.execute(task)
        
        assert result is not None
        assert "success" in result.output or "operation" in result.output
    
    @pytest.mark.asyncio
    async def test_send_message(self, collaboration_engine):
        """Test message sending."""
        task = AgentTask(
            task_id="task_3",
            agent_id="collab_test_1",
            task_type="collaboration",
            input_data={
                "action": "message",
                "operation": "send",
                "sender_id": "agent_1",
                "recipient_id": "agent_2",
                "content": "Hello!",
            },
        )
        
        result = await collaboration_engine.execute(task)
        
        assert result is not None
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_metrics(self, collaboration_engine):
        """Test engine metrics."""
        metrics = collaboration_engine.get_metrics()
        
        assert "sessions_created" in metrics
        assert "messages_sent" in metrics
        assert "engines_enabled" in metrics


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestContextEntry:
    """Tests for ContextEntry."""
    
    def test_entry_creation(self):
        """Test entry creation."""
        entry = ContextEntry(
            entry_id="entry_1",
            context_type=ContextType.TASK,
            key="test_key",
            value="test_value",
        )
        
        assert entry.entry_id == "entry_1"
        assert entry.context_type == ContextType.TASK
    
    def test_entry_expiry(self):
        """Test entry expiry check."""
        from datetime import timedelta
        
        entry = ContextEntry(
            context_type=ContextType.TASK,
            key="test",
            value="test",
            ttl_seconds=1,
        )
        
        assert not entry.is_expired()


class TestSharedContext:
    """Tests for SharedContext."""
    
    def test_context_creation(self):
        """Test context creation."""
        context = SharedContext(
            context_id="ctx_1",
            session_id="session_1",
        )
        
        assert context.context_id == "ctx_1"
        assert context.entries_count == 0
    
    def test_add_entry(self):
        """Test adding entries."""
        context = SharedContext(session_id="session_1")
        
        context.add_entry(ContextEntry(
            context_type=ContextType.TASK,
            key="key1",
            value="value1",
        ))
        
        assert context.entries_count == 1
    
    def test_get_entry(self):
        """Test getting entry by key."""
        context = SharedContext(session_id="session_1")
        
        context.add_entry(ContextEntry(
            context_type=ContextType.TASK,
            key="key1",
            value="value1",
        ))
        
        entry = context.get_entry("key1")
        assert entry is not None
        assert entry.key == "key1"


class TestCollaborationSession:
    """Tests for CollaborationSession."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = CollaborationSession(
            session_id="sess_1",
            session_type="parallel",
        )
        
        assert session.session_id == "sess_1"
        assert session.status == SessionStatus.PENDING
    
    def test_add_participant(self):
        """Test adding participants."""
        session = CollaborationSession(session_type="parallel")
        
        participant = session.add_participant("agent_1", "contributor")
        
        assert participant.agent_id == "agent_1"
        assert len(session.participants) == 1
    
    def test_start_session(self):
        """Test starting session."""
        session = CollaborationSession(session_type="parallel")
        
        session.start()
        
        assert session.status == SessionStatus.ACTIVE
    
    def test_complete_session(self):
        """Test completing session."""
        session = CollaborationSession(session_type="parallel")
        
        session.complete()
        
        assert session.status == SessionStatus.COMPLETED


class TestMessage:
    """Tests for Message."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = Message(
            message_id="msg_1",
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        )
        
        assert message.message_id == "msg_1"
        assert message.sender_id == "agent_1"
        assert message.recipient_id == "agent_2"
    
    def test_mark_read(self):
        """Test marking message as read."""
        message = Message(
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        )
        
        assert not message.read
        message.mark_read()
        assert message.read


class TestAgentConversation:
    """Tests for AgentConversation."""
    
    def test_conversation_creation(self):
        """Test conversation creation."""
        conv = AgentConversation(
            conversation_id="conv_1",
            participants=["agent_1", "agent_2"],
        )
        
        assert conv.conversation_id == "conv_1"
        assert len(conv.participants) == 2
    
    def test_add_message(self):
        """Test adding messages."""
        conv = AgentConversation(participants=["agent_1", "agent_2"])
        
        conv.add_message(Message(
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        ))
        
        assert len(conv.messages) == 1
    
    def test_get_unread_count(self):
        """Test unread count."""
        conv = AgentConversation(participants=["agent_1", "agent_2"])
        
        conv.add_message(Message(
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        ))
        
        assert conv.get_unread_count("agent_2") == 1


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestContextSharing:
    """Tests for ContextSharing."""
    
    @pytest.mark.asyncio
    async def test_share_context(self):
        """Test sharing context."""
        sharing = ContextSharing()
        
        result = await sharing.share_context(
            session_id="session_1",
            source_agent_id="agent_1",
            entries=[("key1", "value1", ContextType.TASK)],
        )
        
        assert result.success is True
        assert result.entries_shared == 1
    
    @pytest.mark.asyncio
    async def test_get_context(self):
        """Test getting context."""
        sharing = ContextSharing()
        
        await sharing.share_context(
            session_id="session_1",
            source_agent_id="agent_1",
            entries=[("key1", "value1", ContextType.TASK)],
        )
        
        context = await sharing.get_context("session_1")
        assert context is not None


class TestAgentMessaging:
    """Tests for AgentMessaging."""
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending message."""
        messaging = AgentMessaging()
        
        result = await messaging.send_message(
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        )
        
        assert result.success is True
        assert result.message_id != ""
    
    @pytest.mark.asyncio
    async def test_receive_messages(self):
        """Test receiving messages."""
        messaging = AgentMessaging()
        
        await messaging.send_message(
            sender_id="agent_1",
            recipient_id="agent_2",
            content="Hello!",
        )
        
        messages = await messaging.get_messages("agent_2")
        assert len(messages) == 1


class TestCollaborationBus:
    """Tests for CollaborationBus."""
    
    @pytest.mark.asyncio
    async def test_publish(self):
        """Test publishing message."""
        bus = CollaborationBus()
        
        message = await bus.publish(
            topic="test.topic",
            sender_id="agent_1",
            content={"key": "value"},
        )
        
        assert message.message_id != ""
        assert message.topic == "test.topic"
    
    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test subscribing to topic."""
        bus = CollaborationBus()
        
        success = await bus.subscribe("agent_1", "test.topic")
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_get_messages(self):
        """Test getting messages."""
        bus = CollaborationBus()
        
        await bus.subscribe("agent_1", "test.topic")
        await bus.publish("test.topic", "agent_2", {"data": "test"})
        
        messages = await bus.get_messages("agent_1", "test.topic")
        assert len(messages) == 1


class TestSharedWorkspace:
    """Tests for SharedWorkspace."""
    
    @pytest.mark.asyncio
    async def test_create_workspace(self):
        """Test creating workspace."""
        workspace = SharedWorkspace()
        
        result = await workspace.create_workspace(
            workspace_id="ws_1",
            owner_id="agent_1",
        )
        
        assert result["workspace_id"] == "ws_1"
    
    @pytest.mark.asyncio
    async def test_add_artifact(self):
        """Test adding artifact."""
        workspace = SharedWorkspace()
        
        await workspace.create_workspace("ws_1", "agent_1")
        success = await workspace.add_artifact(
            "ws_1",
            "agent_1",
            {"type": "report", "content": "Test"},
        )
        
        assert success is True


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_context_type_values(self):
        """Test ContextType enum values."""
        assert ContextType.TASK.value == "task"
        assert ContextType.RESULT.value == "result"
        assert ContextType.STATE.value == "state"
    
    def test_session_status_values(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.PENDING.value == "pending"
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.COMPLETED.value == "completed"
    
    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.REQUEST.value == "request"
        assert MessageType.RESPONSE.value == "response"
        assert MessageType.NOTIFICATION.value == "notification"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
