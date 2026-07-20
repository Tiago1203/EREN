"""Base contract shared by every EREN external-access tool.

In EREN, **all external access must go through a tool** — databases, files,
third-party services and clinical integrations included. Tools are *controlled
leaf capabilities*: they execute, they do not reason or coordinate (that is the
engines' job). This mirrors :class:`core.contracts.tool.Tool` but adds the shared
identity every catalog tool exposes, so the ``ToolsEngine`` registry can
discover, categorize and govern them uniformly.

Pure ``typing.Protocol`` — no logic, AI, or agents.
"""

from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable


class ToolCategory(str, Enum):
    """Coarse grouping used by the registry for discovery and governance."""

    DATA = "data"
    DOCUMENT = "document"
    MESSAGING = "messaging"
    MEDIA = "media"
    CLINICAL = "clinical"


@runtime_checkable
class ExternalTool(Protocol):
    """Common identity every external-access tool exposes.

    Callers depend on this abstraction (and the specific tool protocols that
    extend it), never on concrete vendor adapters — Dependency Inversion. Each
    concrete integration is an adapter that satisfies one of the specialized
    protocols in this catalog.
    """

    @property
    def name(self) -> str:
        """Stable, unique identifier of the tool (e.g. ``"supabase"``)."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    @property
    def category(self) -> ToolCategory:
        """Registry category this tool belongs to."""
        ...
