"""Model registry for EREN OS Cognitive Model Registry.

Manages model registration, discovery, and querying.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.models.catalog import ModelCatalog
from core.models.descriptor import ModelDescriptor
from core.models.exceptions import (
    ModelAlreadyRegisteredError,
    ModelNotFoundError,
)
from core.models.types import (
    ModelCategory,
    ModelSelectionPolicy,
    ModelState,
)

if TYPE_CHECKING:
    pass


class ModelRegistry:
    """Registry for managing LLM models.

    Provides:
    - Model registration
    - Model discovery
    - Model querying
    - Capability matching
    """

    def __init__(self):
        """Initialize the registry."""
        self._models: dict[str, ModelDescriptor] = {}
        self._lock = threading.RLock()
        self._event_handlers: dict[str, list[Callable]] = {}

    # =========================================================================
    # Registration
    # =========================================================================

    def register(self, descriptor: ModelDescriptor) -> None:
        """Register a model.

        Args:
            descriptor: Model descriptor.

        Raises:
            ModelAlreadyRegisteredError: If already registered.
        """
        with self._lock:
            model_id = descriptor.model_id

            if model_id in self._models:
                raise ModelAlreadyRegisteredError(model_id)

            self._models[model_id] = descriptor
            # Auto-set to AVAILABLE if not explicitly set
            if descriptor.state == ModelState.UNREGISTERED:
                descriptor.state = ModelState.REGISTERED

            self._emit_event("ModelRegistered", {
                "model_id": model_id,
                "provider_id": descriptor.provider_id,
                "category": descriptor.category.value,
            })

    def unregister(self, model_id: str) -> bool:
        """Unregister a model.

        Args:
            model_id: Model identifier.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if model_id not in self._models:
                return False

            del self._models[model_id]

            self._emit_event("ModelRemoved", {"model_id": model_id})
            return True

    def register_from_catalog(self) -> int:
        """Register all models from the catalog.

        Returns:
            Number of models registered.
        """
        count = 0
        for descriptor in ModelCatalog.get_all_descriptors():
            if descriptor.model_id not in self._models:
                try:
                    self.register(descriptor)
                    count += 1
                except ModelAlreadyRegisteredError:
                    pass
        return count

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, model_id: str) -> ModelDescriptor:
        """Get a model descriptor.

        Args:
            model_id: Model identifier.

        Returns:
            Model descriptor.

        Raises:
            ModelNotFoundError: If not found.
        """
        with self._lock:
            if model_id not in self._models:
                raise ModelNotFoundError(model_id)
            return self._models[model_id]

    def get_or_none(self, model_id: str) -> ModelDescriptor | None:
        """Get a model descriptor or None.

        Args:
            model_id: Model identifier.

        Returns:
            Model descriptor or None.
        """
        with self._lock:
            return self._models.get(model_id)

    def has(self, model_id: str) -> bool:
        """Check if model is registered.

        Args:
            model_id: Model identifier.

        Returns:
            True if registered.
        """
        with self._lock:
            return model_id in self._models

    # =========================================================================
    # Queries
    # =========================================================================

    def list_all(self) -> list[ModelDescriptor]:
        """List all registered models.

        Returns:
            List of model descriptors.
        """
        with self._lock:
            return list(self._models.values())

    def list_by_provider(self, provider_id: str) -> list[ModelDescriptor]:
        """List models by provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            List of model descriptors.
        """
        with self._lock:
            return [d for d in self._models.values() if d.provider_id == provider_id]

    def list_by_category(self, category: ModelCategory) -> list[ModelDescriptor]:
        """List models by category.

        Args:
            category: Model category.

        Returns:
            List of model descriptors.
        """
        with self._lock:
            return [d for d in self._models.values() if d.category == category]

    def list_by_state(self, state: ModelState) -> list[ModelDescriptor]:
        """List models by state.

        Args:
            state: Model state.

        Returns:
            List of model descriptors.
        """
        with self._lock:
            return [d for d in self._models.values() if d.state == state]

    def list_available(self) -> list[ModelDescriptor]:
        """List all available models.

        Returns:
            List of available model descriptors.
        """
        return self.list_by_state(ModelState.AVAILABLE)

    def list_by_capability(self, capability: str) -> list[ModelDescriptor]:
        """List models by capability.

        Args:
            capability: Capability name.

        Returns:
            List of model descriptors with the capability.
        """
        with self._lock:
            return [d for d in self._models.values() if d.supports_capability(capability)]

    def list_by_context_window(self, min_window: int) -> list[ModelDescriptor]:
        """List models by minimum context window.

        Args:
            min_window: Minimum context window size.

        Returns:
            List of model descriptors.
        """
        with self._lock:
            return [d for d in self._models.values() if d.context_window >= min_window]

    def find_best(
        self,
        policy: ModelSelectionPolicy,
        capabilities: list[str] | None = None,
    ) -> ModelDescriptor | None:
        """Find best model based on policy.

        Args:
            policy: Selection policy.
            capabilities: Required capabilities.

        Returns:
            Best model descriptor or None.
        """
        with self._lock:
            # Filter by capabilities if specified
            candidates = list(self._models.values())

            if capabilities:
                candidates = [
                    d for d in candidates
                    if all(d.supports_capability(c) for c in capabilities)
                ]

            if not candidates:
                return None

            # Apply policy
            if policy == ModelSelectionPolicy.FASTEST:
                return min(candidates, key=lambda d: d.latency_ms)
            elif policy == ModelSelectionPolicy.CHEAPEST:
                return min(candidates, key=lambda d: d.pricing.cost_per_input_token)
            elif policy == ModelSelectionPolicy.HIGHEST_QUALITY:
                return max(candidates, key=lambda d: d.quality_score)
            elif policy == ModelSelectionPolicy.LONGEST_CONTEXT:
                return max(candidates, key=lambda d: d.context_window)
            elif policy == ModelSelectionPolicy.REASONING:
                reasoning = [d for d in candidates if d.supports_reasoning]
                if reasoning:
                    return max(reasoning, key=lambda d: d.quality_score)
                return candidates[0]
            elif policy == ModelSelectionPolicy.MULTIMODAL:
                multimodal = [d for d in candidates if d.supports_multimodal]
                if multimodal:
                    return max(multimodal, key=lambda d: d.quality_score)
                return candidates[0]
            else:
                return candidates[0]

    # =========================================================================
    # State Management
    # =========================================================================

    def enable(self, model_id: str) -> bool:
        """Enable a model.

        Args:
            model_id: Model identifier.

        Returns:
            True if enabled.
        """
        with self._lock:
            if model_id not in self._models:
                return False
            self._models[model_id].enable()
            self._emit_event("ModelUpdated", {"model_id": model_id, "action": "enabled"})
            return True

    def disable(self, model_id: str) -> bool:
        """Disable a model.

        Args:
            model_id: Model identifier.

        Returns:
            True if disabled.
        """
        with self._lock:
            if model_id not in self._models:
                return False
            self._models[model_id].disable()
            self._emit_event("ModelUpdated", {"model_id": model_id, "action": "disabled"})
            return True

    def deprecate(self, model_id: str) -> bool:
        """Deprecate a model.

        Args:
            model_id: Model identifier.

        Returns:
            True if deprecated.
        """
        with self._lock:
            if model_id not in self._models:
                return False
            self._models[model_id].deprecate()
            self._emit_event("ModelUpdated", {"model_id": model_id, "action": "deprecated"})
            return True

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

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._models.clear()

    def __len__(self) -> int:
        """Get model count."""
        with self._lock:
            return len(self._models)

    def __contains__(self, model_id: str) -> bool:
        """Check if model is registered."""
        return self.has(model_id)


# Global registry instance
_global_registry: ModelRegistry | None = None
_registry_lock = threading.Lock()


def get_model_registry() -> ModelRegistry:
    """Get the global model registry.

    Returns:
        Global ModelRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = ModelRegistry()
        return _global_registry


def reset_model_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
