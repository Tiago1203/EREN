"""Base provider interface for EREN OS Multi-Provider Layer.

Defines the contract that all LLM providers must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncIterator

from core.providers.types import (
    ProviderType,
    ProviderState,
    ProviderHealth,
    ProviderMetrics,
    ProviderConfig,
    GenerationRequest,
    GenerationResponse,
)

if TYPE_CHECKING:
    pass


class BaseProvider(ABC):
    """Abstract base class for LLM providers.

    All providers must implement this interface to be used with the
    Multi-Provider Layer.

    Example:
        class OpenAIProvider(BaseProvider):
            def initialize(self, config: ProviderConfig) -> None:
                # Setup client
                pass

            def generate(self, request: GenerationRequest) -> GenerationResponse:
                # Generate text
                pass
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Get provider identifier."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        pass

    @property
    def state(self) -> ProviderState:
        """Get current provider state."""
        return self._state

    @property
    def metrics(self) -> ProviderMetrics:
        """Get provider metrics."""
        return self._metrics

    @property
    def config(self) -> ProviderConfig | None:
        """Get provider configuration."""
        return self._config

    def __init__(self) -> None:
        """Initialize base provider."""
        self._state = ProviderState.UNREGISTERED
        self._metrics = ProviderMetrics()
        self._config: ProviderConfig | None = None
        self._last_health_check: ProviderHealth | None = None

    # =========================================================================
    # Required Methods
    # =========================================================================

    @abstractmethod
    def initialize(self, config: ProviderConfig) -> None:
        """Initialize the provider.

        Args:
            config: Provider configuration.

        Raises:
            ProviderInitializationError: If initialization fails.
        """
        pass

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text from prompt.

        Args:
            request: Generation request.

        Returns:
            Generation response.

        Raises:
            ProviderException: If generation fails.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the provider.

        Must release all resources and stop any background tasks.
        """
        pass

    # =========================================================================
    # Optional Methods
    # =========================================================================

    def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Generate text with streaming.

        Override to implement streaming support.

        Args:
            request: Generation request.

        Yields:
            Text chunks as they are generated.

        Raises:
            ProviderException: If generation fails.
        """
        # Default implementation: generate and yield all at once
        response = self.generate(request)
        if response.success:
            yield response.content
        else:
            raise Exception(response.error)

    def embeddings(self, texts: list[str], model: str = "") -> list[list[float]]:
        """Generate embeddings for texts.

        Override to implement embeddings support.

        Args:
            texts: List of texts to embed.
            model: Model to use for embeddings.

        Returns:
            List of embedding vectors.

        Raises:
            ProviderException: If embeddings generation fails.
        """
        raise NotImplementedError("Embeddings not supported by this provider")

    def health_check(self) -> ProviderHealth:
        """Check provider health.

        Override to implement custom health check logic.

        Returns:
            Provider health status.
        """
        return ProviderHealth(
            healthy=self._state == ProviderState.HEALTHY,
            state=self._state,
            message="Provider is healthy" if self._state == ProviderState.HEALTHY else f"Provider state: {self._state.value}",
        )

    def get_available_models(self) -> list[str]:
        """Get list of available models.

        Override to return available models.

        Returns:
            List of model identifiers.
        """
        if self._config:
            return self._config.models
        return []

    def supports_model(self, model: str) -> bool:
        """Check if provider supports a model.

        Args:
            model: Model identifier.

        Returns:
            True if model is supported.
        """
        return model in self.get_available_models()

    def supports_embeddings(self) -> bool:
        """Check if provider supports embeddings.

        Returns:
            True if embeddings are supported.
        """
        return False

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming.

        Returns:
            True if streaming is supported.
        """
        return False

    # =========================================================================
    # State Management
    # =========================================================================

    def _set_state(self, state: ProviderState) -> None:
        """Set provider state.

        Args:
            state: New state.
        """
        self._state = state

    def _set_health(self, health: ProviderHealth) -> None:
        """Set last health check result.

        Args:
            health: Health status.
        """
        self._last_health_check = health

    # =========================================================================
    # Utility
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type.value,
            "state": self._state.value,
            "metrics": self._metrics.to_dict(),
            "config": self._config.to_dict() if self._config else None,
            "last_health_check": self._last_health_check.to_dict() if self._last_health_check else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.provider_id}, "
            f"type={self.provider_type.value}, "
            f"state={self._state.value})"
        )
