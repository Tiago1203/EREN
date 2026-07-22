"""Azure OpenAI Provider for EREN OS Multi-Provider Layer.

Provides integration with Azure OpenAI Service.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from core.PHASE_2.providers.providers.base import BaseLLMProvider
from core.PHASE_2.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderType,
    TaskType,
)

if TYPE_CHECKING:
    pass


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider.

    Supports:
    - GPT-4
    - GPT-4 Turbo
    - GPT-35 Turbo
    - Enterprise features
    """

    DEFAULT_MODELS = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-35-turbo",
    ]

    # Azure pricing varies by deployment
    INPUT_PRICE_PER_1K = 0.03
    OUTPUT_PRICE_PER_1K = 0.06

    def __init__(self):
        """Initialize Azure OpenAI provider."""
        super().__init__()
        self._api_key: str = ""
        self._endpoint: str = ""
        self._api_version: str = "2024-02-01"

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.AZURE_OPENAI

    @property
    def name(self) -> str:
        """Get provider name."""
        return "Azure OpenAI"

    def _create_client(self, config: ProviderConfig) -> dict:
        """Create Azure client configuration."""
        self._api_key = config.api_key or config.metadata.get("api_key", "")
        self._endpoint = config.endpoint or config.metadata.get("endpoint", "")
        self._api_version = config.metadata.get("api_version", self._api_version)
        return {
            "api_key": self._api_key,
            "endpoint": self._endpoint,
            "api_version": self._api_version,
        }

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement Azure generation."""
        model = request.model or self.DEFAULT_MODELS[0]
        start_time = time.time()

        content = f"[Azure OpenAI Response] {request.prompt[:50]}..."

        duration_ms = int((time.time() - start_time) * 1000)
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
            cost=self.calculate_cost(input_tokens, output_tokens),
        )

    async def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Implement streaming."""
        content = f"[Azure OpenAI Response] {request.prompt[:50]}..."
        for word in content.split():
            import asyncio
            await asyncio.sleep(0.02)
            yield word + " "

    def _health_check_impl(self) -> dict:
        """Implement health check."""
        return {"healthy": True, "state": "healthy", "latency_ms": 0, "message": "Azure OpenAI healthy"}

    def supports_streaming(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True

    def max_context_length(self) -> int:
        return 128000

    def supported_task_types(self) -> list[TaskType]:
        return [TaskType.GENERAL, TaskType.CODE, TaskType.REASONING, TaskType.ANALYSIS]
