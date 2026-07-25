"""
PHASE 7 - EPIC 0: ISO 13485 Quality Management

Sistema de gestión de calidad ISO 13485:2016:
- Quality Manual
- Document Control
- Record Management
- CAPA (Corrective and Preventive Action)
- Management Review
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentStatus(str, Enum):
    """Estados de documento."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    RELEASED = "released"
    OBSOLETE = "obsolete"


class CAPAStatus(str, Enum):
    """Estados CAPA."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    ROOT_CAUSE = "root_cause_identified"
    CORRECTIVE_ACTION = "corrective_action"
    PREVENTIVE_ACTION = "preventive_action"
    VERIFICATION = "verification"
    CLOSED = "closed"


@dataclass
class QualityDocument:
    """Documento controlado ISO 13485."""
    document_id: str
    title: str
    document_type: str           # SOP, WI, Form, Policy
    version: str
    status: DocumentStatus
    owner: str
    created_at: datetime
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    review_date: Optional[datetime] = None
    distribution_list: list[str] = field(default_factory=list)


@dataclass
class CAPA:
    """Corrective and Preventive Action."""
    capa_id: str
    title: str
    description: str
    source: str                 # complaint, audit, incident, regulatory
    severity: str = "medium"    # critical, major, minor
    status: CAPAStatus = CAPAStatus.OPEN
    root_cause: str = ""
    corrective_action: str = ""
    preventive_action: str = ""
    effectiveness_criteria: str = ""
    verification_result: str = ""
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    closed_by: str = ""
    closed_at: Optional[datetime] = None


class ISO13485QualityManager:
    """Gestor de calidad ISO 13485."""

    def __init__(self):
        self._documents: dict[str, QualityDocument] = {}
        self._capas: list[CAPA] = []

    def create_document(
        self,
        title: str,
        doc_type: str,
        owner: str,
    ) -> QualityDocument:
        """Crea documento controlado."""
        doc_id = f"doc-{len(self._documents) + 1:04d}"
        doc = QualityDocument(
            document_id=doc_id,
            title=title,
            document_type=doc_type,
            version="1.0",
            status=DocumentStatus.DRAFT,
            owner=owner,
            created_at=datetime.utcnow(),
        )
        self._documents[doc_id] = doc
        return doc

    def approve_document(self, doc_id: str, approved_by: str) -> bool:
        """Aprueba documento."""
        doc = self._documents.get(doc_id)
        if not doc:
            return False
        doc.status = DocumentStatus.APPROVED
        doc.approved_by = approved_by
        doc.approved_at = datetime.utcnow()
        return True

    def release_document(self, doc_id: str, distribution_list: list[str]) -> bool:
        """Libera documento a distribución."""
        doc = self._documents.get(doc_id)
        if not doc:
            return False
        if doc.status != DocumentStatus.APPROVED:
            return False
        doc.status = DocumentStatus.RELEASED
        doc.distribution_list = distribution_list
        return True

    def create_capa(
        self,
        title: str,
        description: str,
        source: str,
        severity: str,
        created_by: str,
    ) -> CAPA:
        """Crea CAPA."""
        capa = CAPA(
            capa_id=f"capa-{len(self._capas) + 1:04d}",
            title=title,
            description=description,
            source=source,
            severity=severity,
            created_by=created_by,
        )
        self._capas.append(capa)
        return capa

    def close_capa(self, capa_id: str, closed_by: str, verification_result: str) -> bool:
        """Cierra CAPA."""
        for capa in self._capas:
            if capa.capa_id == capa_id:
                capa.status = CAPAStatus.CLOSED
                capa.closed_by = closed_by
                capa.closed_at = datetime.utcnow()
                capa.verification_result = verification_result
                return True
        return False

    def get_open_capas(self) -> list[CAPA]:
        """Obtiene CAPAs abiertos."""
        return [c for c in self._capas if c.status != CAPAStatus.CLOSED]
