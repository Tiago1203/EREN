"""
PHASE 4 - EPIC 8: Knowledge Quality Engine

Motor de calidad de conocimiento:
- Evidence Ranking
- Quality Score
- Bias Detection
- Duplicate Detection
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
import hashlib

from core.PHASE_4.foundation import (
    EvidenceLevel,
    QualityLevel,
    Citation,
)


class BiasType(str, Enum):
    """Tipos de sesgo."""
    PUBLICATION = "publication"           # Sesgo de publicación
    SELECTION = "selection"               # Sesgo de selección
    CONFIRMATION = "confirmation"         # Sesgo de confirmación
    CITATION = "citation"                 # Sesgo de citación
    LANGUAGE = "language"                # Sesgo de idioma
    GEOGRAPHIC = "geographic"             # Sesgo geográfico
    TEMPORAL = "temporal"                # Sesgo temporal


class QualityDimension(str, Enum):
    """Dimensiones de calidad."""
    ACCURACY = "accuracy"               # Exactitud
    COMPLETENESS = "completeness"       # Completitud
    CONSISTENCY = "consistency"         # Consistencia
    CURRENCY = "currency"              # Actualización
    RELEVANCE = "relevance"            # Relevancia
    TRUSTWORTHINESS = "trustworthiness"  # Confiabilidad


@dataclass
class QualityScore:
    """Score de calidad."""
    overall: float
    dimensions: dict[QualityDimension, float] = field(default_factory=dict)
    evidence_level: EvidenceLevel = EvidenceLevel.LEVEL_5
    quality_level: QualityLevel = QualityLevel.UNVERIFIED
    
    # Breakdown
    accuracy_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    currency_score: float = 0.0
    relevance_score: float = 0.0
    
    # Metadata
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    method: str = ""


@dataclass
class BiasReport:
    """Reporte de sesgo."""
    bias_type: BiasType
    severity: float  # 0-1
    description: str
    affected_claims: list[str] = field(default_factory=list)
    mitigation_suggestions: list[str] = field(default_factory=list)


@dataclass
class DuplicateGroup:
    """Grupo de documentos duplicados."""
    group_id: str
    documents: list[DuplicateCandidate] = field(default_factory=list)
    similarity_score: float = 0.0
    preferred_document_id: str = ""


@dataclass
class DuplicateCandidate:
    """Candidato a duplicado."""
    document_id: str
    content_hash: str
    title: str = ""
    similarity_score: float = 0.0


@dataclass
class EvidenceRanking:
    """Ranking de evidencia."""
    claim: str
    evidence_items: list[RankedEvidence] = field(default_factory=list)
    ranked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class RankedEvidence:
    """Evidencia rankeada."""
    citation: Citation
    relevance_score: float
    quality_score: QualityScore
    combined_score: float
    rank: int = 0
    justification: str = ""


class EvidenceRanker:
    """Ranker de evidencia."""
    
    def __init__(self):
        self._weights = {
            "relevance": 0.4,
            "quality": 0.4,
            "evidence_level": 0.2,
        }
    
    async def rank(
        self,
        claim: str,
        citations: list[Citation],
        relevance_scores: dict[str, float],
    ) -> EvidenceRanking:
        """Rankea evidencia para un claim."""
        ranked_items = []
        
        for citation in citations:
            # Get relevance score
            relevance = relevance_scores.get(citation.citation_id, 0.5)
            
            # Get quality score (would calculate from metadata)
            quality = QualityScore(overall=citation.quality_score)
            
            # Calculate combined score
            combined = self._calculate_combined_score(
                relevance,
                quality.overall,
                citation.evidence_level,
            )
            
            ranked_items.append(RankedEvidence(
                citation=citation,
                relevance_score=relevance,
                quality_score=quality,
                combined_score=combined,
                justification=self._generate_justification(
                    citation,
                    relevance,
                    quality,
                ),
            ))
        
        # Sort by combined score
        ranked_items.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Assign ranks
        for i, item in enumerate(ranked_items):
            item.rank = i + 1
        
        return EvidenceRanking(
            claim=claim,
            evidence_items=ranked_items,
        )
    
    def _calculate_combined_score(
        self,
        relevance: float,
        quality: float,
        evidence_level: EvidenceLevel,
    ) -> float:
        """Calcula score combinado."""
        # Evidence level weight
        level_weights = {
            EvidenceLevel.LEVEL_1A: 1.0,
            EvidenceLevel.LEVEL_1B: 0.9,
            EvidenceLevel.LEVEL_2A: 0.8,
            EvidenceLevel.LEVEL_2B: 0.7,
            EvidenceLevel.LEVEL_3: 0.5,
            EvidenceLevel.LEVEL_4: 0.3,
            EvidenceLevel.LEVEL_5: 0.2,
        }
        level_score = level_weights.get(evidence_level, 0.2)
        
        return (
            self._weights["relevance"] * relevance +
            self._weights["quality"] * quality +
            self._weights["evidence_level"] * level_score
        )
    
    def _generate_justification(
        self,
        citation: Citation,
        relevance: float,
        quality: QualityScore,
    ) -> str:
        """Genera justificación del ranking."""
        parts = []
        
        if relevance >= 0.8:
            parts.append("Highly relevant to the query")
        elif relevance >= 0.6:
            parts.append("Moderately relevant")
        
        if citation.evidence_level in [EvidenceLevel.LEVEL_1A, EvidenceLevel.LEVEL_1B]:
            parts.append("High-quality evidence")
        
        if quality.overall >= 0.8:
            parts.append("Well-sourced")
        
        return "; ".join(parts) if parts else "Standard evidence"


class QualityAssessor:
    """Asesor de calidad de conocimiento."""
    
    def __init__(self):
        self._quality_thresholds = {
            QualityLevel.HIGH: 0.8,
            QualityLevel.MEDIUM: 0.6,
            QualityLevel.LOW: 0.4,
        }
    
    async def assess(
        self,
        content: str,
        metadata: dict,
        citations: list[Citation],
    ) -> QualityScore:
        """Evalúa calidad del contenido."""
        # Calculate individual dimensions
        accuracy = await self._assess_accuracy(content, metadata)
        completeness = await self._assess_completeness(content, metadata)
        consistency = await self._assess_consistency(content, citations)
        currency = await self._assess_currency(metadata)
        relevance = await self._assess_relevance(content, metadata)
        
        # Calculate overall
        overall = (
            accuracy * 0.25 +
            completeness * 0.2 +
            consistency * 0.2 +
            currency * 0.15 +
            relevance * 0.2
        )
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall)
        
        # Determine evidence level
        evidence_level = self._determine_evidence_level(citations)
        
        return QualityScore(
            overall=overall,
            dimensions={
                QualityDimension.ACCURACY: accuracy,
                QualityDimension.COMPLETENESS: completeness,
                QualityDimension.CONSISTENCY: consistency,
                QualityDimension.CURRENCY: currency,
                QualityDimension.RELEVANCE: relevance,
            },
            evidence_level=evidence_level,
            quality_level=quality_level,
            accuracy_score=accuracy,
            completeness_score=completeness,
            consistency_score=consistency,
            currency_score=currency,
            relevance_score=relevance,
            method="weighted_average",
        )
    
    async def _assess_accuracy(self, content: str, metadata: dict) -> float:
        """Evalúa exactitud."""
        score = 0.7  # Base score
        
        # Has citations
        if metadata.get("has_citations"):
            score += 0.15
        
        # Has peer review indication
        if metadata.get("peer_reviewed"):
            score += 0.1
        
        # Source credibility
        source_credibility = metadata.get("source_credibility", 0.5)
        score = score * 0.6 + source_credibility * 0.4
        
        return min(score, 1.0)
    
    async def _assess_completeness(self, content: str, metadata: dict) -> float:
        """Evalúa completitud."""
        score = 0.5
        
        # Word count (longer is generally more complete)
        word_count = len(content.split())
        if word_count > 500:
            score += 0.2
        elif word_count > 200:
            score += 0.1
        
        # Has key sections
        if metadata.get("has_abstract"):
            score += 0.1
        if metadata.get("has_references"):
            score += 0.1
        
        return min(score, 1.0)
    
    async def _assess_consistency(
        self,
        content: str,
        citations: list[Citation],
    ) -> float:
        """Evalúa consistencia."""
        # Check if citations are consistent with content
        score = 0.8  # Default
        
        # Cross-reference citations
        if len(citations) > 2:
            score += 0.1  # Multiple sources
        
        # Citation quality consistency
        quality_scores = [c.quality_score for c in citations]
        if quality_scores:
            avg = sum(quality_scores) / len(quality_scores)
            if avg > 0.7:
                score += 0.1
        
        return min(score, 1.0)
    
    async def _assess_currency(self, metadata: dict) -> float:
        """Evalúa vigencia."""
        import time
        
        score = 0.5
        
        # Publication date
        pub_date = metadata.get("publication_date")
        if pub_date:
            try:
                # Check if within last 5 years
                year = int(pub_date.split("-")[0])
                current_year = datetime.now().year
                
                if current_year - year <= 2:
                    score = 0.9
                elif current_year - year <= 5:
                    score = 0.7
                elif current_year - year <= 10:
                    score = 0.5
                else:
                    score = 0.3
            except (ValueError, IndexError):
                pass
        
        # Last updated
        last_updated = metadata.get("last_updated")
        if last_updated:
            score = max(score, 0.8)
        
        return min(score, 1.0)
    
    async def _assess_relevance(self, content: str, metadata: dict) -> float:
        """Evalúa relevancia."""
        # Would use actual relevance scoring
        return metadata.get("relevance_score", 0.6)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determina nivel de calidad."""
        if score >= self._quality_thresholds[QualityLevel.HIGH]:
            return QualityLevel.HIGH
        elif score >= self._quality_thresholds[QualityLevel.MEDIUM]:
            return QualityLevel.MEDIUM
        elif score >= self._quality_thresholds[QualityLevel.LOW]:
            return QualityLevel.LOW
        return QualityLevel.UNVERIFIED
    
    def _determine_evidence_level(self, citations: list[Citation]) -> EvidenceLevel:
        """Determina nivel de evidencia."""
        if not citations:
            return EvidenceLevel.LEVEL_5
        
        # Return best evidence level among citations
        levels = [c.evidence_level for c in citations]
        level_order = [
            EvidenceLevel.LEVEL_1A, EvidenceLevel.LEVEL_1B,
            EvidenceLevel.LEVEL_2A, EvidenceLevel.LEVEL_2B,
            EvidenceLevel.LEVEL_3, EvidenceLevel.LEVEL_4, EvidenceLevel.LEVEL_5,
        ]
        
        best = EvidenceLevel.LEVEL_5
        best_idx = len(level_order) - 1
        
        for level in levels:
            if level in level_order:
                idx = level_order.index(level)
                if idx < best_idx:
                    best = level
                    best_idx = idx
        
        return best


