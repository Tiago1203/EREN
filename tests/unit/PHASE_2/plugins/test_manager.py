"""Unit tests for plugin manager module."""

import pytest

from core.PHASE_2.plugins import (
    PluginManager,
    PluginDescriptor,
    PluginRegistry,
    PluginLoader,
    PluginState,
    PluginCategory,
    PluginPolicy,
    PluginManifest,
    PluginContext,
    ValidationResult,
)
from core.PHASE_2.plugins.exceptions import (
    PluginException,
    PluginNotFoundError,
    PluginAlreadyRegisteredError,
    PluginActivationError,
)


class TestPluginDescriptor:
    """Tests for PluginDescriptor."""

    def test_creation(self):
        """Test descriptor creation."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
            name="Test Plugin",
        )
        descriptor = PluginDescriptor(manifest=manifest)
        assert descriptor.plugin_id == "test-plugin"
        assert descriptor.version == "1.0.0"
        assert descriptor.state == PluginState.DISCOVERED

    def test_state_transition(self):
        """Test state transitions."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        assert descriptor.transition_to(PluginState.REGISTERED) is True
        assert descriptor.state == PluginState.REGISTERED

    def test_invalid_transition(self):
        """Test invalid state transition."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        # Can't go directly from DISCOVERED to ACTIVE
        assert descriptor.transition_to(PluginState.ACTIVE) is False

    def test_error_handling(self):
        """Test error handling."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        descriptor.set_error("Test error")
        assert descriptor.error == "Test error"
        assert descriptor.last_error is not None

        descriptor.clear_error()
        assert descriptor.error == ""


class TestPluginRegistry:
    """Tests for PluginRegistry."""

    def test_creation(self):
        """Test registry creation."""
        registry = PluginRegistry()
        assert len(registry) == 0

    def test_register(self):
        """Test plugin registration."""
        registry = PluginRegistry()
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        registry.register(descriptor)
        assert len(registry) == 1

    def test_register_duplicate(self):
        """Test registering duplicate plugin."""
        registry = PluginRegistry()
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        registry.register(descriptor)
        with pytest.raises(PluginAlreadyRegisteredError):
            registry.register(descriptor)

    def test_unregister(self):
        """Test unregistering plugin."""
        registry = PluginRegistry()
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        registry.register(descriptor)
        assert registry.unregister("test-plugin") is True
        assert len(registry) == 0

    def test_get(self):
        """Test getting plugin."""
        registry = PluginRegistry()
        manifest = PluginManifest(
            plugin_id="test-plugin",
            version="1.0.0",
        )
        descriptor = PluginDescriptor(manifest=manifest)

        registry.register(descriptor)
        retrieved = registry.get("test-plugin")
        assert retrieved.plugin_id == "test-plugin"

    def test_get_not_found(self):
        """Test getting non-existent plugin."""
        registry = PluginRegistry()
        with pytest.raises(PluginNotFoundError):
            registry.get("nonexistent")


class TestPluginManager:
    """Tests for PluginManager."""

    def test_creation(self):
        """Test manager creation."""
        manager = PluginManager()
        assert manager is not None

    def test_discover(self):
        """Test plugin discovery."""
        manager = PluginManager()
        descriptor = manager.discover({
            "plugin_id": "test-plugin",
            "version": "1.0.0",
            "name": "Test Plugin",
        })

        assert descriptor.plugin_id == "test-plugin"
        assert descriptor.state == PluginState.DISCOVERED

    def test_register(self):
        """Test plugin registration."""
        manager = PluginManager()
        descriptor = manager.discover({
            "plugin_id": "test-plugin",
            "version": "1.0.0",
        })

        manager.register(descriptor)
        assert manager._registry.has("test-plugin")

    def test_activate_requires_dependencies(self):
        """Test that activation checks dependencies."""
        manager = PluginManager()

        # Register plugin with dependency (should fail validation)
        descriptor = manager.discover({
            "plugin_id": "test-plugin",
            "version": "1.0.0",
            "dependencies": ["missing-dependency"],
        })

        # This should fail during registration because dependency is missing
        with pytest.raises(PluginException):
            manager.register(descriptor)

    def test_validate(self):
        """Test plugin validation."""
        manager = PluginManager()
        descriptor = manager.discover({
            "plugin_id": "test-plugin",
            "version": "1.0.0",
        })

        result = manager.validate(descriptor)
        assert result.is_valid is True

    def test_validate_missing_dependency(self):
        """Test validation with missing dependency."""
        manager = PluginManager()
        descriptor = manager.discover({
            "plugin_id": "test-plugin",
            "version": "1.0.0",
            "dependencies": ["missing-dep"],
        })

        result = manager.validate(descriptor)
        assert result.is_valid is False
        assert "missing-dep" in result.errors[0]

    def test_statistics(self):
        """Test statistics."""
        manager = PluginManager()
        stats = manager.get_statistics()

        assert "total_plugins" in stats
        assert "active_plugins" in stats


class TestPluginContext:
    """Tests for PluginContext."""

    def test_creation(self):
        """Test context creation."""
        context = PluginContext(
            plugin_id="test-plugin",
            plugin_version="1.0.0",
        )
        assert context.plugin_id == "test-plugin"

    def test_config_access(self):
        """Test configuration access."""
        context = PluginContext(
            plugin_id="test-plugin",
            plugin_config={"key": "value"},
        )

        assert context.get_config("key") == "value"
        assert context.get_config("missing", "default") == "default"

    def test_metadata(self):
        """Test metadata access."""
        context = PluginContext(plugin_id="test-plugin")

        context.set_metadata("key", "value")
        assert context.get_metadata("key") == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
