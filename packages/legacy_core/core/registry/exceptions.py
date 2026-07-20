"""Registry exceptions.

Provides a typed exception hierarchy for the engine registry, making it easy
to handle specific error conditions in calling code.
"""

from __future__ import annotations


class RegistryError(Exception):
    """Base class for all registry errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class EngineNotFoundError(RegistryError):
    """Raised when an engine is not found in the registry.

    Attributes:
        name: The name of the engine that was not found.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"Engine '{name}' not found in registry")
        self.name = name


class EngineAlreadyRegisteredError(RegistryError):
    """Raised when registering a duplicate engine name.

    Attributes:
        name: The name of the engine that is already registered.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"Engine '{name}' already registered")
        self.name = name


class DependencyNotFoundError(RegistryError):
    """Raised when a required dependency is not satisfied.

    Attributes:
        engine: The name of the engine with the missing dependency.
        missing_dependency: The name of the missing dependency.
        required_version: The minimum required version.
    """

    def __init__(
        self,
        engine: str = "",
        missing_dependency: str = "",
        required_version: str = "",
    ) -> None:
        super().__init__(
            f"Engine '{engine}' requires '{missing_dependency}' "
            f"(minimum version: {required_version})"
        )
        self.engine = engine
        self.missing_dependency = missing_dependency
        self.required_version = required_version


class CompatibilityError(RegistryError):
    """Raised when version compatibility check fails.

    Attributes:
        engine: The name of the engine with compatibility issue.
        dependency: The name of the incompatible dependency.
        required_version: The minimum required version.
        actual_version: The actual installed version.
    """

    def __init__(
        self,
        engine: str = "",
        dependency: str = "",
        required_version: str = "",
        actual_version: str = "",
    ) -> None:
        super().__init__(
            f"Engine '{engine}': dependency '{dependency}' "
            f"version {actual_version} does not meet minimum {required_version}"
        )
        self.engine = engine
        self.dependency = dependency
        self.required_version = required_version
        self.actual_version = actual_version


class ValidationError(RegistryError):
    """Raised when engine validation fails.

    Attributes:
        engine: The name of the engine that failed validation.
        message: Description of the validation failure.
    """

    def __init__(self, engine: str = "", message: str = "") -> None:
        super().__init__(f"Engine '{engine}' validation failed: {message}")
        self.engine = engine
        self.message = message


class EventContractError(RegistryError):
    """Raised when an engine's event contracts are not satisfiable.

    Attributes:
        engine: The name of the engine.
        event_type: The problematic event type.
        message: Description of the contract violation.
    """

    def __init__(
        self,
        engine: str = "",
        event_type: str = "",
        message: str = "",
    ) -> None:
        super().__init__(
            f"Engine '{engine}' event contract error for '{event_type}': {message}"
        )
        self.engine = engine
        self.event_type = event_type
        self.message = message


class CircularDependencyError(RegistryError):
    """Raised when a circular dependency is detected.

    Attributes:
        cycle: The list of engines in the cycle.
    """

    def __init__(self, cycle: list[str] | None = None) -> None:
        cycle_str = " -> ".join(cycle or [])
        super().__init__(f"Circular dependency detected: {cycle_str}")
        self.cycle = cycle or []
