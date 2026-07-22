"""EREN OS Cognitive Plugin Framework.

This module implements the Cognitive Plugin Framework (CPF), the official
extensibility system for EREN.

Philosophy:
    The Cognitive Kernel should never be modified to add new capabilities.
    All future capabilities must be incorporated as Cognitive Plugins.

Key Concepts:
    - Plugin: A self-contained capability module
    - Manager: Coordinates plugin lifecycle
    - Registry: Manages plugin registration
    - Loader: Handles plugin loading
    - Manifest: Plugin metadata definition
    - Context: Runtime context for plugins

Example:
    >>> from core.PHASE_2.plugins import PluginManager
    >>> manager = PluginManager()
    >>> descriptor = manager.discover({"plugin_id": "my_plugin", "version": "1.0.0"})
    >>> manager.register(descriptor)
    >>> manager.activate("my_plugin")
"""

from __future__ import annotations

from core.PHASE_2.plugins.context import PluginContext
from core.PHASE_2.plugins.descriptor import PluginDescriptor

# Observability
from core.PHASE_2.plugins.events import (
    PluginEventPublisher,
    PluginEventType,
    get_plugin_event_publisher,
)

# Exceptions
from core.PHASE_2.plugins.exceptions import (
    PluginActivationError,
    PluginAlreadyRegisteredError,
    PluginContractError,
    PluginCyclicDependencyError,
    PluginDependencyError,
    PluginDisabledError,
    PluginException,
    PluginInitializationError,
    PluginLoaderError,
    PluginLoadError,
    PluginManifestError,
    PluginNotFoundError,
    PluginPolicyViolationError,
    PluginStateError,
    PluginValidationError,
    PluginVersionError,
)
from core.PHASE_2.plugins.loader import PluginLoader

# Core Plugin
from core.PHASE_2.plugins.manager import PluginManager, get_plugin_manager

# Manifest
from core.PHASE_2.plugins.manifest import (
    PluginManifestBuilder,
    PluginManifestParser,
)
from core.PHASE_2.plugins.metrics import (
    PluginMetrics,
    get_plugin_metrics,
    reset_plugin_metrics,
)
from core.PHASE_2.plugins.registry import (
    PluginRegistry,
    get_plugin_registry,
    reset_plugin_registry,
)
from core.PHASE_2.plugins.trace import (
    PluginTrace,
    get_plugin_trace,
    reset_plugin_trace,
)
from core.PHASE_2.plugins.types import (
    PluginCapability,
    PluginCategory,
    PluginManifest,
    PluginPolicy,
    PluginPriority,
    PluginState,
    ValidationResult,
)

__all__ = [
    # Core
    "PluginManager",
    "get_plugin_manager",
    "PluginDescriptor",
    "PluginContext",
    "PluginLoader",
    "PluginRegistry",
    "get_plugin_registry",
    "reset_plugin_registry",
    # Manifest
    "PluginManifestParser",
    "PluginManifestBuilder",
    # Types
    "PluginState",
    "PluginCategory",
    "PluginPriority",
    "PluginPolicy",
    "PluginManifest",
    "PluginCapability",
    "ValidationResult",
    # Events
    "PluginEventPublisher",
    "PluginEventType",
    "get_plugin_event_publisher",
    # Metrics
    "PluginMetrics",
    "get_plugin_metrics",
    "reset_plugin_metrics",
    # Trace
    "PluginTrace",
    "get_plugin_trace",
    "reset_plugin_trace",
    # Exceptions
    "PluginException",
    "PluginInitializationError",
    "PluginLoadError",
    "PluginNotFoundError",
    "PluginAlreadyRegisteredError",
    "PluginValidationError",
    "PluginDependencyError",
    "PluginActivationError",
    "PluginStateError",
    "PluginManifestError",
    "PluginContractError",
    "PluginLoaderError",
    "PluginPolicyViolationError",
    "PluginCyclicDependencyError",
    "PluginDisabledError",
    "PluginVersionError",
]
