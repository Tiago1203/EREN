"""Mock Provider for EREN OS Multi-Provider Layer.

Provides a mock provider for testing without API calls.
"""

from __future__ import annotations

import random
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from core.providers.providers.base import BaseLLMProvider
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderType,
    TaskType,
)


class MockProvider(BaseLLMProvider):
    """Mock provider for testing.

    Simulates various provider behaviors including:
    - Successful responses
    - Failures and errors
    - Latency simulation
    - Streaming responses
    """

    DEFAULT_MODELS = ["mock-gpt-4", "mock-gpt-3.5", "mock-claude"]
    INPUT_PRICE_PER_1K = 0.01
    OUTPUT_PRICE_PER_1K = 0.03

    def __init__(
        self,
        simulate_latency: float = 0.1,
        simulate_errors: bool = False,
        error_rate: float = 0.1,
        simulate_timeouts: bool = False,
        timeout_rate: float = 0.05,
    ):
        """Initialize mock provider.

        Args:
            simulate_latency: Latency to simulate in seconds.
            simulate_errors: Whether to simulate errors.
            error_rate: Rate of errors when simulating.
            simulate_timeouts: Whether to simulate timeouts.
            timeout_rate: Rate of timeouts.
        """
        super().__init__()
        self._simulate_latency = simulate_latency
        self._simulate_errors = simulate_errors
        self._error_rate = error_rate
        self._simulate_timeouts = simulate_timeouts
        self._timeout_rate = timeout_rate

        self._request_count = 0
        self._error_count = 0
        self._timeout_count = 0

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.MOCK

    @property
    def name(self) -> str:
        """Get provider name."""
        return "Mock Provider"

    def _create_client(self, config: ProviderConfig) -> Any:
        """Create mock client."""
        return {"initialized": True}

    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement mock generation."""
        self._request_count += 1

        # Simulate latency
        if self._simulate_latency > 0:
            time.sleep(self._simulate_latency)

        # Check for timeout
        if self._simulate_timeouts and random.random() < self._timeout_rate:
            self._timeout_count += 1
            return GenerationResponse(
                content="",
                model=request.model or self.DEFAULT_MODELS[0],
                provider_id=self.provider_id,
                success=False,
                error="Request timeout",
            )

        # Check for error
        if self._simulate_errors and random.random() < self._error_rate:
            self._error_count += 1
            return GenerationResponse(
                content="",
                model=request.model or self.DEFAULT_MODELS[0],
                provider_id=self.provider_id,
                success=False,
                error="Simulated API error",
            )

        # Generate mock response
        content = self._generate_mock_content(request)

        input_tokens = len(request.prompt) // 4  # Rough estimate
        output_tokens = len(content) // 4
        cost = self.calculate_cost(input_tokens, output_tokens)

        return GenerationResponse(
            content=content,
            model=request.model or self.DEFAULT_MODELS[0],
            provider_id=self.provider_id,
            success=True,
            finish_reason="stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=int(self._simulate_latency * 1000),
            cost=cost,
            metadata={"mock": True},
        )

    def _generate_mock_content(self, request: GenerationRequest) -> str:
        """Generate mock content based on request.

        Args:
            request: Generation request.

        Returns:
            Mock response content.
        """
        # Simple mock responses based on prompt content
        prompt_lower = request.prompt.lower()

        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! How can I help you today?"
        elif "code" in prompt_lower or "python" in prompt_lower:
            return "```python\ndef example():\n    print('Hello, World!')\n```"
        elif "translate" in prompt_lower:
            return "Translated text would appear here."
        elif "summarize" in prompt_lower:
            return "This is a summary of the provided text."
        elif "question" in prompt_lower or "?" in request.prompt:
            return "That's an interesting question. Based on the information provided, I would say that it depends on various factors."
        else:
            responses = [
                "I understand your request. Let me provide you with some information.",
                "Thank you for your question. Here's what I can tell you.",
                "Based on my analysis, here's the response.",
                "I've processed your request. Here are my thoughts on the matter.",
            ]
            return random.choice(responses)

    async def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Implement mock streaming.

        Args:
            request: Generation request.

        Yields:
            Text chunks.
        """
        content = self._generate_mock_content(request)

        # Simulate streaming by yielding words
        words = content.split()
        for i, word in enumerate(words):
            # Simulate latency between chunks
            await asyncio.sleep(0.05)
            yield word + (" " if i < len(words) - 1 else "")

    def _health_check_impl(self) -> dict:
        """Implement mock health check."""
        return {
            "healthy": True,
            "state": "healthy",
            "latency_ms": int(self._simulate_latency * 1000),
            "message": "Mock provider is healthy",
            "details": {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "timeout_count": self._timeout_count,
            },
        }

    def supports_streaming(self) -> bool:
        """Mock supports streaming."""
        return True

    def supports_embeddings(self) -> bool:
        """Mock supports embeddings."""
        return True

    def supported_task_types(self) -> list[TaskType]:
        """Mock supports all task types."""
        return list(TaskType)

    def max_context_length(self) -> int:
        """Mock max context length."""
        return 128000

    def _embeddings_impl(self, texts: list[str], model: str) -> list[list[float]]:
        """Implement mock embeddings."""
        # Generate random embeddings
        import numpy as np

        embeddings = []
        for text in texts:
            # Create a random embedding vector
            embedding = np.random.randn(1536).tolist()  # OpenAI dimension
            # Normalize
            norm = sum(x**2 for x in embedding) ** 0.5
            embedding = [x / norm for x in embedding]
            embeddings.append(embedding)

        return embeddings

    def get_stats(self) -> dict:
        """Get mock provider statistics."""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "timeout_count": self._timeout_count,
            "error_rate": self._error_rate,
            "latency": self._simulate_latency,
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._request_count = 0
        self._error_count = 0
        self._timeout_count = 0


# Import asyncio at module level for async methods
import asyncio
