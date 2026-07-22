"""Tests for the orchestration contracts."""

from __future__ import annotations

from core.PHASE_2.orchestration import (
    CycleState,
    CyclePhase,
    EngineState,
    EngineResult,
    ResultFactory,
    ResultStatus,
    ResultType,
    PipelineDefinition,
    PipelineStage,
    PipelineExecutor,
    PipelineBuilder,
    get_default_pipeline,
    EngineStateManager,
    get_state_manager,
    OrchestrationContext,
    ContextFactory,
    ContextKey,
    CognitiveCycle,
    CycleMetadata,
    ExecutionGraph,
    ExecutionGraphFactory,
    NodeType,
    EdgeType,
    GraphNode,
    GraphEdge,
)


class TestCycleStates:
    """Tests for cycle states."""

    def test_cycle_states(self) -> None:
        """All cycle states should be defined."""
        assert CycleState.CREATED
        assert CycleState.READY
        assert CycleState.PLANNING
        assert CycleState.KNOWLEDGE
        assert CycleState.MEMORY
        assert CycleState.REASONING
        assert CycleState.DECISION
        assert CycleState.ACTION
        assert CycleState.COMPLETED
        assert CycleState.FAILED
        assert CycleState.CANCELLED

    def test_cycle_phases(self) -> None:
        """All cycle phases should be defined."""
        assert CyclePhase.INTAKE
        assert CyclePhase.PLANNING
        assert CyclePhase.KNOWLEDGE
        assert CyclePhase.MEMORY
        assert CyclePhase.REASONING
        assert CyclePhase.DECISION
        assert CyclePhase.ACTION
        assert CyclePhase.OUTPUT


class TestEngineStates:
    """Tests for engine states."""

    def test_engine_states(self) -> None:
        """All engine states should be defined."""
        assert EngineState.INITIALIZED
        assert EngineState.REGISTERED
        assert EngineState.IDLE
        assert EngineState.PREPARING
        assert EngineState.EXECUTING
        assert EngineState.CLEANING_UP
        assert EngineState.COMPLETED
        assert EngineState.FAILED


class TestEngineResult:
    """Tests for engine result."""

    def test_result_factory_success(self) -> None:
        """Factory should create success result."""
        result = ResultFactory.success(
            result_id="r1",
            engine_id="e1",
            engine_type="reasoning",
            result_type=ResultType.HYPOTHESIS,
            data={"key": "value"},
        )

        assert result.status == ResultStatus.SUCCESS
        assert result.result_id == "r1"
        assert result.data["key"] == "value"

    def test_result_factory_failure(self) -> None:
        """Factory should create failure result."""
        result = ResultFactory.failure(
            result_id="r2",
            engine_id="e1",
            engine_type="reasoning",
            error="Test error",
        )

        assert result.status == ResultStatus.FAILED
        assert "Test error" in result.errors

    def test_result_factory_partial(self) -> None:
        """Factory should create partial result."""
        result = ResultFactory.partial(
            result_id="r3",
            engine_id="e1",
            engine_type="reasoning",
            result_type=ResultType.HYPOTHESIS,
            warnings=("Warning 1",),
        )

        assert result.status == ResultStatus.PARTIAL
        assert len(result.warnings) == 1


class TestPipeline:
    """Tests for engine pipeline."""

    def test_default_pipeline(self) -> None:
        """Default pipeline should have stages."""
        pipeline = get_default_pipeline()
        stages = pipeline.get_stages_in_order()

        assert len(stages) == 8  # intake, planning, knowledge, memory, reasoning, decision, action, output

    def test_pipeline_stage_order(self) -> None:
        """Stages should be in order."""
        pipeline = get_default_pipeline()
        stages = pipeline.get_stages_in_order()

        assert stages[0].phase == "intake"
        assert stages[-1].phase == "output"

    def test_pipeline_dependencies(self) -> None:
        """Stages should have correct dependencies."""
        pipeline = get_default_pipeline()

        reasoning = pipeline.get_stage("stage_reasoning")
        assert "stage_knowledge" in reasoning.dependencies
        assert "stage_memory" in reasoning.dependencies

    def test_pipeline_builder(self) -> None:
        """Pipeline builder should create pipeline."""
        builder = PipelineBuilder()
        builder.add_stage(
            stage_id="s1",
            phase="intake",
            engine_type="orchestrator",
            engine_id="main",
        )
        builder.add_stage(
            stage_id="s2",
            phase="planning",
            engine_type="planner",
            engine_id="main",
            dependencies=["s1"],
        )

        pipeline = builder.build()
        assert len(pipeline.get_stages_in_order()) == 2

    def test_pipeline_executor(self) -> None:
        """Pipeline executor should track execution."""
        pipeline = get_default_pipeline()
        executor = PipelineExecutor(pipeline)

        # First stage should be executable
        next_stages = executor.get_next_stages()
        assert len(next_stages) > 0
        assert next_stages[0].stage_id == "stage_intake"

        # Mark stage complete
        executor.mark_completed("stage_intake", None)

        # Intake complete, planning should be next
        next_stages = executor.get_next_stages()
        assert "stage_planning" in [s.stage_id for s in next_stages]


