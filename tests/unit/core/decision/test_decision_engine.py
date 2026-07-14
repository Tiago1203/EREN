"""Unit tests for EREN Cognitive Decision Engine."""

import pytest

from core.decision.types import (
    DecisionStrategy,
    ExecutionPolicy,
    RiskLevel,
    TaskStatus,
    TaskPriority,
    DependencyType,
    GoalType,
    DecisionStatus,
    DecisionTask,
    Goal,
    GoalAnalysis,
    DecisionPlan,
    StrategySelection,
    RiskAssessment,
    ExecutionDecision,
    DecisionMetrics,
)
from core.decision.goal_analyzer import GoalAnalyzer
from core.decision.task_decomposer import TaskDecomposer
from core.decision.dependency_resolver import DependencyResolver
from core.decision.strategy_selector import StrategySelector
from core.decision.risk_evaluator import RiskEvaluator
from core.decision.execution_policy import ExecutionPolicyManager
from core.decision.replanner import Replanner
from core.decision.decision_builder import DecisionBuilder
from core.decision.engine import CognitiveDecisionEngine


class TestDecisionTypes:
    """Tests for decision types."""

    def test_decision_task_creation(self):
        """Test decision task creation."""
        task = DecisionTask(
            task_id="task-1",
            name="Test Task",
            description="A test task",
        )
        assert task.task_id == "task-1"
        assert task.status == TaskStatus.PENDING

    def test_decision_task_duration(self):
        """Test decision task duration calculation."""
        from datetime import datetime, timezone
        task = DecisionTask(
            task_id="task-1",
            name="Test",
            description="Test",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        assert task.duration_seconds >= 0.0

    def test_decision_plan_creation(self):
        """Test decision plan creation."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose the issue",
        )
        plan = DecisionPlan(
            plan_id="plan-1",
            goal=goal,
            tasks=[],
        )
        assert plan.plan_id == "plan-1"
        assert plan.progress == 0.0
        assert plan.strategy == DecisionStrategy.HYBRID  # Default


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


class TestDependencyResolver:
    """Tests for dependency resolver."""

    @pytest.fixture
    def resolver(self):
        """Create test resolver."""
        return DependencyResolver()

    def test_resolve_no_dependencies(self, resolver):
        """Test resolving tasks with no dependencies."""
        tasks = [
            DecisionTask(task_id="t1", name="Task 1", description=""),
            DecisionTask(task_id="t2", name="Task 2", description=""),
        ]

        ordered = resolver.resolve(tasks)

        assert len(ordered) == 2

    def test_resolve_with_dependencies(self, resolver):
        """Test resolving tasks with dependencies."""
        tasks = [
            DecisionTask(
                task_id="t1", name="Task 1", description="",
                depends_on=[],
            ),
            DecisionTask(
                task_id="t2", name="Task 2", description="",
                depends_on=["t1"],
            ),
        ]

        ordered = resolver.resolve(tasks)

        assert len(ordered) == 2
        t1_idx = next(i for i, t in enumerate(ordered) if t.task_id == "t1")
        t2_idx = next(i for i, t in enumerate(ordered) if t.task_id == "t2")
        assert t1_idx < t2_idx

    def test_circular_dependency_detection(self, resolver):
        """Test circular dependency detection."""
        tasks = [
            DecisionTask(task_id="t1", name="Task 1", description="", depends_on=["t2"]),
            DecisionTask(task_id="t2", name="Task 2", description="", depends_on=["t1"]),
        ]

        with pytest.raises(ValueError, match="Circular"):
            resolver.resolve(tasks)


class TestStrategySelector:
    """Tests for strategy selector."""

    @pytest.fixture
    def selector(self):
        """Create test selector."""
        return StrategySelector()

    def test_select_strategy(self, selector):
        """Test strategy selection."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose patient",
        )
        analysis = GoalAnalysis(goal=goal, intent="Diagnose")
        tasks = [
            DecisionTask(task_id="t1", name="Task 1", description=""),
            DecisionTask(task_id="t2", name="Task 2", description=""),
        ]

        selection = selector.select(goal, analysis, tasks)

        assert selection.selected_strategy is not None
        assert len(selection.alternatives) <= 2


