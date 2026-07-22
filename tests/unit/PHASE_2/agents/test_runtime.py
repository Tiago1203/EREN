"""Unit tests for EREN Cognitive Agent Runtime."""

import pytest

from core.PHASE_2.agents.types import (
    AgentType,
    AgentStatus,
    AgentHealthStatus,
    TaskStatus,
    AgentCapability,
    AgentManifest,
    AgentHealth,
    AgentTask,
    AgentContext,
    RuntimeState,
)
from core.PHASE_2.agents.capabilities import CapabilityRegistry
from core.PHASE_2.agents.health import AgentHealthManager
from core.PHASE_2.agents.context import ContextManager
from core.PHASE_2.agents.registry import AgentRegistry
from core.PHASE_2.agents.communicator import AgentCommunicator
from core.PHASE_2.agents.lifecycle import LifecycleManager, LifecycleState
from core.PHASE_2.agents.scheduler import AgentScheduler
from core.PHASE_2.agents.events import AgentEventBus, AgentEventType, AgentEvent
from core.PHASE_2.agents.metrics import AgentMetricsCollector
from core.PHASE_2.agents.runtime import CognitiveAgentRuntime


class TestAgentTypes:
    """Tests for agent types."""

    def test_agent_capability(self):
        """Test agent capability."""
        cap = AgentCapability(
            name="test.capability",
            description="Test capability",
        )
        assert cap.name == "test.capability"

    def test_agent_manifest(self):
        """Test agent manifest."""
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test Agent",
            agent_type=AgentType.ENGINEERING,
            description="Test agent",
        )
        assert manifest.agent_id == "agent-1"
        assert manifest.has_capability("test") is False

    def test_agent_manifest_capabilities(self):
        """Test manifest with capabilities."""
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test Agent",
            agent_type=AgentType.MEDICAL,
            description="Test agent",
            capabilities=[
                AgentCapability(name="medical.diagnose", description="Diagnosis"),
            ],
        )
        assert manifest.has_capability("medical.diagnose")
        assert manifest.get_capability("medical.diagnose") is not None

    def test_agent_task(self):
        """Test agent task."""
        task = AgentTask(
            task_id="task-1",
            agent_id="agent-1",
            capability="test",
            description="Test task",
        )
        assert task.task_id == "task-1"
        assert task.status == TaskStatus.PENDING
        assert task.is_blocked is False


class TestCapabilityRegistry:
    """Tests for capability registry."""

    def test_registry(self):
        """Test capability registry."""
        registry = CapabilityRegistry()
        cap = registry.get_capability("medical.diagnose")
        assert cap is not None
        assert cap.name == "medical.diagnose"

    def test_register_capability(self):
        """Test registering capability."""
        registry = CapabilityRegistry()
        cap = AgentCapability(
            name="custom.capability",
            description="Custom",
        )
        registry.register_capability(cap)
        assert registry.get_capability("custom.capability") is not None

    def test_find_agents(self):
        """Test finding agents with capability."""
        registry = CapabilityRegistry()
        registry.register_agent_capabilities("agent-1", ["test.cap"])
        agents = registry.find_agents_with_capability("test.cap")
        assert "agent-1" in agents


class TestAgentHealthManager:
    """Tests for health manager."""

    def test_register_agent(self):
        """Test registering agent."""
        manager = AgentHealthManager()
        health = manager.register_agent("agent-1")
        assert health.agent_id == "agent-1"
        assert health.status == AgentHealthStatus.HEALTHY

    def test_heartbeat(self):
        """Test heartbeat."""
        manager = AgentHealthManager()
        manager.register_agent("agent-1")
        manager.update_heartbeat("agent-1")
        health = manager.get_health("agent-1")
        assert health is not None

    def test_record_success(self):
        """Test recording success."""
        manager = AgentHealthManager()
        manager.register_agent("agent-1")
        manager.record_task_success("agent-1", 100.0)
        health = manager.get_health("agent-1")
        assert health.success_count == 1
        assert health.status == AgentHealthStatus.HEALTHY

    def test_record_failure(self):
        """Test recording failure."""
        manager = AgentHealthManager()
        manager.register_agent("agent-1")
        manager.record_task_failure("agent-1", 100.0)
        health = manager.get_health("agent-1")
        assert health.failure_count == 1


