"""Unit tests for provider registry."""

import pytest
from unittest.mock import MagicMock

from core.providers import (
    BaseProvider,
    ProviderRegistry,
    ProviderType,
    ProviderState,
    ProviderConfig,
    get_provider_registry,
    reset_provider_registry,
)
from core.providers.exceptions import (
    ProviderNotFoundError,
    ProviderAlreadyRegisteredError,
)


class MockProvider(BaseProvider):
    """Mock provider for testing."""

    def __init__(self, provider_id: str = "mock", provider_type: ProviderType = ProviderType.OPENAI):
        super().__init__()
        self._provider_id = provider_id
        self._provider_type = provider_type
        self._initialized = False

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def provider_type(self) -> ProviderType:
        return self._provider_type

    def initialize(self, config: ProviderConfig) -> None:
        self._initialized = True
        self._set_state(ProviderState.INITIALIZED)

    def generate(self, request):
        from core.providers.types import GenerationResponse
        return GenerationResponse(
            content="mock response",
            model=request.model,
            provider_id=self._provider_id,
        )

    def shutdown(self) -> None:
        self._set_state(ProviderState.UNREGISTERED)


class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_provider_registry()

    def test_register(self):
        """Test registering a provider."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")

        registry.register(provider)

        assert registry.has("test-provider")
        assert registry.count() == 1

    def test_register_with_config(self):
        """Test registering with configuration."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        config = ProviderConfig(
            provider_id="test-provider",
            provider_type=ProviderType.OPENAI,
        )

        registry.register(provider, config)

        assert provider._initialized is True
        assert registry.get_config("test-provider") is not None

    def test_register_duplicate_raises(self):
        """Test duplicate registration raises error."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")

        registry.register(provider)

        with pytest.raises(ProviderAlreadyRegisteredError):
            registry.register(provider)

    def test_unregister(self):
        """Test unregistering a provider."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        registry.register(provider)

        result = registry.unregister("test-provider")

        assert result is True
        assert not registry.has("test-provider")

    def test_get(self):
        """Test getting a provider."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        registry.register(provider)

        retrieved = registry.get("test-provider")

        assert retrieved is provider

    def test_get_not_found_raises(self):
        """Test getting non-existent provider raises error."""
        registry = get_provider_registry()

        with pytest.raises(ProviderNotFoundError):
            registry.get("non-existent")

    def test_get_or_none(self):
        """Test getting provider or None."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        registry.register(provider)

        assert registry.get_or_none("test-provider") is provider
        assert registry.get_or_none("non-existent") is None

    def test_list_all(self):
        """Test listing all providers."""
        registry = get_provider_registry()
        registry.register(MockProvider("provider1"))
        registry.register(MockProvider("provider2"))

        providers = registry.list_all()

        assert len(providers) == 2

    def test_list_by_type(self):
        """Test listing providers by type."""
        registry = get_provider_registry()
        registry.register(MockProvider("openai", ProviderType.OPENAI))
        registry.register(MockProvider("claude", ProviderType.CLAUDE))
        registry.register(MockProvider("openai2", ProviderType.OPENAI))

        providers = registry.list_by_type(ProviderType.OPENAI)

        assert len(providers) == 2

    def test_list_healthy(self):
        """Test listing healthy providers."""
        registry = get_provider_registry()
        p1 = MockProvider("healthy")
        p1._set_state(ProviderState.HEALTHY)
        p2 = MockProvider("unhealthy")
        p2._set_state(ProviderState.UNHEALTHY)

        registry.register(p1)
        registry.register(p2)

        healthy = registry.list_healthy()

        assert len(healthy) == 1
        assert healthy[0].provider_id == "healthy"

    def test_enable_disable(self):
        """Test enabling and disabling providers."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        config = ProviderConfig(
            provider_id="test-provider",
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )

        registry.register(provider, config)

        registry.disable("test-provider")
        assert registry.get_config("test-provider").enabled is False

        registry.enable("test-provider")
        assert registry.get_config("test-provider").enabled is True

    def test_clear(self):
        """Test clearing all providers."""
        registry = get_provider_registry()
        registry.register(MockProvider("p1"))
        registry.register(MockProvider("p2"))

        registry.clear()

        assert registry.count() == 0

    def test_len(self):
        """Test length."""
        registry = get_provider_registry()
        assert len(registry) == 0

        registry.register(MockProvider("p1"))
        assert len(registry) == 1

    def test_contains(self):
        """Test contains."""
        registry = get_provider_registry()
        provider = MockProvider("test-provider")
        registry.register(provider)

        assert "test-provider" in registry
        assert "non-existent" not in registry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
