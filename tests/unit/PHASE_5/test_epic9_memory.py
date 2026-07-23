"""
Tests for EPIC 9: Agent Memory Engine

Test suite for the Agent Memory Engine.
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

from core.PHASE_5.epic9_memory import (
    AgentMemory,
    AgentMemoryConfig,
)

from core.PHASE_5.epic9_memory.domain import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    ConversationContext,
    Message,
    AgentExperience,
    ExperienceOutcome,
)

from core.PHASE_5.epic9_memory.engines import (
    EpisodicMemory,
    SharedMemory,
    LongTermMemory,
    ConversationMemory,
    MemorySynchronizer,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def memory_config():
    """Create memory config."""
    return AgentMemoryConfig(
        enable_episodic=True,
        enable_shared=True,
        enable_long_term=True,
        enable_conversation=True,
        enable_sync=True,
    )


@pytest.fixture
def agent_memory(memory_config):
    """Create agent memory."""
    return AgentMemory(
        agent_id="memory_test_1",
        config=memory_config,
    )


# =============================================================================
# TEST AGENT MEMORY
# =============================================================================

class TestAgentMemory:
    """Tests for AgentMemory."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_memory, memory_config):
        """Test agent initializes correctly."""
        assert agent_memory.agent_id == "memory_test_1"
        assert agent_memory.agent_type == AgentType.MEMORY
        assert agent_memory.config == memory_config
        
        # Engines should be initialized
        assert agent_memory._episodic_memory is not None
        assert agent_memory._shared_memory is not None
        assert agent_memory._long_term_memory is not None
        assert agent_memory._conversation_memory is not None
        assert agent_memory._synchronizer is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, agent_memory):
        """Test agent initialization method."""
        await agent_memory.initialize()
        assert agent_memory.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_store_action(self, agent_memory):
        """Test store action."""
        task = AgentTask(
            task_id="task_1",
            agent_id="memory_test_1",
            task_type="memory",
            input_data={
                "action": "store",
                "agent_id": "agent_1",
                "content": "Test memory",
                "type": "episodic",
                "importance": "medium",
            },
        )
        
        result = await agent_memory.execute(task)
        
        assert result is not None
        assert result.success is True
        assert "record_id" in result.output
    
    @pytest.mark.asyncio
    async def test_retrieve_action(self, agent_memory):
        """Test retrieve action."""
        # First store
        await agent_memory.execute(AgentTask(
            task_id="task_store",
            agent_id="memory_test_1",
            task_type="memory",
            input_data={
                "action": "store",
                "agent_id": "agent_1",
                "content": "Test memory",
            },
        ))
        
        # Then retrieve
        task = AgentTask(
            task_id="task_2",
            agent_id="memory_test_1",
            task_type="memory",
            input_data={
                "action": "retrieve",
                "agent_id": "agent_1",
            },
        )
        
        result = await agent_memory.execute(task)
        
        assert result is not None
        assert result.success is True
        assert "records_count" in result.output
    
    @pytest.mark.asyncio
    async def test_experience_action(self, agent_memory):
        """Test experience action."""
        task = AgentTask(
            task_id="task_3",
            agent_id="memory_test_1",
            task_type="memory",
            input_data={
                "action": "experience",
                "operation": "store",
                "agent_id": "agent_1",
                "description": "Fixed device X",
                "outcome": "success",
            },
        )
        
        result = await agent_memory.execute(task)
        
        assert result is not None
        assert result.success is True
        assert "experience_id" in result.output
    
    @pytest.mark.asyncio
    async def test_metrics(self, agent_memory):
        """Test agent metrics."""
        metrics = agent_memory.get_metrics()
        
        assert "records_stored" in metrics
        assert "experiences_stored" in metrics
        assert "engines_enabled" in metrics


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestMemoryRecord:
    """Tests for MemoryRecord."""
    
    def test_record_creation(self):
        """Test record creation."""
        record = MemoryRecord(
            record_id="rec_1",
            agent_id="agent_1",
            memory_type=MemoryType.EPISODIC,
            content="Test content",
        )
        
        assert record.record_id == "rec_1"
        assert record.agent_id == "agent_1"
        assert record.memory_type == MemoryType.EPISODIC
    
    def test_record_access(self):
        """Test record access."""
        record = MemoryRecord(
            agent_id="agent_1",
            content="Test",
        )
        
        initial_count = record.access_count
        record.access()
        assert record.access_count == initial_count + 1
    
    def test_record_expiry(self):
        """Test record expiry."""
        record = MemoryRecord(
            agent_id="agent_1",
            content="Test",
        )
        
        assert not record.is_expired()


class TestConversationContext:
    """Tests for ConversationContext."""
    
    def test_context_creation(self):
        """Test context creation."""
        context = ConversationContext(
            context_id="ctx_1",
            session_id="session_1",
            participants=["agent_1", "agent_2"],
        )
        
        assert context.context_id == "ctx_1"
        assert len(context.participants) == 2
    
    def test_add_message(self):
        """Test adding messages."""
        context = ConversationContext(
            session_id="session_1",
            participants=["agent_1"],
        )
        
        message = Message(sender_id="agent_1", content="Hello")
        context.add_message(message)
        
        assert len(context.messages) == 1


