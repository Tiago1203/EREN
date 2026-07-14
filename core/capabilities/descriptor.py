"""Capability descriptors and snapshots.

Provides extended descriptor types for capability metadata and snapshots.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .capability import Capability
from .types import (
    CapabilityCategory,
    CapabilityPriority,
    CapabilityStatus,
)

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    """Extended descriptor for a capability with full metadata.

    While Capability is the core abstraction, CapabilityDescriptor includes
    additional metadata useful for registry operations, documentation, and
    tooling.

    This is the canonical representation stored in the registry.
    """

    # Core capability
    capability: Capability

    # Extended metadata
    display_name: str = ""
    short_description: str = ""
    long_description: str = ""

    # Usage information
    usage_examples: tuple[str, ...] = field(default_factory=tuple)
    input_schema: str = ""  # JSON schema for inputs
    output_schema: str = ""  # JSON schema for outputs

    # Deprecation info
    replacement_capability_id: str = ""
    migration_guide: str = ""

    @classmethod
    def from_capability(
        cls,
        capability: Capability,
        **kwargs,
    ) -> CapabilityDescriptor:
        """Create a descriptor from a capability."""
        return cls(
            capability=capability,
            display_name=kwargs.get("display_name", capability.name),
            short_description=kwargs.get("short_description", capability.description[:100]),
            long_description=kwargs.get("long_description", capability.description),
        )

    @property
    def capability_id(self) -> str:
        """Get the capability ID."""
        return self.capability.id_string

    @property
    def category(self) -> CapabilityCategory:
        """Get the category."""
        return self.capability.category

    @property
    def status(self) -> CapabilityStatus:
        """Get the status."""
        return self.capability.status

    @property
    def priority(self) -> CapabilityPriority:
        """Get the priority."""
        return self.capability.priority

    @property
    def provider_id(self) -> str:
        """Get the provider ID."""
        return self.capability.provider_id

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.display_name} ({self.capability_id})"


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    """Point-in-time snapshot of the capability registry.

    Useful for:
    - Audit and compliance
    - Debugging and troubleshooting
    - Version rollback
    - Distributed registry synchronization
    - Capability versioning
    """

    timestamp: str
    version: str  # Registry version
    capability_count: int
    capabilities: tuple[Capability, ...]
    descriptors: tuple[CapabilityDescriptor, ...]

    # Statistics
    active_count: int
    deprecated_count: int
    failed_count: int
    by_category: dict[str, int]
    by_provider: dict[str, int]

    @classmethod
    def from_registry(
        cls,
        capabilities: list[Capability],
        descriptors: list[CapabilityDescriptor],
        version: str = "1.0.0",
    ) -> RegistrySnapshot:
        """Create a snapshot from current registry state."""
        timestamp = datetime.now(UTC).isoformat()

        # Calculate statistics
        active = sum(1 for c in capabilities if c.status == CapabilityStatus.ACTIVE)
        deprecated = sum(1 for c in capabilities if c.status == CapabilityStatus.DEPRECATED)
        failed = sum(1 for c in capabilities if c.status == CapabilityStatus.FAILED)

        by_category: dict[str, int] = {}
        for c in capabilities:
            cat = c.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        by_provider: dict[str, int] = {}
        for c in capabilities:
            by_provider[c.provider_id] = by_provider.get(c.provider_id, 0) + 1

        return cls(
            timestamp=timestamp,
            version=version,
            capability_count=len(capabilities),
            capabilities=tuple(capabilities),
            descriptors=tuple(descriptors),
            active_count=active,
            deprecated_count=deprecated,
            failed_count=failed,
            by_category=by_category,
            by_provider=by_provider,
        )


@dataclass(frozen=True, slots=True)
class CapabilityVersion:
    """Version information for a capability."""

    version: str
    changelog: str = ""
    breaking_changes: bool = False
    released_at: str = ""
    deprecated_at: str = ""
    removed_at: str = ""


@dataclass
class CapabilityMatch:
    """Result of a capability match operation."""

    capability: Capability
    score: float  # 0.0 to 1.0 match score
    match_reasons: tuple[str, ...] = field(default_factory=tuple)
    alternative_matches: tuple[Capability, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return f"{self.capability.name} (score: {self.score:.2f})"
