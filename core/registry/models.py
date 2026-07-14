"""Models for the Engine Registry.

Defines the EngineDescriptor - the complete description of a registered engine
including all metadata, capabilities, dependencies, and event contracts.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .types import (
    Capability,
    EngineMetadata,
    EnginePriority,
    EngineStatus,
    EventContracts,
    VersionRequirement,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Engine Descriptor
# =============================================================================


@dataclass(frozen=True, slots=True)
class EngineDescriptor:
    """Complete descriptor of a registered cognitive engine.

    Contains all information about an engine needed for:
    - Discovery and selection
    - Dependency validation
    - Event contract verification
    - Version compatibility checking
    - Audit and documentation

    This is the canonical representation of an engine in the registry.
    """

    # Identity
    engine_id: str  # Unique identifier (matches engine.name)
    display_name: str  # Human-readable name
    description: str  # What the engine does

    # Versioning
    version: str  # Semantic version of the engine
    min_er_en_version: str  # Minimum EREN version required

    # Capabilities
    capabilities: tuple[Capability, ...] = field(default_factory=tuple)

    # Priority and Status
    priority: EnginePriority = EnginePriority.NORMAL
    status: EngineStatus = EngineStatus.INACTIVE

    # Dependencies
    dependencies: tuple[VersionRequirement, ...] = field(default_factory=tuple)

    # Event Contracts
    events: EventContracts = field(default_factory=EventContracts)

    # Metadata
    metadata: EngineMetadata = field(default_factory=EngineMetadata)

    # Factory method for common engines
    @classmethod
    def create(
        cls,
        engine_id: str,
        display_name: str,
        description: str,
        version: str = "1.0.0",
        capabilities: list[Capability] | None = None,
        priority: EnginePriority = EnginePriority.NORMAL,
        events: EventContracts | None = None,
        author: str = "",
    ) -> EngineDescriptor:
        """Create a new engine descriptor with common defaults.

        Args:
            engine_id: Unique identifier for the engine
            display_name: Human-readable name
            description: What the engine does
            version: Semantic version
            capabilities: List of capabilities
            priority: Execution priority
            events: Event contracts
            author: Author name

        Returns:
            A new EngineDescriptor instance
        """
        now = datetime.now(UTC).isoformat()

        return cls(
            engine_id=engine_id,
            display_name=display_name,
            description=description,
            version=version,
            min_er_en_version="1.0.0",
            capabilities=tuple(capabilities or []),
            priority=priority,
            status=EngineStatus.INACTIVE,
            dependencies=(),
            events=events or EventContracts(),
            metadata=EngineMetadata(
                author=author,
                version=version,
                created_at=now,
                updated_at=now,
            ),
        )

    # Capability queries
    def has_capability(self, capability_name: str) -> bool:
        """Check if the engine has a specific capability."""
        return any(c.name == capability_name for c in self.capabilities)

    def get_capability(self, capability_name: str) -> Capability | None:
        """Get a specific capability by name."""
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap
        return None

    # Status queries
    def is_active(self) -> bool:
        """Check if the engine is currently active."""
        return self.status == EngineStatus.ACTIVE

    def is_compatible_with(self, eren_version: str) -> bool:
        """Check if the engine is compatible with an EREN version."""
        from packaging.version import parse as parse_version

        try:
            required = parse_version(self.min_er_en_version)
            actual = parse_version(eren_version)
            return actual >= required
        except Exception:
            return True  # If can't parse, assume compatible

    # Dependency queries
    def get_required_dependencies(self) -> list[VersionRequirement]:
        """Get all required dependencies."""
        return [d for d in self.dependencies if d.required]

    def requires_engine(self, engine_name: str) -> bool:
        """Check if this engine requires another specific engine."""
        return any(d.engine_name == engine_name for d in self.dependencies)

    # Event queries
    def publishes_event(self, event_type: str) -> bool:
        """Check if the engine publishes a specific event type."""
        return any(
            e.event_type == event_type and e.direction == "publishes"
            for e in self.events.publishes
        )

    def consumes_event(self, event_type: str) -> bool:
        """Check if the engine consumes a specific event type."""
        return any(
            e.event_type == event_type and e.direction == "consumes"
            for e in self.events.consumes
        )

    def requires_event(self, event_type: str) -> bool:
        """Check if the engine requires a specific event (consumes with is_critical=True)."""
        return any(
            e.event_type == event_type
            and e.direction == "consumes"
            and e.is_critical
            for e in self.events.consumes
        )

    # String representation
    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"{self.display_name} ({self.engine_id}) "
            f"v{self.version} [{self.status.name}]"
        )


# =============================================================================
# Registry Snapshot
# =============================================================================


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    """A point-in-time snapshot of the engine registry.

    Useful for:
    - Audit and compliance
    - Debugging and troubleshooting
    - Version rollback
    - Distributed registry synchronization
    """

    timestamp: str  # ISO 8601 timestamp
    engine_count: int
    descriptors: tuple[EngineDescriptor, ...]
    active_count: int
    failed_count: int

    @classmethod
    def from_registry(cls, registry: EngineRegistry) -> RegistrySnapshot:
        """Create a snapshot from a live registry."""
        descriptors = tuple(registry.list())
        return cls(
            timestamp=datetime.now(UTC).isoformat(),
            engine_count=len(descriptors),
            descriptors=descriptors,
            active_count=sum(1 for d in descriptors if d.is_active()),
            failed_count=sum(1 for d in descriptors if d.status == EngineStatus.FAILED),
        )


# Import EngineRegistry for type hints
from core.registry.registry import EngineRegistry  # noqa: E402
