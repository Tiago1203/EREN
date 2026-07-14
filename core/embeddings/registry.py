"""Embedding registry for EREN Embedding Provider Layer.

Manages embedding providers.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from core.embeddings.types import EmbeddingProvider
from core.embeddings.provider import BaseEmbeddingProvider
from core.embeddings.exceptions import RegistryError, ProviderNotFoundError

if TYPE_CHECKING:
    pass


class EmbeddingRegistry:
    """Registry for embedding providers.

    Manages registration and access to embedding providers.
    """

    def __init__(self):
        """Initialize registry."""
        self._lock = threading.RLock()
        self._providers: dict[EmbeddingProvider, BaseEmbeddingProvider] = {}
        self._default_provider: EmbeddingProvider | None = None

    def register(
        self,
        provider: BaseEmbeddingProvider,
        set_default: bool = False,
    ) -> None:
        """Register an embedding provider.

        Args:
            provider: Provider to register.
            set_default: Whether to set as default provider.
        """
        with self._lock:
            self._providers[provider.provider_name] = provider

            if set_default or self._default_provider is None:
                self._default_provider = provider.provider_name

    def unregister(self, provider_name: EmbeddingProvider) -> bool:
        """Unregister an embedding provider.

        Args:
            provider_name: Provider to unregister.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if provider_name in self._providers:
                del self._providers[provider_name]

                if self._default_provider == provider_name:
                    self._default_provider = (
                        next(iter(self._providers.keys()), None)
                        if self._providers else None
                    )

                return True
            return False

    def get(self, provider_name: EmbeddingProvider) -> BaseEmbeddingProvider:
        """Get a provider by name.

        Args:
            provider_name: Provider name.

        Returns:
            Provider instance.

        Raises:
            ProviderNotFoundError: If provider not found.
        """
        with self._lock:
            if provider_name not in self._providers:
                raise ProviderNotFoundError(provider_name.value)
            return self._providers[provider_name]

    def get_default(self) -> BaseEmbeddingProvider:
        """Get the default provider.

        Returns:
            Default provider.

        Raises:
            RegistryError: If no provider registered.
        """
        with self._lock:
            if self._default_provider is None:
                raise RegistryError("No default provider set")
            return self._providers[self._default_provider]

    def set_default(self, provider_name: EmbeddingProvider) -> None:
        """Set the default provider.

        Args:
            provider_name: Provider to set as default.

        Raises:
            ProviderNotFoundError: If provider not found.
        """
        with self._lock:
            if provider_name not in self._providers:
                raise ProviderNotFoundError(provider_name.value)
            self._default_provider = provider_name

    def list_providers(self) -> list[EmbeddingProvider]:
        """List all registered providers.

        Returns:
            List of provider names.
        """
        with self._lock:
            return list(self._providers.keys())

    def list_providers_with_info(self) -> list[dict]:
        """List all providers with their information.

        Returns:
            List of provider info dictionaries.
        """
        with self._lock:
            return [
                {
                    "name": p.provider_name.value,
                    "default_model": p.default_model,
                    "models": p.supported_models,
                }
                for p in self._providers.values()
            ]

    def has_provider(self, provider_name: EmbeddingProvider) -> bool:
        """Check if provider is registered.

        Args:
            provider_name: Provider to check.

        Returns:
            True if registered.
        """
        with self._lock:
            return provider_name in self._providers

    def clear(self) -> None:
        """Clear all registered providers."""
        with self._lock:
            self._providers.clear()
            self._default_provider = None

    def get_status(self) -> dict:
        """Get registry status.

        Returns:
            Status dictionary.
        """
        with self._lock:
            return {
                "total_providers": len(self._providers),
                "default_provider": (
                    self._default_provider.value
                    if self._default_provider else None
                ),
                "providers": list(self._providers.keys()),
            }


# Global registry instance
_global_registry: EmbeddingRegistry | None = None
_registry_lock = threading.Lock()


def get_embedding_registry() -> EmbeddingRegistry:
    """Get the global embedding registry.

    Returns:
        Global EmbeddingRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = EmbeddingRegistry()
        return _global_registry


def reset_embedding_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
