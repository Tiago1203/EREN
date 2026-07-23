"""
Tests for PHASE 5 EPIC 0 - Multi-Agent Architecture Foundation
"""

import pytest
from datetime import UTC, datetime
import uuid

from core.PHASE_5.foundation import (
    # Types
    AgentState,
    AgentType,
    AgentCapability,
    AgentPriority,
    MessageType,
    AgentCapabilityVO,
    AgentVersion,
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
    # Events
    EventBus,
    EventFactory,
    AgentEventType,
    # Messaging
    MessageBroker,
    MessageBuilder,
    # Lifecycle
    AgentLifecycleManager,
    StateValidator,
    # Registry
    AgentRegistry,
    AgentLookup,
    # Context
    ContextManager,
    SessionManager,
    # Base
    BaseAgent,
)


# =============================================================================
# TYPE TESTS
# =============================================================================

class TestAgentTypes:
    """Tests for Agent types."""
    
    def test_agent_state_enum(self):
        """Test AgentState enum values."""
        assert AgentState.INITIAL.value == "initial"
        assert AgentState.IDLE.value == "idle"
        assert AgentState.RUNNING.value == "running"
        assert AgentState.COMPLETED.value == "completed"
        assert AgentState.FAILED.value == "failed"
        assert AgentState.STOPPED.value == "stopped"
    
    def test_agent_type_enum(self):
        """Test AgentType enum values."""
        assert AgentType.ORCHESTRATOR.value == "orchestrator"
        assert AgentType.BIOMEDICAL.value == "biomedical"
        assert AgentType.DIAGNOSTIC.value == "diagnostic"
        assert AgentType.KNOWLEDGE.value == "knowledge"
        assert AgentType.RESEARCH.value == "research"
    
    def test_agent_capability_enum(self):
        """Test AgentCapability enum values."""
        assert AgentCapability.DIAGNOSE.value == "diagnose"
        assert AgentCapability.RESEARCH.value == "research"
        assert AgentCapability.PLAN.value == "plan"
        assert AgentCapability.COLLABORATE.value == "collaborate"
    
    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.REQUEST.value == "request"
        assert MessageType.RESPONSE.value == "response"
        assert MessageType.NOTIFICATION.value == "notification"
        assert MessageType.ERROR.value == "error"


# =============================================================================
# DOMAIN OBJECT TESTS
# =============================================================================

class TestAgent:
    """Tests for Agent domain object."""
    
    def test_agent_creation(self):
        """Test Agent creation with defaults."""
        agent = Agent(
            agent_id="test_agent",
            agent_type=AgentType.BIOMEDICAL,
            name="Test Agent",
        )
        
        assert agent.agent_id == "test_agent"
        assert agent.agent_type == AgentType.BIOMEDICAL
        assert agent.name == "Test Agent"
        assert agent.state == AgentState.INITIAL
    
    def test_agent_auto_id(self):
        """Test Agent auto-generates ID if not provided."""
        agent = Agent(
            agent_type=AgentType.DIAGNOSTIC,
            name="Auto ID Agent",
        )
        
        assert agent.agent_id is not None
        assert len(agent.agent_id) > 0
    
    def test_agent_is_available(self):
        """Test Agent is_available property."""
        agent = Agent(
            agent_id="test",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
        )
        
        # Initial state is not available
        assert not agent.is_available
        
        # IDLE state is available
        agent.state = AgentState.IDLE
        assert agent.is_available
        
        # RUNNING state is not available
        agent.state = AgentState.RUNNING
        assert not agent.is_available
    
    def test_agent_has_capability(self):
        """Test Agent has_capability method."""
        agent = Agent(
            agent_id="test",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
            capabilities=[
                AgentCapabilityVO(AgentCapability.DIAGNOSE),
                AgentCapabilityVO(AgentCapability.RESEARCH),
            ],
        )
        
        assert agent.has_capability(AgentCapability.DIAGNOSE)
        assert agent.has_capability(AgentCapability.RESEARCH)
        assert not agent.has_capability(AgentCapability.PLAN)
    
    def test_agent_to_dict(self):
        """Test Agent to_dict method."""
        agent = Agent(
            agent_id="test",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
        )
        
        d = agent.to_dict()
        
        assert d["agent_id"] == "test"
        assert d["agent_type"] == "biomedical"
        assert d["name"] == "Test"


class TestAgentTask:
    """Tests for AgentTask domain object."""
    
    def test_task_creation(self):
        """Test AgentTask creation."""
        task = AgentTask(
            task_id="task_1",
            agent_id="agent_1",
            task_type="diagnose",
            description="Diagnose device issue",
        )
        
        assert task.task_id == "task_1"
        assert task.agent_id == "agent_1"
        assert task.task_type == "diagnose"
        assert task.status == TaskStatus.PENDING
    
    def test_task_can_retry(self):
        """Test AgentTask can_retry method."""
        task = AgentTask(
            task_id="task_1",
            agent_id="agent_1",
            task_type="test",
            max_retries=3,
        )
        
        assert task.can_retry()  # 0 retries
        
        task.retry_count = 2
        assert task.can_retry()  # 2 retries < 3
        
        task.retry_count = 3
        assert not task.can_retry()  # 3 retries == 3


