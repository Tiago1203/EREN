"""
Medical Vocabulary Module

Provides vocabulary management for biomedical concepts
and term mapping between systems.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class VocabularyType(Enum):
    """Types of vocabulary."""
    CLINICAL = "clinical"
    TECHNICAL = "technical"
    REGULATORY = "regulatory"
    LAYMAN = "layman"


@dataclass(frozen=True)
class BiomedicalConcept:
    """Biomedical concept with vocabulary."""
    concept_id: str
    preferred_term: str
    alternate_terms: list[str] = field(default_factory=list)
    definition: str | None = None
    vocabulary_type: VocabularyType = VocabularyType.CLINICAL
    category: str | None = None
    related_concepts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TermMapping:
    """Mapping between terms in different systems."""
    mapping_id: str
    source_term: str
    source_system: str
    target_term: str
    target_system: str
    confidence: float = 1.0
    is_preferred: bool = True
    mapping_type: str = "exact"


class MedicalVocabulary:
    """Medical vocabulary with term mapping."""
    
    def __init__(self):
        self._concepts: dict[str, BiomedicalConcept] = {}
        self._term_index: dict[str, str] = {}
        self._mappings: dict[str, list[TermMapping]] = {}
    
    async def add_concept(
        self,
        concept: BiomedicalConcept,
    ) -> None:
        """Add a biomedical concept."""
        self._concepts[concept.concept_id] = concept
        
        self._term_index[concept.preferred_term.lower()] = concept.concept_id
        for term in concept.alternate_terms:
            self._term_index[term.lower()] = concept.concept_id
    
    async def get_concept(
        self,
        concept_id: str,
    ) -> BiomedicalConcept | None:
        """Get concept by ID."""
        return self._concepts.get(concept_id)
    
    async def search_by_term(
        self,
        term: str,
    ) -> list[BiomedicalConcept]:
        """Search concepts by term."""
        term_lower = term.lower()
        concept_ids = set()
        
        if term_lower in self._term_index:
            concept_ids.add(self._term_index[term_lower])
        
        for concept_id, concept in self._concepts.items():
            if term_lower in concept.preferred_term.lower():
                concept_ids.add(concept_id)
            elif any(term_lower in alt.lower() for alt in concept.alternate_terms):
                concept_ids.add(concept_id)
        
        return [self._concepts[cid] for cid in concept_ids if cid in self._concepts]
    
    async def add_mapping(
        self,
        mapping: TermMapping,
    ) -> None:
        """Add a term mapping."""
        if mapping.source_term not in self._mappings:
            self._mappings[mapping.source_term] = []
        self._mappings[mapping.source_term].append(mapping)
    
    async def get_mappings(
        self,
        term: str,
        target_system: str | None = None,
    ) -> list[TermMapping]:
        """Get mappings for a term."""
        mappings = self._mappings.get(term, [])
        
        if target_system:
            mappings = [m for m in mappings if m.target_system == target_system]
        
        return mappings


__all__ = [
    "VocabularyType",
    "BiomedicalConcept",
    "TermMapping",
    "MedicalVocabulary",
]
