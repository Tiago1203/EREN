"""
Knowledge Module Exceptions

Exception hierarchy for the Biomedical Knowledge Engine.
"""

from typing import Optional


class KnowledgeError(Exception):
    """Base exception for knowledge module."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "KNOWLEDGE_ERROR"
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# Knowledge Graph Exceptions
class KnowledgeGraphError(KnowledgeError):
    """Base exception for knowledge graph operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="GRAPH_ERROR", **kwargs)


class NodeNotFoundError(KnowledgeGraphError):
    """Node not found in knowledge graph."""
    
    def __init__(self, node_id: str):
        super().__init__(
            message=f"Node not found: {node_id}",
            error_code="NODE_NOT_FOUND",
            details={"node_id": node_id},
        )
        self.node_id = node_id


class EdgeNotFoundError(KnowledgeGraphError):
    """Edge not found in knowledge graph."""
    
    def __init__(self, edge_id: str):
        super().__init__(
            message=f"Edge not found: {edge_id}",
            error_code="EDGE_NOT_FOUND",
            details={"edge_id": edge_id},
        )
        self.edge_id = edge_id


class DuplicateNodeError(KnowledgeGraphError):
    """Node already exists in knowledge graph."""
    
    def __init__(self, node_id: str):
        super().__init__(
            message=f"Duplicate node: {node_id}",
            error_code="DUPLICATE_NODE",
            details={"node_id": node_id},
        )
        self.node_id = node_id


class DuplicateEdgeError(KnowledgeGraphError):
    """Edge already exists in knowledge graph."""
    
    def __init__(self, edge_id: str):
        super().__init__(
            message=f"Duplicate edge: {edge_id}",
            error_code="DUPLICATE_EDGE",
            details={"edge_id": edge_id},
        )
        self.edge_id = edge_id


class PathNotFoundError(KnowledgeGraphError):
    """Path not found between nodes."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
    ):
        super().__init__(
            message=f"No path found from {source_id} to {target_id}",
            error_code="PATH_NOT_FOUND",
            details={"source_id": source_id, "target_id": target_id},
        )
        self.source_id = source_id
        self.target_id = target_id


class InvalidNodeTypeError(KnowledgeGraphError):
    """Invalid node type."""
    
    def __init__(self, node_type: str):
        super().__init__(
            message=f"Invalid node type: {node_type}",
            error_code="INVALID_NODE_TYPE",
            details={"node_type": node_type},
        )
        self.node_type = node_type


class InvalidRelationTypeError(KnowledgeGraphError):
    """Invalid relation type."""
    
    def __init__(self, relation_type: str):
        super().__init__(
            message=f"Invalid relation type: {relation_type}",
            error_code="INVALID_RELATION_TYPE",
            details={"relation_type": relation_type},
        )
        self.relation_type = relation_type


# Ontology Exceptions
class OntologyError(KnowledgeError):
    """Base exception for ontology operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="ONTOLOGY_ERROR", **kwargs)


class ConceptNotFoundError(OntologyError):
    """Concept not found in ontology."""
    
    def __init__(
        self,
        concept_id: str,
        code_system: str,
    ):
        super().__init__(
            message=f"Concept not found: {concept_id} in {code_system}",
            error_code="CONCEPT_NOT_FOUND",
            details={"concept_id": concept_id, "code_system": code_system},
        )
        self.concept_id = concept_id
        self.code_system = code_system


class CodeSystemNotSupportedError(OntologyError):
    """Code system not supported."""
    
    def __init__(self, code_system: str):
        super().__init__(
            message=f"Code system not supported: {code_system}",
            error_code="CODE_SYSTEM_NOT_SUPPORTED",
            details={"code_system": code_system},
        )
        self.code_system = code_system


class CodeMappingError(OntologyError):
    """Error mapping codes between systems."""
    
    def __init__(
        self,
        source_code: str,
        source_system: str,
        target_system: str,
        reason: str,
    ):
        super().__init__(
            message=f"Cannot map {source_code} from {source_system} to {target_system}: {reason}",
            error_code="CODE_MAPPING_ERROR",
            details={
                "source_code": source_code,
                "source_system": source_system,
                "target_system": target_system,
                "reason": reason,
            },
        )


