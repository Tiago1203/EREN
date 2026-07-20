"""Tool Discovery for EREN OS Universal Tool Calling Engine.

Discovers and registers tools dynamically.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import pkgutil
import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.tools.catalog.base import ExternalTool, ToolCategory
from core.tools.tool_types import ToolStatus


@dataclass
class DiscoveryConfig:
    """Configuration for tool discovery."""

    auto_discover: bool = True
    discovery_paths: list[str] = field(default_factory=list)
    exclude_packages: set[str] = field(default_factory=lambda: {"test", "tests", "__pycache__"})
    tool_decorator_name: str = "@tool"
    discover_methods: bool = True  # Discover decorated methods


@dataclass
class DiscoveredTool:
    """A tool discovered by the discovery engine."""

    name: str
    source_module: str
    source_class: str | None = None
    source_function: str | None = None
    tool_decorator: str | None = None
    metadata: dict = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ToolDiscovery:
    """Discovers tools from various sources.

    Discovery sources:
    - Python packages (auto-discovery)
    - Specific modules
    - Decorated functions/classes
    - External registries
    """

    def __init__(self, config: DiscoveryConfig | None = None):
        """Initialize tool discovery.

        Args:
            config: Discovery configuration.
        """
        self._config = config or DiscoveryConfig()
        self._discovered_tools: dict[str, DiscoveredTool] = {}
        self._lock = threading.RLock()

    @property
    def config(self) -> DiscoveryConfig:
        """Get discovery configuration."""
        return self._config

    def discover_from_package(self, package_name: str) -> list[DiscoveredTool]:
        """Discover tools from a Python package.

        Args:
            package_name: Name of package to scan.

        Returns:
            List of discovered tools.
        """
        discovered = []

        try:
            package = importlib.import_module(package_name)
            package_path = os.path.dirname(package.__file__)

            if not package_path or not os.path.isdir(package_path):
                return []

            # Scan package for modules
            for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
                if module_name in self._config.exclude_packages:
                    continue

                full_module = f"{package_name}.{module_name}"
                tools = self._discover_from_module(full_module)
                discovered.extend(tools)

        except ImportError:
            pass

        return discovered

    def discover_from_module(self, module_name: str) -> list[DiscoveredTool]:
        """Discover tools from a specific module.

        Args:
            module_name: Full module name.

        Returns:
            List of discovered tools.
        """
        return self._discover_from_module(module_name)

    def _discover_from_module(self, module_name: str) -> list[DiscoveredTool]:
        """Internal module discovery."""
        discovered = []

        try:
            module = importlib.import_module(module_name)

            # Check module-level functions with @tool decorator
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if hasattr(obj, "_tool_metadata"):
                    tool = DiscoveredTool(
                        name=getattr(obj, "_tool_name", name),
                        source_module=module_name,
                        source_function=name,
                        tool_decorator="@tool",
                        metadata=getattr(obj, "_tool_metadata", {}),
                    )
                    discovered.append(tool)
                    self._register_discovered(tool)

            # Check module-level classes with @tool decorator
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, "_tool_metadata"):
                    tool = DiscoveredTool(
                        name=getattr(obj, "_tool_name", name),
                        source_module=module_name,
                        source_class=name,
                        tool_decorator="@tool",
                        metadata=getattr(obj, "_tool_metadata", {}),
                    )
                    discovered.append(tool)
                    self._register_discovered(tool)

                # Check methods with @tool decorator
                if self._config.discover_methods:
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        if hasattr(method, "_tool_metadata"):
                            method_tool = DiscoveredTool(
                                name=getattr(method, "_tool_name", f"{name}.{method_name}"),
                                source_module=module_name,
                                source_class=name,
                                source_function=method_name,
                                tool_decorator="@tool",
                                metadata=getattr(method, "_tool_metadata", {}),
                            )
                            discovered.append(method_tool)
                            self._register_discovered(method_tool)

        except ImportError:
            pass

        return discovered

    def discover_from_path(self, path: str) -> list[DiscoveredTool]:
        """Discover tools from a file path.

        Args:
            path: Path to Python file or package.

        Returns:
            List of discovered tools.
        """
        discovered = []

        if not os.path.exists(path):
            return discovered

        if os.path.isfile(path) and path.endswith(".py"):
            # Single file
            module_name = self._path_to_module_name(path)
            discovered = self._discover_from_module(module_name)

        elif os.path.isdir(path):
            # Package directory
            for root, dirs, files in os.walk(path):
                # Filter excluded directories
                dirs[:] = [d for d in dirs if d not in self._config.exclude_packages]

                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        module_name = self._path_to_module_name(file_path)
                        tools = self._discover_from_module(module_name)
                        discovered.extend(tools)

        return discovered

    def _path_to_module_name(self, path: str) -> str:
        """Convert file path to module name."""
        import sys

        # Find common prefix
        for prefix in sys.path:
            if path.startswith(prefix):
                rel_path = os.path.relpath(path, prefix)
                module = rel_path.replace(os.sep, ".").replace("/", ".")[:-3]  # Remove .py
                return module.rstrip(".")

        # Fallback: use filename as module
        return os.path.basename(path)[:-3]

    def _register_discovered(self, tool: DiscoveredTool) -> None:
        """Register a discovered tool."""
        with self._lock:
            self._discovered_tools[tool.name] = tool

    def get_discovered(self) -> list[DiscoveredTool]:
        """Get all discovered tools.

        Returns:
            List of discovered tools.
        """
        with self._lock:
            return list(self._discovered_tools.values())

    def get_by_category(self, category: ToolCategory) -> list[DiscoveredTool]:
        """Get discovered tools by category.

        Args:
            category: Tool category.

        Returns:
            List of tools in category.
        """
        with self._lock:
            return [
                t for t in self._discovered_tools.values()
                if t.metadata.get("category") == category.value
            ]

    def clear(self) -> None:
        """Clear discovered tools."""
        with self._lock:
            self._discovered_tools.clear()


# =============================================================================
# Tool Decorator Utilities
# =============================================================================


def tool(
    name: str | None = None,
    description: str = "",
    category: ToolCategory | None = None,
    tags: list[str] | None = None,
    **metadata,
) -> Callable:
    """Decorator to mark a function as a tool.

    Args:
        name: Tool name (defaults to function name).
        description: Tool description.
        category: Tool category.
        tags: Tool tags.
        **metadata: Additional metadata.

    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        func._tool_metadata = {
            "name": name or func.__name__,
            "description": description or func.__doc__ or "",
            "category": category.value if category else None,
            "tags": tags or [],
            **metadata,
        }
        func._tool_name = name or func.__name__
        func._is_tool = True
        return func

    return decorator


def get_tool_metadata(func: Callable) -> dict | None:
    """Get tool metadata from decorated function.

    Args:
        func: Function to check.

    Returns:
        Tool metadata or None.
    """
    return getattr(func, "_tool_metadata", None)


def is_tool(func: Callable) -> bool:
    """Check if function is a tool.

    Args:
        func: Function to check.

    Returns:
        True if function is a tool.
    """
    return getattr(func, "_is_tool", False)
