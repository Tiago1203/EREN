"""Type definitions for the Engine Registry.

Provides advanced type definitions for engine registration, including
capabilities, priority levels, and status enums.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Engine Status
# =============================================================================


class EngineStatus(IntEnum):
    """Lifecycle status of a registered engine.

    Engines transition through these states during their lifecycle.
    """

    INACTIVE = 0  # Not loaded, available for activation
    LOADING = 1  # Currently being initialized
    ACTIVE = 2  # Fully operational
    SUSPENDED = 3  # Temporarily paused
    DEPRECATED = 4  # Still functional but will be removed
    FAILED = 5  # Failed to initialize or encountered critical error


# =============================================================================
# Engine Priority
# =============================================================================


class EnginePriority(IntEnum):
    """Priority levels for engine execution and loading order.

    Higher values indicate higher priority. Used for:
    - Load order (higher priority engines load first)
    - Execution preference in conflict resolution
    - Resource allocation during high load
    """

    SYSTEM = 100  # Critical system engines (Orchestrator, Event Bus)
    CRITICAL = 80  # Patient safety critical engines
    HIGH = 60  # Core cognitive engines
    NORMAL = 40  # Standard engines
    LOW = 20  # Auxiliary engines
    BACKGROUND = 10  # Background processing engines


# =============================================================================
# Capability Definition
# =============================================================================


@dataclass(frozen=True, slots=True)
class Capability:
    """A capability that an engine provides.

    Capabilities define what an engine can do, allowing consumers to
    discover engines by capability rather than by name.
    
    Examples:
    - "diagnostic": Engine can perform diagnostic analysis
    - "voice_input": Engine can process voice input
    - "reasoning": Engine can perform reasoning tasks
    """

    name: str
    description: str = ""
    version: str = "1.0.0"
    parameters: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)

    def matches(self, other: Capability) -> bool:
        """Check if this capability matches another.
        
        Two capabilities match if they have the same name.
        """
        return self.name == other.name

    def is_compatible_with(self, version: str) -> bool:
        """Check if this capability is compatible with a version range.
        
        Simple semantic version check: compatible if major versions match.
        """
        try:
            self_major = int(self.version.split(".")[0])
            other_major = int(version.split(".")[0])
            return self_major == other_major
        except (ValueError, IndexError):
            return True  # If can't parse, assume compatible


# =============================================================================
# Engine Metadata
# =============================================================================


@dataclass(frozen=True, slots=True)
class EngineMetadata:
    """Metadata for a registered engine.

    Contains non-functional information about the engine such as
    author, version, registration date, etc.
    """

    author: str = ""
    version: str = "1.0.0"
    license: str = ""
    repository_url: str = ""
    documentation_url: str = ""
    support_contact: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""  # ISO 8601 timestamp
    updated_at: str = ""  # ISO 8601 timestamp


# =============================================================================
# Engine Compatibility
# =============================================================================


@dataclass(frozen=True, slots=True)
class VersionRequirement:
    """Version requirement specification for engine compatibility."""

    engine_name: str  # Name of the required engine
    min_version: str = "0.0.0"  # Minimum compatible version
    max_version: str = ""  # Maximum compatible version (exclusive)
    required: bool = True  # Whether this dependency is required

    def is_satisfied_by(self, version: str) -> bool:
        """Check if a version satisfies this requirement."""
        from packaging.version import parse as parse_version

        try:
            actual = parse_version(version)
            min_ver = parse_version(self.min_version)
            max_ver = parse_version(self.max_version) if self.max_version else None

            if actual < min_ver:
                return False
            if max_ver and actual >= max_ver:
                return False
            return True
        except Exception:
            return True  # If can't parse, assume satisfied


# =============================================================================
# Event Contract
# =============================================================================


@dataclass(frozen=True, slots=True)
class EventContract:
    """Defines an event contract for an engine.

    Specifies which events an engine publishes or consumes.
    Used for validation and dependency analysis.
    """

    event_type: str
    direction: str  # "publishes" or "consumes"
    description: str = ""
    is_critical: bool = False  # Critical for engine operation


@dataclass(frozen=True, slots=True)
class EventContracts:
    """Collection of event contracts for an engine."""

    publishes: tuple[EventContract, ...] = field(default_factory=tuple)
    consumes: tuple[EventContract, ...] = field(default_factory=tuple)

    def get_all_event_types(self) -> set[str]:
        """Get all event types mentioned in contracts."""
        types = {e.event_type for e in self.publishes}
        types |= {e.event_type for e in self.consumes}
        return types

    def requires_event(self, event_type: str) -> bool:
        """Check if this engine requires a specific event."""
        return any(
            e.event_type == event_type and e.direction == "consumes"
            for e in self.consumes
        )


# =============================================================================
# Search and Filter Types
# =============================================================================


@dataclass
class EngineFilter:
    """Filter criteria for searching engines."""

    name_contains: str | None = None
    capability: str | None = None
    status: EngineStatus | None = None
    min_priority: EnginePriority | None = None
    tag: str | None = None
    author: str | None = None
    active_only: bool = False

    def matches(self, descriptor: EngineDescriptor) -> bool:
        """Check if an engine descriptor matches this filter."""
        if self.name_contains and self.name_contains not in descriptor.engine_id:
            return False
        if self.capability and not descriptor.has_capability(self.capability):
            return False
        if self.status and descriptor.status != self.status:
            return False
        if self.min_priority and descriptor.priority < self.min_priority:
            return False
        if self.tag and self.tag not in descriptor.metadata.tags:
            return False
        if self.author and self.author != descriptor.metadata.author:
            return False
        if self.active_only and descriptor.status != EngineStatus.ACTIVE:
            return False
        return True


@dataclass
class SearchOptions:
    """Options for engine search operations."""

    filter: EngineFilter | None = None
    sort_by: str = "priority"  # priority, name, registration_date
    ascending: bool = False
    limit: int | None = None
    offset: int = 0
