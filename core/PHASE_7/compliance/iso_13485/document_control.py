"""
PHASE 7 - EPIC 0: ISO 13485 Document Control

Control de documentos ISO 13485:
- Document lifecycle management
- Version control
- Approval workflows
- Distribution tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib


class DocumentType(str, Enum):
    """Tipos de documentos ISO 13485."""
    QUALITY_MANUAL = "quality_manual"
    SOP = "sop"                     # Standard Operating Procedure
    WI = "wi"                       # Work Instruction
    FORM = "form"                   # Form
    POLICY = "policy"
    SPECIFICATION = "specification"
    RECORD = "record"


@dataclass
class DocumentVersion:
    """Versión de documento."""
    version: str
    content_hash: str
    created_by: str
    created_at: datetime
    changes_summary: str
    approved_by: Optional[str] = None


@dataclass
class DocumentDistribution:
    """Distribución de documento."""
    distribution_id: str
    document_id: str
    version: str
    distributed_to: str
    distributed_at: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class DocumentControlManager:
    """Gestor de control documental ISO 13485."""

    def __init__(self):
        self._documents: dict = {}
        self._distributions: list[DocumentDistribution] = []

    def register_document(
        self,
        doc_id: str,
        title: str,
        doc_type: DocumentType,
        content: str,
        created_by: str,
    ) -> None:
        """Registra documento con control de versiones."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        self._documents[doc_id] = {
            "doc_id": doc_id,
            "title": title,
            "type": doc_type,
            "current_version": "1.0",
            "versions": [
                DocumentVersion(
                    version="1.0",
                    content_hash=content_hash,
                    created_by=created_by,
                    created_at=datetime.utcnow(),
                    changes_summary="Initial version",
                )
            ],
            "created_at": datetime.utcnow(),
            "created_by": created_by,
        }

    def update_document(
        self,
        doc_id: str,
        content: str,
        changes_summary: str,
        updated_by: str,
    ) -> bool:
        """Actualiza documento (nueva versión)."""
        if doc_id not in self._documents:
            return False

        doc = self._documents[doc_id]
        current = doc["current_version"]
        parts = current.split(".")
        major = int(parts[0])
        minor = int(parts[1]) + 1
        new_version = f"{major}.{minor}"

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        doc["versions"].append(DocumentVersion(
            version=new_version,
            content_hash=content_hash,
            created_by=updated_by,
            created_at=datetime.utcnow(),
            changes_summary=changes_summary,
        ))
        doc["current_version"] = new_version
        return True

    def get_document(self, doc_id: str) -> Optional[dict]:
        """Obtiene documento."""
        return self._documents.get(doc_id)

    def get_version(self, doc_id: str, version: str) -> Optional[DocumentVersion]:
        """Obtiene versión específica."""
        doc = self._documents.get(doc_id)
        if not doc:
            return None
        for v in doc["versions"]:
            if v.version == version:
                return v
        return None
