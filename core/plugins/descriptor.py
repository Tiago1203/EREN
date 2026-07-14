"""Plugin Descriptor for EREN OS Cognitive Plugin Framework.

Provides the descriptor for plugin metadata and state management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.plugins.types import PluginManifest, PluginState

if TYPE_CHECKING:
    pass


@dataclass
class PluginDescriptor:
    """Descriptor for a plugin instance.

    Contains all metadata and state information for a plugin.
    """

    # Core information
    manifest: PluginManifest
    state: PluginState = PluginState.DISCOVERED

    # Instance
    instance: Any = None
    factory: Any = None

    # Error tracking
    error: str = ""
    last_error: datetime | None = None

    # Timing
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registered_at: datetime | None = None
    loaded_at: datetime | None = None
    initialized_at: datetime | None = None
    activated_at: datetime | None = None
    paused_at: datetime | None = None
    unloaded_at: datetime | None = None

    # Retry tracking
    retry_count: int = 0
    max_retries: int = 3

    # Additional metadata
    metadata: dict = field(default_factory=dict)
    _lock: object = field(default_factory=lambda: __import__('threading').RLock(), repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        import threading
        if not hasattr(self, '_lock') or self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self.manifest.plugin_id

    @property
    def name(self) -> str:
        """Get plugin name."""
        return self.manifest.name

    @property
    def version(self) -> str:
        """Get plugin version."""
        return self.manifest.version

    @property
    def category(self) -> str:
        """Get plugin category."""
        return self.manifest.category.value

    @property
    def priority(self) -> int:
        """Get plugin priority."""
        return self.manifest.priority

    @property
    def contracts(self) -> tuple[str, ...]:
        """Get plugin contracts."""
        return self.manifest.contracts

    @property
    def dependencies(self) -> tuple[str, ...]:
        """Get plugin dependencies."""
        return self.manifest.dependencies

    @property
    def capabilities(self) -> tuple[str, ...]:
        """Get plugin capabilities."""
        return self.manifest.capabilities

    @property
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.state == PluginState.ACTIVE

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.state in (
            PluginState.LOADED,
            PluginState.INITIALIZED,
            PluginState.ACTIVE,
            PluginState.PAUSED,
        )

    @property
    def can_retry(self) -> bool:
        """Check if plugin can retry."""
        return self.retry_count < self.max_retries

    @property
    def uptime_seconds(self) -> float | None:
        """Get uptime in seconds."""
        if not self.activated_at:
            return None
        return (datetime.now(timezone.utc) - self.activated_at).total_seconds()

    # =========================================================================
    # State Management
    # =========================================================================

    def transition_to(self, new_state: PluginState) -> bool:
        """Transition to a new state.

        Args:
            new_state: New state.

        Returns:
            True if transition was successful.
        """
        with self._lock:
            if not PluginState.can_transition(self.state, new_state):
                return False

            old_state = self.state
            self.state = new_state

            # Update timestamps
            now = datetime.now(timezone.utc)
            if new_state == PluginState.REGISTERED:
                self.registered_at = now
            elif new_state == PluginState.LOADED:
                self.loaded_at = now
            elif new_state == PluginState.INITIALIZED:
                self.initialized_at = now
            elif new_state == PluginState.ACTIVE:
                self.activated_at = now
            elif new_state == PluginState.PAUSED:
                self.paused_at = now
            elif new_state == PluginState.UNLOADED:
                self.unloaded_at = now
            elif new_state == PluginState.FAILED:
                self.last_error = now
                self.retry_count += 1

            return True

    def set_error(self, error: str) -> None:
        """Set error information.

        Args:
            error: Error message.
        """
        with self._lock:
            self.error = error
            self.last_error = datetime.now(timezone.utc)

    def clear_error(self) -> None:
        """Clear error information."""
        with self._lock:
            self.error = ""
            self.last_error = None

    def reset_retry(self) -> None:
        """Reset retry counter."""
        with self._lock:
            self.retry_count = 0

    # =========================================================================
    # Instance Management
    # =========================================================================

    def set_instance(self, instance: Any) -> None:
        """Set plugin instance.

        Args:
            instance: Plugin instance.
        """
        with self._lock:
            self.instance = instance

    def get_instance(self) -> Any | None:
        """Get plugin instance."""
        with self._lock:
            return self.instance

    def has_instance(self) -> bool:
        """Check if plugin has an instance."""
        with self._lock:
            return self.instance is not None

    # =========================================================================
    # Utility
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "plugin_id": self.plugin_id,
                "name": self.name,
                "version": self.version,
                "category": self.category,
                "priority": self.priority,
                "state": self.state.value,
                "contracts": list(self.contracts),
                "dependencies": list(self.dependencies),
                "capabilities": list(self.capabilities),
                "error": self.error,
                "retry_count": self.retry_count,
                "can_retry": self.can_retry,
                "discovered_at": self.discovered_at.isoformat(),
                "registered_at": self.registered_at.isoformat() if self.registered_at else None,
                "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
                "initialized_at": self.initialized_at.isoformat() if self.initialized_at else None,
                "activated_at": self.activated_at.isoformat() if self.activated_at else None,
                "uptime_seconds": self.uptime_seconds,
                "metadata": dict(self.metadata),
            }

    def copy(self) -> "PluginDescriptor":
        """Create a copy of the descriptor.

        Returns:
            New PluginDescriptor copy.
        """
        with self._lock:
            return PluginDescriptor(
                manifest=self.manifest,
                state=self.state,
                instance=self.instance,
                factory=self.factory,
                error=self.error,
                last_error=self.last_error,
                discovered_at=self.discovered_at,
                registered_at=self.registered_at,
                loaded_at=self.loaded_at,
                initialized_at=self.initialized_at,
                activated_at=self.activated_at,
                paused_at=self.paused_at,
                unloaded_at=self.unloaded_at,
                retry_count=self.retry_count,
                max_retries=self.max_retries,
                metadata=dict(self.metadata),
            )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PluginDescriptor("
            f"id={self.plugin_id}, "
            f"version={self.version}, "
            f"state={self.state.value})"
        )
