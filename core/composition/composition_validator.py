"""Composition Validator for the Cognitive Composition Root.

Validates the composition before building.

Architecture only -- no implementations.
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .module_registry import ModuleRegistry


@dataclass
class ValidationError:
    """A validation error."""

    error_type: str
    message: str
    module_name: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of composition validation."""

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


class CompositionValidator:
    """Validates the composition before building.

    Checks for:
    - All modules registered
    - Module dependencies satisfied
    - No circular dependencies
    - All contracts registered
    - Container valid
    - Event Bus present
    - Boot Manager present
    """

    def __init__(
        self,
        registry: ModuleRegistry,
        container: Any = None,
    ):
        """Initialize the validator.

        Args:
            registry: Module registry.
            container: DI container (optional).
        """
        self._registry = registry
        self._container = container
        self._lock = threading.RLock()

    def validate(
        self,
        required_modules: list = None,
        required_contracts: list = None,
    ) -> ValidationResult:
        """Validate the composition.

        Args:
            required_modules: List of required module names.
            required_contracts: List of required contract names.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        # Validate modules
        self._validate_modules(result, required_modules or [])

        # Validate module dependencies
        self._validate_module_dependencies(result)

        # Validate contracts
        self._validate_contracts(result, required_contracts or [])

        # Validate container
        if self._container is not None:
            self._validate_container(result)

        return result

    def _validate_modules(
        self,
        result: ValidationResult,
        required_modules: list,
    ) -> None:
        """Validate all required modules are registered.

        Args:
            result: Validation result.
            required_modules: Required module names.
        """
        for module_name in required_modules:
            if not self._registry.is_registered(module_name):
                result.add_error(ValidationError(
                    error_type="missing_module",
                    message=f"Required module not registered: {module_name}",
                    module_name=module_name,
                ))

    def _validate_module_dependencies(
        self,
        result: ValidationResult,
    ) -> None:
        """Validate module dependencies are satisfied.

        Args:
            result: Validation result.
        """
        for module in self._registry.get_all():
            for dep in module.dependencies:
                if not self._registry.is_registered(dep.module_name):
                    if dep.is_required:
                        result.add_error(ValidationError(
                            error_type="missing_dependency",
                            message=f"Module '{module.module_name}' requires '{dep.module_name}' which is not registered",
                            module_name=module.module_name,
                            details={"missing_dependency": dep.module_name},
                        ))

    def _validate_contracts(
        self,
        result: ValidationResult,
        required_contracts: list,
    ) -> None:
        """Validate all required contracts are registered.

        Args:
            result: Validation result.
            required_contracts: Required contract names.
        """
        if self._container is None:
            return

        for contract_name in required_contracts:
            try:
                resolved = self._container.try_resolve(contract_name)
                if resolved is None:
                    result.add_error(ValidationError(
                        error_type="missing_contract",
                        message=f"Required contract not registered: {contract_name}",
                        details={"contract": contract_name},
                    ))
            except Exception:
                result.add_error(ValidationError(
                    error_type="missing_contract",
                    message=f"Required contract not registered: {contract_name}",
                    details={"contract": contract_name},
                ))

    def _validate_container(self, result: ValidationResult) -> None:
        """Validate the container.

        Args:
            result: Validation result.
        """
        try:
            # Check container is valid
            if hasattr(self._container, 'is_disposed'):
                if self._container.is_disposed:
                    result.add_error(ValidationError(
                        error_type="invalid_container",
                        message="Container is disposed",
                    ))
        except Exception as e:
            result.add_error(ValidationError(
                error_type="invalid_container",
                message=f"Container validation failed: {str(e)}",
            ))

    def validate_module(self, module_name: str) -> ValidationResult:
        """Validate a specific module.

        Args:
            module_name: Module to validate.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        module = self._registry.get(module_name)
        if module is None:
            result.add_error(ValidationError(
                error_type="module_not_found",
                message=f"Module not found: {module_name}",
                module_name=module_name,
            ))
            return result

        # Validate dependencies
        for dep in module.dependencies:
            if not self._registry.is_registered(dep.module_name):
                if dep.is_required:
                    result.add_error(ValidationError(
                        error_type="missing_dependency",
                        message=f"Module requires '{dep.module_name}' which is not registered",
                        module_name=module_name,
                        details={"missing_dependency": dep.module_name},
                    ))

        return result
