"""Provider selector for EREN OS Multi-Provider Layer.

Implements various selection strategies for choosing providers.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from core.providers.exceptions import ProviderUnavailableError
from core.providers.provider import BaseProvider
from core.providers.registry import ProviderRegistry
from core.providers.types import (
    ProviderState,
    SelectionPolicy,
)

if TYPE_CHECKING:
    pass


class ProviderSelector:
    """Selects providers based on various policies.

    Supports:
    - DEFAULT: Use default provider
    - PRIORITY: Select by priority
    - ROUND_ROBIN: Balance across providers
    - HEALTHY_FIRST: Only healthy providers
    - LOWEST_LATENCY: Select by latency
    - FAILOVER: Fallback chain
    - RANDOM: Random selection
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        default_provider_id: str | None = None,
    ):
        """Initialize selector.

        Args:
            registry: Provider registry.
            default_provider_id: Default provider to use.
        """
        self._registry = registry
        self._default_provider_id = default_provider_id
        self._round_robin_index: dict[str, int] = {}
        self._policy: SelectionPolicy = SelectionPolicy.DEFAULT

    @property
    def policy(self) -> SelectionPolicy:
        """Get current selection policy."""
        return self._policy

    @policy.setter
    def policy(self, policy: SelectionPolicy) -> None:
        """Set selection policy."""
        self._policy = policy

    @property
    def default_provider_id(self) -> str | None:
        """Get default provider ID."""
        return self._default_provider_id

    @default_provider_id.setter
    def default_provider_id(self, provider_id: str | None) -> None:
        """Set default provider ID."""
        self._default_provider_id = provider_id

    def select(
        self,
        policy: SelectionPolicy | None = None,
        model: str | None = None,
        exclude_providers: list[str] | None = None,
    ) -> BaseProvider:
        """Select a provider based on policy.

        Args:
            policy: Selection policy (uses default if None).
            model: Optional model requirement.
            exclude_providers: Providers to exclude.

        Returns:
            Selected provider.

        Raises:
            ProviderUnavailableError: If no provider available.
        """
        policy = policy or self._policy
        exclude_providers = exclude_providers or []

        # Get eligible providers
        providers = self._get_eligible_providers(model, exclude_providers)

        if not providers:
            raise ProviderUnavailableError(
                f"No provider available matching criteria (policy: {policy.value})"
            )

        # Apply policy
        if policy == SelectionPolicy.DEFAULT:
            return self._select_default(providers)
        elif policy == SelectionPolicy.PRIORITY:
            return self._select_by_priority(providers)
        elif policy == SelectionPolicy.ROUND_ROBIN:
            return self._select_round_robin(providers)
        elif policy == SelectionPolicy.HEALTHY_FIRST:
            return self._select_healthy_first(providers)
        elif policy == SelectionPolicy.LOWEST_LATENCY:
            return self._select_lowest_latency(providers)
        elif policy == SelectionPolicy.FAILOVER:
            return self._select_failover(providers)
        elif policy == SelectionPolicy.RANDOM:
            return self._select_random(providers)
        else:
            return self._select_default(providers)

    def select_multiple(
        self,
        count: int,
        policy: SelectionPolicy | None = None,
        model: str | None = None,
    ) -> list[BaseProvider]:
        """Select multiple providers.

        Args:
            count: Number of providers to select.
            policy: Selection policy.
            model: Optional model requirement.

        Returns:
            List of selected providers.
        """
        providers = self._get_eligible_providers(model)
        return providers[:count] if len(providers) >= count else providers

    def _get_eligible_providers(
        self,
        model: str | None,
        exclude_providers: list[str] | None = None,
    ) -> list[BaseProvider]:
        """Get eligible providers.

        Args:
            model: Optional model requirement.
            exclude_providers: Providers to exclude.

        Returns:
            List of eligible providers.
        """
        providers = self._registry.list_enabled()

        # Filter by model support
        if model:
            providers = [p for p in providers if p.supports_model(model)]

        # Filter by state
        providers = [
            p for p in providers
            if p.state in (ProviderState.HEALTHY, ProviderState.DEGRADED)
        ]

        # Exclude specified providers
        if exclude_providers:
            providers = [
                p for p in providers
                if p.provider_id not in exclude_providers
            ]

        return providers

    def _select_default(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select default provider.

        Args:
            providers: Eligible providers.

        Returns:
            Default provider.
        """
        # Try default first
        if self._default_provider_id:
            for p in providers:
                if p.provider_id == self._default_provider_id:
                    return p

        # Fall back to first available
        return providers[0]

    def _select_by_priority(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select provider by priority.

        Args:
            providers: Eligible providers.

        Returns:
            Highest priority provider.
        """
        # Sort by priority (lower number = higher priority)
        sorted_providers = sorted(
            providers,
            key=lambda p: (p._config.priority if p._config else 100, p.provider_id)
        )
        return sorted_providers[0]

    def _select_round_robin(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select provider using round-robin.

        Args:
            providers: Eligible providers.

        Returns:
            Next provider in rotation.
        """
        if not providers:
            raise ProviderUnavailableError("No providers available for round-robin")

        # Initialize index if needed
        key = ",".join(sorted(p.provider_id for p in providers))
        if key not in self._round_robin_index:
            self._round_robin_index[key] = 0

        # Get next in rotation
        index = self._round_robin_index[key]
        selected = providers[index % len(providers)]
        self._round_robin_index[key] = (index + 1) % len(providers)

        return selected

    def _select_healthy_first(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select healthy provider first.

        Args:
            providers: Eligible providers.

        Returns:
            Healthy provider with lowest latency.
        """
        healthy = [p for p in providers if p.state == ProviderState.HEALTHY]

        if healthy:
            # Sort by latency
            return sorted(healthy, key=lambda p: p._last_health_check.latency_ms if p._last_health_check else 0)[0]

        # Fall back to degraded
        return providers[0]

    def _select_lowest_latency(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select provider with lowest latency.

        Args:
            providers: Eligible providers.

        Returns:
            Provider with lowest latency.
        """
        # Sort by average latency
        return sorted(
            providers,
            key=lambda p: p.metrics.average_latency_ms
        )[0]

    def _select_failover(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select provider for failover chain.

        Args:
            providers: Eligible providers.

        Returns:
            First healthy provider (highest priority).
        """
        # Sort by priority
        sorted_providers = sorted(
            providers,
            key=lambda p: (p._config.priority if p._config else 100, p.provider_id)
        )

        # Return first healthy
        for p in sorted_providers:
            if p.state == ProviderState.HEALTHY:
                return p

        return sorted_providers[0]

    def _select_random(self, providers: list[BaseProvider]) -> BaseProvider:
        """Select random provider.

        Args:
            providers: Eligible providers.

        Returns:
            Random provider.
        """
        return random.choice(providers)

    def get_failover_chain(
        self,
        exclude_providers: list[str] | None = None,
    ) -> list[BaseProvider]:
        """Get failover chain of providers.

        Args:
            exclude_providers: Providers to exclude.

        Returns:
            Ordered list for failover.
        """
        providers = self._get_eligible_providers(
            model=None,
            exclude_providers=exclude_providers,
        )

        # Sort by priority
        return sorted(
            providers,
            key=lambda p: (p._config.priority if p._config else 100, p.provider_id)
        )
