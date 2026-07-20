"""Contract for the Supabase tool — governed data-platform access.

Read/write access to the Supabase-backed data platform (Postgres, auth, storage)
routed through a single controlled capability. Contract only — no logic.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class SupabaseQuery:
    """A read request against a table/view."""

    table: str
    filters: Mapping[str, str] = field(default_factory=dict)
    columns: tuple[str, ...] = field(default_factory=tuple)
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class SupabaseMutation:
    """A write request (insert/update/delete) against a table."""

    table: str
    values: Mapping[str, object] = field(default_factory=dict)
    filters: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SupabaseResult:
    """Rows returned by a query or affected by a mutation."""

    rows: Sequence[Mapping[str, object]] = field(default_factory=tuple)


@runtime_checkable
class SupabaseTool(ExternalTool, Protocol):
    """Governed access to the Supabase data platform."""

    def query(self, request: SupabaseQuery) -> SupabaseResult:
        """Read rows matching *request*."""
        ...

    def mutate(self, request: SupabaseMutation) -> SupabaseResult:
        """Apply an insert/update/delete described by *request*."""
        ...
