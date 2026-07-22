"""Biomedical Knowledge Graph for EREN OS.

PR-060: Biomedical Knowledge Graph

Provides knowledge representation for medical equipment, hospitals,
manufacturers, and their relationships.
"""

from __future__ import annotations

from core.PHASE_1.infrastructure.biomedical.knowledge_graph.engine import (
    BiomedicalKnowledgeGraph,
    get_knowledge_graph,
    reset_knowledge_graph,
)
from core.PHASE_1.infrastructure.biomedical.knowledge_graph.types import (
    BiomedicalEntity,
    DeviceEntity,
    EntityType,
    GraphQuery,
    GraphQueryResult,
    GraphStatistics,
    GraphVersion,
    HospitalEntity,
    InferenceResult,
    InferenceRule,
    ManufacturerEntity,
    OntologyClass,
    Relationship,
    RelationshipType,
    SensorEntity,
)

__all__ = [
    # Engine
    "BiomedicalKnowledgeGraph",
    "get_knowledge_graph",
    "reset_knowledge_graph",
    # Types
    "EntityType",
    "RelationshipType",
    "BiomedicalEntity",
    "DeviceEntity",
    "SensorEntity",
    "ManufacturerEntity",
    "HospitalEntity",
    "Relationship",
    "GraphQuery",
    "GraphQueryResult",
    "GraphStatistics",
    "GraphVersion",
    "OntologyClass",
    "InferenceRule",
    "InferenceResult",
]