class TestAgentMessage:
    """Tests for AgentMessage domain object."""
    
    def test_message_creation(self):
        """Test AgentMessage creation."""
        msg = AgentMessage(
            message_id="msg_1",
            sender="agent_a",
            receiver="agent_b",
            type=MessageType.REQUEST,
            action="diagnose",
            payload={"device_id": "dev_123"},
        )
        
        assert msg.message_id == "msg_1"
        assert msg.sender == "agent_a"
        assert msg.receiver == "agent_b"
        assert msg.type == MessageType.REQUEST
        assert msg.is_request
        assert not msg.is_response
    
    def test_message_is_broadcast(self):
        """Test AgentMessage is_broadcast property."""
        msg = AgentMessage(
            message_id="msg_1",
            sender="agent_a",
            receiver="*",
            type=MessageType.EVENT,
            action="system_event",
        )
        
        assert msg.is_broadcast
    
    def test_message_create_reply(self):
        """Test AgentMessage create_reply method."""
        original = AgentMessage(
            message_id="msg_1",
            sender="agent_a",
            receiver="agent_b",
            type=MessageType.REQUEST,
            action="diagnose",
        )
        
        reply = original.create_reply({"result": "success"})
        
        assert reply.sender == "agent_b"
        assert reply.receiver == "agent_a"
        assert reply.type == MessageType.RESPONSE
        assert reply.parent_id == "msg_1"


# =============================================================================
# EVENT BUS TESTS
# =============================================================================

class TestEventBus:
    """Tests for EventBus."""
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    @pytest.mark.asyncio
    async def test_publish_event(self, event_bus):
        """Test publishing an event."""
        from core.PHASE_5.foundation import AgentEvent
        
        event = AgentEvent(
            event_id="evt_1",
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id="agent_1",
            message="Agent registered",
        )
        
        result = await event_bus.publish(event)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_event_history(self, event_bus):
        """Test event history retrieval."""
        from core.PHASE_5.foundation import AgentEvent
        
        # Publish some events
        for i in range(5):
            event = AgentEvent(
                event_id=f"evt_{i}",
                event_type=AgentEventType.AGENT_REGISTERED,
                agent_id=f"agent_{i}",
            )
            await event_bus.publish(event)
        
        history = event_bus.get_history(limit=3)
        
        assert len(history) == 3
        assert history[-1].event_id == "evt_4"
    
    def test_event_factory(self):
        """Test EventFactory helpers."""
        evt = EventFactory.agent_registered("agent_1")
        
        assert evt.agent_id == "agent_1"
        assert evt.event_type == AgentEventType.AGENT_REGISTERED


# =============================================================================
# MESSAGE BROKER TESTS
# =============================================================================

class TestMessageBroker:
    """Tests for MessageBroker."""
    
    @pytest.fixture
    def broker(self):
        return MessageBroker()
    
    @pytest.mark.asyncio
    async def test_send_message(self, broker):
        """Test sending a message."""
        msg = AgentMessage(
            message_id="msg_1",
            sender="agent_a",
            receiver="agent_b",
            type=MessageType.REQUEST,
            action="test",
        )
        
        result = await broker.send(msg)
        
        assert result is True
        assert await broker.get_queue_size("agent_b") == 1
    
    @pytest.mark.asyncio
    async def test_receive_message(self, broker):
        """Test receiving a message."""
        msg = AgentMessage(
            message_id="msg_1",
            sender="agent_a",
            receiver="agent_b",
            type=MessageType.REQUEST,
            action="test",
        )
        
        await broker.send(msg)
        received = await broker.receive("agent_b")
        
        assert received is not None
        assert received.message_id == "msg_1"
        assert await broker.get_queue_size("agent_b") == 0
    
    @pytest.mark.asyncio
    async def test_subscribe_to_topic(self, broker):
        """Test subscribing to a topic."""
        result = await broker.subscribe("agent_1", ["topic_a", "topic_b"])
        
        assert result is True
        
        topics = broker.get_subscribed_topics("agent_1")
        assert "topic_a" in topics
        assert "topic_b" in topics
    
    @pytest.mark.asyncio
    async def test_publish_to_topic(self, broker):
        """Test publishing to a topic."""
        await broker.subscribe("agent_1", ["events"])
        
        msg = AgentMessage(
            message_id="msg_1",
            sender="orchestrator",
            receiver="*",
            type=MessageType.NOTIFICATION,
            action="event",
        )
        
        await broker.publish("events", msg)
        
        received = await broker.receive("agent_1")
        assert received is not None
        assert received.topic == "events"


# =============================================================================
# LIFECYCLE TESTS
# =============================================================================

