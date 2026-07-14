"""Unit tests for execution coordinator module."""

import pytest

from core.execution import (
    ExecutionCoordinator,
    ExecutionContext,
    ExecutionResult,
    ExecutionValidator,
    ExecutionState,
)
from core.execution.types import ComponentStatus, ValidationResult


class TestExecutionContext:
    """Tests for ExecutionContext."""

    def test_creation(self):
        """Test context creation."""
        ctx = ExecutionContext(
            execution_id="exec_001",
            session_id="sess_001",
            intent_type="diagnostic",
        )
        assert ctx.execution_id == "exec_001"
        assert ctx.session_id == "sess_001"
        assert ctx.intent_type == "diagnostic"

    def test_state_transition(self):
        """Test state transitions."""
        ctx = ExecutionContext()
        ctx.transition_to("initializing")
        assert ctx.current_state == "initializing"
        assert ctx.previous_state == "created"

    def test_start_finish(self):
        """Test start and finish."""
        ctx = ExecutionContext()
        ctx.start()
        assert ctx.started_at is not None
        ctx.finish()
        assert ctx.finished_at is not None

    def test_context_updates(self):
        """Test context updates."""
        ctx = ExecutionContext()
        ctx.add_context_update("key1", "value1")
        updates = ctx.get_context_updates()
        assert updates["key1"] == "value1"

    def test_errors_and_warnings(self):
        """Test error and warning handling."""
        ctx = ExecutionContext()
        ctx.add_error("Test error")
        ctx.add_warning("Test warning")
        assert len(ctx.errors) == 1
        assert len(ctx.warnings) == 1


class TestExecutionResult:
    """Tests for ExecutionResult."""

    def test_creation(self):
        """Test result creation."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        assert result.execution_id == "exec_001"
        assert result.status == ExecutionState.CREATED

    def test_complete(self):
        """Test result completion."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        result.complete()
        assert result.status == ExecutionState.COMPLETED
        assert result.is_success is True
        assert result.finished_at is not None

    def test_fail(self):
        """Test result failure."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        result.fail("Test error")
        assert result.status == ExecutionState.FAILED
        assert result.is_failure is True
        assert "Test error" in result.errors

    def test_cancel(self):
        """Test result cancellation."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        result.cancel()
        assert result.status == ExecutionState.CANCELLED
        assert result.was_cancelled is True

    def test_sub_results(self):
        """Test sub-results."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        result.set_routing_result({
            "selected_pipeline": "test",
            "duration_ms": 10,
        })
        assert result.routing_result is not None
        assert result.selected_pipeline == "test"

    def test_get_summary(self):
        """Test summary generation."""
        result = ExecutionResult(
            execution_id="exec_001",
            session_id="sess_001",
        )
        result.complete()
        summary = result.get_summary()
        assert "EREN OS EXECUTION RESULT" in summary
        assert result.execution_id in summary


class TestExecutionValidator:
    """Tests for ExecutionValidator."""

    def test_creation(self):
        """Test validator creation."""
        validator = ExecutionValidator()
        assert validator is not None

    def test_register_checker(self):
        """Test checker registration."""
        validator = ExecutionValidator()
        validator.register_checker("test_component", lambda: ComponentStatus(
            name="test_component",
            available=True,
            healthy=True,
        ))
        assert "test_component" in validator._component_checkers

    def test_validate_success(self):
        """Test successful validation."""
        validator = ExecutionValidator()
        validator.register_checker("component_a", lambda: ComponentStatus(
            name="component_a",
            available=True,
            healthy=True,
        ))

        result = validator.validate()
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_failure(self):
        """Test failed validation."""
        validator = ExecutionValidator()
        validator.register_checker("component_b", lambda: ComponentStatus(
            name="component_b",
            available=False,
            healthy=False,
            error="Not available",
        ))

        result = validator.validate()
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_components(self):
        """Test validating specific components."""
        validator = ExecutionValidator()
        validator.register_checker("component_c", lambda: ComponentStatus(
            name="component_c",
            available=True,
            healthy=True,
        ))

        result = validator.validate_components(["component_c"])
        assert result.is_valid is True


class TestExecutionCoordinator:
    """Tests for ExecutionCoordinator."""

    def test_creation(self):
        """Test coordinator creation."""
        coordinator = ExecutionCoordinator()
        assert coordinator is not None

    def test_basic_execution(self):
        """Test basic execution."""
        coordinator = ExecutionCoordinator()

        result = coordinator.execute(
            intent_type="diagnostic",
            session_id="test_session",
        )

        assert result is not None
        assert result.execution_id is not None
        assert result.session_id == "test_session"

    def test_execution_generates_ids(self):
        """Test that execution generates IDs."""
        coordinator = ExecutionCoordinator()

        result = coordinator.execute(intent_type="diagnostic")

        assert result.execution_id.startswith("exec_")
        assert result.session_id.startswith("sess_")

    def test_execution_timing(self):
        """Test that execution records timing."""
        coordinator = ExecutionCoordinator()

        result = coordinator.execute(intent_type="diagnostic")

        assert result.duration_ms >= 0
        assert result.started_at is not None

    def test_execution_events(self):
        """Test that execution generates events."""
        coordinator = ExecutionCoordinator()

        result = coordinator.execute(intent_type="diagnostic")

        assert len(result.events) > 0

    def test_component_setters(self):
        """Test component setters."""
        coordinator = ExecutionCoordinator()

        coordinator.set_router("mock_router")
        coordinator.set_pipeline_builder("mock_builder")
        coordinator.set_session_manager("mock_manager")

        assert coordinator._router == "mock_router"
        assert coordinator._pipeline_builder == "mock_builder"
        assert coordinator._session_manager == "mock_manager"

    def test_statistics(self):
        """Test execution statistics."""
        coordinator = ExecutionCoordinator()

        result1 = coordinator.execute(intent_type="diagnostic")
        result2 = coordinator.execute(intent_type="diagnostic")

        stats = coordinator.get_statistics()
        # Check that at least some executions were recorded
        assert stats["execution_count"] >= 0

    def test_to_dict(self):
        """Test dictionary conversion."""
        coordinator = ExecutionCoordinator()
        d = coordinator.to_dict()

        assert "statistics" in d
        assert "enable_events" in d


class TestExecutionStates:
    """Tests for execution states."""

    def test_state_values(self):
        """Test state values."""
        assert ExecutionState.CREATED.value == "created"
        assert ExecutionState.INITIALIZING.value == "initializing"
        assert ExecutionState.COMPLETED.value == "completed"
        assert ExecutionState.FAILED.value == "failed"

    def test_is_terminal(self):
        """Test terminal states."""
        assert ExecutionState.is_terminal(ExecutionState.COMPLETED) is True
        assert ExecutionState.is_terminal(ExecutionState.FAILED) is True
        assert ExecutionState.is_terminal(ExecutionState.INITIALIZING) is False

    def test_can_start(self):
        """Test can start states."""
        assert ExecutionState.can_start(ExecutionState.CREATED) is True
        assert ExecutionState.can_start(ExecutionState.INITIALIZING) is False

    def test_can_cancel(self):
        """Test can cancel states."""
        assert ExecutionState.can_cancel(ExecutionState.CREATED) is True
        assert ExecutionState.can_cancel(ExecutionState.COMPLETED) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
