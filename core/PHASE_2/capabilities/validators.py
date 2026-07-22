"""Capability validators.

Provides validation logic for capabilities, dependencies, and contracts.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .capability import Capability
from .exceptions import (
    CircularDependencyError,
    DependencyNotSatisfiedError,
    EventContractViolationError,
    PermissionDeniedError,
    ValidationError,
    VersionIncompatibleError,
)

if TYPE_CHECKING:
    from .capability_registry import CapabilityRegistry


class CapabilityValidator:
    """Validates capabilities and their contracts.

    Use this to validate capabilities before registration or execution.
    """

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        """Initialize the validator.

        Args:
            registry: Optional registry for dependency validation.
        """
        self._registry = registry

    def validate_capability(self, capability: Capability) -> list[str]:
        """Validate a capability's structure.

        Args:
            capability: The capability to validate.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []

        # Check ID
        if not capability.capability_id.category:
            violations.append("Capability ID must have a category")
        if not capability.capability_id.action:
            violations.append("Capability ID must have an action")

        # Check name
        if not capability.name:
            violations.append("Capability must have a name")
        elif len(capability.name) > 100:
            violations.append("Capability name must be 100 characters or less")

        # Check description
        if not capability.description:
            violations.append("Capability must have a description")
        elif len(capability.description) > 500:
            violations.append("Description must be 500 characters or less")

        # Check priority
        if capability.priority.value < 0:
            violations.append("Priority must be non-negative")

        # Check timeout
        if capability.timeout_seconds <= 0:
            violations.append("Timeout must be positive")
        elif capability.timeout_seconds > 3600:
            violations.append("Timeout must be 3600 seconds or less")

        # Check event contracts
        for event in capability.publishes:
            if event.direction != "publishes":
                violations.append(
                    f"Event '{event.event_type}' in publishes must have direction='publishes'"
                )

        for event in capability.consumes:
            if event.direction != "consumes":
                violations.append(
                    f"Event '{event.event_type}' in consumes must have direction='consumes'"
                )

        return violations

    def validate_for_registration(
        self,
        capability: Capability,
    ) -> list[ValidationError]:
        """Validate a capability for registration.

        Args:
            capability: The capability to validate.

        Returns:
            List of validation errors.
        """
        errors: list[ValidationError] = []

        # Check structure
        violations = self.validate_capability(capability)
        if violations:
            errors.append(
                ValidationError(
                    capability_id=capability.id_string,
                    violations=violations,
                )
            )

        # Check dependencies if registry is available
        if self._registry:
            dep_errors = self._validate_dependencies(capability)
            errors.extend(dep_errors)

            # Check event contracts
            contract_errors = self._validate_event_contracts(capability)
            errors.extend(contract_errors)

        return errors

    def validate_for_execution(
        self,
        capability: Capability,
        granted_permissions: set[str] | None = None,
    ) -> list[Exception]:
        """Validate a capability for execution.

        Args:
            capability: The capability to validate.
            granted_permissions: Permissions the caller has.

        Returns:
            List of validation errors.
        """
        errors: list[Exception] = []

        # Check status
        if not capability.can_execute():
            from .exceptions import CapabilityUnavailableError
            errors.append(
                CapabilityUnavailableError(
                    capability_id=capability.id_string,
                    current_status=capability.status.name,
                )
            )

        # Check permissions
        if granted_permissions is not None:
            perm_errors = self._validate_permissions(
                capability, granted_permissions
            )
            errors.extend(perm_errors)

        # Check dependencies
        if self._registry:
            dep_errors = self._validate_dependencies(capability)
            errors.extend(dep_errors)

        return errors

    def _validate_dependencies(
        self,
        capability: Capability,
    ) -> list[DependencyNotSatisfiedError]:
        """Validate capability dependencies."""
        errors: list[DependencyNotSatisfiedError] = []

        for dep_id in capability.required_capabilities:
            if not self._registry:
                continue

            try:
                dep_cap = self._registry.get(dep_id)
                if not dep_cap.can_execute():
                    errors.append(
                        DependencyNotSatisfiedError(
                            capability_id=capability.id_string,
                            missing_dependency=dep_id,
                            required_version="ACTIVE",
                        )
                    )
            except Exception:
                errors.append(
                    DependencyNotSatisfiedError(
                        capability_id=capability.id_string,
                        missing_dependency=dep_id,
                        required_version="AVAILABLE",
                    )
                )

        return errors

    def _validate_permissions(
        self,
        capability: Capability,
        granted_permissions: set[str],
    ) -> list[PermissionDeniedError]:
        """Validate capability permissions."""
        errors: list[PermissionDeniedError] = []

        missing = []
        for perm in capability.required_permissions:
            perm_str = str(perm)
            if perm_str not in granted_permissions:
                # Check for wildcard matches
                has_wildcard = any(
                    g.startswith(perm.resource) and "*" in g
                    for g in granted_permissions
                )
                if not has_wildcard:
                    missing.append(perm_str)

        if missing:
            errors.append(
                PermissionDeniedError(
                    capability_id=capability.id_string,
                    missing_permissions=missing,
                )
            )

        return errors

    def _validate_event_contracts(
        self,
        capability: Capability,
    ) -> list[EventContractViolationError]:
        """Validate event contracts."""
        errors: list[EventContractViolationError] = []

        if not self._registry:
            return errors

        # Check that critical consumed events have publishers
        for event in capability.consumes:
            if not event.is_critical:
                continue

            # Find publishers
            publishers = self._registry.find_by_event(event.event_type, direction="publishes")
            if not publishers:
                errors.append(
                    EventContractViolationError(
                        capability_id=capability.id_string,
                        event_type=event.event_type,
                        direction="consumes",
                        message="No active publisher found for required event",
                    )
                )

        return errors


class DependencyValidator:
    """Validates capability dependencies for circular references."""

    def validate_no_circular_dependencies(
        self,
        capability: Capability,
        registry: CapabilityRegistry,
    ) -> list[CircularDependencyError]:
        """Check for circular dependencies.

        Args:
            capability: The capability to check.
            registry: The capability registry.

        Returns:
            List of circular dependency errors.
        """
        errors: list[CircularDependencyError] = []
        visited: set[str] = set()
        path: list[str] = []

        def check_cycle(cap_id: str) -> bool:
            if cap_id in path:
                cycle_start = path.index(cap_id)
                cycle = path[cycle_start:] + [cap_id]
                errors.append(CircularDependencyError(cycle=cycle))
                return True

            if cap_id in visited:
                return False

            visited.add(cap_id)
            path.append(cap_id)

            try:
                cap = registry.get(cap_id)
                for dep_id in cap.required_capabilities:
                    if check_cycle(dep_id):
                        return True
            except Exception:
                pass

            path.pop()
            return False

        check_cycle(capability.id_string)
        return errors


class VersionValidator:
    """Validates version compatibility."""

    def validate_compatibility(
        self,
        capability: Capability,
        target_version: str,
    ) -> VersionIncompatibleError | None:
        """Validate version compatibility.

        Args:
            capability: The capability to validate.
            target_version: The target EREN version.

        Returns:
            An error if incompatible, None if compatible.
        """
        if not capability.version_range.is_satisfied_by(target_version):
            return VersionIncompatibleError(
                capability_id=capability.id_string,
                required_version=(
                    f"{capability.version_range.min_version}"
                    f"{' - ' + capability.version_range.max_version if capability.version_range.max_version else ''}"
                ),
                actual_version=target_version,
            )
        return None
