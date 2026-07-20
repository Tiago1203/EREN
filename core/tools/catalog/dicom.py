"""Contract for the DICOM tool — governed medical imaging access.

Query/retrieve/store of DICOM medical-imaging objects (studies, series,
instances) against a PACS, through a single controlled capability. Contract
only — no logic.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class DicomQuery:
    """A C-FIND-style query at a given retrieval level."""

    level: str = "STUDY"
    filters: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DicomReference:
    """Unique identifiers locating an object within a PACS."""

    study_uid: str = ""
    series_uid: str = ""
    instance_uid: str = ""


@dataclass(frozen=True, slots=True)
class DicomObject:
    """A DICOM object: its identifying reference, tags and pixel payload."""

    reference: DicomReference
    tags: Mapping[str, str] = field(default_factory=dict)
    pixel_data: bytes | None = None


@runtime_checkable
class DICOMTool(ExternalTool, Protocol):
    """Governed access to DICOM medical imaging."""

    def find(self, query: DicomQuery) -> Sequence[DicomReference]:
        """Query the PACS and return matching object references."""
        ...

    def fetch(self, reference: DicomReference) -> DicomObject:
        """Retrieve the object identified by *reference*."""
        ...

    def store(self, obj: DicomObject) -> DicomReference:
        """Store *obj* in the PACS and return its reference."""
        ...