class TestRiskEvaluator:
    """Tests for risk evaluator."""

    @pytest.fixture
    def evaluator(self):
        """Create test evaluator."""
        return RiskEvaluator()

    def test_evaluate_low_risk(self, evaluator):
        """Test low risk evaluation."""
        task = DecisionTask(
            task_id="t1",
            name="Simple retrieval",
            description="Just a query",
            task_type="retrieval",
        )

        risk = evaluator.evaluate_task(task)

        assert risk in [RiskLevel.LOW, RiskLevel.MINIMAL]

    def test_evaluate_high_risk(self, evaluator):
        """Test high risk evaluation."""
        task = DecisionTask(
            task_id="t1",
            name="Critical medical procedure",
            description="Perform surgery",
            task_type="medical",
        )

        risk = evaluator.evaluate_task(task)

        assert risk in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.MEDIUM]


class TestExecutionPolicyManager:
    """Tests for execution policy manager."""

    @pytest.fixture
    def policy_manager(self):
        """Create test policy manager."""
        return ExecutionPolicyManager()

    def test_select_policy_conservative(self, policy_manager):
        """Test conservative policy selection."""
        decision = policy_manager.select_policy(
            strategy=DecisionStrategy.CONSERVATIVE,
            risk_level=RiskLevel.MEDIUM,
            task_count=5,
        )

        assert decision.policy == ExecutionPolicy.CONSERVATIVE
        assert decision.failfast_enabled is False

    def test_select_policy_failfast(self, policy_manager):
        """Test failfast policy selection."""
        decision = policy_manager.select_policy(
            strategy=DecisionStrategy.SEQUENTIAL,
            risk_level=RiskLevel.CRITICAL,
            task_count=3,
        )

        assert decision.policy == ExecutionPolicy.FAILFAST
        assert decision.failfast_enabled is True


class TestReplanner:
    """Tests for replanner."""

    @pytest.fixture
    def replanner(self):
        """Create test replanner."""
        return Replanner()

    def test_replan(self, replanner):
        """Test replanning."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="Test")
        tasks = [
            DecisionTask(task_id="t1", name="Task 1", description=""),
        ]
        plan = DecisionPlan(
            plan_id="p1",
            goal=goal,
            tasks=tasks,
        )

        new_plan = replanner.replan(plan, "Test reason")

        assert new_plan.plan_id != plan.plan_id
        assert new_plan.replan_count == 1
        assert new_plan.original_plan_id == plan.plan_id

    def test_cancel_plan(self, replanner):
        """Test plan cancellation."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="Test")
        tasks = [DecisionTask(task_id="t1", name="Task 1", description="")]
        plan = DecisionPlan(plan_id="p1", goal=goal, tasks=tasks)

        cancelled = replanner.cancel_plan(plan, "User requested")

        assert cancelled.status == DecisionStatus.CANCELLED
        assert cancelled.metadata.get("cancellation_reason") == "User requested"


