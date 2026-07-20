"""Exceptions for the Cognitive Composition Root.

All exceptions are typed and carry context for debugging.

Architecture only -- no implementations.
"""


class CompositionException(Exception):
    """Base exception for composition errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ModuleRegistrationException(CompositionException):
    """Raised when module registration fails."""

    def __init__(self, module_name: str = "", reason: str = ""):
        super().__init__(
            f"Module registration failed for '{module_name}': {reason}"
        )
        self.module_name = module_name
        self.reason = reason


class ModuleValidationException(CompositionException):
    """Raised when module validation fails."""

    def __init__(self, module_name: str = "", errors: list = None):
        super().__init__(
            f"Module validation failed for '{module_name}': {len(errors or [])} errors"
        )
        self.module_name = module_name
        self.errors = errors or []


class CompositionValidationException(CompositionException):
    """Raised when composition validation fails."""

    def __init__(
        self,
        validation_type: str = "",
        errors: list = None,
    ):
        super().__init__(
            f"Composition validation failed ({validation_type}): {len(errors or [])} errors"
        )
        self.validation_type = validation_type
        self.errors = errors or []


class CompositionBuildException(CompositionException):
    """Raised when composition build fails."""

    def __init__(self, reason: str = "", stage: str = ""):
        super().__init__(f"Composition build failed at '{stage}': {reason}")
        self.reason = reason
        self.stage = stage


class ModuleDependencyException(CompositionException):
    """Raised when module dependency resolution fails."""

    def __init__(
        self,
        module_name: str = "",
        missing_dependency: str = "",
    ):
        super().__init__(
            f"Module '{module_name}' has missing dependency: {missing_dependency}"
        )
        self.module_name = module_name
        self.missing_dependency = missing_dependency


class RuntimeInitializationException(CompositionException):
    """Raised when runtime initialization fails."""

    def __init__(self, component: str = "", reason: str = ""):
        super().__init__(
            f"Runtime initialization failed for '{component}': {reason}"
        )
        self.component = component
        self.reason = reason


class ModuleNotFoundException(CompositionException):
    """Raised when a module is not found."""

    def __init__(self, module_name: str = ""):
        super().__init__(f"Module not found: {module_name}")
        self.module_name = module_name


class ModuleAlreadyRegisteredException(CompositionException):
    """Raised when a module is already registered."""

    def __init__(self, module_name: str = ""):
        super().__init__(f"Module already registered: {module_name}")
        self.module_name = module_name


class ContractRegistrationException(CompositionException):
    """Raised when contract registration fails."""

    def __init__(
        self,
        contract_name: str = "",
        module_name: str = "",
        reason: str = "",
    ):
        super().__init__(
            f"Contract registration failed for '{contract_name}' in '{module_name}': {reason}"
        )
        self.contract_name = contract_name
        self.module_name = module_name
        self.reason = reason
