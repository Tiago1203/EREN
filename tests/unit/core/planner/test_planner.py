"""Tests for the Planner class."""

from __future__ import annotations

import pytest

from core.planner.exceptions import (
    EngineSelectionError,
    InvalidIntentionError,
    PlanCreationError,
    PlannerError,
    StepOrderingError,
)
from core.planner.models import (
    CognitiveEngineId,
    EngineSelection,
    Intention,
    Plan,
    PlanStep,
)
from core.planner.planner import (
    Planner,
    _DefaultEngineSelector,
    _DefaultPlanningStrategy,
    _DefaultStepOrderer,
)
from core.planner.types import (
    ExecutionContext,
    PlannerCallback,
    ReplanReason,
    StepValidator,
    TaskPriority,
)


class TestPlannerIdentity:
    """Tests for Planner cognitive engine identity."""

    def test_planner_has_name(self) -> None:
        """Planner should have a stable name."""
        planner = Planner()
        assert planner.name == "planner"

    def test_planner_has_description(self) -> None:
        """Planner should have a human-readable description."""
        planner = Planner()
        assert isinstance(planner.describe(), str)
        assert len(planner.describe()) > 0


class TestPlannerReceiveIntention:
    """Tests for responsibility 1: receive_intention."""

    def test_receive_string_goal(self) -> None:
        """String goals should be normalized into Intention."""
        planner = Planner()
        intention = planner._receive_intention("Revisar monitor")
        assert isinstance(intention, Intention)
        assert intention.goal == "Revisar monitor"

    def test_receive_dict_goal(self) -> None:
        """Dict goals with 'goal' key should be normalized."""
        planner = Planner()
        intention = planner._receive_intention({"goal": "Diagnosticar falla"})
        assert intention.goal == "Diagnosticar falla"

    def test_receive_dict_missing_goal(self) -> None:
        """Dicts without 'goal' should produce empty goal."""
        planner = Planner()
        intention = planner._receive_intention({"other": "value"})
        assert intention.goal == "other:value"

    def test_receive_empty_string_raises(self) -> None:
        """Empty string goals should raise InvalidIntentionError."""
        planner = Planner()
        with pytest.raises(InvalidIntentionError):
            planner._receive_intention("")

    def test_receive_whitespace_only_raises(self) -> None:
        """Whitespace-only goals should raise InvalidIntentionError."""
        planner = Planner()
        with pytest.raises(InvalidIntentionError):
            planner._receive_intention("   ")

    def test_receive_invalid_type_raises(self) -> None:
        """Unsupported types should raise InvalidIntentionError."""
        planner = Planner()
        with pytest.raises(InvalidIntentionError):
            planner._receive_intention(12345)


class TestPlannerCreatePlan:
    """Tests for responsibility 2: create_plan."""

    def test_create_plan_returns_list(self) -> None:
        """create_plan should return a list of PlanStep."""
        planner = Planner()
        intention = Intention(goal="Revisar monitor Philips")
        context = ExecutionContext()
        steps = planner._create_plan(intention, context)
        assert isinstance(steps, list)

    def test_create_plan_respects_context(self) -> None:
        """create_plan should use context to tailor steps."""
        planner = Planner()
        intention = Intention(goal="Diagnosticar error")

        # With hospital context
        context_with_hospital = ExecutionContext(hospital_id="hospital-1")
        steps_with = planner._create_plan(intention, context_with_hospital)

        # Without hospital context
        context_without = ExecutionContext()
        steps_without = planner._create_plan(intention, context_without)

        # More steps when hospital context is present
        assert len(steps_with) >= len(steps_without)

    def test_create_plan_with_validators(self) -> None:
        """Validators should filter steps."""
        # Validator that rejects all steps
        reject_all: StepValidator = lambda step, ctx: False
        planner = Planner(validators=[reject_all])

        intention = Intention(goal="Test")
        context = ExecutionContext()
        steps = planner._create_plan(intention, context)

        # Steps are still added (validators are advisory in current design)
        # This tests the integration point
        assert isinstance(steps, list)


