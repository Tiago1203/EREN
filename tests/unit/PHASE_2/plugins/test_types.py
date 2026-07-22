"""Unit tests for plugin types module."""

import pytest
from datetime import datetime, timezone

from core.PHASE_2.plugins.types import (
    PluginState,
    PluginCategory,
    PluginPriority,
    PluginPolicy,
    PluginManifest,
    PluginCapability,
    PluginContext,
    ValidationResult,
)


class TestPluginState:
    """Tests for PluginState."""

    def test_values(self):
        """Test state values."""
        assert PluginState.DISCOVERED.value == "discovered"
        assert PluginState.REGISTERED.value == "registered"
        assert PluginState.LOADED.value == "loaded"
        assert PluginState.ACTIVE.value == "active"
        assert PluginState.FAILED.value == "failed"

    def test_is_active(self):
        """Test is_active check."""
        assert PluginState.is_active(PluginState.ACTIVE) is True
        assert PluginState.is_active(PluginState.PAUSED) is False

    def test_can_transition(self):
        """Test state transitions."""
        assert PluginState.can_transition(
            PluginState.DISCOVERED,
            PluginState.REGISTERED,
        ) is True

        assert PluginState.can_transition(
            PluginState.DISCOVERED,
            PluginState.ACTIVE,
        ) is False


class TestPluginCategory:
    """Tests for PluginCategory."""

    def test_values(self):
        """Test category values."""
        assert PluginCategory.LLM.value == "llm"
        assert PluginCategory.FHIR.value == "fhir"
        assert PluginCategory.CUSTOM.value == "custom"


class TestPluginPriority:
    """Tests for PluginPriority."""

    def test_values(self):
        """Test priority values."""
        assert PluginPriority.CRITICAL.value == 200
        assert PluginPriority.HIGH.value == 150
        assert PluginPriority.NORMAL.value == 100


class TestPluginPolicy:
    """Tests for PluginPolicy."""

    def test_values(self):
        """Test policy values."""
        assert PluginPolicy.STRICT.value == "strict"
        assert PluginPolicy.GRACEFUL.value == "graceful"


class TestPluginManifest:
    """Tests for PluginManifest."""

    def test_creation(self):
        """Test manifest creation."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
            name="Test Plugin",
        )
        assert manifest.plugin_id == "test-plugin"
        assert manifest.version == "1.0.0"

    def test_to_dict(self):
        """Test conversion to dict."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        d = manifest.to_dict()
        assert d["plugin_id"] == "test-plugin"
        assert d["version"] == "1.0.0"


class TestPluginCapability:
    """Tests for PluginCapability."""

    def test_creation(self):
        """Test capability creation."""
        cap = PluginCapability(
            name="reasoning",
            version="1.0.0",
            contracts=["ReasoningContract"],
        )
        assert cap.name == "reasoning"
        assert "ReasoningContract" in cap.contracts

    def test_to_dict(self):
        """Test conversion to dict."""
        cap = PluginCapability(
            name="reasoning",
            version="1.0.0",
        )
        d = cap.to_dict()
        assert d["name"] == "reasoning"


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_valid_result(self):
        """Test valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_result(self):
        """Test invalid result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Missing dependency"],
        )
        assert result.is_valid is False
        assert "Missing dependency" in result.errors

    def test_to_dict(self):
        """Test conversion to dict."""
        result = ValidationResult(is_valid=True)
        d = result.to_dict()
        assert d["is_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
