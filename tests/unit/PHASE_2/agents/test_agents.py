"""Tests for Multi-Agent Collaboration (PR-053)."""

import pytest
from core.PHASE_2.agents.cognitive_agent_integration import (
    Agent,
    AgentRegistry,
    AgentType,
    AgentEvent,
    AgentEventType,
    TaskManager,
)


class TestAgentRegistry:
    def test_register(self):
        registry = AgentRegistry()
        agent = Agent(id="agent1", name="Test Agent")
        registry.register(agent)
        assert "agent1" in [a.id for a in registry.list_all()]

    def test_unregister(self):
        registry = AgentRegistry()
        agent = Agent(id="agent1", name="Test Agent")
        registry.register(agent)
        assert registry.unregister("agent1") is True
        assert registry.get("agent1") is None

    def test_find_by_type(self):
        registry = AgentRegistry()
        registry.register(Agent(id="a1", name="Orchestrator", agent_type=AgentType.ORCHESTRATOR))
        registry.register(Agent(id="a2", name="Specialist", agent_type=AgentType.SPECIALIST))
        results = registry.find_by_type(AgentType.ORCHESTRATOR)
        assert len(results) == 1
        assert results[0].id == "a1"

    def test_find_by_capability(self):
        registry = AgentRegistry()
        registry.register(Agent(id="a1", name="Med", capabilities=("diagnosis",)))
        registry.register(Agent(id="a2", name="Eng", capabilities=("engineering",)))
        results = registry.find_by_capability("diagnosis")
        assert len(results) == 1

    def test_events(self):
        registry = AgentRegistry()
        events = []
        registry.subscribe(lambda e: events.append(e))
        registry.register(Agent(id="a1", name="Test"))
        assert len(events) == 1
        assert events[0].event_type == AgentEventType.AGENT_REGISTERED


class TestTaskManager:
    def test_create_task(self):
        registry = AgentRegistry()
        registry.register(Agent(id="agent1", name="Test Agent"))
        manager = TaskManager(registry)
        task = manager.create_task("Test task", "agent1")
        assert task.description == "Test task"
        assert task.assigned_to == "agent1"

    def test_execute_task(self):
        registry = AgentRegistry()
        registry.register(Agent(
            id="agent1",
            name="Test Agent",
            handler=lambda ctx: ctx.get("value", 0) * 2,
        ))
        manager = TaskManager(registry)
        task = manager.create_task("Double", "agent1")
        result = manager.execute_task(task.id, {"value": 5})
        assert result["success"] is True
        assert result["result"] == 10

    def test_execute_task_no_handler(self):
        registry = AgentRegistry()
        registry.register(Agent(id="agent1", name="No Handler"))
        manager = TaskManager(registry)
        task = manager.create_task("Test", "agent1")
        result = manager.execute_task(task.id)
        assert result["success"] is False
        assert "no handler" in result["error"].lower()
