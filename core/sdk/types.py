"""SDK types and enums for EREN OS Cognitive Capability SDK.

Defines all types, enums, and value objects used by the SDK.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass


# =============================================================================
# Capability States
# =============================================================================


class CapabilityState(str, Enum):
    """States for the capability lifecycle."""

    CREATED = "created"
    VALIDATED = "validated"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPOSED = "disposed"

    @classmethod
    def is_terminal(cls, state: "CapabilityState") -> bool:
        """Check if state is terminal."""
        return state in (cls.COMPLETED, cls.FAILED, cls.DISPOSED)

    @classmethod
    def is_active(cls, state: "CapabilityState") -> bool:
        """Check if state represents an active capability."""
        return state in (cls.READY, cls.EXECUTING)

    @classmethod
    def can_transition(cls, from_state: "CapabilityState", to_state: "CapabilityState") -> bool:
        """Check if transition is valid."""
        valid_transitions = {
            cls.CREATED: [cls.VALIDATED, cls.FAILED],
            cls.VALIDATED: [cls.REGISTERED, cls.FAILED],
            cls.REGISTERED: [cls.INITIALIZED, cls.FAILED, cls.DISPOSED],
            cls.INITIALIZED: [cls.READY, cls.FAILED],
            cls.READY: [cls.EXECUTING, cls.FAILED],
            cls.EXECUTING: [cls.COMPLETED, cls.FAILED],
            cls.COMPLETED: [cls.READY, cls.DISPOSED],
            cls.FAILED: [cls.READY, cls.DISPOSED],  # Can retry
            cls.DISPOSED: [],  # Terminal
        }
        return to_state in valid_transitions.get(from_state, [])


# =============================================================================
# Capability Categories
# =============================================================================


class CapabilityCategory(str, Enum):
    """Categories for capabilities."""

    REASONING = "reasoning"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    LLM = "llm"
    DEVICE = "device"
    CONNECTOR = "connector"
    CUSTOM = "custom"


# =============================================================================
# Capability Priority
# =============================================================================


class CapabilityPriority(int, Enum):
    """Standard capability priorities."""

    CRITICAL = 200
    HIGH = 150
    NORMAL = 100
    LOW = 50


# =============================================================================
# Value Objects
# =============================================================================


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata for a capability."""

    name: str
    version: str
    category: CapabilityCategory
    description: str = ""
    author: str = ""
    contracts: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    configuration: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category.value,
            "description": self.description,
            "author": self.author,
            "contracts": list(self.contracts),
            "dependencies": list(self.dependencies),
            "configuration": self.configuration,
            "metadata": self.metadata,
        }


@dataclass
class CapabilityContext:
    """Context passed to capabilities during execution."""

    # Identity
    capability_id: str = ""
    execution_id: str = ""

    # Session info
    session_id: str = ""
    user_id: str = ""

    # Runtime context
    runtime_context: dict = field(default_factory=dict)
    pipeline_context: dict = field(default_factory=dict)

    # Services (via contracts)
    memory_service: Any = None
    knowledge_service: Any = None
    event_publisher: Any = None
    metrics_collector: Any = None
    trace_collector: Any = None

    # Configuration
    config: dict = field(default_factory=dict)

    # Metadata
    metadata: dict = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return getattr(self, key, default) or self.metadata.get(key, default)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "capability_id": self.capability_id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "runtime_context": self.runtime_context,
            "pipeline_context": self.pipeline_context,
            "config": self.config,
            "metadata": self.metadata,
        }


@dataclass
class CapabilityResult:
    """Result from capability execution."""

    success: bool
    data: Any = None
    error: str = ""
    duration_ms: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


@dataclass
class CapabilityHealth:
    """Health status for a capability."""

    healthy: bool
    message: str = ""
    latency_ms: int = 0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "healthy": self.healthy,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "details": self.details,
        }


@dataclass
class ValidationResult:
    """Result of capability validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }
