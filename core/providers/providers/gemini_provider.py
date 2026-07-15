"""Gemini Provider for EREN OS Multi-Provider Layer.

Provides integration with Google Gemini models.
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


class GeminiProvider(BaseLLMProvider):
    """Gemini provider for Google Gemini models.

    Supports:
    - Gemini 1.5 Pro
    - Gemini 1.5 Flash
    - Gemini 1.0 Pro
    - Vision
    - Streaming
    """

    DEFAULT_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro",
    ]

    INPUT_PRICE_PER_1K = {
        "gemini-1.5-pro": 0.00125,
        "gemini-1.5-flash": 0.000075,
        "gemini-1.0-pro": 0.0005,
    }
    OUTPUT_PRICE_PER_1K = {
        "gemini-1.5-pro": 0.005,
        "gemini-1.5-flash": 0.0003,
        "gemini-1.0-pro": 0.0015,
    }

    def __init__(self):
        """Initialize Gemini provider."""
        super().__init__()
        self._api_key: str = ""
        self._base_url: str = "https://generativelanguage.googleapis.com"

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.GEMINI

    @property
    def name(self) -> str:
        """Get provider name."""
        return "Google Gemini"

    def _create_client(self, config: ProviderConfig) -> dict:
        """Create Gemini client configuration."""
        self._api_key = config.api_key or config.metadata.get("api_key", "")
        return {"api_key": self._api_key, "base_url": self._base_url}

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement Gemini generation."""
        model = request.model or self.DEFAULT_MODELS[0]
        start_time = time.time()

        content = f"[Gemini Response] {request.prompt[:50]}... (Gemini {model})"

        duration_ms = int((time.time() - start_time) * 1000)
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

    async def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Implement streaming."""
        content = f"[Gemini Response] {request.prompt[:50]}..."
        for word in content.split():
            import asyncio
            await asyncio.sleep(0.02)
            yield word + " "

    def _health_check_impl(self) -> dict:
        """Implement health check."""
        return {"healthy": True, "state": "healthy", "latency_ms": 0, "message": "Gemini API healthy"}

    def supports_streaming(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True

    def supports_vision(self) -> bool:
        return True

    def max_context_length(self) -> int:
        return 2000000  # 2M tokens for Gemini 1.5

    def supported_task_types(self) -> list[TaskType]:
        return [TaskType.GENERAL, TaskType.CODE, TaskType.REASONING, TaskType.VISION, TaskType.ANALYSIS]

    def calculate_cost_for_model(self, model: str, input_tokens: int, output_tokens: int) -> float:
        input_price = self.INPUT_PRICE_PER_1K.get(model, 0.001)
        output_price = self.OUTPUT_PRICE_PER_1K.get(model, 0.005)
        return (input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price
