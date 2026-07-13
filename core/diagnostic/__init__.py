"""EREN core — Diagnostic engine. Scaffolding only; no functionality yet."""

from .engine import DiagnosticEngine
from .exceptions import DiagnosticError
from .interfaces import DiagnosticPort

__all__ = ["DiagnosticEngine", "DiagnosticError", "DiagnosticPort"]
