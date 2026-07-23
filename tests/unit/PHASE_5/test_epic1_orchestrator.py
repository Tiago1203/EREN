"""
Tests for EPIC 1: Agent Orchestrator

Test suite for the orchestration system.
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.foundation import (
    AgentRegistry,
    AgentLifecycleManager,
    MessageBroker,
    EventBus,
    BaseAgent,
    AgentType,
    AgentState,
    AgentTask,
    AgentResult,
    AgentCapability,
)
from core.PHASE_5.foundation.domain import Agent

from core.PHASE_5.epic1_orchestrator import (
    OrchestratorEngine,
    OrchestratorConfig,
    TaskDispatcher,
    TaskScheduler,
    ResponseAggregator,
    AggregationConfig,
    ScheduleStrategy,
)

from core.PHASE_5.epic1_orchestrator.domain import (
    Workflow,
    WorkflowStep,
    WorkflowStatus,
    OrchestrationPlan,
    PlanStep,
    PlanStatus,
    AgentExecution,
    ExecutionResult,
    ExecutionStatus,
    OrchestrationStrategy,
    ExecutionMode,
    AggregationMethod,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_registry():
    """Create a mock agent registry."""
    return AgentRegistry()


@pytest.fixture
def mock_lifecycle():
    """Create a mock lifecycle manager."""
    return AgentLifecycleManager()


@pytest.fixture
def mock_broker():
    """Create a mock message broker."""
    return MessageBroker()


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus."""
    return EventBus()


@pytest.fixture
def mock_config():
    """Create orchestrator config."""
    return OrchestratorConfig(
        default_timeout_seconds=300,
        workflow_timeout_seconds=3600,
        max_retries=3,
        max_concurrent_executions=10,
        default_strategy=OrchestrationStrategy.SEQUENTIAL,
    )


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = MagicMock(spec=BaseAgent)
    agent.agent_id = "test_agent_1"
    agent.agent_type = AgentType.BIOMEDICAL
    agent.state = AgentState.IDLE
    agent.name = "Test Biomedical Agent"
    agent.description = "A test biomedical agent"
    agent.is_available = True
    return agent


@pytest.fixture
def orchestrator_engine(mock_config, mock_registry, mock_lifecycle, mock_broker, mock_event_bus):
    """Create orchestrator engine with mocks."""
    return OrchestratorEngine(
        config=mock_config,
        registry=mock_registry,
        lifecycle=mock_lifecycle,
        broker=mock_broker,
        event_bus=mock_event_bus,
    )


# =============================================================================
# TEST ORCHESTRATOR ENGINE
# =============================================================================

