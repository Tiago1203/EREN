"""
PHASE 4 - EPIC 7: Sources Module

Verificación de fuentes:
- Source Verifier
- Source Tracker
- Audit Trail
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# Use EvidenceLevel from foundation to avoid duplication
from core.PHASE_4.foundation import EvidenceLevel as FoundationEvidenceLevel


class SourceType(str, Enum):
    """Tipos de fuente."""
    PUBMED = "pubmed"
    PMC = "pmc"
    CLINICAL_GUIDELINE = "clinical_guideline"
    REGULATORY = "regulatory"
    MANUFACTURER = "manufacturer"
    TEXTBOOK = "textbook"
    WEBSITE = "website"
    OTHER = "other"


class SourceStatus(str, Enum):
    """Estados de fuente."""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    RETRACTED = "retracted"


# Re-export EvidenceLevel from foundation for backward compatibility
EvidenceLevel = FoundationEvidenceLevel


@dataclass
class SourceEvidence:
    """Evidencia de fuente."""
    source_id: str
    source_type: SourceType
    url: str = ""
    
    # Verification
    status: SourceStatus = SourceStatus.UNVERIFIED
    verification_date: str = ""
    verified_by: str = ""
    
    # Content
    title: str = ""
    content_hash: str = ""
    
    # Evidence level
    evidence_level: EvidenceLevel = EvidenceLevel.LEVEL_5
    
    # Timestamps
    first_seen: str = ""
    last_accessed: str = ""
    last_verified: str = ""
    
    # Reliability
    reliability_score: float = 0.0
    bias_indicators: list[str] = field(default_factory=list)


class BaseSourceVerifier(ABC):
    """Clase base para verificadores de fuente."""
    
    @abstractmethod
    async def verify(self, source: SourceEvidence) -> SourceEvidence:
        """Verifica fuente."""
        ...


class ClinicalSourceVerifier(BaseSourceVerifier):
    """Verificador de fuentes clínicas."""
    
    def __init__(self):
        self._reliability_weights = {
            SourceType.PUBMED: 0.9,
            SourceType.PMC: 0.85,
            SourceType.CLINICAL_GUIDELINE: 0.9,
            SourceType.REGULATORY: 0.85,
            SourceType.MANUFACTURER: 0.6,
            SourceType.TEXTBOOK: 0.7,
            SourceType.WEBSITE: 0.4,
            SourceType.OTHER: 0.3,
        }
    
    async def verify(self, source: SourceEvidence) -> SourceEvidence:
        """Verifica fuente."""
        now = datetime.now().isoformat()
        
        # Check status
        source.status = SourceStatus.VERIFIED
        source.verification_date = now
        source.last_verified = now
        
        # Set reliability based on type
        source.reliability_score = self._reliability_weights.get(
            source.source_type, 0.5
        )
        
        # Determine evidence level
        source.evidence_level = self._determine_evidence_level(source)
        
        return source
    
    def _determine_evidence_level(self, source: SourceEvidence) -> EvidenceLevel:
        """Determina nivel de evidencia."""
        type_to_level = {
            SourceType.PUBMED: EvidenceLevel.LEVEL_2B,
            SourceType.PMC: EvidenceLevel.LEVEL_2B,
            SourceType.CLINICAL_GUIDELINE: EvidenceLevel.LEVEL_1A,
            SourceType.REGULATORY: EvidenceLevel.LEVEL_2A,
            SourceType.MANUFACTURER: EvidenceLevel.LEVEL_4,
            SourceType.TEXTBOOK: EvidenceLevel.LEVEL_4,
            SourceType.WEBSITE: EvidenceLevel.LEVEL_5,
        }
        
        return type_to_level.get(source.source_type, EvidenceLevel.LEVEL_5)


class SourceTracker:
    """Rastreador de fuentes."""
    
    def __init__(self):
        self._sources: dict[str, SourceEvidence] = {}
        self._usage_count: dict[str, int] = {}
    
    async def track(self, source: SourceEvidence) -> None:
        """Registra uso de fuente."""
        self._sources[source.source_id] = source
        
        if source.source_id not in self._usage_count:
            self._usage_count[source.source_id] = 0
        self._usage_count[source.source_id] += 1
        
        source.last_accessed = datetime.now().isoformat()
    
    def get_usage_count(self, source_id: str) -> int:
        """Obtiene conteo de uso."""
        return self._usage_count.get(source_id, 0)
    
    def get_top_sources(self, n: int = 10) -> list[tuple]:
        """Obtiene fuentes más usadas."""
        sorted_sources = sorted(
            self._usage_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_sources[:n]


@dataclass
class AuditEntry:
    """Entrada de auditoría."""
    entry_id: str
    timestamp: str
    action: str
    
    # Who
    user_id: str = ""
    system_id: str = ""
    
    # What
    entity_type: str = ""
    entity_id: str = ""
    
    # Details
    details: dict = field(default_factory=dict)
    
    # Result
    success: bool = True
    error_message: str = ""


class AuditTrail:
    """Pista de auditoría."""
    
    def __init__(self):
        self._entries: list[AuditEntry] = []
    
    def log(
        self,
        action: str,
        entity_type: str = "",
        entity_id: str = "",
        user_id: str = "",
        details: dict | None = None,
        success: bool = True,
        error_message: str = "",
    ) -> AuditEntry:
        """Registra entrada de auditoría."""
        import uuid
        
        entry = AuditEntry(
            entry_id=str(uuid.uuid4())[:16],
            timestamp=datetime.now().isoformat(),
            action=action,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            success=success,
            error_message=error_message,
        )
        
        self._entries.append(entry)
        return entry
    
    def query(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Consulta entradas."""
        results = self._entries
        
        if entity_type:
            results = [e for e in results if e.entity_type == entity_type]
        
        if entity_id:
            results = [e for e in results if e.entity_id == entity_id]
        
        if action:
            results = [e for e in results if e.action == action]
        
        return results[-limit:]
    
    def get_entity_history(self, entity_id: str) -> list[AuditEntry]:
        """Obtiene historial de una entidad."""
        return [e for e in self._entries if e.entity_id == entity_id]


__all__ = [
    "SourceType",
    "SourceStatus",
    "EvidenceLevel",
    "SourceEvidence",
    "BaseSourceVerifier",
    "ClinicalSourceVerifier",
    "SourceTracker",
    "AuditEntry",
    "AuditTrail",
]
