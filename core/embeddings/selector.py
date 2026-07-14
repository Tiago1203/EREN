"""Embedding selector for EREN Embedding Provider Layer.

Selects the best provider based on policies.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from core.embeddings.types import (
    EmbeddingProvider,
    EmbeddingPolicy,
    ProviderHealth,
)
from core.embeddings.provider import BaseEmbeddingProvider
from core.embeddings.registry import EmbeddingRegistry
from core.embeddings.exceptions import SelectionError

if TYPE_CHECKING:
    pass


class EmbeddingSelector:
    """Selector for embedding providers.

    Selects the best provider based on policy and provider health.
    """

    def __init__(
        self,
        registry: EmbeddingRegistry | None = None,
        policy: EmbeddingPolicy = EmbeddingPolicy.DEFAULT,
    ):
        """Initialize selector.

        Args:
            registry: Embedding registry.
            policy: Default selection policy.
        """
        self._registry = registry
        self._policy = policy
        self._provider_states: dict[EmbeddingProvider, ProviderHealth] = {}
        self._round_robin_index: dict[EmbeddingProvider, int] = {}

    @property
    def registry(self) -> EmbeddingRegistry:
        """Get registry."""
        if self._registry is None:
            from core.embeddings import get_embedding_registry
            self._registry = get_embedding_registry()
        return self._registry

    @property
    def policy(self) -> EmbeddingPolicy:
        """Get selection policy."""
        return self._policy

    @policy.setter
    def policy(self, policy: EmbeddingPolicy) -> None:
        """Set selection policy."""
        self._policy = policy

    def select(
        self,
        model: str | None = None,
        policy: EmbeddingPolicy | None = None,
    ) -> BaseEmbeddingProvider:
        """Select a provider based on policy.

        Args:
            model: Preferred model.
            policy: Selection policy (uses default if None).

        Returns:
            Selected provider.

        Raises:
            SelectionError: If no provider can be selected.
        """
        policy = policy or self._policy
        providers = self.registry.list_providers()

        if not providers:
            raise SelectionError("No providers registered")

        # Apply policy
        if policy == EmbeddingPolicy.FAILOVER:
            return self._select_failover(providers)
        elif policy == EmbeddingPolicy.ROUND_ROBIN:
            return self._select_round_robin(providers)
        elif policy == EmbeddingPolicy.HEALTHY_FIRST:
            return self._select_healthy_first(providers)
        elif policy == EmbeddingPolicy.LOCAL_ONLY:
            return self._select_local_only(providers)
        elif policy == EmbeddingPolicy.CLOUD_ONLY:
            return self._select_cloud_only(providers)
        elif policy == EmbeddingPolicy.CHEAPEST:
            return self._select_cheapest(providers)
        elif policy == EmbeddingPolicy.FASTEST:
            return self._select_fastest(providers)
        else:
            # DEFAULT
            return self._select_default(providers)

    async def select_with_health(
        self,
        model: str | None = None,
        policy: EmbeddingPolicy | None = None,
    ) -> BaseEmbeddingProvider:
        """Select a provider considering health status.

        Args:
            model: Preferred model.
            policy: Selection policy.

        Returns:
            Selected provider.

        Raises:
            SelectionError: If no healthy provider found.
        """
        import asyncio

        provider = self.select(model, policy)

        # Check health
        health = await provider.health_check()

        if not health.is_healthy and policy == EmbeddingPolicy.HEALTHY_FIRST:
            # Try to find healthy provider
            providers = self.registry.list_providers()
            for p in providers:
                if p != provider.provider_name:
                    alt_provider = self.registry.get(p)
                    alt_health = await alt_provider.health_check()
                    self._provider_states[p] = alt_health

                    if alt_health.is_healthy:
                        return alt_provider

            raise SelectionError("No healthy providers available")

        return provider

    def _select_default(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select using default policy."""
        return self.registry.get_default()

    def _select_failover(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select with failover."""
        if len(providers) == 1:
            return self.registry.get(providers[0])

        # Return second provider if first fails
        # The actual failover happens at runtime
        return self.registry.get(providers[0])

    def _select_round_robin(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select using round robin."""
        current = self._round_robin_index.get(providers[0], 0)
        selected = providers[current % len(providers)]
        self._round_robin_index[providers[0]] = (current + 1) % len(providers)
        return self.registry.get(selected)

    def _select_healthy_first(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select healthy provider."""
        healthy = [
            p for p in providers
            if self._provider_states.get(p, ProviderHealth(p)).is_healthy
        ]

        if not healthy:
            # All unhealthy, return default
            return self.registry.get_default()

        # Return random healthy provider
        return self.registry.get(random.choice(healthy))

    def _select_local_only(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select local provider."""
        for provider_name in providers:
            provider = self.registry.get(provider_name)
            model_info = provider.get_model_info()

            if model_info.is_local:
                return provider

        raise SelectionError("No local providers available")

    def _select_cloud_only(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select cloud provider."""
        for provider_name in providers:
            provider = self.registry.get(provider_name)
            model_info = provider.get_model_info()

            if not model_info.is_local:
                return provider

        raise SelectionError("No cloud providers available")

    def _select_cheapest(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select cheapest provider."""
        cheapest = None
        cheapest_cost = float('inf')

        for provider_name in providers:
            provider = self.registry.get(provider_name)
            model_info = provider.get_model_info()

            if model_info.cost_per_1k_tokens < cheapest_cost:
                cheapest_cost = model_info.cost_per_1k_tokens
                cheapest = provider

        if cheapest is None:
            raise SelectionError("No providers available")

        return cheapest

    def _select_fastest(self, providers: list[EmbeddingProvider]) -> BaseEmbeddingProvider:
        """Select fastest provider based on recent latency."""
        fastest = None
        fastest_latency = float('inf')

        for provider_name in providers:
            health = self._provider_states.get(provider_name)

            if health and health.is_healthy and health.latency_ms < fastest_latency:
                fastest_latency = health.latency_ms
                fastest = self.registry.get(provider_name)

        if fastest is None:
            # No latency data, return default
            return self.registry.get_default()

        return fastest

    def update_health(self, health: ProviderHealth) -> None:
        """Update provider health status.

        Args:
            health: Health status.
        """
        self._provider_states[health.provider] = health
