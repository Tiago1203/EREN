"""
Biomedical Knowledge Engine

This module provides the knowledge management components for Clinical Intelligence,
including Knowledge Graph, Medical Ontology, Equipment Taxonomy, Standards Repository,
and Evidence Store.

Complete implementation of EPIC 1 for EREN PHASE 3.
"""

# Version
__version__ = "1.0.0"

# Graph module
from core.PHASE_3.intelligence.knowledge.graph import (
    ConceptType,
    RelationType,
    ConceptNode,
    EntityNode,
    StandardNode,
    DeviceNode,
    RelationEdge,
    Subgraph,
    Path,
    GraphStats,
    IKnowledgeGraphRepository,
    BiomedicalKnowledgeGraph,
)

# Ontology module
from core.PHASE_3.intelligence.knowledge.ontology import (
    CodeSystem,
    ConceptType as OntologyConceptType,
    RelationshipType,
    OntologyRelationship,
    MedicalOntologyConcept,
    ConceptHierarchy,
    CodeMapping,
    SearchResult,
    IOntologyRepository,
    MedicalOntology,
)

# Taxonomy module
from core.PHASE_3.intelligence.knowledge.taxonomy import (
    RiskClass,
    DeviceCategory,
    FailureSeverity,
    FailureFrequency,
    MaintenanceType,
    FailureMode,
    MaintenanceLogic,
    CategoryHierarchy,
    FailureModeAnalysis,
    MaintenanceSchedule,
    ITaxonomyRepository,
    EquipmentTaxonomy,
)

# Standards module
from core.PHASE_3.intelligence.knowledge.standards import (
    StandardOrganization,
    StandardCategory,
    VerificationMethod,
    ComplianceStatus,
    RiskClassification,
    Standard,
    StandardRequirement,
    ComplianceCheck,
    ComplianceReport,
    StandardComparison,
    IStandardsRepository,
    StandardsRepository,
)

# Evidence module
from core.PHASE_3.intelligence.knowledge.retrieval import (
    EvidenceSourceType,
    EvidenceLevel,
    QueryType,
    Evidence,
    EvidenceQuery,
    EvidenceFilters,
    EvidenceRetrieval,
    EvidenceWithRelevance,
    EvidenceChain,
    EvidenceStore,
)

# Vocabulary module
from core.PHASE_3.intelligence.knowledge.vocabulary import (
    VocabularyType,
    BiomedicalConcept,
    TermMapping,
    MedicalVocabulary,
)

# Exceptions
from core.PHASE_3.intelligence.knowledge.exceptions import (
    KnowledgeError,
    KnowledgeGraphError,
    NodeNotFoundError,
    EdgeNotFoundError,
    OntologyError,
    ConceptNotFoundError,
    TaxonomyError,
    CategoryNotFoundError,
    StandardsError,
    StandardNotFoundError,
    EvidenceError,
    EvidenceNotFoundError,
)

__all__ = [
    # Version
    "__version__",
    # Graph
    "ConceptType",
    "RelationType",
    "ConceptNode",
    "EntityNode",
    "StandardNode",
    "DeviceNode",
    "RelationEdge",
    "Subgraph",
    "Path",
    "GraphStats",
    "IKnowledgeGraphRepository",
    "BiomedicalKnowledgeGraph",
    # Ontology
    "CodeSystem",
    "OntologyConceptType",
    "RelationshipType",
    "OntologyRelationship",
    "MedicalOntologyConcept",
    "ConceptHierarchy",
    "CodeMapping",
    "SearchResult",
    "IOntologyRepository",
    "MedicalOntology",
    # Taxonomy
    "RiskClass",
    "DeviceCategory",
    "FailureSeverity",
    "FailureFrequency",
    "MaintenanceType",
    "FailureMode",
    "MaintenanceLogic",
    "CategoryHierarchy",
    "FailureModeAnalysis",
    "MaintenanceSchedule",
    "ITaxonomyRepository",
    "EquipmentTaxonomy",
    # Standards
    "StandardOrganization",
    "StandardCategory",
    "VerificationMethod",
    "ComplianceStatus",
    "RiskClassification",
    "Standard",
    "StandardRequirement",
    "ComplianceCheck",
    "ComplianceReport",
    "StandardComparison",
    "IStandardsRepository",
    "StandardsRepository",
    # Evidence
    "EvidenceSourceType",
    "EvidenceLevel",
    "QueryType",
    "Evidence",
    "EvidenceQuery",
    "EvidenceFilters",
    "EvidenceRetrieval",
    "EvidenceWithRelevance",
    "EvidenceChain",
    "EvidenceStore",
    # Vocabulary
    "VocabularyType",
    "BiomedicalConcept",
    "TermMapping",
    "MedicalVocabulary",
    # Exceptions
    "KnowledgeError",
    "KnowledgeGraphError",
    "NodeNotFoundError",
    "EdgeNotFoundError",
    "OntologyError",
    "ConceptNotFoundError",
    "TaxonomyError",
    "CategoryNotFoundError",
    "StandardsError",
    "StandardNotFoundError",
    "EvidenceError",
    "EvidenceNotFoundError",
]