class BiasDetector:
    """Detector de sesgos."""
    
    def __init__(self):
        self._indicators = self._load_indicators()
    
    def _load_indicators(self) -> dict:
        """Carga indicadores de sesgo."""
        return {
            BiasType.PUBLICATION: ["significant", "striking", "remarkable", "dramatic"],
            BiasType.SELECTION: ["only", "exclusively", "limited to", "selected"],
            BiasType.CONFIRMATION: ["as expected", "confirms", "supports our"],
            BiasType.CITATION: ["numerous", "extensive", "comprehensive"],
            BiasType.LANGUAGE: ["positive", "negative", "biased"],
        }
    
    async def detect_bias(
        self,
        content: str,
        citations: list[Citation],
    ) -> list[BiasReport]:
        """Detecta sesgos en contenido."""
        reports = []
        
        # Check each bias type
        for bias_type in BiasType:
            indicators = self._indicators.get(bias_type, [])
            
            for indicator in indicators:
                if indicator.lower() in content.lower():
                    report = BiasReport(
                        bias_type=bias_type,
                        severity=0.5,  # Would calculate actual severity
                        description=f"Potential {bias_type.value} bias detected",
                        mitigation_suggestions=self._get_mitigation_suggestions(bias_type),
                    )
                    reports.append(report)
                    break
        
        # Check citation bias
        citation_bias = await self._check_citation_bias(citations)
        if citation_bias:
            reports.append(citation_bias)
        
        # Check temporal bias
        temporal_bias = await self._check_temporal_bias(citations)
        if temporal_bias:
            reports.append(temporal_bias)
        
        return reports
    
    async def _check_citation_bias(
        self,
        citations: list[Citation],
    ) -> Optional[BiasReport]:
        """Verifica sesgo de citación."""
        if not citations:
            return None
        
        # Check if all citations are from same journal/source
        journals = set()
        for c in citations:
            if c.reference.journal:
                journals.add(c.reference.journal.lower())
        
        if len(journals) == 1:
            return BiasReport(
                bias_type=BiasType.CITATION,
                severity=0.6,
                description="All citations from the same journal",
                mitigation_suggestions=[
                    "Include citations from diverse sources",
                    "Consider broader literature review",
                ],
            )
        
        return None
    
    async def _check_temporal_bias(
        self,
        citations: list[Citation],
    ) -> Optional[BiasReport]:
        """Verifica sesgo temporal."""
        import time
        
        if not citations:
            return None
        
        years = []
        for c in citations:
            if c.reference.year:
                try:
                    years.append(int(c.reference.year))
                except ValueError:
                    pass
        
        if not years:
            return None
        
        avg_year = sum(years) / len(years)
        current_year = datetime.now().year
        
        # If average is very old
        if current_year - avg_year > 15:
            return BiasReport(
                bias_type=BiasType.TEMPORAL,
                severity=0.5,
                description=f"Most citations are from {int(avg_year)}",
                mitigation_suggestions=[
                    "Include more recent literature",
                    "Update with current research",
                ],
            )
        
        return None
    
    def _get_mitigation_suggestions(self, bias_type: BiasType) -> list[str]:
        """Obtiene sugerencias de mitigación."""
        suggestions = {
            BiasType.PUBLICATION: [
                "Report both positive and negative findings",
                "Include null results",
            ],
            BiasType.SELECTION: [
                "Broaden inclusion criteria",
                "Consider diverse populations",
            ],
            BiasType.CONFIRMATION: [
                "Seek contradictory evidence",
                "Consider alternative explanations",
            ],
            BiasType.CITATION: [
                "Include diverse perspectives",
                "Cite multiple journals",
            ],
            BiasType.LANGUAGE: [
                "Use neutral language",
                "Present balanced view",
            ],
            BiasType.GEOGRAPHIC: [
                "Include studies from different regions",
                "Consider global perspective",
            ],
            BiasType.TEMPORAL: [
                "Include recent studies",
                "Balance historical and current research",
            ],
        }
        return suggestions.get(bias_type, [])


