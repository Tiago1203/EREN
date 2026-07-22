"""Unit tests for EREN Cognitive Workflow Platform."""

import pytest

from core.PHASE_1.workflows.workflows.types import (
    WorkflowType,
    WorkflowStatus,
    NodeType,
    NodeStatus,
    WorkflowNode,
    WorkflowEdge,
    WorkflowDefinition,
    WorkflowExecution,
    NodeExecution,
    Checkpoint,
    WorkflowMetrics,
)
from core.PHASE_1.workflows.workflows.graph import ExecutionGraph, get_execution_graph, clear_graph_cache
from core.PHASE_1.workflows.workflows.state_store import StateStore, get_state_store, reset_state_store
from core.PHASE_1.workflows.workflows.state import StateManager, get_state_manager, reset_state_manager
from core.PHASE_1.workflows.workflows.checkpoint import CheckpointManager, get_checkpoint_manager
from core.PHASE_1.workflows.workflows.recovery import RecoveryManager, get_recovery_manager
from core.PHASE_1.workflows.workflows.planner import WorkflowPlanner
from core.PHASE_1.workflows.workflows.executor import WorkflowExecutor, TaskExecutor
from core.PHASE_1.workflows.workflows.scheduler import WorkflowScheduler
from core.PHASE_1.workflows.workflows.engine import WorkflowPlatform, WorkflowEngine, get_workflow_platform


class TestWorkflowTypes:
    """Tests for workflow types."""

    def test_node_creation(self):
        """Test creating a node."""
        node = WorkflowNode.create(
            name="Test Node",
            node_type=NodeType.TASK,
            config={"key": "value"},
        )
        assert node.name == "Test Node"
        assert node.node_type == NodeType.TASK
        assert node.config["key"] == "value"

    def test_edge_creation(self):
        """Test creating an edge."""
        edge = WorkflowEdge.create(
            source_id="node1",
            target_id="node2",
            condition="condition1",
        )
        assert edge.source_id == "node1"
        assert edge.target_id == "node2"
        assert edge.condition == "condition1"

    def test_workflow_definition(self):
        """Test workflow definition."""
        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test Workflow",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )
        assert definition.name == "Test Workflow"
        assert definition.workflow_type == WorkflowType.LINEAR


class TestExecutionGraph:
    """Tests for execution graph."""

    def setup_method(self):
        """Setup for each test."""
        clear_graph_cache()

    def test_create_graph(self):
        """Test creating execution graph."""
        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )

        node1 = WorkflowNode.create("Node1", NodeType.TASK)
        node2 = WorkflowNode.create("Node2", NodeType.TASK)
        definition.nodes = [node1, node2]
        definition.edges = [
            WorkflowEdge.create(node1.node_id, node2.node_id)
        ]
        definition.entry_node_id = node1.node_id

        graph = ExecutionGraph(definition)
        assert graph.get_node(node1.node_id) == node1
        assert graph.get_node(node2.node_id) == node2

    def test_get_outgoing(self):
        """Test getting outgoing edges."""
        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )

        node1 = WorkflowNode.create("Node1", NodeType.TASK)
        node2 = WorkflowNode.create("Node2", NodeType.TASK)
        definition.nodes = [node1, node2]
        definition.edges = [
            WorkflowEdge.create(node1.node_id, node2.node_id)
        ]
        definition.entry_node_id = node1.node_id

        graph = ExecutionGraph(definition)
        outgoing = graph.get_outgoing(node1.node_id)
        assert node2.node_id in outgoing

    def test_get_entry_nodes(self):
        """Test getting entry nodes."""
        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )

        node1 = WorkflowNode.create("Node1", NodeType.TASK)
        definition.nodes = [node1]
        definition.entry_node_id = node1.node_id

        graph = ExecutionGraph(definition)
        entries = graph.get_entry_nodes()
        assert node1.node_id in entries


