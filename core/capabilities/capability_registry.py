"""Cognitive Capability Registry.

The central registry for all cognitive capabilities within EREN.
This is the catalog that the Orchestrator queries to discover capabilities.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Sequence

from .capability import Capability
from .descriptor import CapabilityDescriptor, CapabilityMatch, RegistrySnapshot
from .exceptions import (
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
    CapabilityRegistryError,
)
from .types import (
    CapabilityCategory,
    CapabilityFilter,
    CapabilityId,
    CapabilityStatus,
    SearchOptions,
)


class CapabilityRegistry:
    """Central registry for cognitive capabilities.

    The registry maintains a catalog of all available cognitive capabilities
    within EREN. The Orchestrator queries this registry to discover capabilities
    rather than knowing about specific implementations.

    Features:
    - Thread-safe registration and lookup
    - Category-based organization
    - Event-based indexing
    - Provider-based organization
    - Advanced search with filters
    - Dependency tracking
    - Snapshot for auditing

    Example:
        registry = CapabilityRegistry()

        # Register a capability
        registry.register(my_capability)

        # Discover capabilities
        diagnostics = registry.find_by_category(CapabilityCategory.DIAGNOSTIC)

        # Search with filters
        results = registry.search(SearchOptions(
            filter=CapabilityFilter(
                min_priority=CapabilityPriority.HIGH,
                active_only=True,
            )
        ))

        # Resolve (using resolver)
        match = resolver.resolve(ResolutionCriteria(category=CapabilityCategory.DIAGNOSTIC))
    """

    def __init__(self) -> None:
        """Initialize the capability registry."""
        # Primary storage: capability_id -> Capability
        self._capabilities: dict[str, Capability] = {}

        # Indexes for fast lookup
        self._by_category: dict[CapabilityCategory, list[str]] = defaultdict(list)
        self._by_provider: dict[str, list[str]] = defaultdict(list)
        self._by_status: dict[CapabilityStatus, list[str]] = defaultdict(list)
        self._by_event: dict[str, list[str]] = defaultdict(list)

        # Descriptors
        self._descriptors: dict[str, CapabilityDescriptor] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Version
        self._version = "1.0.0"

    # =========================================================================
    # Registration Operations
    # =========================================================================

    def register(
        self,
        capability: Capability,
        descriptor: CapabilityDescriptor | None = None,
        *,
        replace: bool = False,
    ) -> None:
        """Register a capability in the registry.

        Args:
            capability: The capability to register.
            descriptor: Optional extended descriptor.
            replace: If True, replace existing capability.

        Raises:
            CapabilityAlreadyRegisteredError: If capability exists and replace=False.
        """
        with self._lock:
            cap_id = capability.id_string

            if cap_id in self._capabilities and not replace:
                raise CapabilityAlreadyRegisteredError(cap_id)

            # Store capability
            self._capabilities[cap_id] = capability

            # Create/store descriptor
            if descriptor is None:
                descriptor = CapabilityDescriptor.from_capability(capability)
            self._descriptors[cap_id] = descriptor

            # Update indexes
            self._index_capability(capability)

    def unregister(self, capability_id: str) -> None:
        """Unregister a capability.

        Args:
            capability_id: The ID of the capability to remove.

        Raises:
            CapabilityNotFoundError: If capability not found.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)

            capability = self._capabilities[capability_id]

            # Remove from indexes
            self._unindex_capability(capability)

            # Remove from storage
            del self._capabilities[capability_id]
            del self._descriptors[capability_id]

    def update(
        self,
        capability_id: str,
        capability: Capability,
    ) -> None:
        """Update an existing capability.

        Args:
            capability_id: The ID of the capability to update.
            capability: The updated capability.

        Raises:
            CapabilityNotFoundError: If capability not found.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)

            # Unindex old
            old_cap = self._capabilities[capability_id]
            self._unindex_capability(old_cap)

            # Update
            self._capabilities[capability_id] = capability
            self._index_capability(capability)

    def set_status(
        self,
        capability_id: str,
        status: CapabilityStatus,
    ) -> None:
        """Update the status of a capability.

        Args:
            capability_id: The ID of the capability.
            status: The new status.

        Raises:
            CapabilityNotFoundError: If capability not found.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)

            capability = self._capabilities[capability_id]

            # Create updated capability (immutable)
            from dataclasses import replace
            updated = replace(capability, status=status)

            # Update indexes
            self._unindex_capability(capability)
            self._capabilities[capability_id] = updated
            self._index_capability(updated)

    # =========================================================================
    # Retrieval Operations
    # =========================================================================

    def get(self, capability_id: str) -> Capability:
        """Get a capability by ID.

        Args:
            capability_id: The capability ID.

        Returns:
            The capability.

        Raises:
            CapabilityNotFoundError: If not found.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)
            return self._capabilities[capability_id]

    def get_descriptor(self, capability_id: str) -> CapabilityDescriptor:
        """Get the descriptor for a capability.

        Args:
            capability_id: The capability ID.

        Returns:
            The capability descriptor.
        """
        with self._lock:
            if capability_id not in self._descriptors:
                raise CapabilityNotFoundError(capability_id)
            return self._descriptors[capability_id]

    def list(self) -> Sequence[Capability]:
        """List all registered capabilities."""
        with self._lock:
            return tuple(self._capabilities.values())

    def list_descriptors(self) -> Sequence[CapabilityDescriptor]:
        """List all capability descriptors."""
        with self._lock:
            return tuple(self._descriptors.values())

    def __contains__(self, capability_id: object) -> bool:
        """Check if a capability is registered."""
        if not isinstance(capability_id, str):
            return False
        return capability_id in self._capabilities

    def __len__(self) -> int:
        """Get the number of registered capabilities."""
        return len(self._capabilities)

    # =========================================================================
    # Discovery Operations
    # =========================================================================

    def find_by_category(
        self,
        category: CapabilityCategory,
    ) -> Sequence[Capability]:
        """Find capabilities by category.

        Args:
            category: The category to search.

        Returns:
            Capabilities in that category.
        """
        with self._lock:
            cap_ids = self._by_category.get(category, [])
            return tuple(self._capabilities[cid] for cid in cap_ids if cid in self._capabilities)

    def find_by_provider(
        self,
        provider_id: str,
    ) -> Sequence[Capability]:
        """Find capabilities by provider.

        Args:
            provider_id: The provider ID.

        Returns:
            Capabilities from that provider.
        """
        with self._lock:
            cap_ids = self._by_provider.get(provider_id, [])
            return tuple(self._capabilities[cid] for cid in cap_ids if cid in self._capabilities)

    def find_by_status(
        self,
        status: CapabilityStatus,
    ) -> Sequence[Capability]:
        """Find capabilities by status.

        Args:
            status: The status to search.

        Returns:
            Capabilities with that status.
        """
        with self._lock:
            cap_ids = self._by_status.get(status, [])
            return tuple(self._capabilities[cid] for cid in cap_ids if cid in self._capabilities)

    def find_by_event(
        self,
        event_type: str,
        direction: str = "both",
    ) -> Sequence[Capability]:
        """Find capabilities by event.

        Args:
            event_type: The event type.
            direction: "publishes", "consumes", or "both".

        Returns:
            Capabilities that publish/consume the event.
        """
        with self._lock:
            cap_ids = self._by_event.get(event_type, [])
            results = []
            for cid in cap_ids:
                if cid not in self._capabilities:
                    continue
                cap = self._capabilities[cid]
                if direction == "publishes" and cap.publishes_event(event_type):
                    results.append(cap)
                elif direction == "consumes" and cap.consumes_event(event_type):
                    results.append(cap)
                elif direction == "both":
                    results.append(cap)
            return tuple(results)

    def find_active(self) -> Sequence[Capability]:
        """Find all active capabilities.

        Returns:
            Active capabilities.
        """
        return self.find_by_status(CapabilityStatus.ACTIVE)

    def find_available(self) -> Sequence[Capability]:
        """Find all available capabilities.

        Returns:
            Available capabilities.
        """
        with self._lock:
            results = []
            for status in (CapabilityStatus.ACTIVE, CapabilityStatus.AVAILABLE):
                results.extend(self.find_by_status(status))
            return tuple(results)

    def search(
        self,
        options: SearchOptions,
    ) -> list[Capability]:
        """Search capabilities with filters and pagination.

        Args:
            options: Search options including filter and pagination.

        Returns:
            Matching capabilities.
        """
        with self._lock:
            results = list(self._capabilities.values())

            # Apply filter
            if options.filter:
                results = [c for c in results if options.filter.matches(c)]

            # Sort
            if options.sort_by == "priority":
                results.sort(key=lambda c: c.priority.value, reverse=not options.ascending)
            elif options.sort_by == "name":
                results.sort(key=lambda c: c.name, reverse=not options.ascending)
            elif options.sort_by == "category":
                results.sort(key=lambda c: c.category.value, reverse=not options.ascending)

            # Pagination
            if options.offset:
                results = results[options.offset:]
            if options.limit:
                results = results[:options.limit]

            return results

    # =========================================================================
    # Statistics and Snapshot
    # =========================================================================

    def get_statistics(self) -> dict:
        """Get registry statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            return {
                "total": len(self._capabilities),
                "by_category": {
                    cat.value: len(caps)
                    for cat, caps in self._by_category.items()
                },
                "by_provider": dict(self._by_provider),
                "by_status": {
                    status.name: len(caps)
                    for status, caps in self._by_status.items()
                },
            }

    def snapshot(self) -> RegistrySnapshot:
        """Create a point-in-time snapshot.

        Returns:
            RegistrySnapshot with current state.
        """
        with self._lock:
            return RegistrySnapshot.from_registry(
                capabilities=list(self._capabilities.values()),
                descriptors=list(self._descriptors.values()),
                version=self._version,
            )

    # =========================================================================
    # Indexing (Internal)
    # =========================================================================

    def _index_capability(self, capability: Capability) -> None:
        """Index a capability for fast lookup."""
        cap_id = capability.id_string

        # By category
        self._by_category[capability.category].append(cap_id)

        # By provider
        self._by_provider[capability.provider_id].append(cap_id)

        # By status
        self._by_status[capability.status].append(cap_id)

        # By events
        for event in capability.publishes:
            self._by_event[event.event_type].append(cap_id)
        for event in capability.consumes:
            self._by_event[event.event_type].append(cap_id)

    def _unindex_capability(self, capability: Capability) -> None:
        """Remove capability from indexes."""
        cap_id = capability.id_string

        # From category
        if capability.category in self._by_category:
            self._by_category[capability.category] = [
                c for c in self._by_category[capability.category]
                if c != cap_id
            ]

        # From provider
        if capability.provider_id in self._by_provider:
            self._by_provider[capability.provider_id] = [
                c for c in self._by_provider[capability.provider_id]
                if c != cap_id
            ]

        # From status
        if capability.status in self._by_status:
            self._by_status[capability.status] = [
                c for c in self._by_status[capability.status]
                if c != cap_id
            ]

        # From events
        for event in capability.publishes:
            if event.event_type in self._by_event:
                self._by_event[event.event_type] = [
                    c for c in self._by_event[event.event_type]
                    if c != cap_id
                ]
        for event in capability.consumes:
            if event.event_type in self._by_event:
                self._by_event[event.event_type] = [
                    c for c in self._by_event[event.event_type]
                    if c != cap_id
                ]
