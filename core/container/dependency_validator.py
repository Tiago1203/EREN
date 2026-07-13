"""Dependency Validator for the Cognitive Dependency Injection Container.

Validates the dependency graph before boot.

Architecture only -- no implementations.
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .dependency_graph import DependencyGraph
from .service_registry import ServiceRegistry
from .service_lifetime import ServiceLifetime
from .exceptions import (
    CircularDependencyException,
    OrphanDependencyException,
    ValidationException,
)


@dataclass
class ValidationError:
    """A validation error."""

    error_type: str
    message: str
    contract: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of dependency validation."""

    is_valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def add_error(self, error: ValidationError) -> None:
        """Add an error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: ValidationError) -> None:
        """Add a warning."""
        self.warnings.append(warning)


class DependencyValidator:
    """Validates service dependencies.

    Checks for:
    - Circular dependencies
    - Orphan dependencies
    - Duplicate registrations
    - Invalid lifetimes
    - Lifetime conflicts
    - Missing dependencies
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        graph: DependencyGraph,
    ):
        """Initialize the validator.

        Args:
            registry: Service registry.
            graph: Dependency graph.
        """
        self._registry = registry
        self._graph = graph
        self._lock = threading.RLock()

    def validate(self) -> ValidationResult:
        """Validate all dependencies.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        # Build dependency graph from registry
        self._build_graph()

        # Check for cycles
        self._validate_cycles(result)

        # Check for orphans
        self._validate_orphans(result)

        # Check for duplicates
        self._validate_duplicates(result)

        # Check for invalid implementations
        self._validate_implementations(result)

        # Check for lifetime conflicts
        self._validate_lifetimes(result)

        # Check for inaccessible services
        self._validate_accessibility(result)

        return result

    def _build_graph(self) -> None:
        """Build dependency graph from registry."""
        for descriptor in self._registry.get_all_descriptors():
            self._graph.add_descriptor(descriptor)

    def _validate_cycles(self, result: ValidationResult) -> None:
        """Validate no circular dependencies exist.

        Args:
            result: Validation result to update.
        """
        cycles = self._graph.find_cycles()

        for cycle in cycles:
            result.add_error(ValidationError(
                error_type="circular_dependency",
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                contract=cycle[0] if cycle else "",
                details={"cycle": cycle},
            ))

    def _validate_orphans(self, result: ValidationResult) -> None:
        """Validate no orphan dependencies exist.

        Args:
            result: Validation result to update.
        """
        orphans = self._graph.find_orphans()

        for orphan in orphans:
            result.add_error(ValidationError(
                error_type="orphan_dependency",
                message=f"Orphan dependency: '{orphan}' has no implementation",
                contract=orphan,
                details={"missing_implementation": orphan},
            ))

    def _validate_duplicates(self, result: ValidationResult) -> None:
        """Validate no duplicate registrations.

        Args:
            result: Validation result to update.
        """
        contracts = self._registry.get_all_contracts()

        for contract in contracts:
            descriptors = self._registry.get_descriptors(contract)
            if len(descriptors) > 1:
                result.add_warning(ValidationError(
                    error_type="duplicate_registration",
                    message=f"Multiple implementations for '{contract}'",
                    contract=contract,
                    details={"count": len(descriptors)},
                ))

    def _validate_implementations(self, result: ValidationResult) -> None:
        """Validate implementations are valid.

        Args:
            result: Validation result to update.
        """
        for descriptor in self._registry.get_all_descriptors():
            impl = descriptor.implementation

            # Check if it's a callable or instance
            if not callable(impl) and not isinstance(impl, object):
                result.add_error(ValidationError(
                    error_type="invalid_implementation",
                    message=f"Invalid implementation for '{descriptor.contract}'",
                    contract=descriptor.contract,
                    details={"implementation": str(impl)},
                ))

            # Check if factory is callable when using FACTORY lifetime
            if descriptor.lifetime == ServiceLifetime.FACTORY:
                if descriptor.factory and not callable(descriptor.factory):
                    result.add_error(ValidationError(
                        error_type="invalid_factory",
                        message=f"Factory for '{descriptor.contract}' is not callable",
                        contract=descriptor.contract,
                    ))

    def _validate_lifetimes(self, result: ValidationResult) -> None:
        """Validate lifetime configurations.

        Args:
            result: Validation result to update.
        """
        # Group by contract
        contracts = {}
        for descriptor in self._registry.get_all_descriptors():
            if descriptor.contract not in contracts:
                contracts[descriptor.contract] = []
            contracts[descriptor.contract].append(descriptor)

        # Check for lifetime conflicts
        for contract, descriptors in contracts.items():
            if len(descriptors) > 1:
                lifetimes = set(d.lifetime for d in descriptors)
                if len(lifetimes) > 1:
                    result.add_warning(ValidationError(
                        error_type="lifetime_conflict",
                        message=f"Multiple lifetimes for '{contract}': {lifetimes}",
                        contract=contract,
                        details={"lifetimes": list(lifetimes)},
                    ))

    def _validate_accessibility(self, result: ValidationResult) -> None:
        """Validate all services are accessible.

        Args:
            result: Validation result to update.
        """
        for contract in self._registry.get_all_contracts():
            factory = self._registry.get_factory(contract)
            if factory is None:
                result.add_warning(ValidationError(
                    error_type="inaccessible_service",
                    message=f"Service '{contract}' has no factory",
                    contract=contract,
                ))

    def validate_contract(
        self,
        contract: str,
        dependencies: list = None,
    ) -> ValidationResult:
        """Validate a specific contract and its dependencies.

        Args:
            contract: Contract name.
            dependencies: List of dependency contracts.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        # Check contract exists
        if not self._registry.is_registered(contract):
            result.add_error(ValidationError(
                error_type="service_not_found",
                message=f"Contract '{contract}' is not registered",
                contract=contract,
            ))

        # Check dependencies exist
        for dep in (dependencies or []):
            if not self._registry.is_registered(dep):
                result.add_error(ValidationError(
                    error_type="dependency_not_found",
                    message=f"Dependency '{dep}' for '{contract}' is not registered",
                    contract=contract,
                    details={"missing_dependency": dep},
                ))

        return result

    def check_circular_dependency(
        self,
        start_contract: str,
    ) -> list[list[str]]:
        """Check for circular dependencies starting from a contract.

        Args:
            start_contract: Starting contract.

        Returns:
            List of cycles found.
        """
        # Add the contract to graph if not present
        if not self._registry.is_registered(start_contract):
            return []

        descriptor = self._registry.get_descriptor(start_contract)
        if descriptor:
            self._graph.add_descriptor(descriptor)

        return self._graph.find_cycles()

    def get_resolution_order(self) -> list[str]:
        """Get topologically sorted resolution order.

        Returns:
            List of contracts in resolution order.
        """
        # Build ordering
        sorted_contracts = []
        visited = set()
        temp_visited = set()

        def visit(contract: str):
            if contract in temp_visited:
                raise CircularDependencyException([contract])

            if contract in visited:
                return

            temp_visited.add(contract)

            # Visit dependencies first
            node = self._graph.get_node(contract)
            if node:
                for dep in node.dependencies:
                    visit(dep)

            temp_visited.remove(contract)
            visited.add(contract)
            sorted_contracts.append(contract)

        for contract in self._registry.get_all_contracts():
            if contract not in visited:
                visit(contract)

        return sorted_contracts
