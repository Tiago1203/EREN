"""
Medical Ontology Module

Provides integration with medical coding systems:
- SNOMED-CT
- ICD-10/ICD-11
- LOINC
- RxNorm
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class CodeSystem(Enum):
    """Medical coding systems."""
    SNOMED_CT = "snomed_ct"
    ICD_10 = "icd_10"
    ICD_11 = "icd_11"
    LOINC = "loinc"
    RXNORM = "rxnorm"
    UMLS = "umls"
    ATC = "atc"
    ICD_9_CM = "icd_9_cm"
    CPT = "cpt"
    GMDN = "gmdn"
    CUSTOM = "custom"


class ConceptType(Enum):
    """Types of medical concepts."""
    DISORDER = "disorder"
    PROCEDURE = "procedure"
    FINDING = "finding"
    OBSERVABLE_ENTITY = "observable_entity"
    SUBSTANCE = "substance"
    ORGANISM = "organism"
    BODY_STRUCTURE = "body_structure"
    EVENT = "event"
    SPECIMEN = "specimen"
    DEVICE = "device"
    QUALIFIER_VALUE = "qualifier_value"


@dataclass(frozen=True)
class OntologyRelationship:
    """Relationship between concepts."""
    type_id: str
    target_concept_id: str
    relationship_group: str | None = None
    characteristic_type: str = "inferred"
    modifier: str | None = None


@dataclass(frozen=True)
class MedicalOntologyConcept:
    """Medical ontology concept."""
    concept_id: str
    fully_qualified_name: str
    semantic_tag: str
    is_active: bool = True
    module_id: str | None = None
    definitions: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    relationships: list[OntologyRelationship] = field(default_factory=list)


@dataclass(frozen=True)
class ConceptHierarchy:
    """Hierarchy of a medical concept."""
    root: MedicalOntologyConcept
    ancestors: list[MedicalOntologyConcept] = field(default_factory=list)
    descendants: list[MedicalOntologyConcept] = field(default_factory=list)
    siblings: list[MedicalOntologyConcept] = field(default_factory=list)


class MedicalOntology:
    """
    Medical Ontology integrated with SNOMED-CT, ICD-10/11, LOINC.
    """
    
    def __init__(self):
        self._concepts: dict[str, dict[str, MedicalOntologyConcept]] = {}
    
    async def get_concept(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> MedicalOntologyConcept | None:
        """Get concept by ID."""
        return self._concepts.get(code_system.value, {}).get(concept_id)
    
    async def search_concepts(
        self,
        query: str,
        code_system: CodeSystem | None = None,
        limit: int = 10,
    ) -> list[MedicalOntologyConcept]:
        """Search concepts by term."""
        results = []
        search_lower = query.lower()
        
        systems = [code_system] if code_system else CodeSystem
        
        for system in systems:
            if isinstance(system, CodeSystem):
                for concept in self._concepts.get(system.value, {}).values():
                    if (search_lower in concept.fully_qualified_name.lower() or
                        any(search_lower in syn.lower() for syn in concept.synonyms)):
                        results.append(concept)
                        if len(results) >= limit:
                            return results
        
        return results
    
    async def get_hierarchy(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> ConceptHierarchy | None:
        """Get complete hierarchy for a concept."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return None
        
        ancestors = []
        for parent_id in concept.parents:
            parent = await self.get_concept(parent_id, code_system)
            if parent:
                ancestors.append(parent)
        
        descendants = []
        for child_id in concept.children:
            child = await self.get_concept(child_id, code_system)
            if child:
                descendants.append(child)
        
        siblings = []
        for parent_id in concept.parents:
            parent = await self.get_concept(parent_id, code_system)
            if parent:
                for sibling_id in parent.children:
                    if sibling_id != concept_id:
                        sibling = await self.get_concept(sibling_id, code_system)
                        if sibling:
                            siblings.append(sibling)
        
        return ConceptHierarchy(
            root=concept,
            ancestors=ancestors,
            descendants=descendants,
            siblings=siblings,
        )
    
    async def map_code(
        self,
        code: str,
        source_system: CodeSystem,
        target_system: CodeSystem,
    ) -> list[str]:
        """Map code between coding systems."""
        source_concept = await self.get_concept(code, source_system)
        if not source_concept:
            return []
        
        mapped_codes = []
        for relationship in source_concept.relationships:
            target_concept = await self.get_concept(
                relationship.target_concept_id,
                target_system,
            )
            if target_concept:
                mapped_codes.append(target_concept.concept_id)
        
        return mapped_codes
    
    async def find_narrower(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Find more specific concepts."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return []
        
        results = []
        for child_id in concept.children:
            child = await self.get_concept(child_id, code_system)
            if child:
                results.append(child)
        
        return results
    
    async def find_broader(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Find more general concepts."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return []
        
        results = []
        for parent_id in concept.parents:
            parent = await self.get_concept(parent_id, code_system)
            if parent:
                results.append(parent)
        
        return results


__all__ = [
    "CodeSystem",
    "ConceptType",
    "OntologyRelationship",
    "MedicalOntologyConcept",
    "ConceptHierarchy",
    "MedicalOntology",
]
