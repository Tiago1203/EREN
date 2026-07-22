"""
Medical Ontology Module

Provides integration with medical coding systems:
- SNOMED-CT
- ICD-10/ICD-11
- LOINC
- RxNorm
"""

from core.PHASE_3.intelligence.knowledge.ontology.medical_ontology import (
    CodeSystem,
    ConceptType,
    RelationshipType,
    OntologyRelationship,
    MedicalOntologyConcept,
    ConceptHierarchy,
    CodeMapping,
    SearchResult,
    IOntologyRepository,
    MedicalOntology,
)

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
