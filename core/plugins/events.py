"""Plugin Events for EREN OS Cognitive Plugin Framework.

Publishes plugin events to the Event Bus.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class PluginEventType(str, Enum):
    """Event types for plugin operations."""

    PLUGIN_DISCOVERED = "plugin_discovered"
    PLUGIN_REGISTERED = "plugin_registered"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_INITIALIZED = "plugin_initialized"
    PLUGIN_ACTIVATED = "plugin_activated"
    PLUGIN_PAUSED = "plugin_paused"
    PLUGIN_FAILED = "plugin_failed"
    PLUGIN_RELOADED = "plugin_reloaded"
    PLUGIN_REMOVED = "plugin_removed"
    PLUGIN_VALIDATED = "plugin_validated"
    PLUGIN_VALIDATION_FAILED = "plugin_validation_failed"
    PLUGIN_DEPENDENCY_MISSING = "plugin_dependency_missing"
    PLUGIN_LIFECYCLE_CHANGED = "plugin_lifecycle_changed"


class PluginEventPublisher:
    """Publishes plugin events.

    Integrates with EREN's Event Bus to publish plugin events.
    """

    def __init__(self, event_bus=None):
        """Initialize the event publisher.

        Args:
            event_bus: Optional Event Bus instance.
        """
        self._event_bus = event_bus
        self._event_history: list[dict] = []
        self._lock = threading.RLock()
        self._subscribers: list[callable] = []

    def set_event_bus(self, event_bus) -> None:
        """Set the Event Bus instance.

        Args:
            event_bus: Event Bus to use.
        """
        self._event_bus = event_bus

    def publish(
        self,
        event_type: PluginEventType | str,
        plugin_id: str = "",
        data: dict | None = None,
    ) -> None:
        """Publish a plugin event.

        Args:
            event_type: Type of event.
            plugin_id: Plugin ID.
            data: Event data.
        """
        event_type_str = event_type.value if isinstance(event_type, Enum) else event_type

        event = {
            "event_type": event_type_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plugin_id": plugin_id,
            "data": data or {},
        }

        with self._lock:
            self._event_history.append(event)

        # Publish to Event Bus if available
        if self._event_bus:
            try:
                from core.events.models import Event, EventType
                self._event_bus.publish(Event(
                    type=EventType.PLAN_CREATED,  # Map to generic event
                    source="plugin",
                    payload=event,
                ))
            except Exception:
                pass

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def subscribe(self, callback: callable) -> None:
        """Subscribe to plugin events.

        Args:
            callback: Function to call with each event.
        """
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from plugin events.

        Args:
            callback: Function to remove.
        """
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def get_event_history(self) -> list[dict]:
        """Get history of published events.

        Returns:
            List of event dictionaries.
        """
        with self._lock:
            return list(self._event_history)

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()


# Global event publisher
_event_publisher: PluginEventPublisher | None = None
_publisher_lock = threading.Lock()


def get_plugin_event_publisher() -> PluginEventPublisher:
    """Get the global plugin event publisher.

    Returns:
        Global PluginEventPublisher instance.
    """
    global _event_publisher
    with _publisher_lock:
        if _event_publisher is None:
            _event_publisher = PluginEventPublisher()
        return _event_publisher
