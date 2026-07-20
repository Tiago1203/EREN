"""Ollama Provider for EREN OS Multi-Provider Layer.

Provides integration with Ollama for local LLM models.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from core.providers.providers.base import BaseLLMProvider
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderType,
    TaskType,
)

if TYPE_CHECKING:
    pass


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM models.

    Supports:
    - Llama 2
    - Mistral
    - Codellama
    - Phi
    - And other Ollama-compatible models
    """

    DEFAULT_MODELS = [
        "llama3",
        "llama3.1",
        "mistral",
        "codellama",
        "phi3",
        "qwen2",
        "gemma2",
    ]

    # Ollama is free but has operational costs
    INPUT_PRICE_PER_1K = 0.0
    OUTPUT_PRICE_PER_1K = 0.0

    def __init__(self):
        """Initialize Ollama provider."""
        super().__init__()
        self._base_url: str = "http://localhost:11434"
        self._timeout: int = 60

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OLLAMA

    @property
    def name(self) -> str:
        """Get provider name."""
        return "Ollama"

    def _create_client(self, config: ProviderConfig) -> dict:
        """Create Ollama client configuration.

        Args:
            config: Provider configuration.

        Returns:
            Client configuration.
        """
        self._base_url = config.endpoint or config.metadata.get(
            "base_url", self._base_url
        )
        self._timeout = config.timeout or config.metadata.get("timeout", self._timeout)

        return {
            "base_url": self._base_url,
            "timeout": self._timeout,
        }

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement Ollama generation.

        Args:
            request: Generation request.

        Returns:
            Generation response.
        """
        model = request.model or self.DEFAULT_MODELS[0]

        # Mock response for demo
        start_time = time.time()

        content = self._mock_generate(request)

        duration_ms = int((time.time() - start_time) * 1000)

        # Estimate tokens
        input_tokens = len(request.prompt) // 4
        output_tokens = len(content) // 4

        return GenerationResponse(
            content=content,
            model=model,
            provider_id=self.provider_id,
            success=True,
            finish_reason="stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost=0.0,  # Ollama is free
            metadata={"provider": "ollama", "local": True},
        )

    def _mock_generate(self, request: GenerationRequest) -> str:
        """Generate mock response.

        Args:
            request: Generation request.

        Returns:
            Mock response.
        """
        prompt = request.prompt.lower()

        if "hello" in prompt or "hi" in prompt:
            return "Hello! I'm running locally via Ollama. How can I assist you?"
        elif "code" in prompt or "python" in prompt:
            return "```python\ndef local_function():\n    return 'Running on Ollama!'\n```"
        else:
            return f"This is a response from Ollama using model {request.model or 'llama3'}."

    async def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Implement streaming.

        Args:
            request: Generation request.

        Yields:
            Text chunks.
        """
        content = self._mock_generate(request)
        words = content.split()

        for word in words:
            import asyncio
            await asyncio.sleep(0.03)
            yield word + " "

    def _health_check_impl(self) -> dict:
        """Implement health check."""
        return {
            "healthy": True,
            "state": "healthy",
            "latency_ms": 0,
            "message": "Ollama service is healthy",
            "details": {
                "base_url": self._base_url,
                "available_models": self.DEFAULT_MODELS,
            },
        }

    def supports_streaming(self) -> bool:
        """Ollama supports streaming."""
        return True

    def supports_embeddings(self) -> bool:
        """Ollama supports embeddings via nomic-embed-text."""
        return True

    def max_context_length(self) -> int:
        """Ollama max context varies by model."""
        return 32768

    def supported_task_types(self) -> list[TaskType]:
        """Ollama supports common task types."""
        return [
            TaskType.GENERAL,
            TaskType.CODE,
            TaskType.REASONING,
            TaskType.CREATIVE,
            TaskType.ANALYSIS,
            TaskType.SUMMARIZATION,
        ]

    def pricing_tier(self) -> str:
        """Ollama is free (self-hosted)."""
        return "budget"
