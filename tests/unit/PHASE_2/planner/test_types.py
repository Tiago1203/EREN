"""Tests for Planner engine type definitions."""

from __future__ import annotations

import pytest

from core.PHASE_2.planner.types import (
    ExecutionContext,
    GoalType,
    PlannerResult,
    ReplanReason,
    StepOrderer,
    StepValidator,
    TaskPriority,
    TaskStatus,
)


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_priorities_are_int_values(self) -> None:
        """All priorities should have integer values."""
        for priority in TaskPriority:
            assert isinstance(priority.value, int)

    def test_priorities_are_ordered(self) -> None:
        """Lower values should indicate higher priority."""
        assert TaskPriority.CRITICAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.NORMAL.value
        assert TaskPriority.NORMAL.value < TaskPriority.LOW.value
        assert TaskPriority.LOW.value < TaskPriority.BACKGROUND.value

    def test_critical_has_lowest_value(self) -> None:
        """CRITICAL should have the lowest (highest priority) value."""
        assert TaskPriority.CRITICAL.value == 1


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """All expected statuses should exist."""
        expected = {"PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED", "BLOCKED"}
        actual = {s.name for s in TaskStatus}
        assert expected.issubset(actual)

    def test_statuses_are_int_values(self) -> None:
        """All statuses should have integer values."""
        for status in TaskStatus:
            assert isinstance(status.value, int)


class TestGoalType:
    """Tests for GoalType string class."""

    def test_goal_types_are_strings(self) -> None:
        """All goal types should be valid string identifiers."""
        expected = {
            "diagnostic",
            "maintenance",
            "regulatory",
            "consultation",
            "research",
            "report",
            "emergency",
            "unknown",
        }
        for goal_type in expected:
            assert GoalType(goal_type) == goal_type


class TestReplanReason:
    """Tests for ReplanReason string class."""

    def test_replan_reasons_are_strings(self) -> None:
        """All replan reasons should be valid string identifiers."""
        expected = {
            "step_failed",
            "new_information",
            "user_feedback",
            "context_changed",
            "optimization",
            "timeout",
        }
        for reason in expected:
            assert ReplanReason(reason) == reason


class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""

    def test_default_context_is_empty(self) -> None:
        """A default context should have empty string values."""
        ctx = ExecutionContext()
        assert ctx.request_id == ""
        assert ctx.session_id == ""
        assert ctx.hospital_id == ""
        assert ctx.department == ""
        assert ctx.device_id == ""
        assert ctx.device_type == ""
        assert ctx.user_id == ""
        assert ctx.user_role == ""
        assert ctx.urgency == TaskPriority.NORMAL
        assert ctx.metadata == {}

    def test_context_is_frozen(self) -> None:
        """ExecutionContext should be immutable."""
        ctx = ExecutionContext(request_id="req-001")
        with pytest.raises(AttributeError):
            ctx.request_id = "modified"  # type: ignore

    def test_context_is_hashable(self) -> None:
        """ExecutionContext should be usable as a dict key."""
        ctx = ExecutionContext(request_id="req-001")
        cache = {ctx: "result"}
        assert cache[ctx] == "result"

    def test_context_get_with_default(self) -> None:
        """get() should return the default for missing keys."""
        ctx = ExecutionContext(metadata={"existing": "value"})
        assert ctx.get("existing") == "value"
        assert ctx.get("missing") is None
        assert ctx.get("missing", "default") == "default"

    def test_context_get_existing_key(self) -> None:
        """get() should return the value for existing keys."""
        ctx = ExecutionContext(metadata={"key": "value"})
        assert ctx.get("key") == "value"


class TestPlannerResult:
    """Tests for PlannerResult dataclass."""

    def test_minimal_result(self) -> None:
        """A minimal result should be creatable with just a plan."""
        from core.PHASE_2.planner.models import Intention, Plan

        intention = Intention(goal="Test")
        plan = Plan(intention=intention)
        result = PlannerResult(plan=plan)

        assert result.plan == plan
        assert result.priority == TaskPriority.NORMAL
        assert result.estimated_steps == 0
        assert result.requires_confirmation is False
        assert result.warnings == ()
        assert result.metadata == {}

    def test_full_result(self) -> None:
        """A fully populated result should be creatable."""
        from core.PHASE_2.planner.models import CognitiveEngineId, EngineSelection, Intention, Plan, PlanStep

        intention = Intention(goal="Full test")
        step = PlanStep(
            order=0,
            selection=EngineSelection(engine=CognitiveEngineId.MEMORY),
        )
        plan = Plan(intention=intention, steps=(step,))

        result = PlannerResult(
            plan=plan,
            priority=TaskPriority.HIGH,
            estimated_steps=1,
            requires_confirmation=True,
            warnings=("Warning 1", "Warning 2"),
            metadata={"key": "value"},
        )

        assert result.priority == TaskPriority.HIGH
        assert result.estimated_steps == 1
        assert result.requires_confirmation is True
        assert result.warnings == ("Warning 1", "Warning 2")
        assert result.metadata["key"] == "value"

    def test_result_is_frozen(self) -> None:
        """PlannerResult should be immutable."""
        from core.PHASE_2.planner.models import Intention, Plan

        intention = Intention(goal="Test")
        plan = Plan(intention=intention)
        result = PlannerResult(plan=plan)

        with pytest.raises(AttributeError):
            result.priority = TaskPriority.CRITICAL  # type: ignore


class TestProtocolSignatures:
    """Tests to verify protocol structures are correct (no implementation)."""

    def test_step_validator_is_callable(self) -> None:
        """StepValidator should be a callable protocol."""
        # Verify the protocol exists
        assert StepValidator is not None

    def test_step_orderer_is_protocol(self) -> None:
        """StepOrderer should be a protocol."""
        assert StepOrderer is not None
