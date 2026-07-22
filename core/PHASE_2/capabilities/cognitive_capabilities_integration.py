"""Cognitive Capabilities Integration (PR-052).

Integration layer for capability resolution.
Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


# =============================================================================
# Capability Events
# =============================================================================


class CapabilityEventType(str, Enum):
    """Types of capability events."""
    REGISTERED = "capability_registered"
    RESOLVED = "capability_resolved"
    UNREGISTERED = "capability_unregistered"
    EXECUTED = "capability_executed"
    FAILED = "capability_failed"


@dataclass
class CapabilityEvent:
    """Capability event."""
    event_type: CapabilityEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    capability_id: str = ""
    session_id: str = ""
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Capability Registry
# =============================================================================


@dataclass
class Capability:
    """A registered capability."""
    id: str
    name: str
    description: str = ""
    handler: Callable | None = None
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class CapabilityRegistry:
    """Registry for capabilities."""

    def __init__(self):
        self._capabilities: dict[str, Capability] = {}
        self._subscribers: list[Callable] = []

    def register(self, capability: Capability) -> None:
        """Register a capability."""
        self._capabilities[capability.id] = capability
        self._publish(CapabilityEvent(
            event_type=CapabilityEventType.REGISTERED,
            capability_id=capability.id,
        ))

    def unregister(self, capability_id: str) -> bool:
        """Unregister a capability."""
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            self._publish(CapabilityEvent(
                event_type=CapabilityEventType.UNREGISTERED,
                capability_id=capability_id,
            ))
            return True
        return False

    def resolve(self, capability_id: str) -> Capability | None:
        """Resolve a capability by ID."""
        capability = self._capabilities.get(capability_id)
        if capability:
            self._publish(CapabilityEvent(
                event_type=CapabilityEventType.RESOLVED,
                capability_id=capability_id,
            ))
        return capability

    def find_by_tag(self, tag: str) -> list[Capability]:
        """Find capabilities by tag."""
        return [c for c in self._capabilities.values() if tag in c.tags]

    def find_by_name(self, name: str) -> list[Capability]:
        """Find capabilities by name pattern."""
        return [c for c in self._capabilities.values() if name.lower() in c.name.lower()]

    def list_all(self) -> list[Capability]:
        """List all registered capabilities."""
        return list(self._capabilities.values())

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to capability events."""
        self._subscribers.append(callback)

    def _publish(self, event: CapabilityEvent) -> None:
        """Publish an event."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass


# =============================================================================
# Capability Resolver
# =============================================================================


class CapabilityResolver:
    """Resolves and executes capabilities."""

    def __init__(self, registry: CapabilityRegistry | None = None):
        self._registry = registry or CapabilityRegistry()

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    def resolve_and_execute(
        self,
        capability_id: str,
        context: dict[str, Any] | None = None,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Resolve and execute a capability."""
        capability = self._registry.resolve(capability_id)
        
        if not capability:
            return {
                "success": False,
                "error": f"Capability not found: {capability_id}",
            }

        if not capability.handler:
            return {
                "success": False,
                "error": f"Capability has no handler: {capability_id}",
            }

        try:
            result = capability.handler(context or {})
            return {
                "success": True,
                "capability_id": capability_id,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
