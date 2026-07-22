"""Capability Lifecycle Manager for EREN OS Cognitive Capability SDK.

Manages capability lifecycle transitions.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_2.sdk.capability import BaseCapability
from core.PHASE_2.sdk.exceptions import (
    CapabilityExecutionError,
    CapabilityInitializationError,
)
from core.PHASE_2.sdk.types import (
    CapabilityContext,
    CapabilityResult,
    CapabilityState,
    ValidationResult,
)

if TYPE_CHECKING:
    pass


class LifecycleManager:
    """Manages capability lifecycle transitions.

    Handles:
    - Validation
    - Registration
    - Initialization
    - Ready state
    - Execution
    - Shutdown
    """

    def __init__(self):
        """Initialize the lifecycle manager."""
        self._event_handlers: dict[str, list[Callable]] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Lifecycle Transitions
    # =========================================================================

    def validate(self, capability: BaseCapability) -> ValidationResult:
        """Validate a capability.

        Args:
            capability: Capability to validate.

        Returns:
            Validation result.
        """
        result = capability.validate()

        self._emit_event("CapabilityValidated", {
            "capability_id": capability.capability_id,
            "result": result.to_dict(),
        })

        return result

    def register(
        self,
        capability: BaseCapability,
        context: CapabilityContext | None = None,
    ) -> None:
        """Register a capability.

        Args:
            capability: Capability to register.
            context: Optional capability context.

        Raises:
            CapabilityStateError: If capability cannot be registered.
        """
        capability._transition_to(CapabilityState.VALIDATED)
        capability._transition_to(CapabilityState.REGISTERED)

        self._emit_event("CapabilityRegistered", {
            "capability_id": capability.capability_id,
            "version": capability.version,
        })

    def initialize(
        self,
        capability: BaseCapability,
        context: CapabilityContext,
    ) -> None:
        """Initialize a capability.

        Args:
            capability: Capability to initialize.
            context: Capability context.

        Raises:
            CapabilityInitializationError: If initialization fails.
        """
        try:
            capability._transition_to(CapabilityState.INITIALIZED)
            capability.initialize(context)
            capability._transition_to(CapabilityState.READY)

            self._emit_event("CapabilityInitialized", {
                "capability_id": capability.capability_id,
            })

        except Exception as e:
            capability._transition_to(CapabilityState.FAILED)
            raise CapabilityInitializationError(
                f"Failed to initialize capability: {e}",
                capability.capability_id,
            ) from e

    def execute(
        self,
        capability: BaseCapability,
        context: CapabilityContext,
    ) -> CapabilityResult:
        """Execute a capability.

        Args:
            capability: Capability to execute.
            context: Execution context.

        Returns:
            Execution result.

        Raises:
            CapabilityExecutionError: If execution fails.
        """
        start_time = datetime.now(UTC)

        try:
            capability._transition_to(CapabilityState.EXECUTING)
            capability.prepare(context)

            result = capability.execute(context)

            capability.cleanup()
            capability._transition_to(CapabilityState.COMPLETED)

            # Update duration
            end_time = datetime.now(UTC)
            result.duration_ms = int((end_time - start_time).total_seconds() * 1000)

            self._emit_event("CapabilityCompleted", {
                "capability_id": capability.capability_id,
                "duration_ms": result.duration_ms,
                "success": result.success,
            })

            return result

        except Exception as e:
            capability._transition_to(CapabilityState.FAILED)

            end_time = datetime.now(UTC)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            self._emit_event("CapabilityFailed", {
                "capability_id": capability.capability_id,
                "error": str(e),
                "duration_ms": duration_ms,
            })

            raise CapabilityExecutionError(
                f"Failed to execute capability: {e}",
                capability.capability_id,
            ) from e

    def shutdown(self, capability: BaseCapability) -> None:
        """Shutdown a capability.

        Args:
            capability: Capability to shutdown.
        """
        try:
            capability.shutdown()
            capability._transition_to(CapabilityState.DISPOSED)

            self._emit_event("CapabilityDisposed", {
                "capability_id": capability.capability_id,
            })

        except Exception as e:
            capability._transition_to(CapabilityState.FAILED)

            self._emit_event("CapabilityFailed", {
                "capability_id": capability.capability_id,
                "error": f"Shutdown failed: {e}",
            })

    def health_check(self, capability: BaseCapability) -> dict:
        """Health check a capability.

        Args:
            capability: Capability to check.

        Returns:
            Health status dictionary.
        """
        health = capability.health()

        self._emit_event("CapabilityHealthChecked", {
            "capability_id": capability.capability_id,
            "healthy": health.healthy,
        })

        return health.to_dict()

    # =========================================================================
    # Event Handling
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


# Global lifecycle manager
_lifecycle_manager: LifecycleManager | None = None
_manager_lock = threading.Lock()


def get_lifecycle_manager() -> LifecycleManager:
    """Get the global lifecycle manager.

    Returns:
        Global LifecycleManager instance.
    """
    global _lifecycle_manager
    with _manager_lock:
        if _lifecycle_manager is None:
            _lifecycle_manager = LifecycleManager()
        return _lifecycle_manager
