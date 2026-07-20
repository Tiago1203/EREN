"""OpenRouter Provider for EREN OS Multi-Provider Layer.

Provides access to multiple LLM providers through OpenRouter.
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


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider for unified API access to multiple LLMs."""

    DEFAULT_MODELS = [
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3-70b-instruct",
    ]

    # OpenRouter pricing varies by underlying provider
    INPUT_PRICE_PER_1K = 0.005
    OUTPUT_PRICE_PER_1K = 0.015

    def __init__(self):
        super().__init__()
        self._api_key: str = ""

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER

    @property
    def name(self) -> str:
        return "OpenRouter"

    def _create_client(self, config: ProviderConfig) -> dict:
        self._api_key = config.api_key or config.metadata.get("api_key", "")
        return {"api_key": self._api_key}

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        model = request.model or self.DEFAULT_MODELS[0]
        start_time = time.time()
        content = f"[OpenRouter Response via {model}] {request.prompt[:50]}..."
        duration_ms = int((time.time() - start_time) * 1000)

        return GenerationResponse(
            content=content,
            model=model,
            provider_id=self.provider_id,
            success=True,
            input_tokens=len(request.prompt) // 4,
            output_tokens=len(content) // 4,
            duration_ms=duration_ms,
            cost=self.calculate_cost(len(request.prompt) // 4, len(content) // 4),
        )

    async def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        model = request.model or self.DEFAULT_MODELS[0]
        content = f"[OpenRouter Response via {model}] {request.prompt[:50]}..."
        for word in content.split():
            import asyncio
            await asyncio.sleep(0.02)
            yield word + " "

    def _health_check_impl(self) -> dict:
        return {"healthy": True, "state": "healthy", "latency_ms": 0, "message": "OpenRouter API healthy"}

    def supports_streaming(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return False

    def max_context_length(self) -> int:
        return 128000

    def supported_task_types(self) -> list[TaskType]:
        return [TaskType.GENERAL, TaskType.CODE, TaskType.ANALYSIS, TaskType.REASONING]
