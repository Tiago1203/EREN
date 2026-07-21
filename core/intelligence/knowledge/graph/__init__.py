"""
Knowledge Graph Module

Provides the Biomedical Knowledge Graph for storing and navigating
biomedical knowledge with nodes and relationships.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class RelationType(Enum):
    """Types of relationships in the graph."""
    # Hierarchical
    IS_A = "is_a"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    
    # Causal
    CAUSES = "causes"
    PREVENTS = "prevents"
    TREATS = "treats"
    DIAGNOSES = "diagnoses"
    
    # Semantic
    ASSOCIATED_WITH = "associated_with"
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"
    
    # Temporal
    OCCURS_BEFORE = "occurs_before"
    OVERLAPS = "overlaps"
    
    # Equipment
    USES_DEVICE = "uses_device"
    HAS_FAILURE_MODE = "has_failure_mode"
    REQUIRES_MAINTENANCE = "requires_maintenance"


@dataclass(frozen=True)
class ConceptNode:
    """Node representing a concept in the knowledge graph."""
    node_id: str
    concept_type: str
    name: str
    description: str
    code_system: str | None = None
    code: str | None = None
    properties: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class EntityNode:
    """Node representing a specific entity."""
    entity_id: str
    entity_type: str
    name: str
    properties: dict = field(default_factory=dict)
    linked_concepts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RelationEdge:
    """Edge representing a relationship between nodes."""
    edge_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    evidence: list[str] = field(default_factory=list)
    bidirectional: bool = False


class BiomedicalKnowledgeGraph:
    """
    Biomedical Knowledge Graph for storing and navigating
    biomedical knowledge.
    """
    
    def __init__(self):
        self._nodes: dict[str, ConceptNode | EntityNode] = {}
        self._edges: dict[str, list[RelationEdge]] = {}
        self._index: dict[str, list[str]] = {}
    
    async def add_node(
        self,
        node: ConceptNode | EntityNode,
    ) -> None:
        """Add a node to the graph."""
        node_id = node.node_id if isinstance(node, ConceptNode) else node.entity_id
        self._nodes[node_id] = node
        
        # Index by type
        node_type = node.concept_type if isinstance(node, ConceptNode) else node.entity_type
        if node_type not in self._index:
            self._index[node_type] = []
        self._index[node_type].append(node_id)
    
    async def add_edge(
        self,
        edge: RelationEdge,
    ) -> None:
        """Add an edge to the graph."""
        if edge.source_id not in self._edges:
            self._edges[edge.source_id] = []
        self._edges[edge.source_id].append(edge)
        
        if edge.bidirectional:
            reverse_edge = RelationEdge(
                edge_id=f"{edge.edge_id}_rev",
                source_id=edge.target_id,
                target_id=edge.source_id,
                relation_type=edge.relation_type,
                weight=edge.weight,
                evidence=edge.evidence,
                bidirectional=False,
            )
            if edge.target_id not in self._edges:
                self._edges[edge.target_id] = []
            self._edges[edge.target_id].append(reverse_edge)
    
    async def get_node(
        self,
        node_id: str,
    ) -> ConceptNode | EntityNode | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    async def get_neighbors(
        self,
        node_id: str,
        relation_type: RelationType | None = None,
    ) -> list[tuple[ConceptNode | EntityNode, RelationEdge]]:
        """Get neighboring nodes with their relationships."""
        results = []
        edges = self._edges.get(node_id, [])
        
        for edge in edges:
            if relation_type is None or edge.relation_type == relation_type:
                target = self._nodes.get(edge.target_id)
                if target:
                    results.append((target, edge))
        
        return results
    
    async def find_path(
        self,
        source_id: str,
        target_id: str,
    ) -> list[RelationEdge] | None:
        """Find shortest path between two nodes."""
        if source_id == target_id:
            return []
        
        from collections import deque
        
        visited = {source_id}
        queue = deque([(source_id, [])])
        
        while queue:
            current, path = queue.popleft()
            
            for edge in self._edges.get(current, []):
                if edge.target_id == target_id:
                    return path + [edge]
                
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge]))
        
        return None
    
    async def search_by_type(
        self,
        node_type: str,
    ) -> list[ConceptNode | EntityNode]:
        """Search nodes by type."""
        node_ids = self._index.get(node_type, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    async def subgraph(
        self,
        center_id: str,
        depth: int = 2,
    ) -> "Subgraph":
        """Extract subgraph centered on a node."""
        visited = {center_id}
        nodes = {center_id: self._nodes.get(center_id)}
        edges = []
        
        current_level = {center_id}
        for _ in range(depth):
            next_level = set()
            for node_id in current_level:
                for edge in self._edges.get(node_id, []):
                    edges.append(edge)
                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        next_level.add(edge.target_id)
                        nodes[edge.target_id] = self._nodes.get(edge.target_id)
                    if edge.source_id not in visited and edge.bidirectional:
                        visited.add(edge.source_id)
                        next_level.add(edge.source_id)
                        nodes[edge.source_id] = self._nodes.get(edge.source_id)
            current_level = next_level
        
        return Subgraph(
            nodes=[n for n in nodes.values() if n is not None],
            edges=edges,
        )


@dataclass
class Subgraph:
    """Subgraph extracted from the main graph."""
    nodes: list[ConceptNode | EntityNode]
    edges: list[RelationEdge]


__all__ = [
    "RelationType",
    "ConceptNode",
    "EntityNode",
    "RelationEdge",
    "BiomedicalKnowledgeGraph",
    "Subgraph",
]
