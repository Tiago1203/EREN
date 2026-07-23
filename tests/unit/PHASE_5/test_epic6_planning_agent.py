"""
Tests for EPIC 6: Planning Agent

Test suite for the Planning Agent.
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
    AgentResult,
)

from core.PHASE_5.epic6_planning_agent import (
    PlanningAgent,
    PlanningAgentConfig,
)

from core.PHASE_5.epic6_planning_agent.domain import (
    ActionPlan,
    ActionItem,
    ActionPriority,
    ActionStatus,
    ClinicalPlan,
    ClinicalPhase,
    ClinicalPhaseItem,
    ExecutionTask,
    TaskType,
    TaskStatus,
)

from core.PHASE_5.epic6_planning_agent.engines import (
    ActionPlanner,
    PlanResult,
    ScheduleGenerator,
    ScheduleResult,
    TaskGenerator,
    TaskResult,
    RiskPlanner,
    RiskAssessment,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def agent_config():
    """Create agent config."""
    return PlanningAgentConfig(
        enable_action_planner=True,
        enable_schedule_generator=True,
        enable_task_generator=True,
        enable_risk_planner=True,
    )


@pytest.fixture
def planning_agent(agent_config):
    """Create planning agent."""
    return PlanningAgent(
        agent_id="planning_test_1",
        config=agent_config,
    )


# =============================================================================
# TEST PLANNING AGENT
# =============================================================================

class TestPlanningAgent:
    """Tests for PlanningAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, planning_agent, agent_config):
        """Test agent initializes correctly."""
        assert planning_agent.agent_id == "planning_test_1"
        assert planning_agent.agent_type == AgentType.PLANNING
        assert planning_agent.config == agent_config
        
        # Engines should be initialized
        assert planning_agent._action_planner is not None
        assert planning_agent._schedule_generator is not None
        assert planning_agent._task_generator is not None
        assert planning_agent._risk_planner is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, planning_agent):
        """Test agent initialization method."""
        await planning_agent.initialize()
        assert planning_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_execute_action_plan(self, planning_agent):
        """Test action plan execution."""
        task = AgentTask(
            task_id="task_1",
            agent_id="planning_test_1",
            task_type="planning",
            input_data={
                "plan_type": "action",
                "context_id": "incident_123",
                "objectives": [
                    "Repair critical device",
                    "Verify functionality",
                ],
            },
        )
        
        result = await planning_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.agent_id == "planning_test_1"
        assert result.output["plan_type"] == "action"
    
    @pytest.mark.asyncio
    async def test_execute_clinical_plan(self, planning_agent):
        """Test clinical plan execution."""
        task = AgentTask(
            task_id="task_2",
            agent_id="planning_test_1",
            task_type="planning",
            input_data={
                "plan_type": "clinical",
                "patient_id": "patient_123",
                "title": "Calibration Protocol",
                "phases": [
                    {"phase": "assessment", "order": 1, "duration": 30},
                    {"phase": "implementation", "order": 2, "duration": 60},
                ],
            },
        )
        
        result = await planning_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["plan_type"] == "clinical"
    
    @pytest.mark.asyncio
    async def test_metrics(self, planning_agent):
        """Test agent metrics."""
        metrics = planning_agent.get_metrics()
        
        assert "plans_created" in metrics
        assert "tasks_generated" in metrics
        assert "engines_enabled" in metrics
        
        assert metrics["engines_enabled"]["action_planner"] is True
        assert metrics["engines_enabled"]["schedule_generator"] is True


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestActionItem:
    """Tests for ActionItem."""
    
    def test_item_creation(self):
        """Test item creation."""
        item = ActionItem(
            item_id="item_1",
            title="Test action",
            priority=ActionPriority.HIGH,
        )
        
        assert item.item_id == "item_1"
        assert item.priority == ActionPriority.HIGH
    
    def test_item_auto_id(self):
        """Test automatic ID generation."""
        item = ActionItem(title="Test")
        assert item.item_id != ""


class TestActionPlan:
    """Tests for ActionPlan."""
    
    def test_plan_creation(self):
        """Test plan creation."""
        plan = ActionPlan(
            plan_id="plan_1",
            context_id="incident_123",
        )
        
        assert plan.plan_id == "plan_1"
        assert plan.total_actions == 0
    
    def test_add_action(self):
        """Test adding actions."""
        plan = ActionPlan(context_id="incident_123")
        
        plan.add_action(ActionItem(
            title="Action 1",
            priority=ActionPriority.HIGH,
        ))
        
        assert plan.total_actions == 1
    
    def test_get_progress_percentage(self):
        """Test progress calculation."""
        plan = ActionPlan(context_id="incident_123")
        
        plan.add_action(ActionItem(title="Action 1", status=ActionStatus.COMPLETED))
        plan.add_action(ActionItem(title="Action 2", status=ActionStatus.PENDING))
        
        assert plan.get_progress_percentage() == 50.0


