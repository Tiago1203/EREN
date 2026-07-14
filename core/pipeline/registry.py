"""Pipeline Registry for EREN OS Cognitive Capability Pipeline.

Central registry for managing available pipelines.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.pipeline.exceptions import (
    PipelineAlreadyRegisteredError,
    PipelineNotFoundError,
)

if TYPE_CHECKING:
    from core.pipeline.pipeline import CognitivePipeline


class PipelineRegistry:
    """Registry for managing pipeline instances.

    Provides:
    - Pipeline registration
    - Pipeline retrieval
    - Pipeline discovery
    - Pipeline factories
    """

    def __init__(self):
        """Initialize the registry."""
        self._pipelines: dict[str, CognitivePipeline] = {}
        self._factories: dict[str, Callable[[], CognitivePipeline]] = {}
        self._lock = threading.RLock()

    def register(
        self,
        name: str,
        pipeline: CognitivePipeline,
        replace: bool = False,
    ) -> None:
        """Register a pipeline.

        Args:
            name: Pipeline name.
            pipeline: Pipeline instance.
            replace: Whether to replace existing.

        Raises:
            PipelineAlreadyRegisteredError: If pipeline exists and replace=False.
        """
        with self._lock:
            if name in self._pipelines and not replace:
                raise PipelineAlreadyRegisteredError(name)

            self._pipelines[name] = pipeline

    def register_factory(
        self,
        name: str,
        factory: Callable[[], CognitivePipeline],
        replace: bool = False,
    ) -> None:
        """Register a pipeline factory.

        Args:
            name: Pipeline name.
            factory: Factory function.
            replace: Whether to replace existing.
        """
        with self._lock:
            if name in self._factories and not replace:
                raise PipelineAlreadyRegisteredError(name)

            self._factories[name] = factory

    def get(self, name: str) -> CognitivePipeline:
        """Get a pipeline by name.

        Args:
            name: Pipeline name.

        Returns:
            Pipeline instance.

        Raises:
            PipelineNotFoundError: If not found.
        """
        with self._lock:
            if name in self._pipelines:
                return self._pipelines[name]

            if name in self._factories:
                # Create from factory
                return self._factories[name]()

            raise PipelineNotFoundError(name)

    def get_or_create(self, name: str) -> CognitivePipeline:
        """Get a pipeline or create if not exists.

        If a factory is registered, creates a new instance.
        If a pipeline is registered, returns it.
        If neither exists, raises error.

        Args:
            name: Pipeline name.

        Returns:
            Pipeline instance.
        """
        return self.get(name)

    def unregister(self, name: str) -> bool:
        """Unregister a pipeline.

        Args:
            name: Pipeline name.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if name in self._pipelines:
                del self._pipelines[name]
                return True
            if name in self._factories:
                del self._factories[name]
                return True
            return False

    def list_pipelines(self) -> list[str]:
        """List all registered pipeline names.

        Returns:
            List of pipeline names.
        """
        with self._lock:
            return list(set(list(self._pipelines.keys()) + list(self._factories.keys())))

    def list_instances(self) -> list[str]:
        """List registered pipeline instances (not factories).

        Returns:
            List of pipeline names.
        """
        with self._lock:
            return list(self._pipelines.keys())

    def list_factories(self) -> list[str]:
        """List registered factories.

        Returns:
            List of factory names.
        """
        with self._lock:
            return list(self._factories.keys())

    def __contains__(self, name: str) -> bool:
        """Check if pipeline is registered.

        Args:
            name: Pipeline name.

        Returns:
            True if registered.
        """
        with self._lock:
            return name in self._pipelines or name in self._factories

    def __len__(self) -> int:
        """Get count of registered pipelines.

        Returns:
            Total count.
        """
        with self._lock:
            return len(self._pipelines) + len(self._factories)

    def clear(self) -> None:
        """Clear all registered pipelines."""
        with self._lock:
            self._pipelines.clear()
            self._factories.clear()


# Global registry instance
_global_registry: PipelineRegistry | None = None
_registry_lock = threading.Lock()


def get_pipeline_registry() -> PipelineRegistry:
    """Get the global pipeline registry.

    Returns:
        Global PipelineRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = PipelineRegistry()
            _register_default_pipelines(_global_registry)
        return _global_registry


def _register_default_pipelines(registry: PipelineRegistry) -> None:
    """Register default pipeline factories.

    Args:
        registry: Registry to register with.
    """
    from core.pipeline.builder import DefaultPipelineBuilder

    # Register factory functions
    registry.register_factory("default", DefaultPipelineBuilder.create_default)
    registry.register_factory("minimal", DefaultPipelineBuilder.create_minimal)
    registry.register_factory("research", DefaultPipelineBuilder.create_research)


def register_pipeline(name: str, pipeline: CognitivePipeline, replace: bool = False) -> None:
    """Register a pipeline in the global registry.

    Args:
        name: Pipeline name.
        pipeline: Pipeline instance.
        replace: Whether to replace existing.
    """
    get_pipeline_registry().register(name, pipeline, replace)


def get_pipeline(name: str) -> CognitivePipeline:
    """Get a pipeline from the global registry.

    Args:
        name: Pipeline name.

    Returns:
        Pipeline instance.
    """
    return get_pipeline_registry().get(name)


def unregister_pipeline(name: str) -> bool:
    """Unregister a pipeline from the global registry.

    Args:
        name: Pipeline name.

    Returns:
        True if unregistered.
    """
    return get_pipeline_registry().unregister(name)