class TestStateManager:
    """Tests for state manager."""

    def setup_method(self):
        """Setup for each test."""
        reset_state_manager()

    def test_create_execution(self):
        """Test creating execution."""
        manager = get_state_manager()
        execution = manager.create_execution(
            execution_id="exec1",
            workflow_id="wf1",
            workflow_name="Test",
            input_data={"key": "value"},
        )
        assert execution.execution_id == "exec1"
        assert execution.input_data["key"] == "value"

    def test_get_execution(self):
        """Test getting execution."""
        manager = get_state_manager()
        manager.create_execution("exec1", "wf1", "Test")
        execution = manager.get_execution("exec1")
        assert execution is not None
        assert execution.execution_id == "exec1"

    def test_update_status(self):
        """Test updating status."""
        manager = get_state_manager()
        manager.create_execution("exec1", "wf1", "Test")
        manager.update_status("exec1", WorkflowStatus.RUNNING)
        execution = manager.get_execution("exec1")
        assert execution.status == WorkflowStatus.RUNNING

    def test_start_node(self):
        """Test starting node."""
        manager = get_state_manager()
        manager.create_execution("exec1", "wf1", "Test")

        node_exec = NodeExecution(
            node_id="node1",
            execution_id="exec1",
        )

        manager.start_node("exec1", "node1", node_exec)
        execution = manager.get_execution("exec1")
        assert "node1" in execution.current_node_ids


class TestCheckpointManager:
    """Tests for checkpoint manager."""

    def test_create_checkpoint(self):
        """Test creating checkpoint."""
        manager = get_checkpoint_manager()

        execution = WorkflowExecution(
            execution_id="exec1",
            workflow_id="wf1",
            workflow_name="Test",
        )

        checkpoint = manager.create_checkpoint(execution)
        assert checkpoint.execution_id == "exec1"

    def test_get_checkpoint(self):
        """Test getting checkpoint."""
        manager = get_checkpoint_manager()

        execution = WorkflowExecution(
            execution_id="exec1",
            workflow_id="wf1",
            workflow_name="Test",
        )

        created = manager.create_checkpoint(execution)
        retrieved = manager.get_checkpoint(created.checkpoint_id)
        assert retrieved is not None
        assert retrieved.checkpoint_id == created.checkpoint_id


class TestWorkflowPlanner:
    """Tests for workflow planner."""

    def test_create_execution_plan(self):
        """Test creating execution plan."""
        planner = WorkflowPlanner()

        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )

        node1 = WorkflowNode.create("Node1", NodeType.TASK)
        definition.nodes = [node1]
        definition.entry_node_id = node1.node_id

        planner.set_definition(definition)
        execution = planner.create_execution_plan("exec1")

        assert execution is not None
        assert execution.workflow_id == "wf1"

    def test_get_next_nodes(self):
        """Test getting next nodes."""
        planner = WorkflowPlanner()

        definition = WorkflowDefinition(
            workflow_id="wf1",
            name="Test",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )

        node1 = WorkflowNode.create("Node1", NodeType.TASK)
        definition.nodes = [node1]
        definition.entry_node_id = node1.node_id

        planner.set_definition(definition)
        execution = planner.create_execution_plan("exec1")

        next_nodes = planner.get_next_nodes(execution)
        assert node1.node_id in next_nodes


class TestTaskExecutor:
    """Tests for task executor."""

    def test_register_executor(self):
        """Test registering executor."""
        executor = TaskExecutor()

        def my_task(config, context):
            return {"result": "ok"}

        executor.register_executor("my_task", my_task)
        assert executor.has_executor("my_task")

    def test_execute(self):
        """Test executing task."""
        executor = TaskExecutor()

        def my_task(config, context):
            return {"result": config.get("value")}

        executor.register_executor("my_task", my_task)
        result = executor.execute_task("my_task", {"value": "test"}, {})
        assert result["result"] == "test"


class TestWorkflowScheduler:
    """Tests for workflow scheduler."""

    def test_schedule_task(self):
        """Test scheduling task."""
        scheduler = WorkflowScheduler()
        task = scheduler.schedule_task("wf1", "exec1", "node1")
        assert task.workflow_id == "wf1"
        assert task.node_id == "node1"

    def test_complete_task(self):
        """Test completing task."""
        scheduler = WorkflowScheduler()
        task = scheduler.schedule_task("wf1", "exec1", "node1")
        scheduler.complete_task(task.task_id)
        assert task.status == "completed"


