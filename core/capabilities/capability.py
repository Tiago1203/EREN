"""Core Capability definition.

Defines the Capability class - the central abstraction of the Cognitive Capability
Registry. A Capability represents a discrete unit of cognitive work that can be
performed within EREN.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types import (
    CapabilityCategory,
    CapabilityId,
    CapabilityMetadata,
    CapabilityPriority,
    CapabilityStatus,
    CriticalityLevel,
    EventContract,
    Permission,
    SecurityLevel,
    TimeEstimate,
    VersionRange,
)

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class Capability:
    """A discrete unit of cognitive work within EREN.

    Capabilities are the atomic units of cognitive functionality. They represent
    what can be done, not who does it. The same capability may be provided
    by multiple providers (engines) with different characteristics.

    Key principles:
    - Capabilities are defined by WHAT they do, not WHO does it
    - A capability can have multiple implementations (providers)
    - Capabilities declare dependencies on other capabilities
    - Capabilities specify their event contracts (pub/sub)
    - Capabilities have security and criticality levels

    Example:
        capability_id: planning.create.maintenance
        category: PLANNING
        name: "Create Maintenance Plan"
        description: "Creates a maintenance plan based on device state"
        provider_id: "planner_engine_v1"
        priority: HIGH
        criticality: MODERATE
    """

    # Identity
    capability_id: CapabilityId
    name: str
    description: str
    category: CapabilityCategory

    # Provider
    provider_id: str  # Which engine implements this capability
    provider_version: str = "1.0.0"

    # Classification
    priority: CapabilityPriority = CapabilityPriority.NORMAL
    status: CapabilityStatus = CapabilityStatus.AVAILABLE
    security_level: SecurityLevel = SecurityLevel.AUTHENTICATED
    criticality: CriticalityLevel = CriticalityLevel.LOW

    # Dependencies
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)  # capability IDs
    required_permissions: tuple[Permission, ...] = field(default_factory=tuple)

    # Event Contracts
    publishes: tuple[EventContract, ...] = field(default_factory=tuple)
    consumes: tuple[EventContract, ...] = field(default_factory=tuple)

    # Execution
    timeout_seconds: float = 30.0
    time_estimate: TimeEstimate = field(default_factory=TimeEstimate)
    version_range: VersionRange = field(default_factory=VersionRange)

    # Metadata
    metadata: CapabilityMetadata = field(default_factory=CapabilityMetadata)

    # Factory methods
    @classmethod
    def create(
        cls,
        category: str,
        action: str,
        name: str,
        description: str,
        provider_id: str,
        target: str = "",
        **kwargs,
    ) -> Capability:
        """Create a new capability with common defaults.

        Args:
            category: Capability category (e.g., "planning", "diagnostic")
            action: Action performed (e.g., "create", "analyze")
            name: Human-readable name
            description: What this capability does
            provider_id: Provider engine ID
            target: Optional target specificity
            **kwargs: Additional capability attributes

        Returns:
            A new Capability instance
        """
        return cls(
            capability_id=CapabilityId(
                category=category,
                action=action,
                target=target,
            ),
            name=name,
            description=description,
            category=CapabilityCategory(category) if isinstance(category, str) else category,
            provider_id=provider_id,
            metadata=CapabilityMetadata.now(),
            **kwargs,
        )

    # Identity methods
    @property
    def id_string(self) -> str:
        """Get the capability ID as a string."""
        return str(self.capability_id)

    # Status methods
    def is_active(self) -> bool:
        """Check if the capability is currently active."""
        return self.status == CapabilityStatus.ACTIVE

    def is_available(self) -> bool:
        """Check if the capability is available."""
        return self.status in (
            CapabilityStatus.AVAILABLE,
            CapabilityStatus.ACTIVE,
        )

    def is_deprecated(self) -> bool:
        """Check if the capability is deprecated."""
        return self.status == CapabilityStatus.DEPRECATED

    def can_execute(self) -> bool:
        """Check if the capability can be executed."""
        return self.status in (
            CapabilityStatus.ACTIVE,
            CapabilityStatus.AVAILABLE,
        )

    # Event methods
    def publishes_event(self, event_type: str) -> bool:
        """Check if this capability publishes a specific event type."""
        return any(
            e.event_type == event_type and e.direction == "publishes"
            for e in self.publishes
        )

    def consumes_event(self, event_type: str) -> bool:
        """Check if this capability consumes a specific event type."""
        return any(
            e.event_type == event_type and e.direction == "consumes"
            for e in self.consumes
        )

    def requires_event(self, event_type: str) -> bool:
        """Check if this capability requires a specific event (critical consumer)."""
        return any(
            e.event_type == event_type
            and e.direction == "consumes"
            and e.is_critical
            for e in self.consumes
        )

    def get_all_events(self) -> set[str]:
        """Get all event types this capability touches."""
        events = {e.event_type for e in self.publishes}
        events |= {e.event_type for e in self.consumes}
        return events

    # Dependency methods
    def requires_capability(self, capability_id: str) -> bool:
        """Check if this capability requires another capability."""
        return capability_id in self.required_capabilities

    def requires_permission(self, resource: str) -> bool:
        """Check if this capability requires a specific permission."""
        return any(p.resource == resource for p in self.required_permissions)

    def has_permissions(self, granted_permissions: set[str]) -> bool:
        """Check if all required permissions are granted."""
        for perm in self.required_permissions:
            perm_str = str(perm)
            # Check for wildcard matches
            if perm_str not in granted_permissions:
                if not any(
                    g.startswith(perm.resource) and "*" in granted_permissions
                    for g in granted_permissions
                ):
                    return False
        return True

    # Compatibility methods
    def is_compatible_with_version(self, version: str) -> bool:
        """Check if a version is compatible with this capability."""
        return self.version_range.is_satisfied_by(version)

    def meets_minimum_requirements(
        self,
        min_priority: CapabilityPriority | None = None,
        min_criticality: CriticalityLevel | None = None,
        min_security: SecurityLevel | None = None,
    ) -> bool:
        """Check if capability meets minimum requirements."""
        if min_priority and self.priority < min_priority:
            return False
        if min_criticality and self.criticality < min_criticality:
            return False
        if min_security and self.security_level < min_security:
            return False
        return True

    # String representations
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.id_string}) [{self.status.name}]"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Capability(id={self.id_string!r}, "
            f"name={self.name!r}, "
            f"provider={self.provider_id!r}, "
            f"status={self.status.name!r})"
        )


# =============================================================================
# Predefined Capability Templates
# =============================================================================


class CapabilityTemplates:
    """Predefined capability templates for common operations."""

    @staticmethod
    def diagnostic(device_type: str, provider: str) -> Capability:
        """Template for diagnostic capabilities."""
        return Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            target=device_type,
            name=f"Diagnose {device_type}",
            description=f"Performs diagnostic analysis on {device_type} devices",
            provider_id=provider,
            priority=CapabilityPriority.HIGH,
            criticality=CriticalityLevel.MODERATE,
        )

    @staticmethod
    def knowledge_search(provider: str) -> Capability:
        """Template for knowledge search capabilities."""
        return Capability.create(
            category=CapabilityCategory.KNOWLEDGE,
            action="search",
            target="documents",
            name="Knowledge Search",
            description="Searches knowledge bases for relevant information",
            provider_id=provider,
            priority=CapabilityPriority.NORMAL,
            criticality=CriticalityLevel.LOW,
        )

    @staticmethod
    def plan_creation(provider: str, target: str = "general") -> Capability:
        """Template for plan creation capabilities."""
        return Capability.create(
            category=CapabilityCategory.PLANNING,
            action="create",
            target=target,
            name=f"Create {target} Plan",
            description=f"Creates execution plans for {target} tasks",
            provider_id=provider,
            priority=CapabilityPriority.HIGH,
            criticality=CriticalityLevel.MODERATE,
        )

    @staticmethod
    def voice_input(provider: str) -> Capability:
        """Template for voice input capabilities."""
        return Capability.create(
            category=CapabilityCategory.VOICE,
            action="input",
            target="audio",
            name="Voice Input Processing",
            description="Processes voice input from users",
            provider_id=provider,
            priority=CapabilityPriority.CRITICAL,
            criticality=CriticalityLevel.MODERATE,
        )
