"""Unit tests for EREN Embedding Provider Layer."""

import pytest

from core.embeddings import (
    # Types
    EmbeddingProvider,
    EmbeddingPolicy,
    Embedding,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingModelInfo,
    ProviderHealth,
    # Provider
    BaseEmbeddingProvider,
    OpenAIEmbeddingProvider,
    OllamaEmbeddingProvider,
    # Registry
    EmbeddingRegistry,
    get_embedding_registry,
    reset_embedding_registry,
    # Selector
    EmbeddingSelector,
    # Manager
    EmbeddingManager,
    get_embedding_manager,
    reset_embedding_manager,
    # Exceptions
    EmbeddingError,
    ProviderNotFoundError,
    RegistryError,
)


class TestEmbeddingTypes:
    """Tests for embedding types."""

    def test_embedding_provider_values(self):
        """Test provider values."""
        assert EmbeddingProvider.OPENAI.value == "openai"
        assert EmbeddingProvider.GEMINI.value == "gemini"
        assert EmbeddingProvider.OLLAMA.value == "ollama"

    def test_embedding_policy_values(self):
        """Test policy values."""
        assert EmbeddingPolicy.DEFAULT.value == "default"
        assert EmbeddingPolicy.CHEAPEST.value == "cheapest"
        assert EmbeddingPolicy.FASTEST.value == "fastest"

    def test_embedding_creation(self):
        """Test embedding creation."""
        embedding = Embedding(
            vector=[0.1, 0.2, 0.3],
            model="test-model",
            provider=EmbeddingProvider.OPENAI,
        )
        assert len(embedding.vector) == 3
        assert embedding.dimensions == 3
        assert embedding.size == 3

    def test_embedding_request_creation(self):
        """Test request creation."""
        request = EmbeddingRequest(
            texts=["Hello", "World"],
            model="test-model",
            provider=EmbeddingProvider.OPENAI,
        )
        assert len(request.texts) == 2
        assert request.normalize is True

    def test_embedding_response_creation(self):
        """Test response creation."""
        embedding = Embedding(
            vector=[0.1, 0.2],
            model="test",
            provider=EmbeddingProvider.OPENAI,
        )
        response = EmbeddingResponse(
            embeddings=[embedding],
            model="test",
            provider=EmbeddingProvider.OPENAI,
            tokens_used=10,
            cost_usd=0.001,
        )
        assert response.count == 1
        assert response.dimensions == 2

    def test_provider_health_creation(self):
        """Test health creation."""
        health = ProviderHealth(
            provider=EmbeddingProvider.OPENAI,
            is_healthy=True,
            latency_ms=100,
        )
        assert health.is_healthy is True
        assert health.error_count == 0

    def test_model_info_creation(self):
        """Test model info creation."""
        info = EmbeddingModelInfo(
            name="test-model",
            provider=EmbeddingProvider.OPENAI,
            dimensions=1536,
            max_tokens=8191,
            cost_per_1k_tokens=0.0001,
        )
        assert info.name == "test-model"
        assert info.dimensions == 1536
        assert info.is_local is False


class TestEmbeddingProviders:
    """Tests for embedding providers."""

    def test_openai_provider_properties(self):
        """Test OpenAI provider properties."""
        provider = OpenAIEmbeddingProvider()
        assert provider.provider_name == EmbeddingProvider.OPENAI
        assert "text-embedding-3-small" in provider.supported_models

    def test_ollama_provider_properties(self):
        """Test Ollama provider properties."""
        provider = OllamaEmbeddingProvider()
        assert provider.provider_name == EmbeddingProvider.OLLAMA
        assert "nomic-embed-text" in provider.supported_models

    @pytest.mark.asyncio
    async def test_openai_generate(self):
        """Test OpenAI embedding generation."""
        provider = OpenAIEmbeddingProvider()
        response = await provider.generate(
            texts=["Hello world"],
            model="text-embedding-3-small",
        )
        assert response.success is True
        assert len(response.embeddings) == 1
        assert response.embeddings[0].dimensions == 1536

    @pytest.mark.asyncio
    async def test_ollama_generate(self):
        """Test Ollama embedding generation."""
        provider = OllamaEmbeddingProvider()
        response = await provider.generate(
            texts=["Hello world"],
            model="nomic-embed-text",
        )
        assert response.success is True
        assert len(response.embeddings) == 1

    @pytest.mark.asyncio
    async def test_openai_health_check(self):
        """Test OpenAI health check."""
        provider = OpenAIEmbeddingProvider()
        health = await provider.health_check()
        assert health.provider == EmbeddingProvider.OPENAI

    def test_provider_get_model_info(self):
        """Test getting model info."""
        provider = OpenAIEmbeddingProvider()
        info = provider.get_model_info("text-embedding-3-small")
        assert info.name == "text-embedding-3-small"
        assert info.dimensions == 1536