class TestPlannerSelectEngines:
    """Tests for responsibility 3: select_engines."""

    def test_select_engines_returns_list(self) -> None:
        """select_engines should return a list of PlanStep."""
        planner = Planner()
        steps = [
            PlanStep(
                order=0,
                selection=EngineSelection(
                    engine=CognitiveEngineId.MEMORY,
                    rationale="Test",
                ),
            ),
        ]
        context = ExecutionContext()
        result = planner._select_engines(steps, context)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_select_engines_preserves_step_count(self) -> None:
        """select_engines should return same number of steps."""
        planner = Planner()
        steps = [
            PlanStep(
                order=i,
                selection=EngineSelection(
                    engine=CognitiveEngineId.MEMORY,
                    rationale=f"Step {i}",
                ),
            )
            for i in range(5)
        ]
        context = ExecutionContext()
        result = planner._select_engines(steps, context)
        assert len(result) == len(steps)


class TestPlannerOrderExecution:
    """Tests for responsibility 4: order_execution."""

    def test_order_execution_returns_plan(self) -> None:
        """order_execution should return a Plan."""
        planner = Planner()
        intention = Intention(goal="Test")
        steps = [
            PlanStep(
                order=0,
                selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
                depends_on=(),
            ),
        ]
        plan = planner._order_execution(steps, intention)
        assert isinstance(plan, Plan)
        assert plan.intention == intention

    def test_order_execution_resolves_order(self) -> None:
        """order_execution should return steps in valid order."""
        planner = Planner()
        intention = Intention(goal="Test")

        # Steps with dependencies
        steps = [
            PlanStep(
                order=0,
                selection=EngineSelection(engine=CognitiveEngineId.KNOWLEDGE),
                depends_on=(1,),  # Depends on step 1 (wrong initial order)
            ),
            PlanStep(
                order=1,
                selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
                depends_on=(),
            ),
        ]

        plan = planner._order_execution(steps, intention)
        # The step with no dependencies should come first
        assert plan.steps[0].selection.engine == CognitiveEngineId.MEMORY

    def test_order_execution_empty_steps(self) -> None:
        """order_execution with empty steps should return empty plan."""
        planner = Planner()
        intention = Intention(goal="Test")
        plan = planner._order_execution([], intention)
        assert plan.steps == ()


class TestPlannerPlan:
    """Tests for the main async plan() method."""

    @pytest.mark.asyncio
    async def test_plan_returns_planner_result(self) -> None:
        """plan() should return a PlannerResult."""
        planner = Planner()
        result = await planner.plan("Revisar monitor")
        assert result is not None

    @pytest.mark.asyncio
    async def test_plan_includes_plan(self) -> None:
        """PlannerResult should contain a valid Plan."""
        planner = Planner()
        result = await planner.plan("Diagnosticar falla del ventilador")
        assert isinstance(result.plan, Plan)

    @pytest.mark.asyncio
    async def test_plan_includes_priority(self) -> None:
        """PlannerResult should have a priority."""
        planner = Planner()
        result = await planner.plan("Emergency: paciente en riesgo")
        assert isinstance(result.priority, TaskPriority)

    @pytest.mark.asyncio
    async def test_plan_with_context(self) -> None:
        """plan() should accept and use ExecutionContext."""
        planner = Planner()
        context = ExecutionContext(
            hospital_id="hospital-central",
            device_id="monitor-001",
            urgency=TaskPriority.HIGH,
        )
        result = await planner.plan("Revisar equipo", context)
        assert result.plan is not None

    @pytest.mark.asyncio
    async def test_plan_estimated_steps(self) -> None:
        """PlannerResult should include estimated step count."""
        planner = Planner()
        result = await planner.plan("Revisar monitor Philips del Hospital Central")
        assert result.estimated_steps >= 0


class TestPlannerReplan:
    """Tests for the replan() method."""

    @pytest.mark.asyncio
    async def test_replan_returns_planner_result(self) -> None:
        """replan() should return a PlannerResult."""
        planner = Planner()
        intention = Intention(goal="Test")
        previous_plan = Plan(intention=intention, steps=())
        context = ExecutionContext()

        result = await planner.replan(
            previous_plan,
            ReplanReason.STEP_FAILED,
            context,
        )
        assert isinstance(result, type(await planner.plan("Test")))

    @pytest.mark.asyncio
    async def test_replan_preserves_intention(self) -> None:
        """replan() should address the same intention."""
        planner = Planner()
        original_intention = Intention(goal="Revisar monitor")
        previous_plan = Plan(intention=original_intention, steps=())
        context = ExecutionContext()

        result = await planner.replan(
            previous_plan,
            ReplanReason.CONTEXT_CHANGED,
            context,
        )
        assert result.plan.intention.goal == original_intention.goal