class TestAgentExperience:
    """Tests for AgentExperience."""
    
    def test_experience_creation(self):
        """Test experience creation."""
        experience = AgentExperience(
            experience_id="exp_1",
            agent_id="agent_1",
            description="Fixed device",
            outcome=ExperienceOutcome.SUCCESS,
        )
        
        assert experience.experience_id == "exp_1"
        assert experience.outcome == ExperienceOutcome.SUCCESS
    
    def test_add_lesson(self):
        """Test adding lessons."""
        experience = AgentExperience(
            agent_id="agent_1",
            description="Test",
        )
        
        experience.add_lesson("Always check power first")
        assert len(experience.lessons_learned) == 1
    
    def test_is_applicable(self):
        """Test applicability check."""
        experience = AgentExperience(
            agent_id="agent_1",
            description="Test",
            applicable_scenarios=["device_repair", "calibration"],
        )
        
        assert experience.is_applicable("device_repair") is True
        assert experience.is_applicable("unknown") is False


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestEpisodicMemory:
    """Tests for EpisodicMemory."""
    
    @pytest.mark.asyncio
    async def test_store(self):
        """Test storing memory."""
        memory = EpisodicMemory()
        
        record = await memory.store(
            agent_id="agent_1",
            content="Test event",
            memory_type=MemoryType.EPISODIC,
        )
        
        assert record.record_id != ""
    
    @pytest.mark.asyncio
    async def test_retrieve(self):
        """Test retrieving memory."""
        memory = EpisodicMemory()
        
        await memory.store(agent_id="agent_1", content="Event 1")
        await memory.store(agent_id="agent_1", content="Event 2")
        
        result = await memory.retrieve(agent_id="agent_1")
        
        assert result.records_count >= 2


class TestSharedMemory:
    """Tests for SharedMemory."""
    
    @pytest.mark.asyncio
    async def test_share(self):
        """Test sharing memory."""
        memory = SharedMemory()
        
        record = MemoryRecord(
            agent_id="agent_1",
            content="Shared memory",
        )
        
        result = await memory.share(agent_id="agent_1", record=record)
        
        assert result.shared_count == 1
    
    @pytest.mark.asyncio
    async def test_get_shared(self):
        """Test getting shared memories."""
        memory = SharedMemory()
        
        record = MemoryRecord(
            agent_id="agent_1",
            content="Shared",
            memory_type=MemoryType.SHARED,
        )
        
        await memory.share(agent_id="agent_1", record=record)
        
        shared = await memory.get_shared(memory_type=MemoryType.SHARED)
        assert len(shared) == 1


class TestLongTermMemory:
    """Tests for LongTermMemory."""
    
    @pytest.mark.asyncio
    async def test_store_experience(self):
        """Test storing experience."""
        memory = LongTermMemory()
        
        experience = await memory.store_experience(
            agent_id="agent_1",
            description="Fixed device",
            outcome=ExperienceOutcome.SUCCESS,
        )
        
        assert experience.experience_id != ""
    
    @pytest.mark.asyncio
    async def test_retrieve_experiences(self):
        """Test retrieving experiences."""
        memory = LongTermMemory()
        
        await memory.store_experience(
            agent_id="agent_1",
            description="Exp 1",
            outcome=ExperienceOutcome.SUCCESS,
        )
        
        result = await memory.retrieve_experiences(agent_id="agent_1")
        assert result.experiences_count >= 1


class TestConversationMemory:
    """Tests for ConversationMemory."""
    
    @pytest.mark.asyncio
    async def test_create_context(self):
        """Test creating context."""
        memory = ConversationMemory()
        
        context = await memory.create_context(
            session_id="session_1",
            participants=["agent_1", "agent_2"],
        )
        
        assert context.context_id != ""
    
    @pytest.mark.asyncio
    async def test_add_message(self):
        """Test adding message."""
        memory = ConversationMemory()
        
        context = await memory.create_context(
            session_id="session_1",
            participants=["agent_1"],
        )
        
        message = await memory.add_message(
            context_id=context.context_id,
            sender_id="agent_1",
            content="Hello!",
        )
        
        assert message is not None


class TestMemorySynchronizer:
    """Tests for MemorySynchronizer."""
    
    @pytest.mark.asyncio
    async def test_sync_agent(self):
        """Test syncing agent."""
        sync = MemorySynchronizer()
        shared = SharedMemory()
        episodic = EpisodicMemory()
        
        # Store some memories
        await episodic.store(agent_id="agent_1", content="Important event")
        
        result = await sync.sync_agent(
            agent_id="agent_1",
            shared_memory=shared,
            episodic_memory=episodic,
        )
        
        assert result.synced_count >= 0


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_memory_type_values(self):
        """Test MemoryType enum values."""
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SHARED.value == "shared"
    
    def test_memory_importance_values(self):
        """Test MemoryImportance enum values."""
        assert MemoryImportance.CRITICAL.value == "critical"
        assert MemoryImportance.HIGH.value == "high"
    
    def test_experience_outcome_values(self):
        """Test ExperienceOutcome enum values."""
        assert ExperienceOutcome.SUCCESS.value == "success"
        assert ExperienceOutcome.FAILURE.value == "failure"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
