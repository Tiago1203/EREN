"""Base Capability for EREN OS Cognitive Capability SDK.

Provides the base class for all cognitive capabilities.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.sdk.types import (
    CapabilityState,
    CapabilityMetadata,
    CapabilityContext,
    CapabilityResult,
    CapabilityHealth,
    ValidationResult,
    CapabilityCategory,
)
from core.sdk.exceptions import CapabilityStateError

if TYPE_CHECKING:
    pass


@dataclass
class BaseCapability(ABC):
    """Base class for all cognitive capabilities.

    All capabilities must implement:
    - initialize(): Set up capability
    - execute(context): Execute capability logic
    - shutdown(): Clean up resources

    Optional methods:
    - health(): Return health status
    - metadata(): Return capability metadata
    """

    # Identity
    _capability_id: str = ""
    _version: str = "1.0.0"

    # State
    _state: CapabilityState = CapabilityState.CREATED
    _state_lock: threading.RLock = field(default_factory=threading.RLock)

    # Lifecycle timestamps
    _created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _initialized_at: datetime | None = None
    _ready_at: datetime | None = None
    _disposed_at: datetime | None = None

    # Context
    _context: CapabilityContext | None = None

    # Health
    _health_check_interval: int = 60  # seconds
    _last_health_check: datetime | None = None

    # Configuration
    _config: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize base capability."""
        self._state_lock = threading.RLock()

    # =========================================================================
    # Identity
    # =========================================================================

    @property
    def capability_id(self) -> str:
        """Get capability ID."""
        return self._capability_id

    @property
    def version(self) -> str:
        """Get capability version."""
        return self._version

    @property
    def state(self) -> CapabilityState:
        """Get current state."""
        with self._state_lock:
            return self._state

    @property
    def is_initialized(self) -> bool:
        """Check if capability is initialized."""
        return self._initialized_at is not None

    @property
    def is_ready(self) -> bool:
        """Check if capability is ready."""
        return self._state == CapabilityState.READY

    # =========================================================================
    # State Management
    # =========================================================================

    def _transition_to(self, new_state: CapabilityState) -> bool:
        """Transition to a new state.

        Args:
            new_state: Target state.

        Returns:
            True if transition succeeded.

        Raises:
            CapabilityStateError: If transition is invalid.
        """
        with self._state_lock:
            if not CapabilityState.can_transition(self._state, new_state):
                raise CapabilityStateError(
                    f"Cannot transition from {self._state.value} to {new_state.value}",
                    self.capability_id,
                    self._state.value,
                )

            old_state = self._state
            self._state = new_state

            # Update timestamps
            now = datetime.now(timezone.utc)
            if new_state == CapabilityState.INITIALIZED:
                self._initialized_at = now
            elif new_state == CapabilityState.READY:
                self._ready_at = now
            elif new_state == CapabilityState.DISPOSED:
                self._disposed_at = now

            return True

    # =========================================================================
    # Required Methods (Abstract)
    # =========================================================================

    @abstractmethod
    def initialize(self, context: CapabilityContext) -> None:
        """Initialize the capability.

        Called once during capability setup.

        Args:
            context: Capability context with runtime information.

        Raises:
            CapabilityInitializationError: If initialization fails.
        """
        pass

    @abstractmethod
    def execute(self, context: CapabilityContext) -> CapabilityResult:
        """Execute the capability.

        Main execution logic.

        Args:
            context: Capability context with execution information.

        Returns:
            Capability result with data or error.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the capability.

        Called once during cleanup. Must release all resources.
        """
        pass

    # =========================================================================
    # Optional Methods
    # =========================================================================

    def health(self) -> CapabilityHealth:
        """Return health status.

        Override to provide custom health check logic.

        Returns:
            Capability health status.
        """
        self._last_health_check = datetime.now(timezone.utc)
        return CapabilityHealth(
            healthy=self._state in (CapabilityState.READY, CapabilityState.INITIALIZED),
            message="Capability is healthy" if self.is_ready else "Capability not ready",
        )

    def metadata(self) -> CapabilityMetadata:
        """Return capability metadata.

        Override to provide custom metadata.

        Returns:
            Capability metadata.
        """
        return CapabilityMetadata(
            name=self.__class__.__name__,
            version=self._version,
            category=CapabilityCategory.CUSTOM,
        )

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    def validate(self) -> ValidationResult:
        """Validate the capability.

        Override to add custom validation logic.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        # Check metadata
        metadata = self.metadata()
        if not metadata.name:
            result.is_valid = False
            result.errors.append("Missing capability name in metadata")

        if not metadata.version:
            result.is_valid = False
            result.errors.append("Missing version in metadata")

        return result

    def prepare(self, context: CapabilityContext) -> None:
        """Prepare the capability for execution.

        Called before execute(). Can be overridden.

        Args:
            context: Capability context.
        """
        self._context = context

    def cleanup(self) -> None:
        """Cleanup after execution.

        Called after execute(). Can be overridden.
        """
        pass

    # =========================================================================
    # Configuration
    # =========================================================================

    def configure(self, config: dict) -> None:
        """Configure the capability.

        Args:
            config: Configuration dictionary.
        """
        self._config = config

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value.

        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)

    # =========================================================================
    # Utility
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "state": self._state.value,
            "is_initialized": self.is_initialized,
            "is_ready": self.is_ready,
            "created_at": self._created_at.isoformat(),
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "ready_at": self._ready_at.isoformat() if self._ready_at else None,
            "metadata": self.metadata().to_dict(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.capability_id}, "
            f"version={self.version}, "
            f"state={self._state.value})"
        )
