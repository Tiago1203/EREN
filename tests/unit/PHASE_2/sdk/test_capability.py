"""Unit tests for SDK capability module."""

import pytest

from core.PHASE_2.sdk import (
    BaseCapability,
    CapabilityBuilder,
    CapabilityContext,
    CapabilityResult,
    CapabilityState,
    CapabilityCategory,
    CapabilityMetadata,
    CapabilityHealth,
    ValidationResult,
    get_capability_registry,
    reset_capability_registry,
)


class TestCapabilityContext:
    """Tests for CapabilityContext."""

    def test_creation(self):
        """Test context creation."""
        ctx = CapabilityContext(
            capability_id="test-cap",
            execution_id="exec-001",
        )
        assert ctx.capability_id == "test-cap"
        assert ctx.execution_id == "exec-001"

    def test_get_with_default(self):
        """Test getting context value with default."""
        ctx = CapabilityContext()
        result = ctx.get("missing", "default")
        assert result == "default"

    def test_to_dict(self):
        """Test conversion to dict."""
        ctx = CapabilityContext(capability_id="test-cap")
        d = ctx.to_dict()
        assert d["capability_id"] == "test-cap"


class TestCapabilityResult:
    """Tests for CapabilityResult."""

    def test_success(self):
        """Test success result."""
        result = CapabilityResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data["key"] == "value"

    def test_failure(self):
        """Test failure result."""
        result = CapabilityResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"

    def test_to_dict(self):
        """Test conversion to dict."""
        result = CapabilityResult(success=True)
        d = result.to_dict()
        assert d["success"] is True


