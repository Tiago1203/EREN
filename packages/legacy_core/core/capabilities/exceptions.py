"""Exceptions for the Cognitive Capability Registry.

Provides a typed exception hierarchy for capability operations.

Architecture only — no business logic.
"""

from __future__ import annotations


class CapabilityRegistryError(Exception):
    """Base class for all capability registry errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class CapabilityNotFoundError(CapabilityRegistryError):
    """Raised when a capability is not found in the registry.

    Attributes:
        capability_id: The ID of the capability that was not found.
    """

    def __init__(self, capability_id: str) -> None:
        super().__init__(f"Capability '{capability_id}' not found in registry")
        self.capability_id = capability_id


class CapabilityAlreadyRegisteredError(CapabilityRegistryError):
    """Raised when registering a duplicate capability.

    Attributes:
        capability_id: The ID of the capability that is already registered.
    """

    def __init__(self, capability_id: str) -> None:
        super().__init__(f"Capability '{capability_id}' already registered")
        self.capability_id = capability_id


class DependencyNotSatisfiedError(CapabilityRegistryError):
    """Raised when a required capability dependency is not satisfied.

    Attributes:
        capability_id: The capability with unsatisfied dependencies.
        missing_dependency: The ID of the missing capability.
        required_version: The minimum required version.
    """

    def __init__(
        self,
        capability_id: str = "",
        missing_dependency: str = "",
        required_version: str = "",
    ) -> None:
        super().__init__(
            f"Capability '{capability_id}' requires '{missing_dependency}' "
            f"(minimum version: {required_version})"
        )
        self.capability_id = capability_id
        self.missing_dependency = missing_dependency
        self.required_version = required_version


class PermissionDeniedError(CapabilityRegistryError):
    """Raised when the caller doesn't have required permissions.

    Attributes:
        capability_id: The capability that requires permissions.
        missing_permissions: List of missing permission strings.
    """

    def __init__(
        self,
        capability_id: str = "",
        missing_permissions: list[str] | None = None,
    ) -> None:
        perms = ", ".join(missing_permissions or [])
        super().__init__(
            f"Permission denied for '{capability_id}'. "
            f"Missing permissions: [{perms}]"
        )
        self.capability_id = capability_id
        self.missing_permissions = missing_permissions or []


class CapabilityUnavailableError(CapabilityRegistryError):
    """Raised when a capability is not in a usable state.

    Attributes:
        capability_id: The unavailable capability.
        current_status: The current status of the capability.
    """

    def __init__(
        self,
        capability_id: str = "",
        current_status: str = "",
    ) -> None:
        super().__init__(
            f"Capability '{capability_id}' is not available "
            f"(status: {current_status})"
        )
        self.capability_id = capability_id
        self.current_status = current_status


class VersionIncompatibleError(CapabilityRegistryError):
    """Raised when version compatibility check fails.

    Attributes:
        capability_id: The capability with incompatibility.
        required_version: The required version range.
        actual_version: The actual version.
    """

    def __init__(
        self,
        capability_id: str = "",
        required_version: str = "",
        actual_version: str = "",
    ) -> None:
        super().__init__(
            f"Capability '{capability_id}': version {actual_version} "
            f"does not satisfy requirement {required_version}"
        )
        self.capability_id = capability_id
        self.required_version = required_version
        self.actual_version = actual_version


class EventContractViolationError(CapabilityRegistryError):
    """Raised when an event contract cannot be satisfied.

    Attributes:
        capability_id: The capability with contract violation.
        event_type: The problematic event type.
        direction: The direction (publishes/consumes).
        message: Description of the violation.
    """

    def __init__(
        self,
        capability_id: str = "",
        event_type: str = "",
        direction: str = "",
        message: str = "",
    ) -> None:
        super().__init__(
            f"Capability '{capability_id}' event contract violation "
            f"for '{event_type}' ({direction}): {message}"
        )
        self.capability_id = capability_id
        self.event_type = event_type
        self.direction = direction
        self.message = message


class ResolutionError(CapabilityRegistryError):
    """Raised when capability resolution fails.

    Attributes:
        query: The query that could not be resolved.
        message: Description of why resolution failed.
    """

    def __init__(self, query: str = "", message: str = "") -> None:
        super().__init__(f"Failed to resolve '{query}': {message}")
        self.query = query
        self.message = message


class ValidationError(CapabilityRegistryError):
    """Raised when capability validation fails.

    Attributes:
        capability_id: The capability that failed validation.
        violations: List of validation violations.
    """

    def __init__(
        self,
        capability_id: str = "",
        violations: list[str] | None = None,
    ) -> None:
        violations_str = "; ".join(violations or [])
        super().__init__(
            f"Validation failed for '{capability_id}': {violations_str}"
        )
        self.capability_id = capability_id
        self.violations = violations or []


class CircularDependencyError(CapabilityRegistryError):
    """Raised when a circular dependency is detected.

    Attributes:
        cycle: The list of capabilities in the cycle.
    """

    def __init__(self, cycle: list[str] | None = None) -> None:
        cycle_str = " -> ".join(cycle or [])
        super().__init__(f"Circular dependency detected: {cycle_str}")
        self.cycle = cycle or []


class ProviderNotFoundError(CapabilityRegistryError):
    """Raised when a provider is not registered.

    Attributes:
        provider_id: The ID of the missing provider.
    """

    def __init__(self, provider_id: str) -> None:
        super().__init__(f"Provider '{provider_id}' not found in registry")
        self.provider_id = provider_id
