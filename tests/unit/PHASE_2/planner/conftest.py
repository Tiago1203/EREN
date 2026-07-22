"""Pytest fixtures for Planner engine tests."""

from __future__ import annotations

import pytest

from core.PHASE_2.planner.models import (
    CognitiveEngineId,
    EngineSelection,
    Intention,
    Plan,
    PlanStep,
)
from core.PHASE_2.planner.types import ExecutionContext, TaskPriority


@pytest.fixture
def empty_intention() -> Intention:
    """A minimal empty intention."""
    return Intention(goal="")


@pytest.fixture
def sample_intention() -> Intention:
    """A typical diagnostic intention."""
    return Intention(goal="Revisar monitor Philips MX450 del Hospital Central")


@pytest.fixture
def sample_context() -> ExecutionContext:
    """A populated execution context."""
    return ExecutionContext(
        request_id="req-001",
        session_id="sess-001",
        hospital_id="hospital-central",
        department="cardiologia",
        device_id="device-123",
        device_type="monitor",
        user_id="user-001",
        user_role="biomedico",
        urgency=TaskPriority.HIGH,
    )


@pytest.fixture
def sample_execution_context() -> ExecutionContext:
    """Alias for sample_context for clarity."""
    return ExecutionContext(
        request_id="req-test",
        session_id="sess-test",
        hospital_id="test-hospital",
        device_id="test-device",
        device_type="infusion_pump",
        urgency=TaskPriority.NORMAL,
    )


@pytest.fixture
def minimal_plan_step() -> PlanStep:
    """A minimal plan step with no dependencies."""
    return PlanStep(
        order=0,
        selection=EngineSelection(
            engine=CognitiveEngineId.MEMORY,
            rationale="Test step",
        ),
        description="Retrieve hospital context",
    )


@pytest.fixture
def sample_plan_step_with_dep() -> PlanStep:
    """A plan step that depends on step 0."""
    return PlanStep(
        order=1,
        selection=EngineSelection(
            engine=CognitiveEngineId.KNOWLEDGE,
            rationale="Search technical knowledge",
        ),
        description="Search manuals",
        depends_on=(0,),
    )


@pytest.fixture
def sample_plan(sample_intention, minimal_plan_step, sample_plan_step_with_dep) -> Plan:
    """A plan with two ordered steps."""
    return Plan(
        intention=sample_intention,
        steps=(minimal_plan_step, sample_plan_step_with_dep),
    )