class TestCapabilityHealth:
    """Tests for CapabilityHealth."""

    def test_healthy(self):
        """Test healthy status."""
        health = CapabilityHealth(healthy=True, message="OK")
        assert health.healthy is True
        assert health.message == "OK"

    def test_to_dict(self):
        """Test conversion to dict."""
        health = CapabilityHealth(healthy=True)
        d = health.to_dict()
        assert d["healthy"] is True


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_valid(self):
        """Test valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid(self):
        """Test invalid result."""
        result = ValidationResult(is_valid=False, errors=["Missing field"])
        assert result.is_valid is False
        assert "Missing field" in result.errors

    def test_to_dict(self):
        """Test conversion to dict."""
        result = ValidationResult(is_valid=True)
        d = result.to_dict()
        assert d["is_valid"] is True


class TestCapabilityState:
    """Tests for CapabilityState."""

    def test_values(self):
        """Test state values."""
        assert CapabilityState.CREATED.value == "created"
        assert CapabilityState.READY.value == "ready"
        assert CapabilityState.FAILED.value == "failed"

    def test_is_terminal(self):
        """Test terminal states."""
        assert CapabilityState.is_terminal(CapabilityState.COMPLETED) is True
        assert CapabilityState.is_terminal(CapabilityState.DISPOSED) is True
        assert CapabilityState.is_terminal(CapabilityState.READY) is False

    def test_is_active(self):
        """Test active states."""
        assert CapabilityState.is_active(CapabilityState.READY) is True
        assert CapabilityState.is_active(CapabilityState.EXECUTING) is True
        assert CapabilityState.is_active(CapabilityState.COMPLETED) is False

    def test_can_transition(self):
        """Test valid transitions."""
        assert CapabilityState.can_transition(
            CapabilityState.CREATED,
            CapabilityState.VALIDATED,
        ) is True

        assert CapabilityState.can_transition(
            CapabilityState.CREATED,
            CapabilityState.READY,
        ) is False


class TestCapabilityCategory:
    """Tests for CapabilityCategory."""

    def test_values(self):
        """Test category values."""
        assert CapabilityCategory.REASONING.value == "reasoning"
        assert CapabilityCategory.LLM.value == "llm"
        assert CapabilityCategory.MEMORY.value == "memory"


class TestCapabilityMetadata:
    """Tests for CapabilityMetadata."""

    def test_creation(self):
        """Test metadata creation."""
        metadata = CapabilityMetadata(
            name="TestCapability",
            version="1.0.0",
            category=CapabilityCategory.REASONING,
        )
        assert metadata.name == "TestCapability"
        assert metadata.version == "1.0.0"

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = CapabilityMetadata(
            name="TestCapability",
            version="1.0.0",
            category=CapabilityCategory.LLM,
        )
        d = metadata.to_dict()
        assert d["name"] == "TestCapability"
        assert d["category"] == "llm"


class TestCapabilityBuilder:
    """Tests for CapabilityBuilder."""

    def test_basic_build(self):
        """Test basic builder usage."""
        metadata = (
            CapabilityBuilder()
            .named("TestCapability")
            .version("1.0.0")
            .category(CapabilityCategory.REASONING)
            .build()
        )
        assert metadata.name == "TestCapability"
        assert metadata.version == "1.0.0"
        assert metadata.category == CapabilityCategory.REASONING

    def test_with_contracts(self):
        """Test builder with contracts."""
        metadata = (
            CapabilityBuilder()
            .named("TestCapability")
            .version("1.0.0")
            .implements("ContractA", "ContractB")
            .build()
        )
        assert "ContractA" in metadata.contracts
        assert "ContractB" in metadata.contracts

    def test_with_dependencies(self):
        """Test builder with dependencies."""
        metadata = (
            CapabilityBuilder()
            .named("TestCapability")
            .version("1.0.0")
            .depends_on("DepA", "DepB")
            .build()
        )
        assert "DepA" in metadata.dependencies
        assert "DepB" in metadata.dependencies

    def test_with_configuration(self):
        """Test builder with configuration."""
        metadata = (
            CapabilityBuilder()
            .named("TestCapability")
            .version("1.0.0")
            .configure(api_key="secret", model="gpt-4")
            .build()
        )
        assert metadata.configuration["api_key"] == "secret"
        assert metadata.configuration["model"] == "gpt-4"

    def test_to_dict(self):
        """Test builder to_dict."""
        d = (
            CapabilityBuilder()
            .named("TestCapability")
            .version("1.0.0")
            .to_dict()
        )
        assert d["name"] == "TestCapability"


class TestBaseCapability:
    """Tests for BaseCapability."""

    def test_state_initial(self):
        """Test initial state."""
        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        assert cap.state == CapabilityState.CREATED

    def test_metadata(self):
        """Test metadata."""
        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        metadata = cap.metadata()
        assert metadata.name == "TestCapability"
        assert metadata.category == CapabilityCategory.CUSTOM

    def test_health(self):
        """Test health check."""
        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        health = cap.health()
        assert health.healthy is False  # Not initialized

    def test_configure(self):
        """Test configuration."""
        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        cap.configure({"key": "value"})
        assert cap.get_config("key") == "value"

    def test_to_dict(self):
        """Test to_dict."""
        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        d = cap.to_dict()
        assert "capability_id" in d
        assert "state" in d


class TestCapabilityRegistry:
    """Tests for CapabilityRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_capability_registry()

    def test_register(self):
        """Test registering a capability."""
        registry = get_capability_registry()

        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        registry.register("test-cap", cap)

        assert registry.has("test-cap")
        assert registry.count() == 1

    def test_unregister(self):
        """Test unregistering a capability."""
        registry = get_capability_registry()

        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        registry.register("test-cap", cap)
        registry.unregister("test-cap")

        assert not registry.has("test-cap")

    def test_get(self):
        """Test getting a capability."""
        registry = get_capability_registry()

        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap = TestCapability()
        registry.register("test-cap", cap)

        retrieved = registry.get("test-cap")
        assert retrieved is cap

    def test_list_all(self):
        """Test listing all capabilities."""
        registry = get_capability_registry()

        class TestCapability(BaseCapability):
            def initialize(self, ctx): pass
            def execute(self, ctx): return CapabilityResult(success=True)
            def shutdown(self): pass

        cap1 = TestCapability()
        cap2 = TestCapability()
        registry.register("cap-a", cap1)
        registry.register("cap-b", cap2)

        caps = registry.list_all()
        assert len(caps) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
