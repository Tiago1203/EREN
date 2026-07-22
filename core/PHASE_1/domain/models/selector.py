"""Model selector for EREN OS Cognitive Model Registry.

Implements various selection strategies for choosing models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_1.domain.models.descriptor import ModelDescriptor
from core.PHASE_1.domain.models.exceptions import ModelSelectionError
from core.PHASE_1.domain.models.registry import ModelRegistry
from core.PHASE_1.domain.models.types import (
    ModelCategory,
    ModelSelectionPolicy,
)

if TYPE_CHECKING:
    pass


class ModelSelector:
    """Selects models based on various policies.

    Supports:
    - DEFAULT: Use default model
    - FASTEST: Lowest latency
    - CHEAPEST: Lowest cost
    - HIGHEST_QUALITY: Best quality score
    - LONGEST_CONTEXT: Largest context window
    - REASONING: Optimized for reasoning
    - MULTIMODAL: Optimized for multimodal
    - CUSTOM: Custom policy
    """

    def __init__(
        self,
        registry: ModelRegistry,
        default_model_id: str | None = None,
    ):
        """Initialize selector.

        Args:
            registry: Model registry.
            default_model_id: Default model to use.
        """
        self._registry = registry
        self._default_model_id = default_model_id
        self._policy: ModelSelectionPolicy = ModelSelectionPolicy.DEFAULT

    @property
    def policy(self) -> ModelSelectionPolicy:
        """Get current selection policy."""
        return self._policy

    @policy.setter
    def policy(self, policy: ModelSelectionPolicy) -> None:
        """Set selection policy."""
        self._policy = policy

    @property
    def default_model_id(self) -> str | None:
        """Get default model ID."""
        return self._default_model_id

    @default_model_id.setter
    def default_model_id(self, model_id: str | None) -> None:
        """Set default model ID."""
        self._default_model_id = model_id

    def select(
        self,
        policy: ModelSelectionPolicy | None = None,
        category: ModelCategory | None = None,
        capabilities: list[str] | None = None,
        exclude_models: list[str] | None = None,
    ) -> ModelDescriptor:
        """Select a model based on policy.

        Args:
            policy: Selection policy (uses default if None).
            category: Optional category filter.
            capabilities: Optional capability requirements.
            exclude_models: Models to exclude.

        Returns:
            Selected model.

        Raises:
            ModelSelectionError: If no model available.
        """
        policy = policy or self._policy
        exclude_models = exclude_models or []

        # Get eligible models
        models = self._get_eligible_models(category, capabilities, exclude_models)

        if not models:
            raise ModelSelectionError(
                f"No model available matching criteria (policy: {policy.value})",
                policy=policy.value,
            )

        # Apply policy
        if policy == ModelSelectionPolicy.DEFAULT:
            return self._select_default(models)
        elif policy == ModelSelectionPolicy.FASTEST:
            return self._select_fastest(models)
        elif policy == ModelSelectionPolicy.CHEAPEST:
            return self._select_cheapest(models)
        elif policy == ModelSelectionPolicy.HIGHEST_QUALITY:
            return self._select_highest_quality(models)
        elif policy == ModelSelectionPolicy.LONGEST_CONTEXT:
            return self._select_longest_context(models)
        elif policy == ModelSelectionPolicy.REASONING:
            return self._select_reasoning(models)
        elif policy == ModelSelectionPolicy.MULTIMODAL:
            return self._select_multimodal(models)
        else:
            return self._select_default(models)

    def _get_eligible_models(
        self,
        category: ModelCategory | None,
        capabilities: list[str] | None,
        exclude_models: list[str],
    ) -> list[ModelDescriptor]:
        """Get eligible models.

        Args:
            category: Optional category filter.
            capabilities: Optional capability requirements.
            exclude_models: Models to exclude.

        Returns:
            List of eligible models.
        """
        models = self._registry.list_available()

        # Filter by category
        if category:
            models = [m for m in models if m.category == category]

        # Filter by capabilities
        if capabilities:
            models = [
                m for m in models
                if all(m.supports_capability(c) for c in capabilities)
            ]

        # Exclude specified models
        if exclude_models:
            models = [m for m in models if m.model_id not in exclude_models]

        return models

    def _select_default(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select default model.

        Args:
            models: Eligible models.

        Returns:
            Default model.
        """
        # Try default first
        if self._default_model_id:
            for m in models:
                if m.model_id == self._default_model_id:
                    return m

        # Fall back to first available
        return models[0]

    def _select_fastest(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select fastest model.

        Args:
            models: Eligible models.

        Returns:
            Model with lowest latency.
        """
        return min(models, key=lambda m: m.latency_ms)

    def _select_cheapest(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select cheapest model.

        Args:
            models: Eligible models.

        Returns:
            Model with lowest cost per input token.
        """
        return min(models, key=lambda m: m.pricing.cost_per_input_token)

    def _select_highest_quality(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select highest quality model.

        Args:
            models: Eligible models.

        Returns:
            Model with highest quality score.
        """
        return max(models, key=lambda m: m.quality_score)

    def _select_longest_context(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select model with longest context.

        Args:
            models: Eligible models.

        Returns:
            Model with largest context window.
        """
        return max(models, key=lambda m: m.context_window)

    def _select_reasoning(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select best reasoning model.

        Args:
            models: Eligible models.

        Returns:
            Best reasoning model.
        """
        reasoning_models = [m for m in models if m.supports_reasoning]

        if reasoning_models:
            return max(reasoning_models, key=lambda m: m.quality_score)

        return models[0]

    def _select_multimodal(self, models: list[ModelDescriptor]) -> ModelDescriptor:
        """Select best multimodal model.

        Args:
            models: Eligible models.

        Returns:
            Best multimodal model.
        """
        multimodal_models = [m for m in models if m.supports_multimodal]

        if multimodal_models:
            return max(multimodal_models, key=lambda m: m.quality_score)

        return models[0]

    def select_multiple(
        self,
        count: int,
        policy: ModelSelectionPolicy | None = None,
        category: ModelCategory | None = None,
        capabilities: list[str] | None = None,
    ) -> list[ModelDescriptor]:
        """Select multiple models.

        Args:
            count: Number of models to select.
            policy: Selection policy.
            category: Optional category filter.
            capabilities: Optional capability requirements.

        Returns:
            List of selected models.
        """
        models = self._get_eligible_models(category, capabilities, [])
        return models[:count] if len(models) >= count else models
