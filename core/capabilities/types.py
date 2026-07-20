"""Type definitions for the Cognitive Capability Registry.

Provides comprehensive type definitions for cognitive capabilities including
enums, value objects, and complex types.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Enums
# =============================================================================


class CapabilityCategory(str, Enum):
    """Categories of cognitive capabilities.

    Each category represents a distinct domain of cognitive functionality.
    """

    PLANNING = "planning"  # Task planning and scheduling
    KNOWLEDGE = "knowledge"  # Knowledge retrieval and management
    MEMORY = "memory"  # Memory operations and context
    REASONING = "reasoning"  # Logical reasoning and inference
    DIAGNOSTIC = "diagnostic"  # Diagnostic analysis
    WORKFLOW = "workflow"  # Workflow orchestration
    VOICE = "voice"  # Voice input/output
    TOOL = "tool"  # Tool execution
    LEARNING = "learning"  # Learning and adaptation
    MONITORING = "monitoring"  # System monitoring
    SECURITY = "security"  # Security operations
    ADMINISTRATION = "administration"  # Administrative operations

    @classmethod
    def all(cls) -> list[str]:
        """Get all category values."""
        return [c.value for c in cls]


class CapabilityStatus(IntEnum):
    """Lifecycle status of a capability.

    Capabilities transition through these states during their lifecycle.
    """

    UNREGISTERED = 0  # Not registered
    AVAILABLE = 1  # Registered and available
    LOADING = 2  # Currently being loaded
    ACTIVE = 3  # Fully operational
    SUSPENDED = 4  # Temporarily paused
    DEPRECATED = 5  # Still functional but will be removed
    FAILED = 6  # Failed to initialize
    UNAVAILABLE = 7  # Temporarily unavailable


class CapabilityPriority(IntEnum):
    """Priority levels for capability execution.

    Higher values indicate higher priority.
    """

    SYSTEM = 100  # Critical system capabilities
    CRITICAL = 80  # Patient safety critical
    HIGH = 60  # Core cognitive capabilities
    NORMAL = 40  # Standard capabilities
    LOW = 20  # Auxiliary capabilities
    BACKGROUND = 10  # Background processing


class SecurityLevel(IntEnum):
    """Security clearance levels for capabilities.

    Determines which users can access certain capabilities.
    """

    PUBLIC = 0  # Available to all users
    AUTHENTICATED = 10  # Requires authentication
    PRIVILEGED = 20  # Requires elevated privileges
    ADMIN = 30  # Administrative access required
    SYSTEM = 100  # System-only access


class CriticalityLevel(IntEnum):
    """Criticality levels for capabilities.

    Used for impact assessment and prioritization.
    """

    INFORMATIONAL = 0  # No patient/safety impact
    LOW = 10  # Minor impact, easily recoverable
    MODERATE = 20  # Moderate impact, requires attention
    HIGH = 30  # Significant impact
    CRITICAL = 40  # Patient safety impact
    LIFE_THREATENING = 50  # Direct life threat if fails


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True, slots=True)
class CapabilityId:
    """Unique identifier for a capability.

    Format: category.action.target
    Example: planning.create.maintenance
    """

    category: str
    action: str
    target: str = ""

    def __str__(self) -> str:
        parts = [self.category, self.action]
        if self.target:
            parts.append(self.target)
        return ".".join(parts)

    @classmethod
    def parse(cls, value: str) -> CapabilityId:
        """Parse a string into a CapabilityId."""
        parts = value.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid capability ID format: {value}")
        return cls(
            category=parts[0],
            action=parts[1],
            target=".".join(parts[2:]) if len(parts) > 2 else "",
        )


@dataclass(frozen=True, slots=True)
class VersionRange:
    """Version range specification for compatibility."""

    min_version: str = "0.0.0"
    max_version: str = ""
    exact_version: str = ""

    def is_satisfied_by(self, version: str) -> bool:
        """Check if a version satisfies this range."""
        from packaging.version import parse as parse_version

        try:
            actual = parse_version(version)

            if self.exact_version:
                return actual == parse_version(self.exact_version)

            min_ver = parse_version(self.min_version)
            if actual < min_ver:
                return False

            if self.max_version:
                max_ver = parse_version(self.max_version)
                if actual >= max_ver:
                    return False

            return True
        except Exception:
            return True  # If can't parse, assume compatible


@dataclass(frozen=True, slots=True)
class EventContract:
    """Defines an event contract for a capability."""

    event_type: str
    direction: str  # "publishes" or "consumes"
    is_critical: bool = False
    description: str = ""

    def requires(self) -> bool:
        """Check if this is a required (critical) event."""
        return self.is_critical and self.direction == "consumes"


@dataclass(frozen=True, slots=True)
class Permission:
    """Permission required by a capability."""

    resource: str
    action: str
    scope: str = "execute"  # execute, read, write, delete

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}:{self.scope}"


@dataclass(frozen=True, slots=True)
class TimeEstimate:
    """Expected execution time for a capability."""

    min_seconds: float = 0.0
    max_seconds: float = 60.0
    typical_seconds: float = 5.0

    def is_reasonable(self, elapsed: float) -> bool:
        """Check if elapsed time is within reasonable bounds."""
        return self.min_seconds <= elapsed <= self.max_seconds * 2


@dataclass(frozen=True, slots=True)
class CapabilityMetadata:
    """Additional metadata for a capability."""

    author: str = ""
    version: str = "1.0.0"
    license: str = ""
    repository_url: str = ""
    documentation_url: str = ""
    support_contact: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""
    updated_at: str = ""
    deprecated_at: str = ""
    deprecation_message: str = ""

    @classmethod
    def now(cls, **kwargs) -> CapabilityMetadata:
        """Create metadata with current timestamp."""
        timestamp = datetime.now(UTC).isoformat()
        return cls(
            created_at=timestamp,
            updated_at=timestamp,
            **kwargs,
        )


# =============================================================================
# Filter Types
# =============================================================================


@dataclass
class CapabilityFilter:
    """Filter criteria for searching capabilities."""

    category: CapabilityCategory | None = None
    status: CapabilityStatus | None = None
    min_priority: CapabilityPriority | None = None
    min_criticality: CriticalityLevel | None = None
    min_security: SecurityLevel | None = None
    tag: str | None = None
    author: str | None = None
    provider: str | None = None
    requires_permission: str | None = None
    publishes_event: str | None = None
    consumes_event: str | None = None
    active_only: bool = False
    compatible_with_version: str | None = None

    def matches(self, capability: Capability) -> bool:
        """Check if a capability matches this filter."""
        if self.category and capability.category != self.category:
            return False
        if self.status and capability.status != self.status:
            return False
        if self.min_priority and capability.priority < self.min_priority:
            return False
        if self.min_criticality and capability.criticality < self.min_criticality:
            return False
        if self.min_security and capability.security_level < self.min_security:
            return False
        if self.tag and self.tag not in capability.metadata.tags:
            return False
        if self.author and self.author != capability.metadata.author:
            return False
        if self.provider and self.provider != capability.provider_id:
            return False
        if self.requires_permission:
            if not any(
                p.resource == self.requires_permission
                for p in capability.permissions
            ):
                return False
        if self.publishes_event:
            if not capability.publishes_event(self.publishes_event):
                return False
        if self.consumes_event:
            if not capability.consumes_event(self.consumes_event):
                return False
        if self.active_only and capability.status != CapabilityStatus.ACTIVE:
            return False
        return True


@dataclass
class SearchOptions:
    """Options for capability search operations."""

    filter: CapabilityFilter | None = None
    sort_by: str = "priority"  # priority, name, category, criticality
    ascending: bool = False
    limit: int | None = None
    offset: int = 0