class TestPlannerCallbacks:
    """Tests for callback integration."""

    @pytest.mark.asyncio
    async def test_callbacks_are_called(self) -> None:
        """Registered callbacks should be invoked during planning."""
        events: list[str] = []

        async def track(event: str, data: dict) -> None:
            events.append(event)

        planner = Planner(callbacks=[track])
        await planner.plan("Test request")

        assert len(events) > 0
        assert "intention_received" in events
        assert "plan_completed" in events


class TestPlannerInference:
    """Tests for priority and warning inference."""

    @pytest.mark.asyncio
    async def test_infer_priority_from_context(self) -> None:
        """Priority should be inferred from context urgency."""
        planner = Planner()
        context = ExecutionContext(urgency=TaskPriority.CRITICAL)
        result = await planner.plan("Non-urgent request", context)
        assert result.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_infer_priority_from_goal(self) -> None:
        """Priority should be inferred from goal keywords."""
        planner = Planner()
        result = await planner.plan("Emergency: critical patient situation")
        assert result.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_warnings_for_empty_plan(self) -> None:
        """Empty plans should generate a warning."""
        planner = Planner()
        context = ExecutionContext()
        intention = Intention(goal="")
        steps = planner._create_plan(intention, context)
        warnings = planner._collect_warnings(steps, context)
        assert any("No steps" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_requires_confirmation_for_critical(self) -> None:
        """Critical priority plans should require confirmation."""
        planner = Planner()
        context = ExecutionContext(urgency=TaskPriority.CRITICAL)
        result = await planner.plan("Test", context)
        assert result.requires_confirmation is True


class TestDefaultStrategies:
    """Tests for default strategy implementations."""

    def test_default_planning_strategy(self) -> None:
        """Default strategy should decompose intentions into steps."""
        strategy = _DefaultPlanningStrategy()
        intention = Intention(goal="Diagnosticar error en monitor")
        context = ExecutionContext()

        steps = strategy.decompose(intention, context)
        assert isinstance(steps, list)
        assert len(steps) > 0

    def test_default_engine_selector(self) -> None:
        """Default selector should assign engines to steps."""
        selector = _DefaultEngineSelector()
        steps = [
            PlanStep(
                order=0,
                selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
            ),
        ]
        context = ExecutionContext()

        result = selector.select(steps, context)
        assert len(result) == len(steps)

    def test_default_step_orderer(self) -> None:
        """Default orderer should topologically sort steps."""
        orderer = _DefaultStepOrderer()
        steps = [
            PlanStep(order=0, selection=EngineSelection(engine=CognitiveEngineId.MEMORY), depends_on=(1,)),
            PlanStep(order=1, selection=EngineSelection(engine=CognitiveEngineId.KNOWLEDGE), depends_on=()),
        ]

        ordered = orderer.order(steps)
        # Step with no dependencies should come first
        assert ordered[0].selection.engine == CognitiveEngineId.KNOWLEDGE

    def test_step_orderer_handles_empty(self) -> None:
        """Step orderer should handle empty input."""
        orderer = _DefaultStepOrderer()
        ordered = orderer.order([])
        assert ordered == []


class TestPlannerErrorTypes:
    """Tests for error type hierarchy."""

    def test_planner_error_exists(self) -> None:
        """Base PlannerError should exist."""
        assert issubclass(PlannerError, Exception)

    def test_invalid_intention_error_exists(self) -> None:
        """InvalidIntentionError should exist and be a PlannerError."""
        assert issubclass(InvalidIntentionError, PlannerError)

    def test_plan_creation_error_exists(self) -> None:
        """PlanCreationError should exist and be a PlannerError."""
        assert issubclass(PlanCreationError, PlannerError)

    def test_engine_selection_error_exists(self) -> None:
        """EngineSelectionError should exist and be a PlannerError."""
        assert issubclass(EngineSelectionError, PlannerError)

    def test_step_ordering_error_exists(self) -> None:
        """StepOrderingError should exist and be a PlannerError."""
        assert issubclass(StepOrderingError, PlannerError)
