"""Unit tests for EREN Cognitive Planning Engine."""

import pytest

from core.PHASE_2.planning.types import (
    TaskStatus,
    TaskPriority,
    DependencyType,
    GoalType,
    PlanStatus,
    Task,
    Goal,
    GoalAnalysis,
    ExecutionPlan,
    PlanningMetrics,
)
from core.PHASE_2.planning.goal_analyzer import GoalAnalyzer
from core.PHASE_2.planning.task_decomposer import TaskDecomposer
from core.PHASE_2.planning.dependency_resolver import DependencyResolver
from core.PHASE_2.planning.plan_builder import PlanBuilder
from core.PHASE_2.planning.planner import CognitivePlanningEngine


class TestPlanningTypes:
    """Tests for planning types."""

    def test_task_creation(self):
        """Test task creation."""
        task = Task(
            task_id="task-1",
            name="Test Task",
            description="A test task",
        )
        assert task.task_id == "task-1"
        assert task.status == TaskStatus.PENDING

    def test_task_duration(self):
        """Test task duration calculation."""
        from datetime import datetime, timezone
        task = Task(
            task_id="task-1",
            name="Test",
            description="Test",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        # Duration is very small but positive
        assert task.duration_seconds >= 0.0

    def test_goal_creation(self):
        """Test goal creation."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose the issue",
        )
        assert goal.goal_id == "goal-1"
        assert goal.goal_type == GoalType.DIAGNOSIS

    def test_execution_plan(self):
        """Test execution plan."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Test",
        )
        plan = ExecutionPlan(
            plan_id="plan-1",
            goal=goal,
            tasks=[],
        )
        assert plan.plan_id == "plan-1"
        assert plan.progress == 0.0


class TestGoalAnalyzer:
    """Tests for goal analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create test analyzer."""
        return GoalAnalyzer()

    def test_analyze_diagnosis(self, analyzer):
        """Test diagnosing goal detection."""
        analysis = analyzer.analyze(
            "What is wrong with the patient?"
        )
        assert analysis.goal_type == GoalType.DIAGNOSIS

    def test_analyze_troubleshooting(self, analyzer):
        """Test troubleshooting goal detection."""
        analysis = analyzer.analyze(
            "The monitor is not working. Fix it."
        )
        assert analysis.goal_type == GoalType.TROUBLESHOOTING

    def test_analyze_research(self, analyzer):
        """Test research goal detection."""
        analysis = analyzer.analyze(
            "Find information about diabetes"
        )
        # Should be research or treatment
        assert analysis.goal_type in [GoalType.RESEARCH, GoalType.TREATMENT]

    def test_extract_capabilities(self, analyzer):
        """Test capability extraction."""
        analysis = analyzer.analyze(
            "Analyze the device status"
        )
        assert len(analysis.required_capabilities) >= 1

    def test_complexity_estimation(self, analyzer):
        """Test complexity estimation."""
        simple = analyzer.analyze("Simple question")
        complex_q = analyzer.analyze(
            "Please provide a detailed comprehensive analysis of all the factors"
        )
        assert complex_q.estimated_complexity >= simple.estimated_complexity