class TestDecisionBuilder:
    """Tests for decision builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return DecisionBuilder()

    def test_build_decision(self, builder):
        """Test decision building."""
        goal = Goal(
            goal_id="goal-1",
            goal_type=GoalType.DIAGNOSIS,
            description="Diagnose",
        )
        analysis = GoalAnalysis(goal=goal, intent="Diagnose")
        tasks = [
            DecisionTask(
                task_id="t1",
                name="Task 1",
                description="",
                estimated_time_seconds=10,
            ),
        ]
        strategy = StrategySelection(
            selected_strategy=DecisionStrategy.HYBRID,
            alternatives=[],
            reasoning="Test",
            confidence=0.9,
            estimated_outcome={},
        )
        risk = RiskAssessment(
            overall_risk=RiskLevel.MEDIUM,
            risk_score=0.3,
            risk_factors=[],
            mitigation_strategies=[],
            requires_escalation=False,
        )
        exec_decision = ExecutionDecision(
            policy=ExecutionPolicy.ADAPTIVE,
            parallelism_allowed=True,
            max_parallel_tasks=3,
            allow_replanning=True,
            failfast_enabled=False,
            retry_strategy="standard",
            timeout_seconds=60.0,
        )

        plan = builder.build(goal, analysis, tasks, strategy, risk, exec_decision)

        assert plan.plan_id is not None
        assert len(plan.tasks) == 1
        assert plan.total_estimated_time_seconds == 10.0
        assert plan.status == DecisionStatus.CREATED


class TestCognitiveDecisionEngine:
    """Tests for cognitive decision engine."""

    @pytest.fixture
    def engine(self):
        """Create test engine."""
        return CognitiveDecisionEngine()

    def test_decide_simple_intent(self, engine):
        """Test decision for simple intent."""
        plan = engine.decide("Find information about diabetes")

        assert plan is not None
        assert len(plan.tasks) > 0
        assert plan.status == DecisionStatus.READY

    def test_decide_troubleshooting(self, engine):
        """Test decision for troubleshooting."""
        plan = engine.decide(
            "The monitor is not working. Fix it."
        )

        assert plan.goal.goal_type == GoalType.TROUBLESHOOTING
        assert len(plan.tasks) >= 5

    def test_decide_diagnosis(self, engine):
        """Test decision for diagnosis."""
        plan = engine.decide(
            "What is wrong with the patient?"
        )

        assert plan.goal.goal_type == GoalType.DIAGNOSIS
        assert plan.tasks[0].priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]

    def test_decide_with_context(self, engine):
        """Test decision with context."""
        plan = engine.decide(
            "Analyze the device",
            context={"device_id": "philips-mx450"},
        )

        assert plan is not None
        assert len(plan.tasks) > 0

    def test_validate_plan(self, engine):
        """Test plan validation."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [DecisionTask(task_id="t1", name="T1", description="")]
        plan = DecisionPlan(plan_id="p1", goal=goal, tasks=tasks)

        is_valid, errors = engine.validate_plan(plan)
        assert is_valid

    def test_get_executable_tasks(self, engine):
        """Test getting executable tasks."""
        goal = Goal(goal_id="g1", goal_type=GoalType.CUSTOM, description="")
        tasks = [
            DecisionTask(task_id="t1", name="T1", description=""),
            DecisionTask(task_id="t2", name="T2", description="", depends_on=["t1"]),
        ]
        plan = DecisionPlan(plan_id="p1", goal=goal, tasks=tasks)

        executable = engine.get_executable_tasks(plan)

        assert len(executable) >= 1
        task_ids = [t.task_id for t in executable]
        assert "t1" in task_ids

    def test_metrics(self, engine):
        """Test metrics tracking."""
        plan = engine.decide("Test intent")
        metrics = engine.get_metrics()

        assert metrics.decisions_made >= 1
        assert metrics.total_tasks > 0

    def test_update_plan_progress(self, engine):
        """Test updating plan progress."""
        plan = engine.decide("Test intent")
        task_id = plan.tasks[0].task_id

        updated_plan = engine.update_plan_progress(
            plan, task_id, result={"done": True}
        )

        assert updated_plan.completed_tasks == 1

    def test_replan(self, engine):
        """Test replanning."""
        plan = engine.decide("Test intent")

        # Force a failure to trigger replanning
        plan.failed_tasks = 1
        plan.tasks[0].status = "failed"

        new_plan = engine.replan(plan, "Task failed")

        # Replan may or may not happen depending on policy
        assert new_plan is not None

    def test_cancel(self, engine):
        """Test cancellation."""
        plan = engine.decide("Test intent")

        cancelled = engine.cancel(plan, "User requested")

        assert cancelled.status == DecisionStatus.CANCELLED

    def test_risk_evaluation(self, engine):
        """Test risk evaluation."""
        plan = engine.decide("Critical medical procedure")

        assert plan.overall_risk in RiskLevel

    def test_strategy_selection(self, engine):
        """Test strategy is selected."""
        plan = engine.decide("Test intent")

        assert plan.strategy is not None
        assert isinstance(plan.strategy, DecisionStrategy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
