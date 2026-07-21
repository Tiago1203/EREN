"""
Biomedical Knowledge Engine

This module provides the knowledge management components for Clinical Intelligence,
including Knowledge Graph, Medical Ontology, Equipment Taxonomy, Standards Repository,
and Evidence Store.
"""

from core.intelligence.knowledge.graph import (
    BiomedicalKnowledgeGraph,
    ConceptNode,
    EntityNode,
    RelationEdge,
    RelationType,
)
from core.intelligence.knowledge.ontology import (
    MedicalOntology,
    MedicalOntologyConcept,
    CodeSystem,
    ConceptType,
)
from core.intelligence.knowledge.taxonomy import (
    EquipmentTaxonomy,
    DeviceCategory,
    FailureMode,
    MaintenanceLogic,
    RiskClass,
)
from core.intelligence.knowledge.standards import (
    StandardsRepository,
    Standard,
    StandardOrganization,
    VerificationMethod,
)
from core.intelligence.knowledge.retrieval import (
    EvidenceStore,
    Evidence,
    EvidenceSourceType,
    EvidenceLevel,
)

__version__ = "0.1.0"

__all__ = [
    # Graph
    "BiomedicalKnowledgeGraph",
    "ConceptNode",
    "EntityNode",
    "RelationEdge",
    "RelationType",
    # Ontology
    "MedicalOntology",
    "MedicalOntologyConcept",
    "CodeSystem",
    "ConceptType",
    # Taxonomy
    "EquipmentTaxonomy",
    "DeviceCategory",
    "FailureMode",
    "MaintenanceLogic",
    "RiskClass",
    # Standards
    "StandardsRepository",
    "Standard",
    "StandardOrganization",
    "VerificationMethod",
    # Retrieval
    "EvidenceStore",
    "Evidence",
    "EvidenceSourceType",
    "EvidenceLevel",
]