class TestContextManager:
    """Tests for context manager."""

    def test_create_context(self):
        """Test creating context."""
        manager = ContextManager()
        context = manager.create_context("session-1")
        assert context.session_id == "session-1"

    def test_store_result(self):
        """Test storing result."""
        manager = ContextManager()
        manager.create_context("session-1")
        manager.store_result("session-1", "task-1", {"result": "ok"})
        result = manager.retrieve_result("session-1", "task-1")
        assert result == {"result": "ok"}

    def test_send_message(self):
        """Test sending message."""
        manager = ContextManager()
        msg = manager.send_message(
            "session-1",
            "sender",
            "receiver",
            "Hello",
        )
        assert msg.content == "Hello"


class TestAgentRegistry:
    """Tests for agent registry."""

    def test_register(self):
        """Test registering agent."""
        registry = AgentRegistry()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
        )
        registry.register(manifest)
        assert registry.get("agent-1") is not None

    def test_get_by_type(self):
        """Test getting agents by type."""
        registry = AgentRegistry()
        registry.register(AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.MEDICAL,
            description="Test",
        ))
        agents = registry.get_by_type(AgentType.MEDICAL)
        assert len(agents) == 1

    def test_find_best_agent(self):
        """Test finding best agent."""
        registry = AgentRegistry()
        registry.register(AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.MEDICAL,
            description="Test",
            capabilities=[AgentCapability(name="test", description="Test")],
        ))
        registry.set_status("agent-1", AgentStatus.IDLE)
        agent = registry.find_best_agent("test")
        assert agent is not None


class TestAgentCommunicator:
    """Tests for communicator."""

    def test_send(self):
        """Test sending message."""
        comm = AgentCommunicator()
        msg = comm.send("sender", "receiver", "Hello")
        assert msg.content == "Hello"

    def test_receive(self):
        """Test receiving message."""
        comm = AgentCommunicator()
        comm.send("sender", "receiver", "Hello")
        msg = comm.receive("receiver")
        assert msg.content == "Hello"

    def test_reply(self):
        """Test sending reply."""
        comm = AgentCommunicator()
        original = comm.send("sender", "receiver", "Question?")
        reply = comm.send_reply(original, "Answer")
        assert reply.content == "Answer"


class TestLifecycleManager:
    """Tests for lifecycle manager."""

    def test_initialize(self):
        """Test initializing agent."""
        manager = LifecycleManager()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
        )
        state = manager.initialize("agent-1", manifest)
        assert state == LifecycleState.READY

    def test_start(self):
        """Test starting agent."""
        manager = LifecycleManager()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
        )
        manager.initialize("agent-1", manifest)
        manager.start("agent-1")
        assert manager.is_running("agent-1")

    def test_stop(self):
        """Test stopping agent."""
        manager = LifecycleManager()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
        )
        manager.initialize("agent-1", manifest)
        manager.start("agent-1")
        manager.stop("agent-1")
        state = manager.get_state("agent-1")
        assert state in [LifecycleState.STOPPING, LifecycleState.STOPPED]


class TestAgentScheduler:
    """Tests for scheduler."""

    def test_submit_task(self):
        """Test submitting task."""
        scheduler = AgentScheduler()
        task = scheduler.submit_task(
            agent_id="agent-1",
            capability="test",
            description="Test task",
        )
        assert task.agent_id == "agent-1"
        assert task.status == TaskStatus.PENDING

    def test_start_task(self):
        """Test starting task."""
        scheduler = AgentScheduler()
        task = scheduler.submit_task("agent-1", "test", "Test")
        started = scheduler.start_task(task.task_id, "agent-1")
        assert started.status == TaskStatus.RUNNING

    def test_complete_task(self):
        """Test completing task."""
        scheduler = AgentScheduler()
        task = scheduler.submit_task("agent-1", "test", "Test")
        scheduler.start_task(task.task_id, "agent-1")
        completed = scheduler.complete_task(task.task_id, {"done": True})
        assert completed.status == TaskStatus.COMPLETED
        assert completed.output_data == {"done": True}


