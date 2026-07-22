"""Routing Context for EREN OS Cognitive Capability Router.

Provides the context used during pipeline selection.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from core.PHASE_2.router.types import RoutingContext

if TYPE_CHECKING:
    pass


@dataclass
class RouterContext:
    """Context passed through routing operations.

    Contains all information needed to make routing decisions.
    """

    # Intent information
    intent_type: str = ""
    intent_data: dict = field(default_factory=dict)

    # Session information
    session_id: str = ""
    correlation_id: str = ""

    # User information
    user_id: str = ""
    tenant_id: str = ""
    hospital_id: str = ""

    # Priority
    priority: int = 0

    # Capabilities
    available_capabilities: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)

    # Context data
    context_data: dict = field(default_factory=dict)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Internal state
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        if self._lock is None:
            self._lock = threading.RLock()

    @classmethod
    def from_intent(
        cls,
        intent_type: str,
        intent_data: dict | None = None,
        **kwargs,
    ) -> RouterContext:
        """Create context from intent.

        Args:
            intent_type: Type of intent.
            intent_data: Intent data.
            **kwargs: Additional context fields.

        Returns:
            RouterContext instance.
        """
        return cls(
            intent_type=intent_type,
            intent_data=intent_data or {},
            **kwargs,
        )

    @classmethod
    def from_routing_context(cls, context: RoutingContext) -> RouterContext:
        """Create from RoutingContext.

        Args:
            context: RoutingContext instance.

        Returns:
            RouterContext instance.
        """
        return cls(
            intent_type=context.intent_type,
            intent_data=context.intent_data,
            session_id=context.session_id,
            correlation_id=context.correlation_id,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            hospital_id=context.hospital_id,
            priority=context.priority,
            available_capabilities=context.available_capabilities,
            required_capabilities=context.required_capabilities,
            context_data=context.context_data,
            metadata=context.metadata,
        )

    # =========================================================================
    # Capability Operations
    # =========================================================================

    def has_capability(self, capability: str) -> bool:
        """Check if capability is available.

        Args:
            capability: Capability name.

        Returns:
            True if capability is available.
        """
        with self._lock:
            return capability in self.available_capabilities

    def has_all_capabilities(self, capabilities: list[str]) -> bool:
        """Check if all capabilities are available.

        Args:
            capabilities: List of capability names.

        Returns:
            True if all capabilities are available.
        """
        with self._lock:
            return all(c in self.available_capabilities for c in capabilities)

    def has_any_capability(self, capabilities: list[str]) -> bool:
        """Check if any capability is available.

        Args:
            capabilities: List of capability names.

        Returns:
            True if any capability is available.
        """
        with self._lock:
            return any(c in self.available_capabilities for c in capabilities)

    def add_capability(self, capability: str) -> None:
        """Add a capability.

        Args:
            capability: Capability name.
        """
        with self._lock:
            if capability not in self.available_capabilities:
                self.available_capabilities.append(capability)

    def remove_capability(self, capability: str) -> bool:
        """Remove a capability.

        Args:
            capability: Capability name.

        Returns:
            True if removed.
        """
        with self._lock:
            if capability in self.available_capabilities:
                self.available_capabilities.remove(capability)
                return True
            return False

    # =========================================================================
    # Context Data Operations
    # =========================================================================

    def set(self, key: str, value: Any) -> None:
        """Set context data.

        Args:
            key: Data key.
            value: Data value.
        """
        with self._lock:
            self.context_data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get context data.

        Args:
            key: Data key.
            default: Default value.

        Returns:
            Data value or default.
        """
        with self._lock:
            return self.context_data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Data key.

        Returns:
            True if key exists.
        """
        with self._lock:
            return key in self.context_data

    def delete(self, key: str) -> bool:
        """Delete context data.

        Args:
            key: Data key.

        Returns:
            True if deleted.
        """
        with self._lock:
            if key in self.context_data:
                del self.context_data[key]
                return True
            return False

    # =========================================================================
    # Metadata Operations
    # =========================================================================

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        with self._lock:
            self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata.

        Args:
            key: Metadata key.
            default: Default value.

        Returns:
            Metadata value or default.
        """
        with self._lock:
            return self.metadata.get(key, default)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_routing_context(self) -> RoutingContext:
        """Convert to RoutingContext.

        Returns:
            RoutingContext instance.
        """
        return RoutingContext(
            intent_type=self.intent_type,
            intent_data=self.intent_data,
            session_id=self.session_id,
            correlation_id=self.correlation_id,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            hospital_id=self.hospital_id,
            priority=self.priority,
            available_capabilities=self.available_capabilities,
            required_capabilities=self.required_capabilities,
            context_data=self.context_data,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "intent_type": self.intent_type,
                "intent_data": dict(self.intent_data),
                "session_id": self.session_id,
                "correlation_id": self.correlation_id,
                "user_id": self.user_id,
                "tenant_id": self.tenant_id,
                "hospital_id": self.hospital_id,
                "priority": self.priority,
                "available_capabilities": list(self.available_capabilities),
                "required_capabilities": list(self.required_capabilities),
                "context_data": dict(self.context_data),
                "metadata": dict(self.metadata),
            }

    def copy(self) -> RouterContext:
        """Create a deep copy.

        Returns:
            New RouterContext with copied data.
        """
        with self._lock:
            return RouterContext(
                intent_type=self.intent_type,
                intent_data=dict(self.intent_data),
                session_id=self.session_id,
                correlation_id=self.correlation_id,
                user_id=self.user_id,
                tenant_id=self.tenant_id,
                hospital_id=self.hospital_id,
                priority=self.priority,
                available_capabilities=list(self.available_capabilities),
                required_capabilities=list(self.required_capabilities),
                context_data=dict(self.context_data),
                metadata=dict(self.metadata),
            )
