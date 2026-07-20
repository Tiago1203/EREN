"""OpenAI Provider for EREN OS Multi-Provider Layer.

Provides integration with OpenAI's GPT models.
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


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for GPT models.

    Supports:
    - GPT-4
    - GPT-4 Turbo
    - GPT-3.5 Turbo
    - Embeddings
    - Streaming
    - Function calling
    """

    DEFAULT_MODELS = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    # Pricing (as of 2024)
    INPUT_PRICE_PER_1K = {
        "gpt-4o": 0.005,
        "gpt-4-turbo": 0.01,
        "gpt-4": 0.03,
        "gpt-3.5-turbo": 0.0005,
    }
    OUTPUT_PRICE_PER_1K = {
        "gpt-4o": 0.015,
        "gpt-4-turbo": 0.03,
        "gpt-4": 0.06,
        "gpt-3.5-turbo": 0.0015,
    }

    def __init__(self):
        """Initialize OpenAI provider."""
        super().__init__()
        self._api_key: str = ""
        self._base_url: str = "https://api.openai.com/v1"
        self._organization: str | None = None

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OPENAI

    @property
    def name(self) -> str:
        """Get provider name."""
        return "OpenAI"

    def _create_client(self, config: ProviderConfig) -> dict:
        """Create OpenAI client configuration.

        Args:
            config: Provider configuration.

        Returns:
            Client configuration dict.
        """
        self._api_key = config.api_key or config.metadata.get("api_key", "")
        self._base_url = config.endpoint or config.metadata.get("base_url", self._base_url)
        self._organization = config.metadata.get("organization")

        return {
            "api_key": self._api_key,
            "base_url": self._base_url,
            "organization": self._organization,
        }

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement OpenAI generation.

        Args:
            request: Generation request.

        Returns:
            Generation response.
        """
        # For demo purposes, return a mock response
        # In production, this would call the OpenAI API
        model = request.model or self.DEFAULT_MODELS[0]

        # Simulate API call
        start_time = time.time()

        # Mock response
        content = self._mock_generate(request)

        duration_ms = int((time.time() - start_time) * 1000)

        # Estimate tokens
        input_tokens = len(request.prompt) // 4
        output_tokens = len(content) // 4
        cost = self.calculate_cost_for_model(model, input_tokens, output_tokens)

        return GenerationResponse(
            content=content,
            model=model,
            provider_id=self.provider_id,
            success=True,
            finish_reason="stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost=cost,
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
            return "Hello! I'm here to help. What would you like to know?"
        elif "code" in prompt or "python" in prompt:
            return "Here's some code:\n```python\ndef hello():\n    print('Hello!')\n```"
        else:
            return f"This is a response from OpenAI using model {request.model or 'gpt-4o'}."

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
            await asyncio.sleep(0.02)
            yield word + " "

    def _health_check_impl(self) -> dict:
        """Implement health check."""
        return {
            "healthy": True,
            "state": "healthy",
            "latency_ms": 0,
            "message": "OpenAI API is healthy",
        }

    def supports_streaming(self) -> bool:
        """OpenAI supports streaming."""
        return True

    def supports_embeddings(self) -> bool:
        """OpenAI supports embeddings."""
        return True

    def supports_function_calling(self) -> bool:
        """OpenAI supports function calling."""
        return True

    def supports_json_mode(self) -> bool:
        """OpenAI supports JSON mode."""
        return True

    def max_context_length(self) -> int:
        """OpenAI max context."""
        return 128000

    def supported_task_types(self) -> list[TaskType]:
        """OpenAI supports all common task types."""
        return [
            TaskType.GENERAL,
            TaskType.CODE,
            TaskType.REASONING,
            TaskType.CREATIVE,
            TaskType.ANALYSIS,
            TaskType.SUMMARIZATION,
            TaskType.TRANSLATION,
            TaskType.CLASSIFICATION,
            TaskType.EXTRACTION,
            TaskType.QUESTION_ANSWERING,
            TaskType.FUNCTION_CALLING,
        ]

    def calculate_cost_for_model(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for a specific model.

        Args:
            model: Model name.
            input_tokens: Input tokens.
            output_tokens: Output tokens.

        Returns:
            Cost in USD.
        """
        input_price = self.INPUT_PRICE_PER_1K.get(model, 0.01)
        output_price = self.OUTPUT_PRICE_PER_1K.get(model, 0.03)

        input_cost = (input_tokens / 1000) * input_price
        output_cost = (output_tokens / 1000) * output_price

        return input_cost + output_cost
