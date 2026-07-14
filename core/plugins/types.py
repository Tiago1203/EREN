"""Plugin types and enums for EREN OS Cognitive Plugin Framework.

Defines all types, enums, and value objects used by the plugin system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Plugin States
# =============================================================================


class PluginState(str, Enum):
    """States for the plugin lifecycle."""

    DISCOVERED = "discovered"
    REGISTERED = "registered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    UNLOADED = "unloaded"

    @classmethod
    def is_active(cls, state: PluginState) -> bool:
        """Check if state represents an active plugin."""
        return state == cls.ACTIVE

    @classmethod
    def can_transition(cls, from_state: PluginState, to_state: PluginState) -> bool:
        """Check if transition is valid."""
        valid_transitions = {
            cls.DISCOVERED: [cls.REGISTERED, cls.FAILED],
            cls.REGISTERED: [cls.LOADED, cls.FAILED],
            cls.LOADED: [cls.INITIALIZED, cls.FAILED, cls.UNLOADED],
            cls.INITIALIZED: [cls.ACTIVE, cls.PAUSED, cls.FAILED],
            cls.ACTIVE: [cls.PAUSED, cls.FAILED],
            cls.PAUSED: [cls.ACTIVE, cls.FAILED],
            cls.FAILED: [cls.LOADED, cls.UNLOADED],  # Can retry
            cls.UNLOADED: [cls.LOADED],  # Can reload
        }
        return to_state in valid_transitions.get(from_state, [])


# =============================================================================
# Plugin Categories
# =============================================================================


class PluginCategory(str, Enum):
    """Categories for plugins."""

    COGNITIVE = "cognitive"
    LLM = "llm"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    DEVICE = "device"
    FHIR = "fhir"
    HL7 = "hl7"
    PACS = "pacs"
    TOOLS = "tools"
    CONNECTOR = "connector"
    CUSTOM = "custom"


# =============================================================================
# Plugin Priority
# =============================================================================


class PluginPriority(int, Enum):
    """Standard plugin priorities."""

    CRITICAL = 200
    HIGH = 150
    NORMAL = 100
    LOW = 50
    BACKGROUND = 10


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Manifest defining plugin metadata."""

    plugin_id: str
    version: str
    name: str = ""
    description: str = ""
    author: str = ""
    category: PluginCategory = PluginCategory.CUSTOM
    priority: int = PluginPriority.NORMAL.value
    contracts: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    configuration: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "category": self.category.value,
            "priority": self.priority,
            "contracts": list(self.contracts),
            "dependencies": list(self.dependencies),
            "capabilities": list(self.capabilities),
            "configuration": self.configuration,
            "metadata": self.metadata,
        }


@dataclass
class PluginDescriptor:
    """Descriptor for a plugin instance."""

    manifest: PluginManifest
    state: PluginState = PluginState.DISCOVERED
    instance: Any = None
    error: str = ""
    loaded_at: datetime | None = None
    initialized_at: datetime | None = None
    activated_at: datetime | None = None
    last_error: datetime | None = None
    retry_count: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self.manifest.plugin_id

    @property
    def version(self) -> str:
        """Get plugin version."""
        return self.manifest.version

    @property
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.state == PluginState.ACTIVE

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.state in (
            PluginState.LOADED,
            PluginState.INITIALIZED,
            PluginState.ACTIVE,
            PluginState.PAUSED,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "manifest": self.manifest.to_dict(),
            "state": self.state.value,
            "error": self.error,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "initialized_at": self.initialized_at.isoformat() if self.initialized_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
        }


@dataclass
class PluginCapability:
    """A capability provided by a plugin."""

    name: str
    version: str
    contracts: list[str] = field(default_factory=list)
    description: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "contracts": self.contracts,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class PluginContext:
    """Context passed to plugins during lifecycle."""

    plugin_id: str
    runtime_config: dict = field(default_factory=dict)
    dependency_context: dict = field(default_factory=dict)
    capability_registry: Any = None
    event_bus: Any = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "runtime_config": self.runtime_config,
            "dependency_context": self.dependency_context,
            "metadata": self.metadata,
        }


# =============================================================================
# Policy Types
# =============================================================================


class PluginPolicy(str, Enum):
    """Policies for plugin management."""

    STRICT = "strict"
    GRACEFUL = "graceful"
    LAZY = "lazy"
    EAGER = "eager"
    RECOMMENDED = "recommended"


# =============================================================================
# Validation Result
# =============================================================================


@dataclass
class ValidationResult:
    """Result of plugin validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manifest_valid: bool = True
    dependencies_satisfied: bool = True
    contracts_satisfied: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "manifest_valid": self.manifest_valid,
            "dependencies_satisfied": self.dependencies_satisfied,
            "contracts_satisfied": self.contracts_satisfied,
        }
