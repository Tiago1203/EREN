"""Cognitive Composition Root (CCRoot).

The official composition root for EREN OS.

Architecture only -- no implementations, no business logic.

This component does NOT:
- Implement business logic
- Use AI
- Break existing contracts
- Modify existing motors

It ONLY assembles the EREN Cognitive Operating System.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .composition_builder import CompositionBuilder
from .composition_events import CompositionEventPublisher, CompositionEventType
from .composition_metrics import CompositionMetricsCollector
from .composition_trace import CompositionTraceCollector
from .composition_validator import CompositionValidator
from .exceptions import (
    CompositionBuildException,
    CompositionValidationException,
)
from .module_descriptor import ModuleDescriptor
from .module_loader import ModuleLoader
from .module_registry import ModuleRegistry


class CognitiveCompositionRoot:
    """The main Cognitive Composition Root.

    Responsibilities:
    - Build the DI Container
    - Register modules
    - Register contracts
    - Configure Event Bus
    - Configure Boot Manager
    - Configure Orchestrator
    - Configure all EREN components
    - Validate the system
    - Deliver a ready Runtime

    The Composition Root does NOT:
    - Implement business logic
    - Use AI
    - Break existing contracts
    - Modify existing motors
    """

    def __init__(
        self,
        builder: Optional[CompositionBuilder] = None,
    ):
        """Initialize the composition root.

        Args:
            builder: Optional composition builder.
        """
        self._id = str(uuid.uuid4())
        self._builder = builder or CompositionBuilder()

        # Observability
        self._event_publisher = CompositionEventPublisher()
        self._metrics = CompositionMetricsCollector()
        self._trace = CompositionTraceCollector()

        # State
        self._is_built = False
        self._is_validated = False
        self._runtime: Optional[dict] = None
        self._lock = threading.RLock()
        self._created_at = datetime.now(timezone.utc).isoformat()

        # Publish creation event
        self._event_publisher.publish(
            CompositionEventType.COMPOSITION_STARTED,
            root_id=self._id,
        )

    @property
    def id(self) -> str:
        """Get composition root ID."""
        return self._id

    @property
    def is_built(self) -> bool:
        """Check if root is built."""
        return self._is_built

    @property
    def is_validated(self) -> bool:
        """Check if root is validated."""
        return self._is_validated

    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at

    def with_default_modules(self) -> "CognitiveCompositionRoot":
        """Add default EREN modules.

        Returns:
            Self for chaining.
        """
        self._builder.add_default_modules()
        return self

    def with_module(self, module: ModuleDescriptor) -> "CognitiveCompositionRoot":
        """Add a module.

        Args:
            module: Module descriptor.

        Returns:
            Self for chaining.
        """
        self._builder.add_module(module)
        return self

    def with_modules(
        self,
        modules: list[ModuleDescriptor],
    ) -> "CognitiveCompositionRoot":
        """Add multiple modules.

        Args:
            modules: Module descriptors.

        Returns:
            Self for chaining.
        """
        for module in modules:
            self._builder.add_module(module)
        return self

    def configure(self, **kwargs) -> "CognitiveCompositionRoot":
        """Configure the composition.

        Args:
            **kwargs: Configuration options.

        Returns:
            Self for chaining.
        """
        self._builder.configure(**kwargs)
        return self

    def validate(self) -> "CognitiveCompositionRoot":
        """Validate the composition.

        Returns:
            Self for chaining.

        Raises:
            CompositionValidationException: If validation fails.
        """
        start_time = datetime.now(timezone.utc)

        self._trace.add_entry(
            operation="validate",
            module_name="root",
            success=True,
        )

        self._builder.validate()
        self._is_validated = True

        duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        self._metrics.record_validation_time(duration_ms)

        self._event_publisher.publish(
            CompositionEventType.COMPOSITION_VALIDATED,
            root_id=self._id,
            duration_ms=duration_ms,
        )

        return self

    def build(self) -> dict:
        """Build the composition.

        Returns:
            Runtime dictionary.

        Raises:
            CompositionBuildException: If build fails.
        """
        start_time = datetime.now(timezone.utc)

        self._trace.add_entry(
            operation="build",
            module_name="root",
            success=True,
        )

        self._event_publisher.publish(
            CompositionEventType.COMPOSITION_STARTED,
            root_id=self._id,
        )

        try:
            self._runtime = self._builder.build()
            self._is_built = True

            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            self._metrics.record_build_time(duration_ms)

            self._event_publisher.publish(
                CompositionEventType.COMPOSITION_COMPLETED,
                root_id=self._id,
                duration_ms=duration_ms,
                module_count=len(self._runtime.get("modules", [])),
            )

            self._trace.add_entry(
                operation="build_complete",
                module_name="root",
                duration_ms=duration_ms,
                success=True,
            )

            return self._runtime

        except Exception as e:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            self._metrics.record_build_error()

            self._event_publisher.publish(
                CompositionEventType.COMPOSITION_FAILED,
                root_id=self._id,
                error=str(e),
            )

            self._trace.add_entry(
                operation="build",
                module_name="root",
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

            raise CompositionBuildException(str(e), stage="build")

    def get_trace(self) -> list:
        """Get composition trace."""
        return self._trace.get_all_entries()

    def get_metrics(self) -> dict:
        """Get composition metrics."""
        return self._metrics.to_dict()

    def get_runtime(self) -> Optional[dict]:
        """Get the runtime."""
        return self._runtime

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return False


class CompositionRootFactory:
    """Factory for creating composition roots."""

    @staticmethod
    def create_default() -> CognitiveCompositionRoot:
        """Create a default composition root with all default modules."""
        return CognitiveCompositionRoot().with_default_modules()

    @staticmethod
    def create_builder() -> CompositionBuilder:
        """Create a composition builder."""
        return CompositionBuilder()
