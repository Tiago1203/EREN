"""Tests for Planner engine models."""

from __future__ import annotations

import pytest

from core.planner.models import (
    CognitiveEngineId,
    EngineSelection,
    Intention,
    Plan,
    PlanStep,
)


class TestCognitiveEngineId:
    """Tests for the CognitiveEngineId enum."""

    def test_all_engine_ids_are_strings(self) -> None:
        """All enum values should be valid string identifiers."""
        for engine_id in CognitiveEngineId:
            assert isinstance(engine_id.value, str)
            assert len(engine_id.value) > 0

    def test_engine_ids_are_unique(self) -> None:
        """All enum values should be unique."""
        values = [e.value for e in CognitiveEngineId]
        assert len(values) == len(set(values))

    def test_known_engine_ids_exist(self) -> None:
        """All expected engine IDs should exist."""
        expected = {
            "orchestrator",
            "planner",
            "reasoning",
            "memory",
            "knowledge",
            "diagnostic",
            "workflow",
            "tools",
        }
        actual = {e.value for e in CognitiveEngineId}
        assert expected.issubset(actual)


class TestIntention:
    """Tests for the Intention model."""

    def test_default_goal_is_empty(self) -> None:
        """Default goal should be an empty string."""
        intention = Intention()
        assert intention.goal == ""

    def test_goal_can_be_set(self) -> None:
        """Goal should be settable via constructor."""
        intention = Intention(goal="Revisar monitor")
        assert intention.goal == "Revisar monitor"

    def test_intention_is_frozen(self) -> None:
        """Intention should be immutable (frozen)."""
        intention = Intention(goal="Test")
        with pytest.raises(AttributeError):
            intention.goal = "Modified"  # type: ignore

    def test_intention_is_hashable(self) -> None:
        """Intention should be usable as a dict key."""
        intention = Intention(goal="Test")
        cache = {intention: "result"}
        assert cache[intention] == "result"


class TestEngineSelection:
    """Tests for the EngineSelection model."""

    def test_engine_must_be_valid_id(self) -> None:
        """Engine should be a CognitiveEngineId value."""
        selection = EngineSelection(engine=CognitiveEngineId.MEMORY)
        assert selection.engine == CognitiveEngineId.MEMORY

    def test_rationale_is_empty_by_default(self) -> None:
        """Rationale should default to empty string."""
        selection = EngineSelection(engine=CognitiveEngineId.REASONING)
        assert selection.rationale == ""

    def test_rationale_can_be_set(self) -> None:
        """Rationale should be settable via constructor."""
        selection = EngineSelection(
            engine=CognitiveEngineId.KNOWLEDGE,
            rationale="Manual lookup",
        )
        assert selection.rationale == "Manual lookup"

    def test_engine_selection_is_frozen(self) -> None:
        """EngineSelection should be immutable."""
        selection = EngineSelection(engine=CognitiveEngineId.REASONING)
        with pytest.raises(AttributeError):
            selection.engine = CognitiveEngineId.MEMORY  # type: ignore


class TestPlanStep:
    """Tests for the PlanStep model."""

    def test_minimal_plan_step(self) -> None:
        """A minimal plan step should be creatable."""
        step = PlanStep(
            order=0,
            selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
        )
        assert step.order == 0
        assert step.selection.engine == CognitiveEngineId.MEMORY
        assert step.description == ""
        assert step.depends_on == ()

    def test_full_plan_step(self) -> None:
        """A fully populated plan step should be creatable."""
        step = PlanStep(
            order=5,
            selection=EngineSelection(
                engine=CognitiveEngineId.DIAGNOSTIC,
                rationale="Risk assessment",
            ),
            description="Assess clinical risk",
            depends_on=(1, 2, 3),
        )
        assert step.order == 5
        assert step.description == "Assess clinical risk"
        assert step.depends_on == (1, 2, 3)

    def test_plan_step_is_frozen(self) -> None:
        """PlanStep should be immutable."""
        step = PlanStep(
            order=0,
            selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
        )
        with pytest.raises(AttributeError):
            step.order = 1  # type: ignore

    def test_depends_on_defaults_to_empty_tuple(self) -> None:
        """depends_on should default to an empty tuple."""
        step = PlanStep(
            order=0,
            selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
        )
        assert step.depends_on == ()


class TestPlan:
    """Tests for the Plan model."""

    def test_minimal_plan(self) -> None:
        """A plan with empty steps should be creatable."""
        intention = Intention(goal="Test")
        plan = Plan(intention=intention)
        assert plan.intention == intention
        assert plan.steps == ()

    def test_plan_with_steps(self, sample_intention, minimal_plan_step) -> None:
        """A plan with steps should be creatable."""
        plan = Plan(
            intention=sample_intention,
            steps=(minimal_plan_step,),
        )
        assert len(plan.steps) == 1
        assert plan.steps[0].order == 0

    def test_plan_is_frozen(self, sample_intention) -> None:
        """Plan should be immutable."""
        plan = Plan(intention=sample_intention)
        with pytest.raises(AttributeError):
            plan.intention = Intention(goal="Modified")  # type: ignore

    def test_plan_steps_is_tuple(self, sample_intention) -> None:
        """Steps should be stored as an immutable tuple."""
        step1 = PlanStep(
            order=0,
            selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
        )
        step2 = PlanStep(
            order=1,
            selection=EngineSelection(engine=CognitiveEngineId.KNOWLEDGE),
        )
        plan = Plan(intention=sample_intention, steps=(step1, step2))
        assert isinstance(plan.steps, tuple)
        assert len(plan.steps) == 2
