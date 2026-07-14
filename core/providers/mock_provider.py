"""Mock providers for EREN OS Multi-Provider Layer (PR-056).

Provides mock implementations for testing without real API calls.
"""

from __future__ import annotations

import time
import random
from dataclasses import dataclass, field
from typing import Any, Generator

from core.providers.provider import BaseProvider
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderHealth,
    ProviderMetrics,
    ProviderState,
    ProviderType,
)
from core.providers.streaming import StreamChunk, GeneratorStreamHandler


# =============================================================================
# Mock Provider Base
# =============================================================================


@dataclass
class MockProviderConfig:
    """Configuration for mock providers."""
    latency_ms: float = 100.0
    error_rate: float = 0.0
    max_tokens: int = 1000
    streaming_chunk_size: int = 10
    streaming_delay_ms: float = 50.0


class MockProvider(BaseProvider):
    """Mock LLM provider for testing."""

    def __init__(
        self,
        provider_id: str = "mock",
        model: str = "mock-model",
        config: MockProviderConfig | None = None,
    ):
        """Initialize mock provider."""
        super().__init__()
        self._provider_id = provider_id
        self._model = model
        self._mock_config = config or MockProviderConfig()

    @property
    def provider_id(self) -> str:
        """Get provider ID."""
        return self._provider_id
    
    @property
    def model(self) -> str:
        """Get model name."""
        return self._model

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.MOCK

    def initialize(self, config: ProviderConfig) -> None:
        """Initialize the provider."""
        self._config = config
        self._state = ProviderState.INITIALIZED

    def shutdown(self) -> None:
        """Shutdown the provider."""
        self._state = ProviderState.DISABLED

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate response (mock)."""
        start = time.perf_counter()
        self._metrics.total_requests += 1

        # Simulate latency
        time.sleep(self._mock_config.latency_ms / 1000)

        # Simulate errors
        if random.random() < self._mock_config.error_rate:
            self._metrics.failed_requests += 1
            raise Exception("Mock provider error")

        # Generate mock response
        prompt = request.prompt or ""
        response_text = self._generate_mock_response(prompt, request.max_tokens or self._mock_config.max_tokens)

        duration_ms = (time.perf_counter() - start) * 1000
        self._metrics.total_output_tokens += len(response_text.split())
        self._metrics.total_duration_ms += int(duration_ms)

        return GenerationResponse(
            content=response_text,
            provider_id=self.provider_id,
            model=self.model,
            output_tokens=len(response_text.split()),
            duration_ms=int(duration_ms),
            finish_reason="stop",
        )

    def _generate_mock_response(self, prompt: str, max_tokens: int) -> str:
        """Generate mock response based on prompt."""
        responses = [
            f"This is a mock response to your query about: {prompt[:50]}...",
            f"Based on the context provided, here is my analysis of: {prompt[:50]}...",
            f"The answer to your question regarding: {prompt[:50]} involves several factors...",
        ]
        return random.choice(responses)[:max_tokens]

    def health_check(self) -> ProviderHealth:
        """Health check (mock)."""
        return ProviderHealth(
            healthy=self._state == ProviderState.HEALTHY,
            state=self._state,
            latency_ms=10,
            message="Mock provider is healthy",
        )


# =============================================================================
# Mock Providers for Different Types
# =============================================================================


class OpenAIMockProvider(MockProvider):
    """Mock OpenAI provider."""

    def __init__(self, model: str = "gpt-4"):
        """Initialize mock provider."""
        super().__init__(provider_id="openai-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OPENAI


class ClaudeMockProvider(MockProvider):
    """Mock Claude provider (Anthropic)."""

    def __init__(self, model: str = "claude-3"):
        """Initialize mock provider."""
        super().__init__(provider_id="claude-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CLAUDE


class GeminiMockProvider(MockProvider):
    """Mock Google Gemini provider."""

    def __init__(self, model: str = "gemini-pro"):
        """Initialize mock provider."""
        super().__init__(provider_id="gemini-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.GEMINI


class OllamaMockProvider(MockProvider):
    """Mock Ollama provider."""

    def __init__(self, model: str = "llama2"):
        """Initialize mock provider."""
        super().__init__(provider_id="ollama-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OLLAMA


class AzureOpenAIMockProvider(MockProvider):
    """Mock Azure OpenAI provider."""

    def __init__(self, model: str = "gpt-4"):
        """Initialize mock provider."""
        super().__init__(provider_id="azure-openai-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.AZURE_OPENAI


class DeepSeekMockProvider(MockProvider):
    """Mock DeepSeek provider."""

    def __init__(self, model: str = "deepseek-chat"):
        """Initialize mock provider."""
        super().__init__(provider_id="deepseek-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CUSTOM


class MistralMockProvider(MockProvider):
    """Mock Mistral provider."""

    def __init__(self, model: str = "mistral-tiny"):
        """Initialize mock provider."""
        super().__init__(provider_id="mistral-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CUSTOM


class OpenRouterMockProvider(MockProvider):
    """Mock OpenRouter provider."""

    def __init__(self, model: str = "anthropic/claude-3"):
        """Initialize mock provider."""
        super().__init__(provider_id="openrouter-mock", model=model)

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CUSTOM


# =============================================================================
# Streaming Mock Provider
# =============================================================================


class StreamingMockProvider(MockProvider):
    """Mock provider with streaming support."""

    def __init__(self, **kwargs):
        """Initialize streaming mock provider."""
        super().__init__(**kwargs)
        self._streaming_delay_ms = 50.0

    async def generate_stream(
        self,
        request: GenerationRequest,
        handler: Any = None,
    ) -> GeneratorStreamHandler:
        """Generate streaming response (mock)."""
        if handler is None:
            handler = GeneratorStreamHandler()

        # Start in background
        def generate():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get prompt
                prompt = request.prompt or ""
                response = self._generate_mock_response(prompt, request.max_tokens or 100)
                
                # Stream chunks
                words = response.split()
                for i in range(0, len(words), self._mock_config.streaming_chunk_size):
                    chunk_words = words[i:i + self._mock_config.streaming_chunk_size]
                    chunk_text = " ".join(chunk_words)
                    
                    time.sleep(self._mock_config.streaming_delay_ms / 1000)
                    
                    chunk = StreamChunk(
                        content=chunk_text + " ",
                        is_final=False,
                    )
                    handler.on_chunk(chunk)
                
                # Final chunk
                handler.on_chunk(StreamChunk(content="", is_final=True))
                handler.on_complete()
                
            except Exception as e:
                handler.on_error(e)
            finally:
                try:
                    loop.close()
                except:
                    pass

        import threading
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()

        return handler


# =============================================================================
# Provider Factory
# =============================================================================


class MockProviderFactory:
    """Factory for creating mock providers."""

    @staticmethod
    def create(
        provider_type: ProviderType,
        model: str | None = None,
        **kwargs,
    ) -> MockProvider:
        """Create mock provider by type."""
        # Use duck typing to match provider types
        providers = {
            "openai": OpenAIMockProvider,
            "claude": ClaudeMockProvider,
            "gemini": GeminiMockProvider,
            "ollama": OllamaMockProvider,
            "azure_openai": AzureOpenAIMockProvider,
            "custom": DeepSeekMockProvider,  # Default for unknown types
            "mock": MockProvider,
        }

        provider_class = providers.get(provider_type.value, MockProvider)
        return provider_class(model=model or "mock-model", **kwargs)

    @staticmethod
    def create_all() -> list[MockProvider]:
        """Create all mock providers."""
        return [
            OpenAIMockProvider(),
            ClaudeMockProvider(),
            GeminiMockProvider(),
            OllamaMockProvider(),
            AzureOpenAIMockProvider(),
            DeepSeekMockProvider(),
            MistralMockProvider(),
            OpenRouterMockProvider(),
        ]
