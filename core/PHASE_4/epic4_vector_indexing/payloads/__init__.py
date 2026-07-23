"""
PHASE 4 - EPIC 4: Payloads Module

Generación de payloads para Qdrant:
- Payload Builder
- Payload Schema
- Payload Validation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import uuid


@dataclass
class VectorPayload:
    """Payload para vector en Qdrant."""
    # Identificación
    id: str
    source_id: str = ""  # ID del documento o entidad original
    
    # Contenido
    text: str = ""
    title: str = ""
    chunk_index: int = 0
    
    # Metadatos
    domain: str = ""  # cardiology, radiology, etc.
    source_type: str = ""  # pdf, docx, etc.
    source_name: str = ""
    language: str = "en"
    
    # Códigos médicos
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    mesh_terms: list[str] = field(default_factory=list)
    
    # Calidad
    quality_score: float = 0.0
    confidence_score: float = 0.0
    
    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    
    # Versión
    version: str = "1.0.0"
    embedding_model: str = ""
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "text": self.text,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "domain": self.domain,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "language": self.language,
            "icd_codes": self.icd_codes,
            "snomed_codes": self.snomed_codes,
            "mesh_terms": self.mesh_terms,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "embedding_model": self.embedding_model,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VectorPayload":
        """Crea desde diccionario."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            text=data.get("text", ""),
            title=data.get("title", ""),
            chunk_index=data.get("chunk_index", 0),
            domain=data.get("domain", ""),
            source_type=data.get("source_type", ""),
            source_name=data.get("source_name", ""),
            language=data.get("language", "en"),
            icd_codes=data.get("icd_codes", []),
            snomed_codes=data.get("snomed_codes", []),
            mesh_terms=data.get("mesh_terms", []),
            quality_score=data.get("quality_score", 0.0),
            confidence_score=data.get("confidence_score", 0.0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            version=data.get("version", "1.0.0"),
            embedding_model=data.get("embedding_model", ""),
        )


class BasePayloadBuilder(ABC):
    """Clase base para builders de payload."""
    
    @abstractmethod
    def build(self, data: dict) -> VectorPayload:
        """Construye payload."""
        ...
    
    @abstractmethod
    def validate(self, payload: VectorPayload) -> bool:
        """Valida payload."""
        ...


class KnowledgePayloadBuilder(BasePayloadBuilder):
    """Builder para payloads de conocimiento."""
    
    def __init__(self):
        self.required_fields = ["text", "source_id"]
        self.optional_fields = [
            "title", "domain", "source_type", "language",
            "icd_codes", "snomed_codes", "mesh_terms",
            "quality_score", "confidence_score",
        ]
    
    def build(self, data: dict) -> VectorPayload:
        """Construye payload de conocimiento."""
        now = datetime.now().isoformat()
        
        return VectorPayload(
            id=data.get("id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            text=data.get("text", ""),
            title=data.get("title", ""),
            chunk_index=data.get("chunk_index", 0),
            domain=data.get("domain", ""),
            source_type=data.get("source_type", "document"),
            source_name=data.get("source_name", ""),
            language=data.get("language", "en"),
            icd_codes=data.get("icd_codes", []),
            snomed_codes=data.get("snomed_codes", []),
            mesh_terms=data.get("mesh_terms", []),
            quality_score=data.get("quality_score", 0.8),
            confidence_score=data.get("confidence_score", 0.8),
            created_at=now,
            updated_at=now,
            version=data.get("version", "1.0.0"),
            embedding_model=data.get("embedding_model", ""),
        )
    
    def validate(self, payload: VectorPayload) -> bool:
        """Valida payload."""
        # Check required fields
        if not payload.text or len(payload.text.strip()) == 0:
            return False
        
        if not payload.source_id:
            return False
        
        # Check text length
        if len(payload.text) > 100000:  # Max 100KB
            return False
        
        return True


class EntityPayloadBuilder(BasePayloadBuilder):
    """Builder para payloads de entidades."""
    
    def build(self, data: dict) -> VectorPayload:
        """Construye payload de entidad."""
        now = datetime.now().isoformat()
        
        return VectorPayload(
            id=data.get("id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            text=data.get("text", ""),
            title=data.get("entity_type", ""),
            chunk_index=0,
            domain=data.get("domain", ""),
            source_type="entity",
            source_name=data.get("entity_name", ""),
            language="en",
            icd_codes=data.get("icd_codes", []),
            snomed_codes=data.get("snomed_codes", []),
            mesh_terms=data.get("mesh_terms", []),
            quality_score=data.get("quality_score", 0.9),
            confidence_score=data.get("confidence_score", 0.9),
            created_at=now,
            updated_at=now,
            version=data.get("version", "1.0.0"),
        )
    
    def validate(self, payload: VectorPayload) -> bool:
        """Valida payload de entidad."""
        if not payload.text:
            return False
        
        if len(payload.text) > 1000:  # Entidades son cortas
            return False
        
        return True


class PayloadSchema:
    """Esquema de payload para indexación."""
    
    @staticmethod
    def get_knowledge_schema() -> dict:
        """Obtiene esquema para conocimiento."""
        return {
            "id": {"type": "keyword"},
            "source_id": {"type": "keyword"},
            "text": {"type": "text"},
            "title": {"type": "text"},
            "chunk_index": {"type": "integer"},
            "domain": {"type": "keyword"},
            "source_type": {"type": "keyword"},
            "source_name": {"type": "keyword"},
            "language": {"type": "keyword"},
            "icd_codes": {"type": "keyword"},
            "snomed_codes": {"type": "keyword"},
            "mesh_terms": {"type": "keyword"},
            "quality_score": {"type": "float"},
            "confidence_score": {"type": "float"},
            "created_at": {"type": "datetime"},
            "updated_at": {"type": "datetime"},
            "version": {"type": "keyword"},
            "embedding_model": {"type": "keyword"},
        }
    
    @staticmethod
    def get_entity_schema() -> dict:
        """Obtiene esquema para entidades."""
        return {
            "id": {"type": "keyword"},
            "source_id": {"type": "keyword"},
            "text": {"type": "text"},
            "entity_type": {"type": "keyword"},
            "entity_name": {"type": "keyword"},
            "domain": {"type": "keyword"},
            "icd_codes": {"type": "keyword"},
            "snomed_codes": {"type": "keyword"},
            "quality_score": {"type": "float"},
            "confidence_score": {"type": "float"},
            "created_at": {"type": "datetime"},
        }


__all__ = [
    "VectorPayload",
    "BasePayloadBuilder",
    "KnowledgePayloadBuilder",
    "EntityPayloadBuilder",
    "PayloadSchema",
]