class TestEngineStateManager:
    """Tests for engine state manager."""

    def test_state_manager_initialization(self) -> None:
        """State manager should initialize engines."""
        manager = EngineStateManager()
        manager.initialize("test_engine")

        assert manager.get_state("test_engine") == EngineState.INITIALIZED

    def test_state_transitions(self) -> None:
        """State transitions should be valid."""
        manager = EngineStateManager()
        manager.initialize("test_engine")

        # Valid transition
        result = manager.transition("test_engine", EngineState.IDLE)
        assert result is True
        assert manager.get_state("test_engine") == EngineState.IDLE

    def test_invalid_transition(self) -> None:
        """Invalid transitions should be rejected."""
        manager = EngineStateManager()
        manager.initialize("test_engine")

        # Can't go directly from INITIALIZED to EXECUTING
        result = manager.transition("test_engine", EngineState.EXECUTING)
        assert result is False

    def test_global_state_manager(self) -> None:
        """Global state manager should be available."""
        manager = get_state_manager()
        assert manager is not None


class TestOrchestrationContext:
    """Tests for orchestration context."""

    def test_context_creation(self) -> None:
        """Context should be created with IDs."""
        ctx = OrchestrationContext(user_input="Test input")

        assert ctx.request_id.startswith("req_")
        assert ctx.cycle_id.startswith("cycle_")

    def test_context_methods(self) -> None:
        """Context get/set methods should work."""
        ctx = OrchestrationContext()
        ctx.set("custom_key", "custom_value")

        assert ctx.get("custom_key") == "custom_value"
        assert ctx.get("missing", "default") == "default"

    def test_context_add_hypothesis(self) -> None:
        """Adding hypotheses should work."""
        ctx = OrchestrationContext()
        ctx.add_hypothesis({"id": "h1", "description": "Test"})

        assert len(ctx.hypotheses) == 1

    def test_context_factory(self) -> None:
        """Context factory should create contexts."""
        ctx = ContextFactory.create_from_user_input(
            user_input="Test",
            user_id="user1",
            session_id="session1",
        )

        assert ctx.user_input == "Test"
        assert ctx.user_id == "user1"


class TestCognitiveCycle:
    """Tests for cognitive cycle."""

    def test_cycle_metadata(self) -> None:
        """Cycle metadata should be created."""
        metadata = CycleMetadata(cycle_id="cycle_1")

        assert metadata.cycle_id == "cycle_1"
        assert metadata.created_at != ""

    def test_cycle_transitions(self) -> None:
        """Cycle should transition states."""
        metadata = CycleMetadata(cycle_id="cycle_1")
        cycle = CognitiveCycle(metadata=metadata)

        cycle.transition_to(CycleState.READY, CyclePhase.PLANNING)

        assert cycle.current_state == CycleState.READY
        assert cycle.current_phase == CyclePhase.PLANNING


class TestExecutionGraph:
    """Tests for execution graph."""

    def test_graph_creation(self) -> None:
        """Graph should be created."""
        graph = ExecutionGraph()

        graph.add_node(GraphNode(
            node_id="n1",
            node_type=NodeType.ENGINE,
            label="Test Node",
        ))

        assert len(graph.get_all_nodes()) == 1

    def test_graph_edges(self) -> None:
        """Graph edges should be created."""
        graph = ExecutionGraph()

        graph.add_node(GraphNode(node_id="n1", node_type=NodeType.ENGINE, label="Node 1"))
        graph.add_node(GraphNode(node_id="n2", node_type=NodeType.ENGINE, label="Node 2"))

        graph.add_edge(GraphEdge(
            edge_id="e1",
            from_node="n1",
            to_node="n2",
            edge_type=EdgeType.EXECUTES,
        ))

        assert len(graph.get_all_edges()) == 1

    def test_default_graph(self) -> None:
        """Default cognitive graph should be created."""
        graph = ExecutionGraphFactory.create_cognitive_graph()

        assert len(graph.get_all_nodes()) > 0
        assert len(graph.get_all_edges()) > 0

    def test_topological_sort(self) -> None:
        """Topological sort should work."""
        graph = ExecutionGraphFactory.create_cognitive_graph()

        sorted_nodes = graph.topological_sort()
        assert sorted_nodes is not None  # No cycles


class TestContextKeys:
    """Tests for context keys."""

    def test_well_known_keys(self) -> None:
        """Well-known keys should be defined."""
        assert ContextKey.USER_ID == "user_id"
        assert ContextKey.SESSION_ID == "session_id"
        assert ContextKey.HYPOTHESES == "hypotheses"
        assert ContextKey.EVIDENCE == "evidence"
        assert ContextKey.DECISIONS == "decisions"
