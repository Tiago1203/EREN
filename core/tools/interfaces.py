"""Abstract interfaces (ports) for the Tools engine.

Defines the contract the Tools engine exposes: a controlled **registry** through
which cognitive engines discover and invoke external-access tools. Pure
``typing.Protocol`` — no logic, AI, or agents. The concrete tool contracts live
in :mod:`core.tools.catalog`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from .catalog.base import ExternalTool, ToolCategory


@runtime_checkable
class ToolsPort(Protocol):
    """Contract for registering, discovering and retrieving tools.

    Callers depend on this abstraction rather than on concrete adapters
    (Dependency Inversion), so external integrations can be added or swapped
    without changing the engines that use them.
    """

    def register(self, tool: ExternalTool) -> None:
        """Add *tool* to the registry under its ``name``."""
        ...

    def get(self, name: str) -> ExternalTool:
        """Return the registered tool identified by *name*."""
        ...

    def list(self, category: ToolCategory | None = None) -> Sequence[ExternalTool]:
        """List registered tools, optionally filtered by *category*."""
        ...