class TestEmbeddingRegistry:
    """Tests for embedding registry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_embedding_registry()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return EmbeddingRegistry()

    def test_register_provider(self, registry):
        """Test registering a provider."""
        provider = OpenAIEmbeddingProvider()
        registry.register(provider)
        assert registry.has_provider(EmbeddingProvider.OPENAI)

    def test_unregister_provider(self, registry):
        """Test unregistering a provider."""
        provider = OpenAIEmbeddingProvider()
        registry.register(provider)
        result = registry.unregister(EmbeddingProvider.OPENAI)
        assert result is True
        assert not registry.has_provider(EmbeddingProvider.OPENAI)

    def test_get_provider(self, registry):
        """Test getting a provider."""
        provider = OpenAIEmbeddingProvider()
        registry.register(provider)
        retrieved = registry.get(EmbeddingProvider.OPENAI)
        assert retrieved.provider_name == EmbeddingProvider.OPENAI

    def test_get_provider_not_found(self, registry):
        """Test getting non-existent provider."""
        with pytest.raises(ProviderNotFoundError):
            registry.get(EmbeddingProvider.OPENAI)

    def test_set_default(self, registry):
        """Test setting default provider."""
        provider1 = OpenAIEmbeddingProvider()
        provider2 = OllamaEmbeddingProvider()
        registry.register(provider1)
        registry.register(provider2, set_default=True)
        assert registry.get_default().provider_name == EmbeddingProvider.OLLAMA

    def test_list_providers(self, registry):
        """Test listing providers."""
        provider1 = OpenAIEmbeddingProvider()
        provider2 = OllamaEmbeddingProvider()
        registry.register(provider1)
        registry.register(provider2)
        providers = registry.list_providers()
        assert len(providers) == 2

    def test_get_status(self, registry):
        """Test getting status."""
        provider = OpenAIEmbeddingProvider()
        registry.register(provider)
        status = registry.get_status()
        assert status["total_providers"] == 1
        assert status["default_provider"] == "openai"


class TestEmbeddingSelector:
    """Tests for embedding selector."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_embedding_registry()

    def test_selector_creation(self):
        """Test selector creation."""
        selector = EmbeddingSelector()
        assert selector.policy == EmbeddingPolicy.DEFAULT

    def test_selector_policy_change(self):
        """Test changing policy."""
        selector = EmbeddingSelector()
        selector.policy = EmbeddingPolicy.CHEAPEST
        assert selector.policy == EmbeddingPolicy.CHEAPEST

    def test_select_default_provider(self):
        """Test selecting default provider."""
        registry = get_embedding_registry()
        registry.register(OpenAIEmbeddingProvider(), set_default=True)
        selector = EmbeddingSelector(registry)
        provider = selector.select()
        assert provider.provider_name == EmbeddingProvider.OPENAI

    def test_select_with_policy(self):
        """Test selecting with policy."""
        registry = get_embedding_registry()
        registry.register(OpenAIEmbeddingProvider(), set_default=True)
        registry.register(OllamaEmbeddingProvider())
        selector = EmbeddingSelector(registry)
        provider = selector.select(policy=EmbeddingPolicy.ROUND_ROBIN)
        assert provider is not None


class TestEmbeddingManager:
    """Tests for embedding manager."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset manager before each test."""
        reset_embedding_manager()
        reset_embedding_registry()

    @pytest.fixture
    def manager(self):
        """Create test manager."""
        return EmbeddingManager()

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None
        assert manager.registry is not None
        assert manager.selector is not None

    def test_manager_register_provider(self, manager):
        """Test registering provider through manager."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        assert manager.registry.has_provider(EmbeddingProvider.OPENAI)

    @pytest.mark.asyncio
    async def test_embed(self, manager):
        """Test embedding generation."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        response = await manager.embed(
            texts=["Hello world"],
            model="text-embedding-3-small",
        )
        assert response.success is True
        assert len(response.embeddings) == 1

    @pytest.mark.asyncio
    async def test_embed_single(self, manager):
        """Test single embedding generation."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        embedding = await manager.embed_single(
            text="Hello world",
            model="text-embedding-3-small",
        )
        assert embedding.dimensions == 1536

    def test_estimate_cost(self, manager):
        """Test cost estimation."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        cost = manager.estimate_cost(
            texts=["Hello world"],
            model="text-embedding-3-small",
        )
        assert cost >= 0

    def test_get_model_info(self, manager):
        """Test getting model info."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        info = manager.get_model_info("text-embedding-3-small")
        assert info.name == "text-embedding-3-small"

    def test_list_models(self, manager):
        """Test listing models."""
        provider = OpenAIEmbeddingProvider()
        manager.registry.register(provider)
        models = manager.list_models()
        assert len(models) > 0

    def test_get_metrics(self, manager):
        """Test getting metrics."""
        metrics = manager.get_metrics()
        assert "total_requests" in metrics
        assert "successful_requests" in metrics

    def test_get_status(self, manager):
        """Test getting status."""
        status = manager.get_status()
        assert "registry" in status
        assert "selector_policy" in status
        assert "metrics" in status


class TestEmbeddingExceptions:
    """Tests for embedding exceptions."""

    def test_embedding_error(self):
        """Test base error."""
        error = EmbeddingError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_provider_not_found_error(self):
        """Test provider not found error."""
        error = ProviderNotFoundError("openai")
        assert "openai" in str(error)

    def test_registry_error(self):
        """Test registry error."""
        error = RegistryError("get", "Provider not found")
        assert "get" in str(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
