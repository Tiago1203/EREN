"""Exception types for the Tools engine.

Scaffolding only — type declarations, no logic. One base error plus registry
and invocation failures shared across all external-access tools.
"""

from __future__ import annotations


class ToolsError(Exception):
    """Base class for all tools-related errors."""


class ToolNotFoundError(ToolsError):
    """Raised when a requested tool is not registered."""


class ToolAlreadyRegisteredError(ToolsError):
    """Raised when registering a tool whose name is already taken."""


class ToolInvocationError(ToolsError):
    """Raised when an external tool fails during invocation."""