class HierarchyError(OntologyError):
    """Error in concept hierarchy."""
    
    def __init__(self, concept_id: str, reason: str):
        super().__init__(
            message=f"Hierarchy error for {concept_id}: {reason}",
            error_code="HIERARCHY_ERROR",
            details={"concept_id": concept_id, "reason": reason},
        )


# Taxonomy Exceptions
class TaxonomyError(KnowledgeError):
    """Base exception for taxonomy operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="TAXONOMY_ERROR", **kwargs)


class CategoryNotFoundError(TaxonomyError):
    """Category not found in taxonomy."""
    
    def __init__(self, category_id: str):
        super().__init__(
            message=f"Category not found: {category_id}",
            error_code="CATEGORY_NOT_FOUND",
            details={"category_id": category_id},
        )
        self.category_id = category_id


class FailureModeNotFoundError(TaxonomyError):
    """Failure mode not found."""
    
    def __init__(self, failure_mode_id: str):
        super().__init__(
            message=f"Failure mode not found: {failure_mode_id}",
            error_code="FAILURE_MODE_NOT_FOUND",
            details={"failure_mode_id": failure_mode_id},
        )
        self.failure_mode_id = failure_mode_id


class MaintenanceLogicNotFoundError(TaxonomyError):
    """Maintenance logic not found."""
    
    def __init__(self, logic_id: str):
        super().__init__(
            message=f"Maintenance logic not found: {logic_id}",
            error_code="MAINTENANCE_LOGIC_NOT_FOUND",
            details={"logic_id": logic_id},
        )
        self.logic_id = logic_id


class InvalidRiskClassError(TaxonomyError):
    """Invalid risk class."""
    
    def __init__(self, risk_class: str):
        super().__init__(
            message=f"Invalid risk class: {risk_class}",
            error_code="INVALID_RISK_CLASS",
            details={"risk_class": risk_class},
        )


# Standards Exceptions
class StandardsError(KnowledgeError):
    """Base exception for standards operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="STANDARDS_ERROR", **kwargs)


class StandardNotFoundError(StandardsError):
    """Standard not found."""
    
    def __init__(self, standard_id: str):
        super().__init__(
            message=f"Standard not found: {standard_id}",
            error_code="STANDARD_NOT_FOUND",
            details={"standard_id": standard_id},
        )
        self.standard_id = standard_id


class RequirementNotFoundError(StandardsError):
    """Requirement not found."""
    
    def __init__(self, requirement_id: str):
        super().__init__(
            message=f"Requirement not found: {requirement_id}",
            error_code="REQUIREMENT_NOT_FOUND",
            details={"requirement_id": requirement_id},
        )
        self.requirement_id = requirement_id


class ComplianceError(StandardsError):
    """Error in compliance checking."""
    
    def __init__(
        self,
        device_id: str,
        standard_id: str,
        reason: str,
    ):
        super().__init__(
            message=f"Compliance error for device {device_id} on {standard_id}: {reason}",
            error_code="COMPLIANCE_ERROR",
            details={
                "device_id": device_id,
                "standard_id": standard_id,
                "reason": reason,
            },
        )


class StandardVersionError(StandardsError):
    """Standard version error."""
    
    def __init__(self, standard_id: str, version: str):
        super().__init__(
            message=f"Invalid version {version} for standard {standard_id}",
            error_code="STANDARD_VERSION_ERROR",
            details={"standard_id": standard_id, "version": version},
        )