class TestStateStore:
    """Tests for state store."""

    def setup_method(self):
        """Setup for each test."""
        reset_state_store()

    def test_create_execution(self):
        """Test creating execution."""
        store = get_state_store()
        execution = store.create_execution(
            execution_id="exec1",
            workflow_id="wf1",
            workflow_name="Test",
        )
        assert execution.execution_id == "exec1"

    def test_load_execution(self):
        """Test loading execution."""
        store = get_state_store()
        store.create_execution("exec1", "wf1", "Test")
        loaded = store.load_execution("exec1")
        assert loaded is not None
        assert loaded.execution_id == "exec1"


class TestRecoveryManager:
    """Tests for recovery manager."""

    def test_create_compensation(self):
        """Test creating compensation."""
        manager = RecoveryManager()
        record = manager.create_compensation("exec1", "node1", "rollback")
        assert record.action == "rollback"

    def test_execute_compensation(self):
        """Test executing compensation."""
        manager = RecoveryManager()
        manager.create_compensation("exec1", "node1", "rollback")
        success, errors = manager.execute_compensation("exec1")
        assert success
        assert len(errors) == 0


class TestWorkflowExecutor:
    """Tests for workflow executor."""

    def test_register_executor(self):
        """Test registering executor."""
        executor = WorkflowExecutor()
        executor.register_executor("task1", lambda config, context: {"result": "ok"})
        assert executor.has_executor("task1")

    def test_invoke_agent(self):
        """Test invoking agent."""
        executor = WorkflowExecutor()
        result = executor.invoke_agent("agent1", {"task": "test"}, {})
        assert result["type"] == "agent1"


class TestWorkflowScheduler:
    """Tests for workflow scheduler."""

    def test_calculate_order(self):
        """Test calculating order."""
        scheduler = WorkflowScheduler()
        order = scheduler.calculate_order(["n1", "n2", "n3"], {"n1": 3, "n2": 1, "n3": 2})
        assert order[0] == "n1"

    def test_resolve_dependencies(self):
        """Test resolving dependencies."""
        scheduler = WorkflowScheduler()
        node = WorkflowNode.create("n1", NodeType.TASK, depends_on=["n0"])
        assert scheduler.resolve_dependencies(node, ["n0"]) is True
        assert scheduler.resolve_dependencies(node, []) is False


class TestWorkflowPlatform:
    """Tests for workflow platform."""

    def test_create_definition(self):
        """Test creating workflow definition."""
        platform = WorkflowPlatform()
        workflow = platform.create_definition(
            name="Test Workflow",
            description="Test",
            workflow_type=WorkflowType.LINEAR,
        )
        assert workflow.name == "Test Workflow"
        assert workflow.workflow_type == WorkflowType.LINEAR

    def test_add_node(self):
        """Test adding node."""
        platform = WorkflowPlatform()
        workflow = platform.create_definition("Test", "Test")

        node = platform.add_node(
            workflow_id=workflow.workflow_id,
            name="Test Node",
            node_type=NodeType.TASK,
        )

        assert node is not None
        assert node.name == "Test Node"

    def test_add_edge(self):
        """Test adding edge."""
        platform = WorkflowPlatform()
        workflow = platform.create_definition("Test", "Test")

        node1 = platform.add_node(workflow.workflow_id, "Node1", NodeType.TASK)
        node2 = platform.add_node(workflow.workflow_id, "Node2", NodeType.TASK)

        edge = platform.add_edge(workflow.workflow_id, node1.node_id, node2.node_id)

        assert edge is not None
        assert edge.source_id == node1.node_id
        assert edge.target_id == node2.node_id

    def test_get_definition(self):
        """Test getting definition."""
        platform = WorkflowPlatform()
        workflow = platform.create_definition("Test", "Test")

        retrieved = platform.get_definition(workflow.workflow_id)
        assert retrieved is not None
        assert retrieved.workflow_id == workflow.workflow_id

    def test_get_metrics(self):
        """Test getting metrics."""
        platform = WorkflowPlatform()
        platform.create_definition("Test", "Test")

        metrics = platform.get_metrics()
        assert metrics.workflows_created >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
