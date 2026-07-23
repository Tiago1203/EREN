"""
Medical Ontology Module

Complete implementation for medical ontology integration with
SNOMED-CT, ICD-10/ICD-11, LOINC, RxNorm and other coding systems.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Protocol
from collections import defaultdict


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
    HCPCS = "hcpcs"
    NDC = "ndc"
    CUSTOM = "custom"


class ConceptType(Enum):
    """Types of medical concepts."""
    # SNOMED-CT semantic tags
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
    SOCIAL_CONTEXT = "social_context"
    ENVIRONMENT = "environment"
    SITUATION = "situation"
    
    # Extended types
    MEDICATION = "medication"
    LAB_TEST = "lab_test"
    IMAGING = "imaging"
    ANATOMY = "anatomy"


class RelationshipType(Enum):
    """Types of relationships between concepts."""
    # IS_A hierarchy
    IS_A = "is_a"
    
    # Finding relationships
    ASSOCIATED_FINDING = "associated_finding"
    CAUSATIVE_AGENT = "causative_agent"
    DUE_TO = "due_to"
    MANIFESTS_AS = "manifests_as"
    
    # Procedure relationships
    METHOD = "method"
    HAS_PROCEDURE_SITE = "has_procedure_site"
    USES_DEVICE = "uses_device"
    HAS_INTENT = "has_intent"
    
    # Substance relationships
    HAS_ACTIVE_INGREDIENT = "has_active_ingredient"
    HAS_MECHANISM_OF_ACTION = "has_mechanism_of_action"
    
    # Anatomy relationships
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    SURGICAL_APPROACH = "surgical_approach"
    
    # Medication relationships
    HAS_DOSE_FORM = "has_dose_form"
    HAS_ROUTE_OF_ADMINISTRATION = "has_route_of_administration"
    CONTRAINDICATED_WITH = "contraindicated_with"
    
    # Finding/procedure relationships
    AFTER = "after"
    BEFORE = "before"
    ASSOCIATED_WITH = "associated_with"
    
    # Mapping relationships
    MAPS_TO = "maps_to"
    SAME_AS = "same_as"


@dataclass(frozen=True)
class OntologyRelationship:
    """Relationship between concepts in the ontology."""
    type_id: RelationshipType
    target_concept_id: str
    relationship_group: Optional[str] = None
    characteristic_type: str = "inferred"
    modifier: Optional[str] = None
    is_active: bool = True


@dataclass(frozen=True)
class MedicalOntologyConcept:
    """
    Medical ontology concept with full metadata.
    
    Represents a concept from SNOMED-CT, ICD, LOINC, etc.
    """
    concept_id: str
    fully_qualified_name: str
    semantic_tag: str
    is_active: bool = True
    module_id: Optional[str] = None
    definition_status: str = "Primitive"
    definitions: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    relationships: list[OntologyRelationship] = field(default_factory=list)
    language: str = "en"
    code_system: CodeSystem = CodeSystem.SNOMED_CT
    
    def __post_init__(self):
        if isinstance(self.code_system, str):
            object.__setattr__(self, 'code_system', CodeSystem(self.code_system))


@dataclass(frozen=True)
class ConceptHierarchy:
    """Complete hierarchy for a medical concept."""
    root: MedicalOntologyConcept
    ancestors: list[MedicalOntologyConcept] = field(default_factory=list)
    descendants: list[MedicalOntologyConcept] = field(default_factory=list)
    siblings: list[MedicalOntologyConcept] = field(default_factory=list)
    level: int = 0


@dataclass(frozen=True)
class CodeMapping:
    """Mapping between codes in different systems."""
    source_code: str
    source_system: CodeSystem
    target_code: str
    target_system: CodeSystem
    mapping_type: str = "exact"
    is_preferred: bool = True
    confidence: float = 1.0
    notes: Optional[str] = None


@dataclass(frozen=True)
class SearchResult:
    """Result of ontology search."""
    concept: MedicalOntologyConcept
    match_type: str
    score: float
    matched_term: str


class IOntologyRepository(Protocol):
    """Repository interface for ontology persistence."""
    
    async def get_concept(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> MedicalOntologyConcept | None: ...
    
    async def search_concepts(
        self,
        query: str,
        code_system: CodeSystem | None = None,
        limit: int = 10,
    ) -> list[MedicalOntologyConcept]: ...


class MedicalOntology:
    """
    Medical Ontology integrated with SNOMED-CT, ICD-10/11, LOINC.
    
    Provides:
    - Concept search and retrieval
    - Hierarchy navigation (parents, children, ancestors)
    - Code mapping between systems
    - Relationship traversal
    """
    
    def __init__(
        self,
        repository: Optional[IOntologyRepository] = None,
    ):
        self._repository = repository
        self._concepts: dict[str, dict[str, MedicalOntologyConcept]] = defaultdict(dict)
        self._mappings: dict[tuple[str, CodeSystem, CodeSystem], list[CodeMapping]] = defaultdict(list)
        self._search_index: dict[str, list[str]] = defaultdict(list)
    
    async def get_concept(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> MedicalOntologyConcept | None:
        """Get concept by ID."""
        if self._repository:
            return await self._repository.get_concept(concept_id, code_system)
        return self._concepts.get(code_system.value, {}).get(concept_id)
    
    async def add_concept(
        self,
        concept: MedicalOntologyConcept,
    ) -> None:
        """Add a concept to the ontology."""
        code_system = concept.code_system.value
        self._concepts[code_system][concept.concept_id] = concept
        
        self._search_index[concept.fully_qualified_name.lower()].append(concept.concept_id)
        for syn in concept.synonyms:
            self._search_index[syn.lower()].append(concept.concept_id)
    
    async def search_concepts(
        self,
        query: str,
        code_system: CodeSystem | None = None,
        concept_types: list[ConceptType] | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search concepts by term with fuzzy matching.
        
        Supports:
        - Exact term match
        - Partial match
        - Synonym matching
        - Concept type filtering
        """
        results: list[SearchResult] = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        systems_to_search = (
            [code_system.value] if code_system
            else list(self._concepts.keys())
        )
        
        for system in systems_to_search:
            for concept in self._concepts.get(system, {}).values():
                if concept_types and concept.semantic_tag not in [t.value for t in concept_types]:
                    continue
                
                score = 0.0
                match_type = "none"
                
                if query_lower == concept.fully_qualified_name.lower():
                    score = 1.0
                    match_type = "exact"
                elif query_lower in concept.fully_qualified_name.lower():
                    score = 0.8
                    match_type = "contains"
                elif any(query_lower == syn.lower() for syn in concept.synonyms):
                    score = 0.9
                    match_type = "synonym"
                elif any(query_lower in syn.lower() for syn in concept.synonyms):
                    score = 0.7
                    match_type = "synonym_contains"
                else:
                    concept_words = set(
                        concept.fully_qualified_name.lower().split()
                    )
                    overlap = query_words & concept_words
                    if overlap:
                        score = len(overlap) / max(len(query_words), len(concept_words))
                        match_type = "word_match"
                
                if score > 0:
                    results.append(SearchResult(
                        concept=concept,
                        match_type=match_type,
                        score=score,
                        matched_term=query,
                    ))
        
        results.sort(key=lambda r: (r.score, len(r.concept.fully_qualified_name)), reverse=True)
        return results[:limit]
    
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
        
        level = await self._calculate_level(concept_id, code_system)
        
        return ConceptHierarchy(
            root=concept,
            ancestors=ancestors,
            descendants=descendants,
            siblings=siblings,
            level=level,
        )
    
    async def get_parents(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Get parent concepts (more general)."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return []
        
        results = []
        for parent_id in concept.parents:
            parent = await self.get_concept(parent_id, code_system)
            if parent:
                results.append(parent)
        
        return results
    
    async def get_children(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Get child concepts (more specific)."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return []
        
        results = []
        for child_id in concept.children:
            child = await self.get_concept(child_id, code_system)
            if child:
                results.append(child)
        
        return results
    
    async def get_ancestors(
        self,
        concept_id: str,
        code_system: CodeSystem,
        max_depth: int = 20,
    ) -> list[MedicalOntologyConcept]:
        """Get all ancestor concepts up to root."""
        ancestors = []
        visited = set()
        current_ids = [concept_id]
        
        for _ in range(max_depth):
            if not current_ids:
                break
            
            next_ids = []
            for cid in current_ids:
                if cid in visited:
                    continue
                visited.add(cid)
                
                concept = await self.get_concept(cid, code_system)
                if concept:
                    for parent_id in concept.parents:
                        if parent_id not in visited:
                            parent = await self.get_concept(parent_id, code_system)
                            if parent:
                                ancestors.append(parent)
                                next_ids.append(parent_id)
            
            current_ids = next_ids
        
        return ancestors
    
    async def get_descendants(
        self,
        concept_id: str,
        code_system: CodeSystem,
        max_depth: int = 20,
    ) -> list[MedicalOntologyConcept]:
        """Get all descendant concepts."""
        descendants = []
        visited = set()
        current_ids = [concept_id]
        
        for _ in range(max_depth):
            if not current_ids:
                break
            
            next_ids = []
            for cid in current_ids:
                if cid in visited:
                    continue
                visited.add(cid)
                
                concept = await self.get_concept(cid, code_system)
                if concept:
                    for child_id in concept.children:
                        if child_id not in visited:
                            child = await self.get_concept(child_id, code_system)
                            if child:
                                descendants.append(child)
                                next_ids.append(child_id)
            
            current_ids = next_ids
        
        return descendants
    
    async def find_narrower(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Find more specific concepts (narrower terms)."""
        return await self.get_children(concept_id, code_system)
    
    async def find_broader(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> list[MedicalOntologyConcept]:
        """Find more general concepts (broader terms)."""
        return await self.get_parents(concept_id, code_system)
    
    async def map_code(
        self,
        code: str,
        source_system: CodeSystem,
        target_system: CodeSystem,
    ) -> list[CodeMapping]:
        """Map code between coding systems."""
        mapping_key = (code, source_system, target_system)
        
        if mapping_key in self._mappings:
            return self._mappings[mapping_key]
        
        source_concept = await self.get_concept(code, source_system)
        if not source_concept:
            return []
        
        mappings = []
        for relationship in source_concept.relationships:
            if relationship.type_id == RelationshipType.MAPS_TO:
                target_concept = await self.get_concept(
                    relationship.target_concept_id,
                    target_system,
                )
                if target_concept:
                    mappings.append(CodeMapping(
                        source_code=code,
                        source_system=source_system,
                        target_code=relationship.target_concept_id,
                        target_system=target_system,
                        mapping_type="semantic",
                        confidence=0.8,
                    ))
        
        self._mappings[mapping_key] = mappings
        return mappings
    
    async def add_code_mapping(
        self,
        mapping: CodeMapping,
    ) -> None:
        """Add a code mapping between systems."""
        key = (mapping.source_code, mapping.source_system, mapping.target_system)
        self._mappings[key].append(mapping)
    
    async def get_related_concepts(
        self,
        concept_id: str,
        code_system: CodeSystem,
        relationship_types: list[RelationshipType] | None = None,
    ) -> list[tuple[MedicalOntologyConcept, RelationshipType]]:
        """Get related concepts through relationships."""
        concept = await self.get_concept(concept_id, code_system)
        if not concept:
            return []
        
        results = []
        for rel in concept.relationships:
            if relationship_types and rel.type_id not in relationship_types:
                continue
            
            related = await self.get_concept(rel.target_concept_id, code_system)
            if related:
                results.append((related, rel.type_id))
        
        return results
    
    async def validate_code(
        self,
        code: str,
        code_system: CodeSystem,
    ) -> bool:
        """Validate if a code exists in the ontology."""
        concept = await self.get_concept(code, code_system)
        return concept is not None and concept.is_active
    
    async def get_concepts_by_type(
        self,
        concept_type: ConceptType,
        code_system: CodeSystem,
        limit: int = 100,
    ) -> list[MedicalOntologyConcept]:
        """Get all concepts of a specific type."""
        results = []
        for concept in self._concepts.get(code_system.value, {}).values():
            if concept.semantic_tag == concept_type.value:
                results.append(concept)
                if len(results) >= limit:
                    break
        
        return results
    
    async def find_common_ancestor(
        self,
        concept_id_1: str,
        concept_id_2: str,
        code_system: CodeSystem,
    ) -> MedicalOntologyConcept | None:
        """Find the most specific common ancestor of two concepts."""
        ancestors_1 = set(a.concept_id for a in await self.get_ancestors(concept_id_1, code_system))
        ancestors_1.add(concept_id_1)
        
        for ancestor in await self.get_ancestors(concept_id_2, code_system):
            if ancestor.concept_id in ancestors_1:
                return ancestor
        
        ancestors_2 = set(a.concept_id for a in await self.get_ancestors(concept_id_2, code_system))
        ancestors_2.add(concept_id_2)
        
        for ancestor in ancestors_1:
            if ancestor in ancestors_2:
                concept = await self.get_concept(ancestor, code_system)
                if concept:
                    return concept
        
        return None
    
    async def _calculate_level(
        self,
        concept_id: str,
        code_system: CodeSystem,
    ) -> int:
        """Calculate the depth level of a concept in the hierarchy."""
        level = 0
        visited = set()
        current_ids = [concept_id]
        
        while current_ids:
            next_ids = []
            for cid in current_ids:
                if cid in visited:
                    continue
                visited.add(cid)
                
                concept = await self.get_concept(cid, code_system)
                if concept:
                    for parent_id in concept.parents:
                        if parent_id not in visited:
                            next_ids.append(parent_id)
            
            if next_ids:
                level += 1
            current_ids = next_ids
        
        return level


__all__ = [
    "CodeSystem",
    "ConceptType",
    "RelationshipType",
    "OntologyRelationship",
    "MedicalOntologyConcept",
    "ConceptHierarchy",
    "CodeMapping",
    "SearchResult",
    "IOntologyRepository",
    "MedicalOntology",
]
