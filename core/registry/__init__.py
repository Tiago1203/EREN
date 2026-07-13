"""EREN engine registry.

Dynamic, dependency-injected registry of cognitive engines. Exposes the
concrete :class:`EngineRegistry`, its :class:`EngineRegistryPort` abstraction,
and registry exceptions.
"""

from __future__ import annotations

from core.registry.exceptions import (
    EngineAlreadyRegisteredError,
    EngineNotFoundError,
    RegistryError,
)
from core.registry.interfaces import EngineRegistryPort
from core.registry.registry import EngineRegistry

__all__ = [
    "EngineRegistry",
    "EngineRegistryPort",
    "RegistryError",
    "EngineNotFoundError",
    "EngineAlreadyRegisteredError",
]
