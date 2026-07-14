"""Unit tests for provider selector."""

import pytest
from unittest.mock import MagicMock, patch

from core.providers import (
    BaseProvider,
    ProviderRegistry,
    ProviderSelector,
    ProviderManager,
    ProviderType,
    ProviderState,
    ProviderConfig,
    ProviderHealth,
    SelectionPolicy,
    reset_provider_registry,
)
from core.providers.types import GenerationRequest
from core.providers.exceptions import ProviderUnavailableError


class MockProvider(BaseProvider):
    """Mock provider for testing."""

    _counter = 0

    def __init__(
        self,
        provider_id: str | None = None,
        provider_type: ProviderType = ProviderType.OPENAI,
        priority: int = 100,
    ):
        super().__init__()
        MockProvider._counter += 1
        self._provider_id = provider_id or f"mock-{MockProvider._counter}"
        self._provider_type = provider_type
        self._priority = priority
        self._state = ProviderState.HEALTHY
        self._models = ["gpt-4", "gpt-3.5"]

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def provider_type(self) -> ProviderType:
        return self._provider_type

    @property
    def state(self) -> ProviderState:
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def initialize(self, config: ProviderConfig) -> None:
        pass

    def generate(self, request):
        from core.providers.types import GenerationResponse
        return GenerationResponse(
            content="mock response",
            model=request.model,
            provider_id=self._provider_id,
        )

    def shutdown(self) -> None:
        pass

    def supports_model(self, model: str) -> bool:
        return model in self._models

    def get_available_models(self) -> list[str]:
        return self._models


class TestProviderSelector:
    """Tests for ProviderSelector."""

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return ProviderRegistry()

    @pytest.fixture
    def selector(self, registry):
        """Create test selector."""
        return ProviderSelector(registry, "provider1")

    def _register_provider(self, registry, provider):
        """Register provider with default config."""
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=provider.provider_type,
            enabled=True,
            priority=provider._priority,
        )
        registry.register(provider, config)
        provider._set_state(ProviderState.HEALTHY)

    def test_select_default(self, registry, selector):
        """Test default selection."""
        p1 = MockProvider("provider1", priority=1)
        p2 = MockProvider("provider2", priority=2)
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(SelectionPolicy.DEFAULT)

        assert selected.provider_id == "provider1"

    def test_select_priority(self, registry, selector):
        """Test priority-based selection."""
        p1 = MockProvider("low", priority=100)
        p2 = MockProvider("high", priority=1)
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(SelectionPolicy.PRIORITY)

        assert selected.provider_id == "high"

    def test_select_round_robin(self, registry, selector):
        """Test round-robin selection."""
        p1 = MockProvider("round1")
        p2 = MockProvider("round2")
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        # First selection
        selected1 = selector.select(SelectionPolicy.ROUND_ROBIN)
        # Second selection should be different
        selected2 = selector.select(SelectionPolicy.ROUND_ROBIN)

        assert selected1.provider_id != selected2.provider_id

    def test_select_healthy_first(self, registry, selector):
        """Test healthy-first selection."""
        p1 = MockProvider("healthy")
        p1._state = ProviderState.HEALTHY
        p2 = MockProvider("degraded")
        p2._state = ProviderState.DEGRADED
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(SelectionPolicy.HEALTHY_FIRST)

        assert selected.provider_id == "healthy"

    def test_select_lowest_latency(self, registry, selector):
        """Test lowest-latency selection."""
        # Record some requests to set average latency
        p1 = MockProvider("lat1")
        p1._metrics.record_request(success=True, duration_ms=200)
        p2 = MockProvider("lat2")
        p2._metrics.record_request(success=True, duration_ms=50)
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(SelectionPolicy.LOWEST_LATENCY)

        # Should select the one with lowest latency (lat2 with 50ms)
        assert selected.provider_id == "lat2"

    def test_select_random(self, registry, selector):
        """Test random selection."""
        p1 = MockProvider("random1")
        p2 = MockProvider("random2")
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        # Just verify it returns a provider
        selected = selector.select(SelectionPolicy.RANDOM)
        assert selected.provider_id in ("random1", "random2")

    def test_select_with_model_filter(self, registry, selector):
        """Test selection with model filter."""
        p1 = MockProvider("filter1")
        p1._models = ["gpt-4"]
        p2 = MockProvider("filter2")
        p2._models = ["claude"]
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(model="claude")

        assert selected.provider_id == "filter2"

    def test_select_no_provider_raises(self, registry, selector):
        """Test selection raises when no provider available."""
        with pytest.raises(ProviderUnavailableError):
            selector.select()

    def test_select_exclude_providers(self, registry, selector):
        """Test selection with excluded providers."""
        p1 = MockProvider("excl1")
        p2 = MockProvider("excl2")
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        selected = selector.select(exclude_providers=["excl1"])

        assert selected.provider_id == "excl2"

    def test_get_failover_chain(self, registry, selector):
        """Test getting failover chain."""
        p1 = MockProvider("chain1", priority=100)
        p2 = MockProvider("chain2", priority=50)
        self._register_provider(registry, p1)
        self._register_provider(registry, p2)

        chain = selector.get_failover_chain()

        # Should be sorted by priority (lowest first)
        assert chain[0].provider_id == "chain2"
        assert chain[1].provider_id == "chain1"