class DuplicateDetector:
    """Detector de duplicados."""
    
    def __init__(self):
        self._hash_cache: dict[str, list[str]] = {}  # hash -> document_ids
    
    def _compute_hash(self, content: str) -> str:
        """Computa hash de contenido."""
        # Normalize content
        normalized = content.lower().strip()
        # Compute hash
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    async def detect_duplicates(
        self,
        documents: list[dict],  # [{id, content, title}]
        threshold: float = 0.9,
    ) -> list[DuplicateGroup]:
        """Detecta documentos duplicados."""
        groups = []
        processed = set()
        
        for i, doc1 in enumerate(documents):
            if doc1["id"] in processed:
                continue
            
            hash1 = self._compute_hash(doc1["content"])
            candidates = [doc1]
            
            for j, doc2 in enumerate(documents[i+1:], i+1):
                if doc2["id"] in processed:
                    continue
                
                hash2 = self._compute_hash(doc2["content"])
                
                # Calculate similarity
                similarity = self._calculate_similarity(
                    doc1["content"],
                    doc2["content"],
                )
                
                if similarity >= threshold:
                    candidates.append(doc2)
                    processed.add(doc2["id"])
            
            if len(candidates) > 1:
                processed.add(doc1["id"])
                
                group = DuplicateGroup(
                    group_id=str(i),
                    documents=[
                        DuplicateCandidate(
                            document_id=d["id"],
                            content_hash=self._compute_hash(d["content"]),
                            title=d.get("title", ""),
                            similarity_score=1.0,
                        )
                        for d in candidates
                    ],
                    similarity_score=threshold,
                    preferred_document_id=candidates[0]["id"],
                )
                groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud entre textos."""
        # Simple Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def index_document(self, document_id: str, content: str) -> str:
        """Indexa documento para detección de duplicados."""
        hash_val = self._compute_hash(content)
        
        if hash_val not in self._hash_cache:
            self._hash_cache[hash_val] = []
        
        self._hash_cache[hash_val].append(document_id)
        
        return hash_val


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "BiasType",
    "QualityDimension",
    # Data Classes
    "QualityScore",
    "BiasReport",
    "DuplicateGroup",
    "DuplicateCandidate",
    "EvidenceRanking",
    "RankedEvidence",
    # Engines
    "EvidenceRanker",
    "QualityAssessor",
    "BiasDetector",
    "DuplicateDetector",
]
