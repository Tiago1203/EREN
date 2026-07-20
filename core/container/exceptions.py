"""Exceptions for the Cognitive Dependency Injection Container.

All exceptions are typed and carry context for debugging.

Architecture only -- no implementations.
"""


class ContainerException(Exception):
    """Base exception for container errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ServiceNotFoundException(ContainerException):
    """Raised when a service is not found in the container."""

    def __init__(self, service_type: str = ""):
        super().__init__(f"Service not found: {service_type}")
        self.service_type = service_type


class DuplicateServiceException(ContainerException):
    """Raised when registering a service that already exists."""

    def __init__(
        self,
        service_type: str = "",
        existing_registration: str = "",
    ):
        super().__init__(
            f"Duplicate service registration: {service_type} "
            f"(existing: {existing_registration})"
        )
        self.service_type = service_type
        self.existing_registration = existing_registration


class InvalidLifetimeException(ContainerException):
    """Raised when an invalid lifetime is specified."""

    def __init__(self, lifetime: str = ""):
        super().__init__(f"Invalid service lifetime: {lifetime}")
        self.lifetime = lifetime


class CircularDependencyException(ContainerException):
    """Raised when a circular dependency is detected."""

    def __init__(self, dependency_chain: list = None):
        chain_str = " -> ".join(dependency_chain or [])
        super().__init__(f"Circular dependency detected: {chain_str}")
        self.dependency_chain = dependency_chain or []


class DependencyResolutionException(ContainerException):
    """Raised when dependency resolution fails."""

    def __init__(self, service_type: str = "", reason: str = ""):
        super().__init__(
            f"Failed to resolve dependency '{service_type}': {reason}"
        )
        self.service_type = service_type
        self.reason = reason


class ContainerDisposedException(ContainerException):
    """Raised when accessing a disposed container."""

    def __init__(self):
        super().__init__("Container has been disposed")
        self.is_disposed = True


class ScopeDisposedException(ContainerException):
    """Raised when accessing a disposed scope."""

    def __init__(self, scope_name: str = ""):
        super().__init__(f"Scope '{scope_name}' has been disposed")
        self.scope_name = scope_name


class FactoryExecutionException(ContainerException):
    """Raised when a factory function fails."""

    def __init__(self, service_type: str = "", error: str = ""):
        super().__init__(
            f"Factory execution failed for '{service_type}': {error}"
        )
        self.service_type = service_type
        self.error = error


class RegistrationException(ContainerException):
    """Raised when service registration fails."""

    def __init__(self, service_type: str = "", reason: str = ""):
        super().__init__(
            f"Registration failed for '{service_type}': {reason}"
        )
        self.service_type = service_type
        self.reason = reason


class ValidationException(ContainerException):
    """Raised when validation fails."""

    def __init__(
        self,
        validation_type: str = "",
        errors: list = None,
    ):
        super().__init__(
            f"Validation failed ({validation_type}): {len(errors or [])} errors"
        )
        self.validation_type = validation_type
        self.errors = errors or []


class InvalidScopeException(ContainerException):
    """Raised when scope operations are invalid."""

    def __init__(self, scope_name: str = "", reason: str = ""):
        super().__init__(
            f"Invalid scope '{scope_name}': {reason}"
        )
        self.scope_name = scope_name
        self.reason = reason


class ServiceDescriptorException(ContainerException):
    """Raised when service descriptor is invalid."""

    def __init__(self, descriptor_type: str = "", reason: str = ""):
        super().__init__(
            f"Invalid service descriptor '{descriptor_type}': {reason}"
        )
        self.descriptor_type = descriptor_type
        self.reason = reason


class OrphanDependencyException(ContainerException):
    """Raised when an orphan dependency is detected."""

    def __init__(self, contract: str = "", missing_dependency: str = ""):
        super().__init__(
            f"Orphan dependency: '{contract}' requires '{missing_dependency}' "
            "which is not registered"
        )
        self.contract = contract
        self.missing_dependency = missing_dependency