class TestAgentLifecycleManager:
    """Tests for AgentLifecycleManager."""
    
    @pytest.fixture
    def lifecycle_manager(self):
        return AgentLifecycleManager()
    
    @pytest.mark.asyncio
    async def test_register_agent(self, lifecycle_manager):
        """Test registering an agent."""
        agent = Agent(
            agent_id="agent_1",
            agent_type=AgentType.BIOMEDICAL,
            name="Test Agent",
        )
        
        result = await lifecycle_manager.register_agent(agent)
        
        assert result is True
        assert await lifecycle_manager.get_agent("agent_1") is not None
    
    @pytest.mark.asyncio
    async def test_state_transitions(self, lifecycle_manager):
        """Test valid state transitions."""
        agent = Agent(
            agent_id="agent_1",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
        )
        await lifecycle_manager.register_agent(agent)
        
        # Initial -> IDLE
        await lifecycle_manager.initialize_agent("agent_1")
        assert agent.state == AgentState.IDLE
        
        # IDLE -> RUNNING
        await lifecycle_manager.start_task("agent_1", "task_1")
        assert agent.state == AgentState.RUNNING
        
        # RUNNING -> COMPLETED
        await lifecycle_manager.complete_task("agent_1", "task_1")
        assert agent.state == AgentState.COMPLETED
    
    @pytest.mark.asyncio
    async def test_invalid_transition(self, lifecycle_manager):
        """Test invalid state transition."""
        agent = Agent(
            agent_id="agent_1",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
        )
        await lifecycle_manager.register_agent(agent)
        await lifecycle_manager.initialize_agent("agent_1")
        
        # Cannot go from IDLE directly to COMPLETED
        result = await lifecycle_manager.transition(
            "agent_1",
            AgentState.COMPLETED,
        )
        
        assert result is False


class TestStateValidator:
    """Tests for StateValidator."""
    
    def test_valid_transition(self):
        """Test valid transition check."""
        assert StateValidator.can_transition(
            AgentState.IDLE,
            AgentState.RUNNING,
        ) is True
    
    def test_invalid_transition(self):
        """Test invalid transition check."""
        assert StateValidator.can_transition(
            AgentState.IDLE,
            AgentState.COMPLETED,
        ) is False
    
    def test_get_valid_transitions(self):
        """Test getting valid transitions."""
        transitions = StateValidator.get_valid_transitions(AgentState.IDLE)
        
        assert AgentState.RUNNING in transitions
        assert AgentState.STOPPED in transitions
    
    def test_terminal_state(self):
        """Test terminal state check."""
        assert StateValidator.is_terminal_state(AgentState.STOPPED) is True
        assert StateValidator.is_terminal_state(AgentState.IDLE) is False


# =============================================================================
# REGISTRY TESTS
# =============================================================================

class TestAgentRegistry:
    """Tests for AgentRegistry."""
    
    @pytest.fixture
    def registry(self):
        return AgentRegistry()
    
    @pytest.mark.asyncio
    async def test_register_agent(self, registry):
        """Test registering an agent."""
        agent = Agent(
            agent_id="agent_1",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
        )
        
        result = await registry.register(agent)
        
        assert result is True
        assert await registry.exists("agent_1")
    
    @pytest.mark.asyncio
    async def test_get_by_type(self, registry):
        """Test getting agents by type."""
        agents = [
            Agent(agent_id=f"a{i}", agent_type=AgentType.BIOMEDICAL, name=f"Agent {i}")
            for i in range(3)
        ]
        
        for agent in agents:
            await registry.register(agent)
        
        biomedical = await registry.get_by_type(AgentType.BIOMEDICAL)
        
        assert len(biomedical) == 3
    
    @pytest.mark.asyncio
    async def test_get_by_capability(self, registry):
        """Test getting agents by capability."""
        agent = Agent(
            agent_id="agent_1",
            agent_type=AgentType.BIOMEDICAL,
            name="Test",
            capabilities=[
                AgentCapabilityVO(AgentCapability.DIAGNOSE),
            ],
        )
        await registry.register(agent)
        
        capable = await registry.get_by_capability(AgentCapability.DIAGNOSE)
        
        assert len(capable) == 1
        assert capable[0].agent_id == "agent_1"


# =============================================================================
# CONTEXT TESTS
# =============================================================================

class TestContextManager:
    """Tests for ContextManager."""
    
    @pytest.fixture
    def context_manager(self):
        return ContextManager()
    
    @pytest.mark.asyncio
    async def test_create_context(self, context_manager):
        """Test creating a context."""
        context = await context_manager.create_context("session_1")
        
        assert context is not None
        assert context.session_id == "session_1"
    
    @pytest.mark.asyncio
    async def test_update_context(self, context_manager):
        """Test updating context data."""
        context = await context_manager.create_context("session_1")
        
        result = await context_manager.update_context(
            context.context_id,
            {"key": "value"},
        )
        
        assert result is True
        assert context.get_value("key") == "value"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
