"""Module Descriptor for the Cognitive Composition Root.

Describes a module and its registration requirements.

Architecture only -- no implementations.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class ModuleDependency:
    """A dependency on another module."""

    module_name: str
    is_required: bool = True
    version: str = ""


@dataclass
class ModuleContract:
    """A contract registered by a module."""

    contract_name: str
    implementation: Any
    lifetime: str = "transient"
    dependencies: list = field(default_factory=list)


@dataclass
class ModuleDescriptor:
    """Descriptor for a composition module.

    Contains all information needed to register a module.
    """

    # Module identity
    module_name: str
    module_version: str = "1.0.0"

    # Module type
    module_type: str = "core"

    # Description
    description: str = ""

    # Dependencies on other modules
    dependencies: list = field(default_factory=list)

    # Contracts registered by this module
    contracts: list = field(default_factory=list)

    # Capabilities provided
    capabilities: list = field(default_factory=list)

    # Tags for grouping
    tags: set = field(default_factory=set)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Module registration function
    register_fn: Optional[Callable] = None

    # Validation function
    validate_fn: Optional[Callable] = None

    # Initialization function
    init_fn: Optional[Callable] = None

    # Order (for explicit ordering)
    order: int = 0

    # Whether this is an optional module
    is_optional: bool = False

    def add_dependency(self, module_name: str, is_required: bool = True) -> "ModuleDescriptor":
        """Add a module dependency.

        Args:
            module_name: Name of the required module.
            is_required: Whether the dependency is required.

        Returns:
            Self for chaining.
        """
        self.dependencies.append(
            ModuleDependency(module_name=module_name, is_required=is_required)
        )
        return self

    def add_contract(
        self,
        contract_name: str,
        implementation: Any,
        lifetime: str = "transient",
        dependencies: list = None,
    ) -> "ModuleDescriptor":
        """Add a contract registration.

        Args:
            contract_name: Name of the contract.
            implementation: Implementation type or instance.
            lifetime: Service lifetime.
            dependencies: List of dependency contracts.

        Returns:
            Self for chaining.
        """
        self.contracts.append(
            ModuleContract(
                contract_name=contract_name,
                implementation=implementation,
                lifetime=lifetime,
                dependencies=dependencies or [],
            )
        )
        return self

    def add_capability(self, capability_name: str) -> "ModuleDescriptor":
        """Add a capability.

        Args:
            capability_name: Name of the capability.

        Returns:
            Self for chaining.
        """
        self.capabilities.append(capability_name)
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "module_name": self.module_name,
            "module_version": self.module_version,
            "module_type": self.module_type,
            "description": self.description,
            "dependencies": [
                {"module_name": d.module_name, "is_required": d.is_required}
                for d in self.dependencies
            ],
            "contracts": [
                {
                    "contract_name": c.contract_name,
                    "lifetime": c.lifetime,
                    "dependencies": c.dependencies,
                }
                for c in self.contracts
            ],
            "capabilities": self.capabilities,
            "tags": list(self.tags),
            "is_optional": self.is_optional,
            "order": self.order,
        }


@dataclass
class ModuleInstance:
    """Represents a loaded module instance."""

    descriptor: ModuleDescriptor
    is_initialized: bool = False
    is_validated: bool = False
    error: str = ""
    initialized_at: str = ""

    def mark_initialized(self):
        """Mark module as initialized."""
        from datetime import datetime, timezone
        self.is_initialized = True
        self.initialized_at = datetime.now(timezone.utc).isoformat()

    def mark_validated(self):
        """Mark module as validated."""
        self.is_validated = True

    def mark_failed(self, error: str):
        """Mark module as failed."""
        self.error = error

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "module_name": self.descriptor.module_name,
            "is_initialized": self.is_initialized,
            "is_validated": self.is_validated,
            "error": self.error,
            "initialized_at": self.initialized_at,
        }