class TestClinicalPlan:
    """Tests for ClinicalPlan."""
    
    def test_plan_creation(self):
        """Test plan creation."""
        plan = ClinicalPlan(
            plan_id="plan_1",
            patient_id="patient_123",
        )
        
        assert plan.plan_id == "plan_1"
        assert plan.progress_percentage == 0.0
    
    def test_add_phase(self):
        """Test adding phases."""
        plan = ClinicalPlan(patient_id="patient_123")
        
        plan.add_phase(ClinicalPhaseItem(
            phase=ClinicalPhase.ASSESSMENT,
            order=1,
        ))
        
        assert len(plan.phases) == 1
    
    def test_advance_phase(self):
        """Test advancing phases."""
        plan = ClinicalPlan(patient_id="patient_123")
        
        plan.add_phase(ClinicalPhaseItem(phase=ClinicalPhase.ASSESSMENT, order=1))
        plan.add_phase(ClinicalPhaseItem(phase=ClinicalPhase.IMPLEMENTATION, order=2))
        
        assert plan.current_phase_index == 0
        plan.advance_phase()
        assert plan.current_phase_index == 1


class TestExecutionTask:
    """Tests for ExecutionTask."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = ExecutionTask(
            task_id="task_1",
            title="Execute repair",
            task_type=TaskType.MAINTENANCE,
        )
        
        assert task.task_id == "task_1"
        assert task.task_type == TaskType.MAINTENANCE
    
    def test_complete(self):
        """Test task completion."""
        task = ExecutionTask(task_id="task_1")
        
        task.complete(output="Repair completed successfully")
        
        assert task.status == TaskStatus.COMPLETED
        assert task.output == "Repair completed successfully"


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestActionPlanner:
    """Tests for ActionPlanner."""
    
    @pytest.mark.asyncio
    async def test_create_plan(self):
        """Test plan creation."""
        planner = ActionPlanner()
        
        result = await planner.create_plan(
            context_id="incident_123",
            objectives=["Fix device", "Test functionality", "Document"],
        )
        
        assert result.context_id == "incident_123"
        assert result.actions_count > 0
        assert result.plan is not None
    
    @pytest.mark.asyncio
    async def test_critical_action(self):
        """Test first action is critical."""
        planner = ActionPlanner()
        
        result = await planner.create_plan(
            context_id="incident_123",
            objectives=["Fix device"],
        )
        
        assert result.critical_count >= 1


class TestScheduleGenerator:
    """Tests for ScheduleGenerator."""
    
    @pytest.mark.asyncio
    async def test_generate_schedule(self):
        """Test schedule generation."""
        generator = ScheduleGenerator()
        
        plan = ActionPlan(context_id="incident_123")
        plan.add_action(ActionItem(title="Action 1", estimated_duration_minutes=30))
        
        result = await generator.generate_schedule(plan)
        
        assert result.plan_id == plan.plan_id
        assert result.total_tasks > 0


class TestTaskGenerator:
    """Tests for TaskGenerator."""
    
    @pytest.mark.asyncio
    async def test_generate_tasks(self):
        """Test task generation."""
        generator = TaskGenerator()
        
        plan = ActionPlan(context_id="incident_123")
        plan.add_action(ActionItem(title="Action 1"))
        
        result = await generator.generate_tasks(plan)
        
        assert result.plan_id == plan.plan_id
        assert len(result.tasks) > 0


class TestRiskPlanner:
    """Tests for RiskPlanner."""
    
    @pytest.mark.asyncio
    async def test_assess_risks(self):
        """Test risk assessment."""
        planner = RiskPlanner()
        
        plan = ActionPlan(context_id="incident_123")
        plan.add_action(ActionItem(title="Action 1"))
        
        result = await planner.assess_risks(plan)
        
        assert result.plan_id == plan.plan_id
        assert result.risk_level is not None


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_action_priority_values(self):
        """Test ActionPriority enum values."""
        assert ActionPriority.CRITICAL.value == "critical"
        assert ActionPriority.HIGH.value == "high"
        assert ActionPriority.MEDIUM.value == "medium"
    
    def test_action_status_values(self):
        """Test ActionStatus enum values."""
        assert ActionStatus.PENDING.value == "pending"
        assert ActionStatus.IN_PROGRESS.value == "in_progress"
        assert ActionStatus.COMPLETED.value == "completed"
    
    def test_task_type_values(self):
        """Test TaskType enum values."""
        assert TaskType.CLINICAL.value == "clinical"
        assert TaskType.TECHNICAL.value == "technical"
        assert TaskType.MAINTENANCE.value == "maintenance"
    
    def test_task_status_values(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
    
    def test_clinical_phase_values(self):
        """Test ClinicalPhase enum values."""
        assert ClinicalPhase.ASSESSMENT.value == "assessment"
        assert ClinicalPhase.PLANNING.value == "planning"
        assert ClinicalPhase.IMPLEMENTATION.value == "implementation"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