class TestOrchestratorEngine:
    """Tests for OrchestratorEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, orchestrator_engine, mock_config):
        """Test that engine initializes correctly."""
        assert orchestrator_engine.config == mock_config
        assert orchestrator_engine.registry is not None
        assert orchestrator_engine.broker is not None
        assert orchestrator_engine.dispatcher is not None
        assert orchestrator_engine.scheduler is not None
        assert orchestrator_engine.aggregator is not None
    
    @pytest.mark.asyncio
    async def test_intent_analysis(self, orchestrator_engine):
        """Test intent analysis from query."""
        # Diagnostic query
        intent = orchestrator_engine._analyze_intent(
            "Diagnose the issue with the infusion pump"
        )
        assert intent == "diagnostic"
        
        # Device query
        intent = orchestrator_engine._analyze_intent(
            "Analyze device XYZ-123 specifications"
        )
        assert intent == "device_analysis"
        
        # Maintenance query
        intent = orchestrator_engine._analyze_intent(
            "Schedule preventive maintenance for equipment"
        )
        assert intent == "maintenance"
        
        # Research query (uses "investigate" to avoid "incident")
        intent = orchestrator_engine._analyze_intent(
            "Investigate similar issues"
        )
        assert intent == "research"
        
        # General query
        intent = orchestrator_engine._analyze_intent(
            "What is the status of the system?"
        )
        assert intent == "general"
    
    @pytest.mark.asyncio
    async def test_step_determination(self, orchestrator_engine):
        """Test step determination based on intent."""
        # Diagnostic intent should produce multiple steps
        steps = orchestrator_engine._determine_steps("diagnostic", {})
        assert len(steps) >= 2
        assert any(s.agent_type == "biomedical" for s in steps)
        
        # Research intent should produce single step
        steps = orchestrator_engine._determine_steps("research", {})
        assert len(steps) == 1
        assert steps[0].agent_type == "research"
        
        # Planning intent should produce single step
        steps = orchestrator_engine._determine_steps("planning", {})
        assert len(steps) == 1
        assert steps[0].agent_type == "planning"
    
    @pytest.mark.asyncio
    async def test_plan_creation(self, orchestrator_engine):
        """Test orchestration plan creation."""
        plan = await orchestrator_engine.create_plan(
            request_id="test_request_1",
            query="Analyze device for issues",
            context={"device_id": "XYZ-123"},
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )
        
        assert plan is not None
        assert plan.request_id == "test_request_1"
        assert plan.original_query == "Analyze device for issues"
        assert len(plan.steps) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self, orchestrator_engine):
        """Test workflow creation from plan."""
        # Create plan first
        plan = await orchestrator_engine.create_plan(
            request_id="test_request_2",
            query="Full diagnostic analysis",
            context={},
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )
        
        # Create workflow
        workflow = await orchestrator_engine.create_workflow(plan)
        
        assert workflow is not None
        assert workflow.strategy == OrchestrationStrategy.SEQUENTIAL
        assert len(workflow.steps) == len(plan.steps)
        
        # For sequential, dependencies should be set
        for i, step in enumerate(workflow.steps):
            if i > 0:
                assert workflow.steps[i-1].step_id in step.depends_on
    
    @pytest.mark.asyncio
    async def test_workflow_status(self, orchestrator_engine):
        """Test workflow status tracking."""
        # Create plan and workflow
        plan = await orchestrator_engine.create_plan(
            request_id="test_request_3",
            query="Test workflow",
            context={},
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )
        
        workflow = await orchestrator_engine.create_workflow(plan)
        
        # Check status
        status = orchestrator_engine.get_workflow_status(workflow.workflow_id)
        assert status is not None
        assert status["workflow_id"] == workflow.workflow_id
        assert status["status"] == "pending"
        assert status["progress"] == 0.0
    
    @pytest.mark.asyncio
    async def test_stats(self, orchestrator_engine):
        """Test orchestrator statistics."""
        stats = orchestrator_engine.get_stats()
        
        assert "active_workflows" in stats
        assert "active_plans" in stats
        assert "active_executions" in stats
        assert "registered_agents" in stats


# =============================================================================
# TEST WORKFLOW
# =============================================================================

class TestWorkflow:
    """Tests for Workflow domain object."""
    
    def test_workflow_creation(self):
        """Test workflow creation."""
        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )
        
        assert workflow.workflow_id == "wf_1"
        assert workflow.name == "Test Workflow"
        assert workflow.status == WorkflowStatus.PENDING
        assert len(workflow.steps) == 0
    
    def test_workflow_add_step(self):
        """Test adding steps to workflow."""
        workflow = Workflow(
            workflow_id="wf_2",
            name="Test Workflow",
        )
        
        step1 = WorkflowStep(
            step_id="step_1",
            agent_type="biomedical",
        )
        step2 = WorkflowStep(
            step_id="step_2",
            agent_type="diagnostic",
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        assert len(workflow.steps) == 2
        assert workflow.get_step("step_1") == step1
        assert workflow.get_step("step_2") == step2
    
    def test_workflow_get_ready_steps(self):
        """Test getting ready steps."""
        workflow = Workflow(
            workflow_id="wf_3",
            name="Test Workflow",
        )
        
        step1 = WorkflowStep(
            step_id="step_1",
            agent_type="biomedical",
        )
        step2 = WorkflowStep(
            step_id="step_2",
            agent_type="diagnostic",
            depends_on=["step_1"],
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        # Initially, only step1 should be ready
        ready = workflow.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].step_id == "step_1"
        
        # After completing step1, step2 should be ready
        step1.status = ExecutionStatus.COMPLETED
        ready = workflow.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].step_id == "step_2"
    
    def test_workflow_progress(self):
        """Test workflow progress calculation."""
        workflow = Workflow(
            workflow_id="wf_4",
            name="Test Workflow",
        )
        
        workflow.add_step(WorkflowStep(step_id="s1", agent_type="biomedical"))
        workflow.add_step(WorkflowStep(step_id="s2", agent_type="diagnostic"))
        workflow.add_step(WorkflowStep(step_id="s3", agent_type="knowledge"))
        
        # Initially 0% progress
        assert workflow.progress == 0.0
        
        # After completing one step
        workflow.steps[0].status = ExecutionStatus.COMPLETED
        assert workflow.progress == pytest.approx(1/3, rel=0.01)
        
        # After completing all steps
        workflow.steps[1].status = ExecutionStatus.COMPLETED
        workflow.steps[2].status = ExecutionStatus.COMPLETED
        assert workflow.progress == 1.0


# =============================================================================
# TEST ORCHESTRATION PLAN
# =============================================================================

class TestOrchestrationPlan:
    """Tests for OrchestrationPlan domain object."""
    
    def test_plan_creation(self):
        """Test plan creation."""
        plan = OrchestrationPlan(
            plan_id="plan_1",
            request_id="req_1",
            original_query="Test query",
            intent="diagnostic",
        )
        
        assert plan.plan_id == "plan_1"
        assert plan.request_id == "req_1"
        assert plan.intent == "diagnostic"
        assert plan.status == PlanStatus.CREATED
        assert len(plan.steps) == 0
    
    def test_plan_add_step(self):
        """Test adding steps to plan."""
        plan = OrchestrationPlan(
            plan_id="plan_2",
            request_id="req_2",
            original_query="Test query",
        )
        
        step1 = PlanStep(step_id="s1", order=1, agent_type="biomedical")
        step2 = PlanStep(step_id="s2", order=0, agent_type="diagnostic")
        
        plan.add_step(step1)
        plan.add_step(step2)
        
        # Should be sorted by order
        assert plan.steps[0].step_id == "s2"
        assert plan.steps[1].step_id == "s1"
    
    def test_plan_get_next_step(self):
        """Test getting next pending step."""
        plan = OrchestrationPlan(
            plan_id="plan_3",
            request_id="req_3",
            original_query="Test query",
        )
        
        step1 = PlanStep(step_id="s1", order=1, agent_type="biomedical")
        step2 = PlanStep(step_id="s2", order=2, agent_type="diagnostic")
        
        plan.add_step(step1)
        plan.add_step(step2)
        
        # First step should be next
        next_step = plan.get_next_step()
        assert next_step.step_id == "s1"
        
        # After completing first step
        step1.status = ExecutionStatus.COMPLETED
        next_step = plan.get_next_step()
        assert next_step.step_id == "s2"


# =============================================================================
# TEST TASK DISPATCHER
# =============================================================================

class TestTaskDispatcher:
    """Tests for TaskDispatcher."""
    
    @pytest.mark.asyncio
    async def test_dispatcher_initialization(self, mock_registry, mock_broker):
        """Test dispatcher initialization."""
        dispatcher = TaskDispatcher(
            registry=mock_registry,
            broker=mock_broker,
        )
        
        assert dispatcher.registry == mock_registry
        assert dispatcher.broker == mock_broker
        assert dispatcher._dispatch_count == 0
    
    @pytest.mark.asyncio
    async def test_dispatch_direct(self, mock_registry, mock_broker, mock_agent):
        """Test direct dispatch to agent."""
        dispatcher = TaskDispatcher(
            registry=mock_registry,
            broker=mock_broker,
        )
        
        # Mock agent execution
        mock_agent.execute = AsyncMock(return_value=AgentResult(
            task_id="task_1",
            agent_id="test_agent_1",
            success=True,
            output={"result": "test_output"},
            confidence=0.9,
        ))
        
        execution = AgentExecution(
            execution_id="exec_1",
            workflow_id="wf_1",
            step_id="step_1",
            agent_id="test_agent_1",
            agent_type="biomedical",
            task_type="diagnose",
            task_input={"query": "test"},
        )
        
        result = await dispatcher.dispatch(execution, mock_agent)
        
        assert result is not None
        assert result.success is True
        assert result.execution_id == "exec_1"
        assert dispatcher._dispatch_count == 1
        assert dispatcher._success_count == 1


# =============================================================================
# TEST TASK SCHEDULER
# =============================================================================

class TestTaskScheduler:
    """Tests for TaskScheduler."""
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        scheduler = TaskScheduler(max_concurrent=5)
        
        assert scheduler.max_concurrent == 5
        assert len(scheduler._running_tasks) == 0
        assert len(scheduler._completed_tasks) == 0
    
    def test_schedule_fifo(self):
        """Test FIFO scheduling."""
        scheduler = TaskScheduler()
        
        workflow = Workflow(
            workflow_id="wf_fifo",
            name="Test FIFO",
        )
        workflow.add_step(WorkflowStep(step_id="s1", agent_type="a"))
        workflow.add_step(WorkflowStep(step_id="s2", agent_type="b"))
        workflow.add_step(WorkflowStep(step_id="s3", agent_type="c"))
        
        scheduled = scheduler.schedule_workflow(
            workflow,
            strategy=ScheduleStrategy.FIFO,
        )
        
        assert len(scheduled) == 3
        assert [s.step_id for s in scheduled] == ["s1", "s2", "s3"]
    
    def test_schedule_priority(self):
        """Test priority scheduling."""
        scheduler = TaskScheduler()
        
        workflow = Workflow(
            workflow_id="wf_priority",
            name="Test Priority",
        )
        
        step1 = WorkflowStep(step_id="s1", agent_type="a")
        step2 = WorkflowStep(step_id="s2", agent_type="b")
        step3 = WorkflowStep(step_id="s3", agent_type="c")
        
        # Set priorities dynamically
        step1.priority = 1
        step2.priority = 3
        step3.priority = 2
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        workflow.add_step(step3)
        
        scheduled = scheduler.schedule_workflow(
            workflow,
            strategy=ScheduleStrategy.PRIORITY,
        )
        
        # Should be ordered by priority (highest first)
        assert scheduled[0].step_id == "s2"  # priority 3
        assert scheduled[1].step_id == "s3"  # priority 2
        assert scheduled[2].step_id == "s1"  # priority 1
    
    def test_schedule_dependency(self):
        """Test dependency-based scheduling."""
        scheduler = TaskScheduler()
        
        workflow = Workflow(
            workflow_id="wf_dep",
            name="Test Dependency",
        )
        
        step1 = WorkflowStep(step_id="s1", agent_type="a")
        step2 = WorkflowStep(step_id="s2", agent_type="b", depends_on=["s1"])
        step3 = WorkflowStep(step_id="s3", agent_type="c", depends_on=["s2"])
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        workflow.add_step(step3)
        
        scheduled = scheduler.schedule_workflow(
            workflow,
            strategy=ScheduleStrategy.DEPENDENCY,
        )
        
        # Should respect dependencies
        assert scheduled[0].step_id == "s1"
        assert scheduled[1].step_id == "s2"
        assert scheduled[2].step_id == "s3"
    
    def test_get_ready_steps(self):
        """Test getting ready steps."""
        scheduler = TaskScheduler()
        
        workflow = Workflow(
            workflow_id="wf_ready",
            name="Test Ready",
        )
        
        step1 = WorkflowStep(step_id="s1", agent_type="a")
        step2 = WorkflowStep(step_id="s2", agent_type="b", depends_on=["s1"])
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        # Initially only s1 should be ready
        ready = scheduler.get_ready_steps(workflow)
        assert len(ready) == 1
        assert ready[0].step_id == "s1"
        
        # After marking s1 as running (should still be ready until completed)
        step1.status = ExecutionStatus.RUNNING
        scheduler.mark_running(step1)
        ready = scheduler.get_ready_steps(workflow)
        # Running steps are not considered "ready" for new execution
        assert len(ready) == 0
        
        # After marking s1 as completed
        step1.status = ExecutionStatus.COMPLETED
        scheduler.mark_completed(step1)
        ready = scheduler.get_ready_steps(workflow)
        assert len(ready) == 1
        assert ready[0].step_id == "s2"


# =============================================================================
# TEST RESPONSE AGGREGATOR
# =============================================================================

class TestResponseAggregator:
    """Tests for ResponseAggregator."""
    
    @pytest.mark.asyncio
    async def test_aggregator_initialization(self):
        """Test aggregator initialization."""
        config = AggregationConfig(
            method=AggregationMethod.BEST,
            min_confidence=0.7,
        )
        aggregator = ResponseAggregator(config=config)
        
        assert aggregator.config.method == AggregationMethod.BEST
        assert aggregator.config.min_confidence == 0.7
    
    @pytest.mark.asyncio
    async def test_aggregate_first(self):
        """Test FIRST aggregation method."""
        aggregator = ResponseAggregator(
            config=AggregationConfig(method=AggregationMethod.FIRST)
        )
        
        results = {
            "step_1": {"success": True, "output": {"data": "first"}},
            "step_2": {"success": True, "output": {"data": "second"}},
        }
        
        aggregated = await aggregator.aggregate(results, {})
        
        assert aggregated["success"] is True
        assert aggregated["output"]["data"] == "first"
        assert aggregated["method_used"] == "first"
    
    @pytest.mark.asyncio
    async def test_aggregate_best(self):
        """Test BEST aggregation method."""
        aggregator = ResponseAggregator(
            config=AggregationConfig(method=AggregationMethod.BEST)
        )
        
        results = {
            "step_1": {"success": True, "output": {"value": 10}, "confidence": 0.7},
            "step_2": {"success": True, "output": {"value": 20}, "confidence": 0.9},
            "step_3": {"success": True, "output": {"value": 15}, "confidence": 0.8},
        }
        
        aggregated = await aggregator.aggregate(results, {})
        
        assert aggregated["success"] is True
        # Should select the highest confidence result
        assert aggregated["sources"] == ["step_2"]
    
    @pytest.mark.asyncio
    async def test_aggregate_all(self):
        """Test ALL aggregation method."""
        aggregator = ResponseAggregator(
            config=AggregationConfig(method=AggregationMethod.ALL)
        )
        
        results = {
            "step_1": {"success": True, "output": {"data": 1}},
            "step_2": {"success": True, "output": {"data": 2}},
        }
        
        aggregated = await aggregator.aggregate(results, {})
        
        assert aggregated["success"] is True
        assert "_all_results" in aggregated["output"]
        assert len(aggregated["sources"]) == 2
    
    @pytest.mark.asyncio
    async def test_aggregate_merge(self):
        """Test MERGE aggregation method."""
        aggregator = ResponseAggregator(
            config=AggregationConfig(method=AggregationMethod.MERGE)
        )
        
        results = {
            "step_1": {
                "success": True,
                "output": {"field1": "value1", "field2": "from_step1"},
            },
            "step_2": {
                "success": True,
                "output": {"field2": "from_step2", "field3": "value3"},
            },
        }
        
        aggregated = await aggregator.aggregate(results, {})
        
        assert aggregated["success"] is True
        assert aggregated["output"]["field1"] == "value1"
        assert aggregated["output"]["field2"] == "from_step2"  # Last wins
        assert aggregated["output"]["field3"] == "value3"
    
    @pytest.mark.asyncio
    async def test_aggregate_with_failures(self):
        """Test aggregation with some failures."""
        aggregator = ResponseAggregator(
            config=AggregationConfig(method=AggregationMethod.BEST)
        )
        
        results = {
            "step_1": {"success": False, "error": "Failed"},
            "step_2": {"success": True, "output": {"data": "ok"}, "confidence": 0.9},
        }
        
        aggregated = await aggregator.aggregate(results, {})
        
        # Should succeed because at least one succeeded
        assert aggregated["success"] is True
        # Check that we have results from successful steps
        assert "step_2" in aggregated["sources"]


# =============================================================================
# TEST EXECUTION STATUS
# =============================================================================

class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""
    
    def test_execution_status_values(self):
        """Test ExecutionStatus enum values."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.SKIPPED.value == "skipped"


# =============================================================================
# TEST ORCHESTRATION STRATEGY
# =============================================================================

class TestOrchestrationStrategy:
    """Tests for OrchestrationStrategy enum."""
    
    def test_strategy_values(self):
        """Test OrchestrationStrategy enum values."""
        assert OrchestrationStrategy.SEQUENTIAL.value == "sequential"
        assert OrchestrationStrategy.PARALLEL.value == "parallel"
        assert OrchestrationStrategy.FAN_OUT.value == "fan_out"
        assert OrchestrationStrategy.PIPELINE.value == "pipeline"
        assert OrchestrationStrategy.HYBRID.value == "hybrid"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
