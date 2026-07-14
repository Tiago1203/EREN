"""Tests for streaming and mock providers (PR-056)."""

import pytest
import asyncio
from core.providers.streaming import (
    StreamChunk,
    StreamMetrics,
    CallbackStreamHandler,
    CollectingStreamHandler,
    MockStreamAdapter,
)
from core.providers.mock_provider import (
    MockProvider,
    MockProviderFactory,
    MockProviderConfig,
    OpenAIMockProvider,
    ClaudeMockProvider,
    StreamingMockProvider,
)
from core.providers.types import GenerationRequest


class TestStreamChunk:
    """Tests for StreamChunk."""

    def test_create_chunk(self):
        """Test creating a chunk."""
        chunk = StreamChunk(content="Hello")
        assert chunk.content == "Hello"
        assert chunk.is_final is False
        assert chunk.chunk_type == "text"

    def test_final_chunk(self):
        """Test creating final chunk."""
        chunk = StreamChunk(content="", is_final=True)
        assert chunk.is_final is True


class TestStreamMetrics:
    """Tests for StreamMetrics."""

    def test_initial_metrics(self):
        """Test initial metrics."""
        metrics = StreamMetrics()
        assert metrics.chunks_received == 0
        assert metrics.total_tokens == 0
        assert metrics.first_token_latency_ms == 0.0


class TestCollectingStreamHandler:
    """Tests for CollectingStreamHandler."""

    def test_collects_chunks(self):
        """Test collecting chunks."""
        handler = CollectingStreamHandler()
        handler.on_chunk(StreamChunk(content="Hello "))
        handler.on_chunk(StreamChunk(content="world"))
        handler.on_complete()
        
        assert handler.get_content() == "Hello world"
        assert len(handler.get_chunks()) == 2

    def test_handles_error(self):
        """Test handling error."""
        handler = CollectingStreamHandler()
        handler.on_error(Exception("test error"))
        
        assert handler.get_error() is not None
        assert str(handler.get_error()) == "test error"


class TestMockProvider:
    """Tests for MockProvider."""

    def test_initialization(self):
        """Test initialization."""
        provider = MockProvider("test", "test-model")
        assert provider.provider_id == "test"
        assert provider.model == "test-model"

    def test_health_check(self):
        """Test health check."""
        provider = MockProvider()
        health = provider.health_check()
        
        # Check that health check returns proper values
        assert health.state is not None
        assert "Mock provider" in health.message

    def test_get_metrics(self):
        """Test getting metrics."""
        provider = MockProvider()
        metrics = provider.metrics  # Use property instead of method
        
        assert metrics.total_requests == 0
        assert metrics.failed_requests == 0


class TestMockProviderFactory:
    """Tests for MockProviderFactory."""

    def test_create_by_type(self):
        """Test creating providers by type."""
        from core.providers.types import ProviderType
        
        openai = MockProviderFactory.create(ProviderType.OPENAI)
        assert isinstance(openai, OpenAIMockProvider)
        
        # Test with claude
        claude = MockProviderFactory.create(ProviderType.CLAUDE)
        assert isinstance(claude, ClaudeMockProvider)

    def test_create_all(self):
        """Test creating all mock providers."""
        providers = MockProviderFactory.create_all()
        
        assert len(providers) == 8
        assert all(isinstance(p, MockProvider) for p in providers)


class TestStreamingMockProvider:
    """Tests for StreamingMockProvider."""

    def test_initialization(self):
        """Test initialization."""
        provider = StreamingMockProvider(
            provider_id="stream",
            model="stream-model",
        )
        assert provider.provider_id == "stream"
        assert provider.model == "stream-model"


class TestMockStreamAdapter:
    """Tests for MockStreamAdapter."""

    def test_adapt(self):
        """Test adapting stream."""
        adapter = MockStreamAdapter()
        chunks = list(adapter.adapt(["Hello", " ", "world"]))
        
        assert len(chunks) == 4  # 3 content + 1 final
        assert chunks[-1].is_final is True


class TestAsyncGeneration:
    """Tests for async generation."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation."""
        provider = MockProvider("test", config=MockProviderConfig(latency_ms=10))
        request = GenerationRequest(prompt="Hello")
        
        response = await provider.generate(request)
        
        assert response.success is True
        assert response.content != ""
        assert response.provider_id == "test"

    @pytest.mark.asyncio
    async def test_generate_with_error_rate(self):
        """Test generation with error rate."""
        provider = MockProvider(
            "test",
            config=MockProviderConfig(error_rate=1.0),
        )
        request = GenerationRequest(prompt="Hello")
        
        with pytest.raises(Exception):
            await provider.generate(request)
