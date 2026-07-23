"""
PHASE 4 - EPIC 6: Evidence Module

Empaquetado de evidencia:
- EvidencePackage
- EvidenceItem
- EvidenceBuilder
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib


class EvidenceQuality(str, Enum):
    """Calidad de evidencia."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class EvidenceType(str, Enum):
    """Tipo de evidencia."""
    PEER_REVIEWED = "peer_reviewed"
    CLINICAL_GUIDELINE = "clinical_guideline"
    REGULATORY = "regulatory"
    MANUFACTURER = "manufacturer"
    CASE_STUDY = "case_study"
    EXPERT_OPINION = "expert_opinion"
    WEB_CONTENT = "web_content"


@dataclass
class EvidenceItem:
    """Item de evidencia."""
    source_id: str
    content: str
    evidence_type: EvidenceType
    quality: EvidenceQuality
    
    # Metadata
    title: str = ""
    authors: list[str] = field(default_factory=list)
    publication_date: str = ""
    url: str = ""
    doi: str = ""
    
    # Scores
    relevance_score: float = 0.0
    reliability_score: float = 0.0
    
    # Attribution
    citation: str = ""
    
    def get_citation(self) -> str:
        """Obtiene citación formateada."""
        if self.citation:
            return self.citation
        
        parts = []
        if self.authors:
            parts.append(", ".join(self.authors[:3]))
            if len(self.authors) > 3:
                parts[-1] += ", et al."
        if self.title:
            parts.append(f'"{self.title}"')
        if self.publication_date:
            parts.append(f"({self.publication_date[:4]})")
        if self.doi:
            parts.append(f"DOI: {self.doi}")
        
        return ". ".join(parts) if parts else self.source_id


@dataclass
class EvidencePackage:
    """Paquete de evidencia."""
    query: str
    items: list[EvidenceItem] = field(default_factory=list)
    
    # Aggregated scores
    total_evidence: int = 0
    high_quality_count: int = 0
    avg_relevance: float = 0.0
    avg_reliability: float = 0.0
    
    # Metadata
    package_id: str = ""
    created_at: str = ""
    version: str = "1.0.0"
    
    def get_citations(self) -> list[str]:
        """Obtiene todas las citaciones."""
        return [item.get_citation() for item in self.items]
    
    def get_best_evidence(self, n: int = 3) -> list[EvidenceItem]:
        """Obtiene las N mejores evidencias."""
        sorted_items = sorted(
            self.items,
            key=lambda x: (x.quality.value, x.relevance_score),
            reverse=True
        )
        return sorted_items[:n]
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "query": self.query,
            "total_evidence": self.total_evidence,
            "high_quality_count": self.high_quality_count,
            "avg_relevance": self.avg_relevance,
            "items": [
                {
                    "source_id": item.source_id,
                    "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                    "evidence_type": item.evidence_type.value,
                    "quality": item.quality.value,
                    "citation": item.get_citation(),
                }
                for item in self.items
            ],
        }


class BaseEvidenceBuilder(ABC):
    """Clase base para builder de evidencia."""
    
    @abstractmethod
    def build(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> EvidencePackage:
        """Construye paquete de evidencia."""
        ...


class ClinicalEvidenceBuilder(BaseEvidenceBuilder):
    """Builder de evidencia clínica."""
    
    def __init__(self):
        self._source_type_map = {
            "pdf": EvidenceType.PEER_REVIEWED,
            "docx": EvidenceType.MANUFACTURER,
            "html": EvidenceType.WEB_CONTENT,
        }
    
    def build(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> EvidencePackage:
        """Construye paquete de evidencia clínica."""
        from datetime import datetime
        
        items = []
        
        for chunk in retrieved_chunks:
            # Determine evidence type
            source_type = chunk.get("source_type", "")
            evidence_type = self._source_type_map.get(
                source_type.lower(),
                EvidenceType.WEB_CONTENT
            )
            
            # Determine quality based on metadata
            quality = self._assess_quality(chunk)
            
            # Extract metadata
            metadata = chunk.get("metadata", {})
            
            item = EvidenceItem(
                source_id=chunk.get("id", chunk.get("source_id", "unknown")),
                content=chunk.get("text", "") or chunk.get("content", ""),
                evidence_type=evidence_type,
                quality=quality,
                title=metadata.get("title", ""),
                authors=metadata.get("authors", []),
                publication_date=metadata.get("date", ""),
                url=metadata.get("url", ""),
                doi=metadata.get("doi", ""),
                relevance_score=chunk.get("score", 0.5),
                reliability_score=self._calculate_reliability(quality, evidence_type),
            )
            
            items.append(item)
        
        # Calculate aggregated scores
        total = len(items)
        high_quality = sum(1 for i in items if i.quality == EvidenceQuality.HIGH)
        avg_relevance = sum(i.relevance_score for i in items) / total if total else 0
        avg_reliability = sum(i.reliability_score for i in items) / total if total else 0
        
        return EvidencePackage(
            query=query,
            items=items,
            total_evidence=total,
            high_quality_count=high_quality,
            avg_relevance=avg_relevance,
            avg_reliability=avg_reliability,
            package_id=self._generate_id(query),
            created_at=datetime.now().isoformat(),
        )
    
    def _assess_quality(self, chunk: dict) -> EvidenceQuality:
        """Evalúa calidad de evidencia."""
        metadata = chunk.get("metadata", {})
        
        # Check for peer-reviewed indicators
        if metadata.get("peer_reviewed"):
            return EvidenceQuality.HIGH
        
        # Check for clinical guideline
        if metadata.get("guideline"):
            return EvidenceQuality.HIGH
        
        # Check for regulatory approval
        if metadata.get("fda_approved") or metadata.get("ce_mark"):
            return EvidenceQuality.HIGH
        
        # Check for manufacturer docs
        if metadata.get("manufacturer_doc"):
            return EvidenceQuality.MEDIUM
        
        # Check for recent date (within 5 years)
        date = metadata.get("date", "")
        if date:
            try:
                year = int(date[:4])
                if 2021 <= year <= 2026:
                    return EvidenceQuality.MEDIUM
            except ValueError:
                pass
        
        # Default to low
        return EvidenceQuality.LOW
    
    def _calculate_reliability(
        self,
        quality: EvidenceQuality,
        evidence_type: EvidenceType,
    ) -> float:
        """Calcula score de confiabilidad."""
        base_scores = {
            EvidenceType.PEER_REVIEWED: 0.9,
            EvidenceType.CLINICAL_GUIDELINE: 0.85,
            EvidenceType.REGULATORY: 0.9,
            EvidenceType.MANUFACTURER: 0.6,
            EvidenceType.CASE_STUDY: 0.5,
            EvidenceType.EXPERT_OPINION: 0.4,
            EvidenceType.WEB_CONTENT: 0.3,
        }
        
        quality_multipliers = {
            EvidenceQuality.HIGH: 1.0,
            EvidenceQuality.MEDIUM: 0.8,
            EvidenceQuality.LOW: 0.5,
            EvidenceQuality.UNKNOWN: 0.3,
        }
        
        base = base_scores.get(evidence_type, 0.3)
        multiplier = quality_multipliers.get(quality, 0.5)
        
        return base * multiplier
    
    def _generate_id(self, query: str) -> str:
        """Genera ID único para el paquete."""
        content = f"{query}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


__all__ = [
    "EvidenceQuality",
    "EvidenceType",
    "EvidenceItem",
    "EvidencePackage",
    "BaseEvidenceBuilder",
    "ClinicalEvidenceBuilder",
]
