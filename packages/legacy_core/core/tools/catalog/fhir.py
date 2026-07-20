"""Contract for the FHIR tool — governed HL7 FHIR resource access.

Read/search/create of FHIR R4-style resources on a clinical data server, through
a single controlled capability. Contract only — no logic.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class FhirReference:
    """A logical reference to a resource (e.g. ``Device/123``)."""

    resource_type: str
    resource_id: str = ""


@dataclass(frozen=True, slots=True)
class FhirResource:
    """A FHIR resource represented as its parsed body."""

    resource_type: str
    body: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FhirQuery:
    """A search over a resource type with query parameters."""

    resource_type: str
    params: Mapping[str, str] = field(default_factory=dict)


@runtime_checkable
class FHIRTool(ExternalTool, Protocol):
    """Governed access to FHIR clinical resources."""

    def read(self, reference: FhirReference) -> FhirResource:
        """Read the resource identified by *reference*."""
        ...

    def search(self, query: FhirQuery) -> Sequence[FhirResource]:
        """Search for resources matching *query*."""
        ...

    def create(self, resource: FhirResource) -> FhirReference:
        """Create *resource* and return its new reference."""
        ...
