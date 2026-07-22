"""Base LLM Provider for EREN OS Multi-Provider Layer.

Provides the foundation for all LLM provider implementations.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from core.PHASE_2.providers.provider import BaseProvider
from core.PHASE_2.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderCapabilities,
    ProviderConfig,
    ProviderMetadata,
    ProviderType,
    TaskType,
)

if TYPE_CHECKING:
    pass


class BaseLLMProvider(BaseProvider):
    """Abstract base class for LLM providers.

    All specific provider implementations should inherit from this class
    and implement the required abstract methods.

    Features:
    - Common interface for all providers
    - Built-in retry and timeout handling
    - Streaming support
    - Telemetry hooks
    """

    # Default models for this provider type
    DEFAULT_MODELS: list[str] = []

    # Pricing info (per 1K tokens)
    INPUT_PRICE_PER_1K: float = 0.0
    OUTPUT_PRICE_PER_1K: float = 0.0

    def __init__(self):
        """Initialize base LLM provider."""
        super().__init__()
        self._client: Any = None

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name."""
        pass

    @property
    def default_models(self) -> list[str]:
        """Get default models for this provider."""
        return self.DEFAULT_MODELS

    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities.

        Returns:
            Provider capabilities.
        """
        return ProviderCapabilities(
            provider_type=self.provider_type,
            supports_streaming=self.supports_streaming(),
            supports_embeddings=self.supports_embeddings(),
            supports_vision=self.supports_vision(),
            supports_function_calling=self.supports_function_calling(),
            supports_json_mode=self.supports_json_mode(),
            max_context_length=self.max_context_length(),
            max_output_tokens=self.max_output_tokens(),
            supported_task_types=self.supported_task_types(),
            privacy_compliant=True,
            pricing_tier=self.pricing_tier(),
        )

    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata.

        Returns:
            Provider metadata.
        """
        return ProviderMetadata(
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            name=self.name,
            description=self.description(),
            capabilities=self.get_capabilities(),
        )

    # =========================================================================
    # Capability Methods (Override as needed)
    # =========================================================================

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming.

        Returns:
            True if streaming is supported.
        """
        return ProviderType.supports_streaming(self.provider_type)

    def supports_embeddings(self) -> bool:
        """Check if provider supports embeddings.

        Returns:
            True if embeddings are supported.
        """
        return ProviderType.supports_embeddings(self.provider_type)

    def supports_vision(self) -> bool:
        """Check if provider supports vision/multimodal.

        Returns:
            True if vision is supported.
        """
        return ProviderType.supports_vision(self.provider_type)

    def supports_function_calling(self) -> bool:
        """Check if provider supports function calling.

        Returns:
            True if function calling is supported.
        """
        return False

    def supports_json_mode(self) -> bool:
        """Check if provider supports JSON mode.

        Returns:
            True if JSON mode is supported.
        """
        return True

    def max_context_length(self) -> int:
        """Get maximum context length.

        Returns:
            Maximum context length in tokens.
        """
        return 4096

    def max_output_tokens(self) -> int:
        """Get maximum output tokens.

        Returns:
            Maximum output tokens.
        """
        return 4096

    def supported_task_types(self) -> list[TaskType]:
        """Get list of supported task types.

        Returns:
            List of supported task types.
        """
        return [
            TaskType.GENERAL,
            TaskType.CODE,
            TaskType.REASONING,
            TaskType.CREATIVE,
            TaskType.ANALYSIS,
            TaskType.SUMMARIZATION,
        ]

    def pricing_tier(self) -> str:
        """Get pricing tier.

        Returns:
            Pricing tier (budget, standard, premium).
        """
        return "standard"

    def description(self) -> str:
        """Get provider description.

        Returns:
            Provider description.
        """
        return f"{self.name} LLM Provider"

    # =========================================================================
    # Abstract Methods
    # =========================================================================

    @abstractmethod
    def _create_client(self, config: ProviderConfig) -> Any:
        """Create the provider client.

        Args:
            config: Provider configuration.

        Returns:
            Provider client instance.
        """
        pass

    @abstractmethod
    def _generate_impl(self, request: GenerationRequest) -> GenerationResponse:
        """Implement actual generation logic.

        Args:
            request: Generation request.

        Returns:
            Generation response.
        """
        pass

    @abstractmethod
    def _stream_impl(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Implement actual streaming logic.

        Args:
            request: Generation request.

        Yields:
            Text chunks.
        """
        pass

    @abstractmethod
    def _health_check_impl(self) -> dict:
        """Implement actual health check.

        Returns:
            Health check result.
        """
        pass

    # =========================================================================
    # Implementation
    # =========================================================================

    def initialize(self, config: ProviderConfig) -> None:
        """Initialize the provider.

        Args:
            config: Provider configuration.
        """
        super().initialize(config)
        self._client = self._create_client(config)
        self._set_state(config.metadata.get("initial_state", "initialized"))

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text from prompt.

        Args:
            request: Generation request.

        Returns:
            Generation response.
        """
        return self._generate_impl(request)

    def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Generate text with streaming.

        Args:
            request: Generation request.

        Yields:
            Text chunks.
        """
        return self._stream_impl(request)

    def embeddings(self, texts: list[str], model: str = "") -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed.
            model: Model to use.

        Returns:
            List of embedding vectors.
        """
        if not self.supports_embeddings():
            raise NotImplementedError(f"{self.name} does not support embeddings")

        return self._embeddings_impl(texts, model)

    def _embeddings_impl(self, texts: list[str], model: str) -> list[list[float]]:
        """Implement embeddings generation.

        Args:
            texts: Texts to embed.
            model: Model to use.

        Returns:
            Embeddings.
        """
        raise NotImplementedError("Embeddings not implemented")

    def health_check(self) -> dict:
        """Check provider health.

        Returns:
            Health check result.
        """
        return self._health_check_impl()

    def shutdown(self) -> None:
        """Shutdown the provider."""
        self._client = None
        self._set_state("unregistered")

    def get_available_models(self) -> list[str]:
        """Get list of available models.

        Returns:
            List of model identifiers.
        """
        if self._config and self._config.models:
            return self._config.models
        return self.default_models

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for tokens.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Cost in USD.
        """
        input_cost = (input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
