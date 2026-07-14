"""Provider manager for EREN OS Multi-Provider Layer.

Orchestrates all provider operations including selection, failover, and generation.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.providers.exceptions import (
    ProviderFallbackError,
)
from core.providers.provider import BaseProvider
from core.providers.registry import ProviderRegistry, get_provider_registry
from core.providers.selector import ProviderSelector
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderHealth,
    ProviderState,
    SelectionPolicy,
)

if TYPE_CHECKING:
    pass


class ProviderManager:
    """Manages LLM providers with selection, failover, and metrics.

    Provides a unified interface for generating text using multiple providers
    with automatic failover and load balancing.
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        default_provider_id: str | None = None,
        default_policy: SelectionPolicy = SelectionPolicy.PRIORITY,
    ):
        """Initialize provider manager.

        Args:
            registry: Provider registry (uses global if None).
            default_provider_id: Default provider ID.
            default_policy: Default selection policy.
        """
        self._registry = registry or get_provider_registry()
        self._selector = ProviderSelector(self._registry, default_provider_id)
        self._default_policy = default_policy
        self._lock = threading.RLock()

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def registry(self) -> ProviderRegistry:
        """Get provider registry."""
        return self._registry

    @property
    def selector(self) -> ProviderSelector:
        """Get provider selector."""
        return self._selector

    @property
    def default_policy(self) -> SelectionPolicy:
        """Get default selection policy."""
        return self._default_policy

    @default_policy.setter
    def default_policy(self, policy: SelectionPolicy) -> None:
        """Set default selection policy."""
        self._default_policy = policy
        self._selector.policy = policy

    # =========================================================================
    # Provider Management
    # =========================================================================

    def add_provider(
        self,
        provider: BaseProvider,
        config: ProviderConfig | None = None,
    ) -> None:
        """Add a provider.

        Args:
            provider: Provider instance.
            config: Optional configuration.
        """
        with self._lock:
            self._registry.register(provider, config)

            # Set as default if first provider
            if self._registry.count() == 1:
                self._selector.default_provider_id = provider.provider_id

            self._emit_event("ProviderAdded", {
                "provider_id": provider.provider_id,
                "provider_type": provider.provider_type.value,
            })

    def remove_provider(self, provider_id: str) -> bool:
        """Remove a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if removed.
        """
        with self._lock:
            result = self._registry.unregister(provider_id)

            if result:
                self._emit_event("ProviderRemoved", {"provider_id": provider_id})

            return result

    def get_provider(self, provider_id: str) -> BaseProvider:
        """Get a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider instance.
        """
        return self._registry.get(provider_id)

    def list_providers(self) -> list[BaseProvider]:
        """List all providers.

        Returns:
            List of providers.
        """
        return self._registry.list_all()

    # =========================================================================
    # Generation
    # =========================================================================

    def generate(
        self,
        request: GenerationRequest,
        policy: SelectionPolicy | None = None,
        fallback_enabled: bool = True,
    ) -> GenerationResponse:
        """Generate text using selected provider.

        Args:
            request: Generation request.
            policy: Selection policy (uses default if None).
            fallback_enabled: Enable automatic failover.

        Returns:
            Generation response.

        Raises:
            ProviderUnavailableError: If no provider available.
            ProviderFallbackError: If all fallback providers fail.
        """
        policy = policy or self._default_policy

        # Select provider
        provider = self._selector.select(
            policy=policy,
            model=request.model,
        )

        self._emit_event("ProviderSelected", {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type.value,
            "policy": policy.value,
            "model": request.model,
        })

        # Generate with fallback
        if fallback_enabled and policy in (
            SelectionPolicy.FAILOVER,
            SelectionPolicy.PRIORITY,
        ):
            return self._generate_with_fallback(
                request,
                exclude_providers=[provider.provider_id],
            )

        return self._generate_single(provider, request)

    def _generate_single(
        self,
        provider: BaseProvider,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate using single provider.

        Args:
            provider: Provider to use.
            request: Generation request.

        Returns:
            Generation response.
        """
        start_time = time.time()

        try:
            self._emit_event("ProviderRequestStarted", {
                "provider_id": provider.provider_id,
                "model": request.model,
            })

            response = provider.generate(request)

            # Update metrics
            provider.metrics.record_request(
                success=response.success,
                duration_ms=response.duration_ms,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=response.cost,
            )

            self._emit_event("ProviderRequestCompleted", {
                "provider_id": provider.provider_id,
                "success": response.success,
                "duration_ms": response.duration_ms,
            })

            return response

        except Exception as e:
            provider.metrics.record_request(success=False)

            self._emit_event("ProviderRequestFailed", {
                "provider_id": provider.provider_id,
                "error": str(e),
            })

            return GenerationResponse(
                content="",
                model=request.model,
                provider_id=provider.provider_id,
                success=False,
                error=str(e),
            )

    def _generate_with_fallback(
        self,
        request: GenerationRequest,
        exclude_providers: list[str] | None = None,
    ) -> GenerationResponse:
        """Generate with fallback to other providers.

        Args:
            request: Generation request.
            exclude_providers: Providers to exclude.

        Returns:
            Generation response.

        Raises:
            ProviderFallbackError: If all providers fail.
        """
        exclude_providers = exclude_providers or []
        failed_providers: list[str] = []
        last_error: Exception | None = None

        # Get failover chain
        chain = self._selector.get_failover_chain(exclude_providers)

        for provider in chain:
            try:
                response = self._generate_single(provider, request)

                if response.success:
                    return response

                # Record failover
                provider.metrics.record_failover()
                failed_providers.append(provider.provider_id)
                last_error = Exception(response.error)

                self._emit_event("ProviderChanged", {
                    "from_provider": failed_providers[-2] if len(failed_providers) > 1 else failed_providers[0],
                    "to_provider": provider.provider_id,
                    "reason": "failover",
                })

            except Exception as e:
                failed_providers.append(provider.provider_id)
                last_error = e

                provider.metrics.record_failover()
                self._emit_event("ProviderUnavailable", {
                    "provider_id": provider.provider_id,
                    "error": str(e),
                })

        # All providers failed
        self._emit_event("ProviderRequestFailed", {
            "providers": failed_providers,
            "error": str(last_error) if last_error else "All providers failed",
        })

        raise ProviderFallbackError(failed_providers)

    # =========================================================================
    # Health and State
    # =========================================================================

    def health_check(self, provider_id: str) -> ProviderHealth:
        """Health check a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider health.
        """
        provider = self._registry.get(provider_id)
        health = provider.health_check()

        # Update state based on health
        if health.healthy:
            provider._set_state(ProviderState.HEALTHY)
        elif health.state == ProviderState.DEGRADED:
            provider._set_state(ProviderState.DEGRADED)
        else:
            provider._set_state(ProviderState.UNHEALTHY)

        provider._set_health(health)
        return health

    def health_check_all(self) -> dict[str, ProviderHealth]:
        """Health check all providers.

        Returns:
            Dictionary of provider_id -> health.
        """
        results = {}
        for provider in self._registry.list_all():
            results[provider.provider_id] = self.health_check(provider.provider_id)
        return results

    def set_state(self, provider_id: str, state: ProviderState) -> bool:
        """Set provider state.

        Args:
            provider_id: Provider identifier.
            state: New state.

        Returns:
            True if state was set.
        """
        return self._registry.set_state(provider_id, state)

    def enable(self, provider_id: str) -> bool:
        """Enable a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if enabled.
        """
        return self._registry.enable(provider_id)

    def disable(self, provider_id: str) -> bool:
        """Disable a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if disabled.
        """
        return self._registry.disable(provider_id)

    # =========================================================================
    # Events
    # =========================================================================

    def on(self, event_type: str, handler: Callable) -> None:
        """Register an event handler.

        Args:
            event_type: Event type.
            handler: Event handler function.
        """
        with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            if handler not in self._event_handlers[event_type]:
                self._event_handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable) -> None:
        """Unregister an event handler.

        Args:
            event_type: Event type.
            handler: Event handler function.
        """
        with self._lock:
            if event_type in self._event_handlers:
                if handler in self._event_handlers[event_type]:
                    self._event_handlers[event_type].remove(handler)

    def _emit_event(self, event_type: str, data: dict) -> None:
        """Emit an event.

        Args:
            event_type: Event type.
            data: Event data.
        """
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass

    # =========================================================================
    # Utility
    # =========================================================================

    def get_metrics(self) -> dict[str, dict]:
        """Get metrics for all providers.

        Returns:
            Dictionary of provider_id -> metrics.
        """
        return {
            p.provider_id: p.metrics.to_dict()
            for p in self._registry.list_all()
        }

    def get_status(self) -> dict:
        """Get overall status.

        Returns:
            Status dictionary.
        """
        providers = self._registry.list_all()
        healthy = sum(1 for p in providers if p.state == ProviderState.HEALTHY)
        enabled = sum(1 for p in providers if p._config and p._config.enabled)

        return {
            "total_providers": len(providers),
            "healthy_providers": healthy,
            "enabled_providers": enabled,
            "default_policy": self._default_policy.value,
            "default_provider": self._selector.default_provider_id,
        }


# Global manager instance
_global_manager: ProviderManager | None = None
_manager_lock = threading.Lock()


def get_provider_manager() -> ProviderManager:
    """Get the global provider manager.

    Returns:
        Global ProviderManager instance.
    """
    global _global_manager
    with _manager_lock:
        if _global_manager is None:
            _global_manager = ProviderManager()
        return _global_manager


def reset_provider_manager() -> None:
    """Reset the global manager."""
    global _global_manager
    with _manager_lock:
        if _global_manager is not None:
            _global_manager.registry.clear()
        _global_manager = None