class TestAgentEventBus:
    """Tests for event bus."""

    def test_publish(self):
        """Test publishing event."""
        bus = AgentEventBus()
        event = AgentEvent(
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id="agent-1",
        )
        bus.publish(event)
        history = bus.get_history()
        assert len(history) == 1

    def test_subscribe(self):
        """Test subscribing to events."""
        bus = AgentEventBus()
        received = []

        def callback(event):
            received.append(event)

        bus.subscribe(AgentEventType.AGENT_REGISTERED, callback)
        bus.publish(AgentEvent(
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id="agent-1",
        ))

        assert len(received) == 1


class TestAgentMetricsCollector:
    """Tests for metrics collector."""

    def test_record_task_submitted(self):
        """Test recording task submission."""
        collector = AgentMetricsCollector()
        collector.record_task_submitted("task-1", "agent-1", "test")
        metrics = collector.get_metrics()
        assert metrics.tasks_submitted == 1

    def test_record_task_completed(self):
        """Test recording task completion."""
        collector = AgentMetricsCollector()
        collector.record_task_submitted("task-1", "agent-1", "test")
        collector.record_task_completed("task-1", "agent-1", 100.0)
        metrics = collector.get_metrics()
        assert metrics.tasks_completed == 1
        assert metrics.success_rate > 0


class TestCognitiveAgentRuntime:
    """Tests for cognitive agent runtime."""

    def test_start_stop(self):
        """Test starting and stopping runtime."""
        runtime = CognitiveAgentRuntime()
        runtime.start()
        assert runtime._is_running is True
        runtime.stop()
        assert runtime._is_running is False

    def test_register_agent(self):
        """Test registering agent."""
        runtime = CognitiveAgentRuntime()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test Agent",
            agent_type=AgentType.ENGINEERING,
            description="Test",
        )
        registered = runtime.register_agent(manifest)
        assert registered.agent_id == "agent-1"

    def test_submit_task(self):
        """Test submitting task."""
        runtime = CognitiveAgentRuntime()
        runtime.start()

        # Register agent first
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
            capabilities=[AgentCapability(name="test", description="Test")],
        )
        runtime.register_agent(manifest)

        # Submit task
        task = runtime.submit_task(
            capability="test",
            description="Test task",
        )

        assert task is not None
        assert task.description == "Test task"

    def test_task_lifecycle(self):
        """Test complete task lifecycle."""
        runtime = CognitiveAgentRuntime()
        runtime.start()

        # Register agent
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.ENGINEERING,
            description="Test",
            capabilities=[AgentCapability(name="test", description="Test")],
        )
        runtime.register_agent(manifest)

        # Submit task
        task = runtime.submit_task("test", "Test")

        # Start task
        started = runtime.start_task(task.task_id, "agent-1")
        assert started.status == TaskStatus.RUNNING

        # Complete task
        completed = runtime.complete_task(task.task_id, {"result": "ok"})
        assert completed.status == TaskStatus.COMPLETED

    def test_get_state(self):
        """Test getting runtime state."""
        runtime = CognitiveAgentRuntime()
        runtime.start()
        state = runtime.get_state()
        assert state.is_running is True

    def test_get_agent(self):
        """Test getting agent."""
        runtime = CognitiveAgentRuntime()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.MEDICAL,
            description="Test",
        )
        runtime.register_agent(manifest)
        agent = runtime.get_agent("agent-1")
        assert agent is not None
        assert agent.agent_id == "agent-1"

    def test_unregister_agent(self):
        """Test unregistering agent."""
        runtime = CognitiveAgentRuntime()
        manifest = AgentManifest(
            agent_id="agent-1",
            name="Test",
            agent_type=AgentType.MEDICAL,
            description="Test",
        )
        runtime.register_agent(manifest)
        result = runtime.unregister_agent("agent-1")
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
