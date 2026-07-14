"""Capability Builder for EREN OS Cognitive Capability SDK.

Provides a builder pattern for creating capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Type

from core.sdk.types import (
    CapabilityCategory,
    CapabilityPriority,
    CapabilityMetadata,
)
from core.sdk.capability import BaseCapability
from core.sdk.exceptions import CapabilityBuilderError

if TYPE_CHECKING:
    pass


@dataclass
class CapabilityBuilder:
    """Builder for creating capabilities.

    Example:
        capability = (
            CapabilityBuilder()
            .named("OpenAI")
            .category(CapabilityCategory.LLM)
            .version("1.0")
            .implements("ReasoningContract")
            .build()
        )
    """

    # Identity
    _name: str = ""
    _version: str = "1.0.0"
    _category: CapabilityCategory = CapabilityCategory.CUSTOM

    # Description
    _description: str = ""
    _author: str = ""

    # Contracts and dependencies
    _contracts: list[str] = field(default_factory=list)
    _dependencies: list[str] = field(default_factory=list)

    # Priority
    _priority: int = CapabilityPriority.NORMAL.value

    # Configuration
    _configuration: dict = field(default_factory=dict)
    _metadata: dict = field(default_factory=dict)

    # Implementation
    _implementation: Type[BaseCapability] | None = None

    def named(self, name: str) -> "CapabilityBuilder":
        """Set capability name.

        Args:
            name: Capability name.

        Returns:
            Self for chaining.
        """
        self._name = name
        return self

    def version(self, version: str) -> "CapabilityBuilder":
        """Set capability version.

        Args:
            version: Version string.

        Returns:
            Self for chaining.
        """
        self._version = version
        return self

    def category(self, category: CapabilityCategory) -> "CapabilityBuilder":
        """Set capability category.

        Args:
            category: Capability category.

        Returns:
            Self for chaining.
        """
        self._category = category
        return self

    def description(self, description: str) -> "CapabilityBuilder":
        """Set capability description.

        Args:
            description: Capability description.

        Returns:
            Self for chaining.
        """
        self._description = description
        return self

    def author(self, author: str) -> "CapabilityBuilder":
        """Set capability author.

        Args:
            author: Author name.

        Returns:
            Self for chaining.
        """
        self._author = author
        return self

    def implements(self, *contracts: str) -> "CapabilityBuilder":
        """Add contracts.

        Args:
            contracts: Contract names.

        Returns:
            Self for chaining.
        """
        self._contracts.extend(contracts)
        return self

    def depends_on(self, *dependencies: str) -> "CapabilityBuilder":
        """Add dependencies.

        Args:
            dependencies: Capability names of dependencies.

        Returns:
            Self for chaining.
        """
        self._dependencies.extend(dependencies)
        return self

    def priority(self, priority: int) -> "CapabilityBuilder":
        """Set priority.

        Args:
            priority: Priority value.

        Returns:
            Self for chaining.
        """
        self._priority = priority
        return self

    def configure(self, **config: Any) -> "CapabilityBuilder":
        """Add configuration.

        Args:
            **config: Configuration key-value pairs.

        Returns:
            Self for chaining.
        """
        self._configuration.update(config)
        return self

    def metadata(self, **meta: Any) -> "CapabilityBuilder":
        """Add metadata.

        Args:
            **meta: Metadata key-value pairs.

        Returns:
            Self for chaining.
        """
        self._metadata.update(meta)
        return self

    def with_implementation(self, implementation: Type[BaseCapability]) -> "CapabilityBuilder":
        """Set capability implementation.

        Args:
            implementation: BaseCapability subclass.

        Returns:
            Self for chaining.
        """
        self._implementation = implementation
        return self

    def build(self) -> CapabilityMetadata:
        """Build the capability metadata.

        Returns:
            Capability metadata.

        Raises:
            CapabilityBuilderError: If build fails.
        """
        if not self._name:
            raise CapabilityBuilderError("Capability name is required")

        return CapabilityMetadata(
            name=self._name,
            version=self._version,
            category=self._category,
            description=self._description,
            author=self._author,
            contracts=tuple(self._contracts),
            dependencies=tuple(self._dependencies),
            configuration=self._configuration,
            metadata=self._metadata,
        )

    def create(self) -> Type[BaseCapability]:
        """Create a capability class.

        Returns:
            Capability class.

        Raises:
            CapabilityBuilderError: If create fails.
        """
        if not self._implementation:
            raise CapabilityBuilderError("Implementation is required")

        metadata = self.build()

        # Create a wrapper class with metadata
        class WrappedCapability(self._implementation):
            _capability_id = metadata.name
            _version = metadata.version

            def metadata(self):
                return metadata

        return WrappedCapability

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return self.build().to_dict()


@dataclass
class CapabilityClassBuilder(CapabilityBuilder):
    """Builder for creating capability classes directly.

    Provides a simpler interface for creating capabilities without
    needing to subclass BaseCapability manually.
    """

    # Execution function
    _execute_func: Any = None

    # Lifecycle functions
    _initialize_func: Any = None
    _shutdown_func: Any = None
    _health_func: Any = None

    def executes(self, func: Any) -> "CapabilityClassBuilder":
        """Set execution function.

        Args:
            func: Function to execute.

        Returns:
            Self for chaining.
        """
        self._execute_func = func
        return self

    def on_initialize(self, func: Any) -> "CapabilityClassBuilder":
        """Set initialization function.

        Args:
            func: Function to call on initialize.

        Returns:
            Self for chaining.
        """
        self._initialize_func = func
        return self

    def on_shutdown(self, func: Any) -> "CapabilityClassBuilder":
        """Set shutdown function.

        Args:
            func: Function to call on shutdown.

        Returns:
            Self for chaining.
        """
        self._shutdown_func = func
        return self

    def on_health(self, func: Any) -> "CapabilityClassBuilder":
        """Set health check function.

        Args:
            func: Function to call for health check.

        Returns:
            Self for chaining.
        """
        self._health_func = func
        return self

    def create_class(self) -> Type[BaseCapability]:
        """Create a capability class.

        Returns:
            Capability class.

        Raises:
            CapabilityBuilderError: If create fails.
        """
        if not self._execute_func:
            raise CapabilityBuilderError("execute function is required")

        metadata = self.build()

        # Create a dynamic capability class
        def make_capability():
            class DynamicCapability(BaseCapability):
                _capability_id = metadata.name
                _version = metadata.version

                def initialize(self, context):
                    if self._initialize_func:
                        self._initialize_func(context)

                def execute(self, context):
                    return self._execute_func(context)

                def shutdown(self):
                    if self._shutdown_func:
                        self._shutdown_func()

                def health(self):
                    if self._health_func:
                        return self._health_func()
                    return super().health()

                def metadata(self):
                    return metadata

            return DynamicCapability

        return make_capability()