# Evidence Store Exceptions
class EvidenceError(KnowledgeError):
    """Base exception for evidence operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="EVIDENCE_ERROR", **kwargs)


class EvidenceNotFoundError(EvidenceError):
    """Evidence not found."""
    
    def __init__(self, evidence_id: str):
        super().__init__(
            message=f"Evidence not found: {evidence_id}",
            error_code="EVIDENCE_NOT_FOUND",
            details={"evidence_id": evidence_id},
        )
        self.evidence_id = evidence_id


class EvidenceExpiredError(EvidenceError):
    """Evidence has expired."""
    
    def __init__(self, evidence_id: str, expiry_date: str):
        super().__init__(
            message=f"Evidence {evidence_id} expired on {expiry_date}",
            error_code="EVIDENCE_EXPIRED",
            details={"evidence_id": evidence_id, "expiry_date": expiry_date},
        )


class EvidenceRetrievalError(EvidenceError):
    """Error retrieving evidence."""
    
    def __init__(
        self,
        query: str,
        reason: str,
    ):
        super().__init__(
            message=f"Failed to retrieve evidence for query '{query}': {reason}",
            error_code="EVIDENCE_RETRIEVAL_ERROR",
            details={"query": query, "reason": reason},
        )


class EvidenceSourceError(EvidenceError):
    """Error with evidence source."""
    
    def __init__(
        self,
        source: str,
        reason: str,
    ):
        super().__init__(
            message=f"Error with evidence source {source}: {reason}",
            error_code="EVIDENCE_SOURCE_ERROR",
            details={"source": source, "reason": reason},
        )


# Vocabulary Exceptions
class VocabularyError(KnowledgeError):
    """Base exception for vocabulary operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="VOCABULARY_ERROR", **kwargs)


class TermNotFoundError(VocabularyError):
    """Term not found in vocabulary."""
    
    def __init__(self, term: str):
        super().__init__(
            message=f"Term not found: {term}",
            error_code="TERM_NOT_FOUND",
            details={"term": term},
        )
        self.term = term


class TermMappingError(VocabularyError):
    """Error in term mapping."""
    
    def __init__(
        self,
        source_term: str,
        target_system: str,
        reason: str,
    ):
        super().__init__(
            message=f"Cannot map term '{source_term}' to {target_system}: {reason}",
            error_code="TERM_MAPPING_ERROR",
            details={
                "source_term": source_term,
                "target_system": target_system,
                "reason": reason,
            },
        )


# Validation Exceptions
class ValidationError(KnowledgeError):
    """Validation error in knowledge module."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)


class InvalidConceptError(ValidationError):
    """Invalid concept structure."""
    
    def __init__(self, concept_id: str, reason: str):
        super().__init__(
            message=f"Invalid concept {concept_id}: {reason}",
            error_code="INVALID_CONCEPT",
            details={"concept_id": concept_id, "reason": reason},
        )


class InvalidStandardError(ValidationError):
    """Invalid standard structure."""
    
    def __init__(self, standard_id: str, reason: str):
        super().__init__(
            message=f"Invalid standard {standard_id}: {reason}",
            error_code="INVALID_STANDARD",
            details={"standard_id": standard_id, "reason": reason},
        )


__all__ = [
    # Base
    "KnowledgeError",
    # Graph
    "KnowledgeGraphError",
    "NodeNotFoundError",
    "EdgeNotFoundError",
    "DuplicateNodeError",
    "DuplicateEdgeError",
    "PathNotFoundError",
    "InvalidNodeTypeError",
    "InvalidRelationTypeError",
    # Ontology
    "OntologyError",
    "ConceptNotFoundError",
    "CodeSystemNotSupportedError",
    "CodeMappingError",
    "HierarchyError",
    # Taxonomy
    "TaxonomyError",
    "CategoryNotFoundError",
    "FailureModeNotFoundError",
    "MaintenanceLogicNotFoundError",
    "InvalidRiskClassError",
    # Standards
    "StandardsError",
    "StandardNotFoundError",
    "RequirementNotFoundError",
    "ComplianceError",
    "StandardVersionError",
    # Evidence
    "EvidenceError",
    "EvidenceNotFoundError",
    "EvidenceExpiredError",
    "EvidenceRetrievalError",
    "EvidenceSourceError",
    # Vocabulary
    "VocabularyError",
    "TermNotFoundError",
    "TermMappingError",
    # Validation
    "ValidationError",
    "InvalidConceptError",
    "InvalidStandardError",
]