class TestTaskDecomposer:
    """Tests for task decomposer."""

    @pytest.fixture
    def decomposer(self):
        """Create test decomposer."""
        return TaskDecomposer()

    def test_decompose_diagnosis(self, decomposer):
        """Test diagnosis decomposition."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose patient condition",
        )
        analysis = GoalAnalysis(goal=goal, intent="Diagnose patient")

        tasks = decomposer.decompose(goal, analysis)

        assert len(tasks) >= 3
        assert any(t.task_type == "reasoning" for t in tasks)

    def test_decompose_troubleshooting(self, decomposer):
        """Test troubleshooting decomposition."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.TROUBLESHOOTING,
            description="Fix device",
        )
        analysis = GoalAnalysis(goal=goal, intent="Fix device")

        tasks = decomposer.decompose(goal, analysis)

        assert len(tasks) >= 5
        assert any(t.priority == TaskPriority.CRITICAL for t in tasks)

    def test_priority_assignment(self, decomposer):
        """Test priority assignment."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.RESEARCH,
            description="Research",
        )
        analysis = GoalAnalysis(goal=goal, intent="Research")

        tasks = decomposer.decompose(goal, analysis)

        # First task should be high priority
        assert tasks[0].priority == TaskPriority.HIGH


class TestDependencyResolver:
    """Tests for dependency resolver."""

    @pytest.fixture
    def resolver(self):
        """Create test resolver."""
        return DependencyResolver()

    def test_resolve_no_dependencies(self, resolver):
        """Test resolving tasks with no dependencies."""
        tasks = [
            Task(task_id="t1", name="Task 1", description=""),
            Task(task_id="t2", name="Task 2", description=""),
        ]

        ordered = resolver.resolve(tasks)

        assert len(ordered) == 2

    def test_resolve_with_dependencies(self, resolver):
        """Test resolving tasks with dependencies."""
        tasks = [
            Task(
                task_id="t1", name="Task 1", description="",
                depends_on=[],
            ),
            Task(
                task_id="t2", name="Task 2", description="",
                depends_on=["t1"],
            ),
        ]

        ordered = resolver.resolve(tasks)

        assert len(ordered) == 2
        # t1 should come before t2
        t1_idx = next(i for i, t in enumerate(ordered) if t.task_id == "t1")
        t2_idx = next(i for i, t in enumerate(ordered) if t.task_id == "t2")
        assert t1_idx < t2_idx

    def test_circular_dependency_detection(self, resolver):
        """Test circular dependency detection."""
        tasks = [
            Task(task_id="t1", name="Task 1", description="", depends_on=["t2"]),
            Task(task_id="t2", name="Task 2", description="", depends_on=["t1"]),
        ]

        with pytest.raises(ValueError, match="Circular"):
            resolver.resolve(tasks)

    def test_validate_dependencies(self, resolver):
        """Test dependency validation."""
        tasks = [
            Task(task_id="t1", name="Task 1", description=""),
        ]

        is_valid, errors = resolver.validate_dependencies(tasks)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_dependency(self, resolver):
        """Test validation with invalid dependency."""
        tasks = [
            Task(task_id="t1", name="Task 1", description="", depends_on=["unknown"]),
        ]

        is_valid, errors = resolver.validate_dependencies(tasks)
        assert not is_valid
        assert len(errors) > 0

    def test_parallel_groups(self, resolver):
        """Test parallel group calculation."""
        tasks = [
            Task(task_id="t1", name="Task 1", description=""),
            Task(task_id="t2", name="Task 2", description=""),
            Task(task_id="t3", name="Task 3", description="", depends_on=["t1"]),
        ]

        groups = resolver.calculate_execution_order(tasks)

        # Should have 2 groups - first has parallel tasks, second has t3
        assert len(groups) >= 1
        # First group should have t1 at least
        assert groups[0][0].task_id == "t1"


class TestPlanBuilder:
    """Tests for plan builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return PlanBuilder()

    def test_build_plan(self, builder):
        """Test plan building."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose",
        )
        analysis = GoalAnalysis(goal=goal, intent="Diagnose")
        tasks = [
            Task(task_id="t1", name="Task 1", description="", estimated_time_seconds=10),
            Task(task_id="t2", name="Task 2", description="", estimated_time_seconds=20),
        ]

        plan = builder.build(goal, analysis, tasks)

        assert plan.plan_id is not None
        assert len(plan.tasks) == 2
        assert plan.total_estimated_time_seconds == 30.0
        assert plan.status == PlanStatus.CREATED

    def test_validate_valid_plan(self, builder):
        """Test validating valid plan."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [Task(task_id="t1", name="T1", description="")]
        plan = ExecutionPlan(plan_id="p1", goal=goal, tasks=tasks)

        is_valid, errors = builder.validate(plan)
        assert is_valid

    def test_validate_empty_plan(self, builder):
        """Test validating empty plan."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        plan = ExecutionPlan(plan_id="p1", goal=goal, tasks=[])

        is_valid, errors = builder.validate(plan)
        assert not is_valid

    def test_update_progress(self, builder):
        """Test updating plan progress."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [Task(task_id="t1", name="T1", description="")]
        plan = ExecutionPlan(plan_id="p1", goal=goal, tasks=tasks)

        plan = builder.update_progress(plan, "t1", result={"done": True})

        assert plan.completed_tasks == 1
        assert plan.tasks[0].status == "completed"


class TestCognitivePlanningEngine:
    """Tests for cognitive planning engine."""

    @pytest.fixture
    def engine(self):
        """Create test engine."""
        return CognitivePlanningEngine()

    def test_plan_simple_intent(self, engine):
        """Test planning for simple intent."""
        plan = engine.plan("Find information about diabetes")

        assert plan is not None
        assert len(plan.tasks) > 0
        assert plan.status == PlanStatus.READY

    def test_plan_troubleshooting(self, engine):
        """Test planning for troubleshooting."""
        plan = engine.plan(
            "The monitor is not working. Fix it."
        )

        assert plan.goal.goal_type == GoalType.TROUBLESHOOTING
        assert len(plan.tasks) >= 5

    def test_plan_diagnosis(self, engine):
        """Test planning for diagnosis."""
        plan = engine.plan(
            "What is wrong with the patient?"
        )

        assert plan.goal.goal_type == GoalType.DIAGNOSIS
        # First task should be high or critical priority
        assert plan.tasks[0].priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]

    def test_plan_with_context(self, engine):
        """Test planning with context."""
        plan = engine.plan(
            "Analyze the device",
            context={"device_id": "philips-mx450"},
        )

        assert plan is not None
        assert len(plan.tasks) > 0

    def test_validate_plan(self, engine):
        """Test plan validation."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [Task(task_id="t1", name="T1", description="")]
        plan = ExecutionPlan(plan_id="p1", goal=goal, tasks=tasks)

        is_valid, errors = engine.validate_plan(plan)
        assert is_valid

    def test_get_executable_tasks(self, engine):
        """Test getting executable tasks."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [
            Task(task_id="t1", name="T1", description=""),
            Task(task_id="t2", name="T2", description="", depends_on=["t1"]),
        ]
        plan = ExecutionPlan(plan_id="p1", goal=goal, tasks=tasks)

        executable = engine.get_executable_tasks(plan)

        # t1 should be executable (no dependencies)
        assert len(executable) >= 1
        task_ids = [t.task_id for t in executable]
        assert "t1" in task_ids

    def test_metrics(self, engine):
        """Test metrics tracking."""
        plan = engine.plan("Test intent")
        metrics = engine.get_metrics()

        assert metrics.plans_created >= 1
        assert metrics.total_tasks > 0

    def test_update_plan_progress(self, engine):
        """Test updating plan progress."""
        plan = engine.plan("Test intent")
        task_id = plan.tasks[0].task_id

        updated_plan = engine.update_plan_progress(
            plan, task_id, result={"done": True}
        )

        assert updated_plan.completed_tasks == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
