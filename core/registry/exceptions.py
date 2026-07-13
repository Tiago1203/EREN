"""Exceptions for the engine registry.

Declarative exception types only.
"""

from __future__ import annotations


class RegistryError(Exception):
    """Base class for all registry errors."""


class EngineNotFoundError(RegistryError):
    """Raised when a requested engine name is not registered."""


class EngineAlreadyRegisteredError(RegistryError):
    """Raised when registering a name that is already taken."""
