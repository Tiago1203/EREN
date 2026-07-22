"""Unit tests for execution types module."""

import pytest
from datetime import datetime, timezone

from core.PHASE_2.execution.types import (
    ExecutionState,
    ExecutionPolicy,
    ExecutionMetadata,
    ComponentStatus,
    ValidationResult,
)


class TestExecutionState:
    """Tests for ExecutionState."""

    def test_values(self):
        """Test state values."""
        assert ExecutionState.CREATED.value == "created"
        assert ExecutionState.INITIALIZING.value == "initializing"
        assert ExecutionState.COMPLETED.value == "completed"
        assert ExecutionState.FAILED.value == "failed"

    def test_is_terminal(self):
        """Test terminal state check."""
        assert ExecutionState.is_terminal(ExecutionState.COMPLETED) is True
        assert ExecutionState.is_terminal(ExecutionState.FAILED) is True
        assert ExecutionState.is_terminal(ExecutionState.INITIALIZING) is False

    def test_can_start(self):
        """Test can start check."""
        assert ExecutionState.can_start(ExecutionState.CREATED) is True
        assert ExecutionState.can_start(ExecutionState.COMPLETED) is False

    def test_can_cancel(self):
        """Test can cancel check."""
        assert ExecutionState.can_cancel(ExecutionState.CREATED) is True
        assert ExecutionState.can_cancel(ExecutionState.COMPLETED) is False


class TestExecutionPolicy:
    """Tests for ExecutionPolicy."""

    def test_values(self):
        """Test policy values."""
        assert ExecutionPolicy.STRICT.value == "strict"
        assert ExecutionPolicy.GRACEFUL.value == "graceful"
        assert ExecutionPolicy.RESILIENT.value == "resilient"


class TestExecutionMetadata:
    """Tests for ExecutionMetadata."""

    def test_creation(self):
        """Test metadata creation."""
        metadata = ExecutionMetadata(
            execution_id="exec_001",
            intent_type="diagnostic",
            intent_data={"query": "test"},
        )
        assert metadata.execution_id == "exec_001"
        assert metadata.intent_type == "diagnostic"

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = ExecutionMetadata(
            execution_id="exec_001",
            intent_type="diagnostic",
            intent_data={},
        )
        d = metadata.to_dict()
        assert d["execution_id"] == "exec_001"
        assert d["intent_type"] == "diagnostic"


class TestComponentStatus:
    """Tests for ComponentStatus."""

    def test_creation(self):
        """Test status creation."""
        status = ComponentStatus(
            name="router",
            available=True,
            healthy=True,
        )
        assert status.name == "router"
        assert status.available is True
        assert status.healthy is True

    def test_to_dict(self):
        """Test conversion to dict."""
        status = ComponentStatus(
            name="router",
            available=True,
            healthy=True,
        )
        d = status.to_dict()
        assert d["name"] == "router"
        assert d["available"] is True


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_creation_valid(self):
        """Test valid result creation."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_creation_invalid(self):
        """Test invalid result creation."""
        result = ValidationResult(
            is_valid=False,
            errors=["Component not available"],
        )
        assert result.is_valid is False
        assert "Component not available" in result.errors

    def test_to_dict(self):
        """Test conversion to dict."""
        result = ValidationResult(is_valid=True)
        d = result.to_dict()
        assert d["is_valid"] is True
        assert "errors" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
