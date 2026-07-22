"""Provider registry for EREN OS Multi-Provider Layer.

Manages provider registration and discovery.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.providers.exceptions import (
    ProviderAlreadyRegisteredError,
    ProviderNotFoundError,
)
from core.PHASE_2.providers.provider import BaseProvider
from core.PHASE_2.providers.types import ProviderConfig, ProviderState, ProviderType

if TYPE_CHECKING:
    pass


class ProviderRegistry:
    """Registry for managing LLM providers.

    Provides:
    - Provider registration
    - Provider discovery
    - State management
    - Factory registration
    """

    def __init__(self):
        """Initialize the registry."""
        self._providers: dict[str, BaseProvider] = {}
        self._factories: dict[str, Callable[[], BaseProvider]] = {}
        self._configs: dict[str, ProviderConfig] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Registration
    # =========================================================================

    def register(
        self,
        provider: BaseProvider,
        config: ProviderConfig | None = None,
    ) -> None:
        """Register a provider.

        Args:
            provider: Provider instance.
            config: Optional provider configuration.

        Raises:
            ProviderAlreadyRegisteredError: If already registered.
        """
        with self._lock:
            provider_id = provider.provider_id

            if provider_id in self._providers:
                raise ProviderAlreadyRegisteredError(provider_id)

            self._providers[provider_id] = provider

            if config:
                self._configs[provider_id] = config
                provider._config = config

            # Initialize if config is provided
            if config:
                provider.initialize(config)

    def unregister(self, provider_id: str) -> bool:
        """Unregister a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if provider_id not in self._providers:
                return False

            provider = self._providers[provider_id]

            # Shutdown if needed
            if provider.state == ProviderState.HEALTHY:
                provider.shutdown()

            del self._providers[provider_id]
            if provider_id in self._configs:
                del self._configs[provider_id]

            return True

    def register_factory(
        self,
        provider_type: ProviderType,
        factory: Callable[[], BaseProvider],
    ) -> None:
        """Register a provider factory.

        Args:
            provider_type: Type of provider.
            factory: Factory function that creates provider instances.
        """
        with self._lock:
            self._factories[provider_type.value] = factory

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, provider_id: str) -> BaseProvider:
        """Get a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider instance.

        Raises:
            ProviderNotFoundError: If not found.
        """
        with self._lock:
            if provider_id not in self._providers:
                raise ProviderNotFoundError(provider_id)
            return self._providers[provider_id]

    def get_or_none(self, provider_id: str) -> BaseProvider | None:
        """Get a provider or None.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider or None.
        """
        with self._lock:
            return self._providers.get(provider_id)

    def get_config(self, provider_id: str) -> ProviderConfig | None:
        """Get provider configuration.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider configuration or None.
        """
        with self._lock:
            return self._configs.get(provider_id)

    def has(self, provider_id: str) -> bool:
        """Check if provider is registered.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if registered.
        """
        with self._lock:
            return provider_id in self._providers

    def create(self, provider_id: str, config: ProviderConfig) -> BaseProvider | None:
        """Create a provider from factory.

        Args:
            provider_id: Provider identifier.
            config: Provider configuration.

        Returns:
            Created provider or None.
        """
        with self._lock:
            factory = self._factories.get(config.provider_type.value)
            if not factory:
                return None

            provider = factory()

            # Auto-register
            self._providers[provider_id] = provider
            self._configs[provider_id] = config
            provider._config = config

            return provider

    # =========================================================================
    # Queries
    # =========================================================================

    def list_all(self) -> list[BaseProvider]:
        """List all registered providers.

        Returns:
            List of providers.
        """
        with self._lock:
            return list(self._providers.values())

    def list_by_type(self, provider_type: ProviderType) -> list[BaseProvider]:
        """List providers by type.

        Args:
            provider_type: Provider type.

        Returns:
            List of providers of the type.
        """
        with self._lock:
            return [
                p for p in self._providers.values()
                if p.provider_type == provider_type
            ]

    def list_by_state(self, state: ProviderState) -> list[BaseProvider]:
        """List providers by state.

        Args:
            state: Provider state.

        Returns:
            List of providers in the state.
        """
        with self._lock:
            return [p for p in self._providers.values() if p.state == state]

    def list_healthy(self) -> list[BaseProvider]:
        """List all healthy providers.

        Returns:
            List of healthy providers.
        """
        return self.list_by_state(ProviderState.HEALTHY)

    def list_enabled(self) -> list[BaseProvider]:
        """List all enabled providers.

        Returns:
            List of enabled providers.
        """
        with self._lock:
            return [
                p for p in self._providers.values()
                if p._config and p._config.enabled
            ]

    # =========================================================================
    # Counts
    # =========================================================================

    def count(self) -> int:
        """Get total provider count."""
        with self._lock:
            return len(self._providers)

    def count_by_state(self, state: ProviderState) -> int:
        """Get provider count by state."""
        with self._lock:
            return len([p for p in self._providers.values() if p.state == state])

    def healthy_count(self) -> int:
        """Get healthy provider count."""
        return self.count_by_state(ProviderState.HEALTHY)

    # =========================================================================
    # State Management
    # =========================================================================

    def set_state(self, provider_id: str, state: ProviderState) -> bool:
        """Set provider state.

        Args:
            provider_id: Provider identifier.
            state: New state.

        Returns:
            True if state was set.
        """
        with self._lock:
            if provider_id not in self._providers:
                return False

            self._providers[provider_id]._set_state(state)
            return True

    def enable(self, provider_id: str) -> bool:
        """Enable a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if enabled.
        """
        with self._lock:
            if provider_id not in self._configs:
                return False
            self._configs[provider_id].enabled = True
            return True

    def disable(self, provider_id: str) -> bool:
        """Disable a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if disabled.
        """
        with self._lock:
            if provider_id not in self._configs:
                return False
            self._configs[provider_id].enabled = False
            return True

    # =========================================================================
    # Utility
    # =========================================================================

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            for provider in self._providers.values():
                if provider.state == ProviderState.HEALTHY:
                    provider.shutdown()
            self._providers.clear()
            self._configs.clear()
            self._factories.clear()

    def __len__(self) -> int:
        """Get provider count."""
        with self._lock:
            return len(self._providers)

    def __contains__(self, provider_id: str) -> bool:
        """Check if provider is registered."""
        return self.has(provider_id)


# Global registry instance
_global_registry: ProviderRegistry | None = None
_registry_lock = threading.Lock()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry.

    Returns:
        Global ProviderRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = ProviderRegistry()
        return _global_registry


def reset_provider_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