class TestProviderManager:
    """Tests for ProviderManager."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_provider_registry()

    @pytest.fixture
    def manager(self):
        """Create test manager with isolated registry."""
        registry = ProviderRegistry()
        return ProviderManager(registry)

    def test_add_provider(self, manager):
        """Test adding a provider."""
        provider = MockProvider("mgr-add")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        assert manager.registry.has("mgr-add")

    def test_remove_provider(self, manager):
        """Test removing a provider."""
        provider = MockProvider("mgr-rem")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        result = manager.remove_provider("mgr-rem")

        assert result is True
        assert not manager.registry.has("mgr-rem")

    def test_generate(self, manager):
        """Test generating with provider."""
        provider = MockProvider("mgr-gen")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        request = GenerationRequest(prompt="Hello")
        # Use DEFAULT policy to avoid failover
        response = manager.generate(request, fallback_enabled=False)

        assert response.success is True
        assert response.provider_id == "mgr-gen"

    def test_generate_with_multiple_providers(self, manager):
        """Test generation with multiple providers."""
        p1 = MockProvider("mgr-multi-1")
        p2 = MockProvider("mgr-multi-2")
        for p in [p1, p2]:
            config = ProviderConfig(
                provider_id=p.provider_id,
                provider_type=ProviderType.OPENAI,
                enabled=True,
            )
            manager.add_provider(p, config)

        request = GenerationRequest(prompt="Hello")
        response = manager.generate(request, policy=SelectionPolicy.PRIORITY)

        assert response.success is True

    def test_health_check(self, manager):
        """Test health check."""
        provider = MockProvider("mgr-hc")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        health = manager.health_check("mgr-hc")

        assert health.healthy is True

    def test_health_check_all(self, manager):
        """Test health check all."""
        p1 = MockProvider("mgr-hca-1")
        p2 = MockProvider("mgr-hca-2")
        for p in [p1, p2]:
            config = ProviderConfig(
                provider_id=p.provider_id,
                provider_type=ProviderType.OPENAI,
                enabled=True,
            )
            manager.add_provider(p, config)

        results = manager.health_check_all()

        assert len(results) == 2
        assert "mgr-hca-1" in results
        assert "mgr-hca-2" in results

    def test_enable_disable(self, manager):
        """Test enabling and disabling."""
        provider = MockProvider("mgr-ed")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        manager.disable("mgr-ed")
        assert manager.registry.get_config("mgr-ed").enabled is False

        manager.enable("mgr-ed")
        assert manager.registry.get_config("mgr-ed").enabled is True

    def test_get_metrics(self, manager):
        """Test getting metrics."""
        provider = MockProvider("mgr-metrics")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        metrics = manager.get_metrics()

        assert "mgr-metrics" in metrics

    def test_get_status(self, manager):
        """Test getting status."""
        provider = MockProvider("mgr-status")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        status = manager.get_status()

        assert status["total_providers"] == 1
        assert status["healthy_providers"] == 1

    def test_event_handlers(self, manager):
        """Test event handlers."""
        events = []

        def handler(data):
            events.append(data)

        manager.on("ProviderSelected", handler)

        provider = MockProvider("mgr-events")
        config = ProviderConfig(
            provider_id=provider.provider_id,
            provider_type=ProviderType.OPENAI,
            enabled=True,
        )
        manager.add_provider(provider, config)

        request = GenerationRequest(prompt="Hello")
        # Use fallback_enabled=False to avoid failover error
        manager.generate(request, fallback_enabled=False)

        assert len(events) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
