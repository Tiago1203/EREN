"""
Biomedical Knowledge Graph Module

Complete implementation of the knowledge graph for storing and navigating
biomedical knowledge with nodes, edges, and traversal algorithms.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Protocol, AsyncIterator
from collections import defaultdict
import heapq


class ConceptType(Enum):
    """Types of concepts in the knowledge graph."""
    # Medical concepts
    DISORDER = "disorder"
    PROCEDURE = "procedure"
    FINDING = "finding"
    OBSERVABLE = "observable"
    SUBSTANCE = "substance"
    ORGANISM = "organism"
    BODY_STRUCTURE = "body_structure"
    
    # Equipment concepts
    DEVICE = "device"
    DEVICE_COMPONENT = "device_component"
    ACCESSORY = "accessory"
    MATERIAL = "material"
    
    # Standard concepts
    STANDARD = "standard"
    REGULATION = "regulation"
    GUIDELINE = "guideline"
    
    # Clinical concepts
    PROTOCOL = "protocol"
    WORKFLOW = "workflow"
    ALERT = "alert"
    
    # Knowledge concepts
    ARTICLE = "article"
    REFERENCE = "reference"
    EVIDENCE = "evidence"


class RelationType(Enum):
    """Types of relationships in the graph."""
    # Hierarchical
    IS_A = "is_a"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    HAS_COMPONENT = "has_component"
    
    # Causal
    CAUSES = "causes"
    PREVENTS = "prevents"
    TREATS = "treats"
    DIAGNOSES = "diagnoses"
    COMPLICATES = "complicates"
    
    # Semantic
    ASSOCIATED_WITH = "associated_with"
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"
    MANIFESTS_AS = "manifests_as"
    
    # Equipment-specific
    USES_DEVICE = "uses_device"
    HAS_FAILURE_MODE = "has_failure_mode"
    REQUIRES_MAINTENANCE = "requires_maintenance"
    HAS_ACCESSORY = "has_accessory"
    REPLACES = "replaces"
    
    # Standard-related
    COMPLIES_WITH = "complies_with"
    REFERENCES = "references"
    SUPERSEDES = "supersedes"
    
    # Clinical
    APPLIES_TO = "applies_to"
    INDICATED_FOR = "indicated_for"
    CONTRAINDICATED_IN = "contraindicated_in"
    
    # Temporal
    OCCURS_BEFORE = "occurs_before"
    OVERLAPS = "overlaps"
    FOLLOWS = "follows"


@dataclass(frozen=True)
class ConceptNode:
    """
    Node representing a concept in the knowledge graph.
    
    Immutable dataclass for thread-safety.
    """
    node_id: str
    concept_type: ConceptType
    name: str
    description: str
    code_system: Optional[str] = None
    code: Optional[str] = None
    synonyms: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.concept_type, str):
            object.__setattr__(self, 'concept_type', ConceptType(self.concept_type))


@dataclass(frozen=True)
class EntityNode:
    """
    Node representing a specific entity (device instance, hospital, etc).
    """
    entity_id: str
    entity_type: str
    name: str
    properties: dict = field(default_factory=dict)
    linked_concepts: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    active: bool = True


@dataclass(frozen=True)
class StandardNode:
    """
    Node representing a standard or regulation.
    """
    standard_id: str
    code: str
    title: str
    version: str
    organization: str
    scope: str
    publication_date: Optional[str] = None
    url: Optional[str] = None
    requirements: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DeviceNode:
    """
    Node representing a medical device.
    """
    device_id: str
    manufacturer: str
    model: str
    serial_number: Optional[str] = None
    category: str
    risk_class: str
    installed_date: Optional[str] = None
    location: Optional[str] = None
    status: str = "active"
    linked_standards: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RelationEdge:
    """
    Edge representing a relationship between nodes.
    """
    edge_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    evidence: list[str] = field(default_factory=list)
    bidirectional: bool = False
    properties: dict = field(default_factory=dict)
    confidence: float = 1.0
    
    def __post_init__(self):
        if isinstance(self.relation_type, str):
            object.__setattr__(self, 'relation_type', RelationType(self.relation_type))


@dataclass
class Subgraph:
    """Subgraph extracted from the main graph."""
    nodes: list[ConceptNode | EntityNode | StandardNode | DeviceNode]
    edges: list[RelationEdge]
    center_id: str
    depth: int


@dataclass
class Path:
    """Path between nodes."""
    nodes: list[str]
    edges: list[RelationEdge]
    total_weight: float
    
    def __len__(self) -> int:
        return len(self.nodes)


@dataclass
class GraphStats:
    """Statistics about the knowledge graph."""
    total_nodes: int
    concept_nodes: int
    entity_nodes: int
    standard_nodes: int
    device_nodes: int
    total_edges: int
    relation_types: dict[str, int]
    avg_connections_per_node: float


class IKnowledgeGraphRepository(Protocol):
    """Repository interface for knowledge graph persistence."""
    
    async def save_node(self, node: ConceptNode | EntityNode) -> None: ...
    async def save_edge(self, edge: RelationEdge) -> None: ...
    async def get_node(self, node_id: str) -> ConceptNode | EntityNode | None: ...
    async def get_edges_from(self, node_id: str) -> list[RelationEdge]: ...
    async def get_edges_to(self, node_id: str) -> list[RelationEdge]: ...
    async def search_nodes(self, query: str, limit: int = 10) -> list[ConceptNode]: ...


class BiomedicalKnowledgeGraph:
    """
    Biomedical Knowledge Graph for storing and navigating biomedical knowledge.
    
    Supports:
    - Adding/removing nodes and edges
    - Path finding (BFS, Dijkstra)
    - Subgraph extraction
    - Neighborhood queries
    - Graph statistics
    """
    
    def __init__(
        self,
        repository: Optional[IKnowledgeGraphRepository] = None,
    ):
        self._repository = repository
        self._nodes: dict[str, ConceptNode | EntityNode | StandardNode | DeviceNode] = {}
        self._edges_from: dict[str, list[RelationEdge]] = defaultdict(list)
        self._edges_to: dict[str, list[RelationEdge]] = defaultdict(list)
        self._type_index: dict[ConceptType, list[str]] = defaultdict(list)
        self._code_index: dict[tuple[str, str], str] = {}
        self._name_index: dict[str, list[str]] = defaultdict(list)
    
    @property
    def stats(self) -> GraphStats:
        """Get statistics about the graph."""
        concept_nodes = sum(
            1 for n in self._nodes.values() if isinstance(n, ConceptNode)
        )
        entity_nodes = sum(
            1 for n in self._nodes.values() if isinstance(n, EntityNode)
        )
        standard_nodes = sum(
            1 for n in self._nodes.values() if isinstance(n, StandardNode)
        )
        device_nodes = sum(
            1 for n in self._nodes.values() if isinstance(n, DeviceNode)
        )
        
        relation_counts: dict[str, int] = defaultdict(int)
        for edges in self._edges_from.values():
            for edge in edges:
                relation_counts[edge.relation_type.value] += 1
        
        total_edges = sum(len(e) for e in self._edges_from.values())
        avg_connections = (
            total_edges * 2 / len(self._nodes) if self._nodes else 0
        )
        
        return GraphStats(
            total_nodes=len(self._nodes),
            concept_nodes=concept_nodes,
            entity_nodes=entity_nodes,
            standard_nodes=standard_nodes,
            device_nodes=device_nodes,
            total_edges=total_edges,
            relation_types=dict(relation_counts),
            avg_connections_per_node=avg_connections,
        )
    
    async def add_node(
        self,
        node: ConceptNode | EntityNode | StandardNode | DeviceNode,
    ) -> None:
        """Add a node to the graph."""
        node_id = self._get_node_id(node)
        self._nodes[node_id] = node
        
        if isinstance(node, ConceptNode):
            self._type_index[node.concept_type].append(node_id)
            if node.code_system and node.code:
                self._code_index[(node.code_system, node.code)] = node_id
            self._name_index[node.name.lower()].append(node_id)
            for syn in node.synonyms:
                self._name_index[syn.lower()].append(node_id)
        
        if self._repository:
            await self._repository.save_node(node)
    
    async def add_edge(self, edge: RelationEdge) -> None:
        """Add an edge to the graph."""
        self._edges_from[edge.source_id].append(edge)
        
        reverse_edge = RelationEdge(
            edge_id=f"{edge.edge_id}_reverse",
            source_id=edge.target_id,
            target_id=edge.source_id,
            relation_type=self._get_reverse_relation(edge.relation_type),
            weight=edge.weight,
            evidence=edge.evidence,
            bidirectional=False,
            properties=edge.properties,
            confidence=edge.confidence,
        )
        self._edges_to[edge.target_id].append(reverse_edge)
        
        if self._repository:
            await self._repository.save_edge(edge)
    
    async def get_node(
        self,
        node_id: str,
    ) -> ConceptNode | EntityNode | StandardNode | DeviceNode | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    async def get_neighbors(
        self,
        node_id: str,
        relation_type: RelationType | None = None,
        direction: str = "outgoing",
    ) -> list[tuple[ConceptNode | EntityNode, RelationEdge]]:
        """Get neighboring nodes with their relationships."""
        results = []
        
        if direction in ("outgoing", "both"):
            for edge in self._edges_from.get(node_id, []):
                if relation_type is None or edge.relation_type == relation_type:
                    target = self._nodes.get(edge.target_id)
                    if target:
                        results.append((target, edge))
        
        if direction in ("incoming", "both"):
            for edge in self._edges_to.get(node_id, []):
                if relation_type is None or edge.relation_type == relation_type:
                    source = self._nodes.get(edge.source_id)
                    if source:
                        results.append((source, edge))
        
        return results
    
    async def find_shortest_path(
        self,
        source_id: str,
        target_id: str,
    ) -> Path | None:
        """Find shortest path between two nodes using BFS."""
        if source_id == target_id:
            return Path(nodes=[source_id], edges=[], total_weight=0.0)
        
        visited = {source_id}
        queue = [(source_id, [source_id], [], 0.0)]
        
        while queue:
            current, path, edges, weight = queue.pop(0)
            
            for edge in self._edges_from.get(current, []):
                if edge.target_id == target_id:
                    return Path(
                        nodes=path + [edge.target_id],
                        edges=edges + [edge],
                        total_weight=weight + edge.weight,
                    )
                
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((
                        edge.target_id,
                        path + [edge.target_id],
                        edges + [edge],
                        weight + edge.weight,
                    ))
        
        return None
    
    async def find_all_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
        max_paths: int = 10,
    ) -> list[Path]:
        """Find all paths between two nodes up to max_depth."""
        if source_id == target_id:
            return [Path(nodes=[source_id], edges=[], total_weight=0.0)]
        
        all_paths: list[Path] = []
        
        def dfs(
            current: str,
            target: str,
            path: list[str],
            edges: list[RelationEdge],
            weight: float,
            depth: int,
        ):
            if len(all_paths) >= max_paths:
                return
            
            if depth > max_depth:
                return
            
            for edge in self._edges_from.get(current, []):
                new_path = path + [edge.target_id]
                new_edges = edges + [edge]
                new_weight = weight + edge.weight
                
                if edge.target_id == target:
                    all_paths.append(Path(
                        nodes=new_path,
                        edges=new_edges,
                        total_weight=new_weight,
                    ))
                elif edge.target_id not in path:
                    dfs(
                        edge.target_id, target, new_path,
                        new_edges, new_weight, depth + 1,
                    )
        
        dfs(source_id, target_id, [source_id], [], 0.0, 0)
        
        all_paths.sort(key=lambda p: p.total_weight)
        return all_paths[:max_paths]
    
    async def find_dijkstra_path(
        self,
        source_id: str,
        target_id: str,
    ) -> Path | None:
        """Find shortest path using Dijkstra's algorithm."""
        if source_id == target_id:
            return Path(nodes=[source_id], edges=[], total_weight=0.0)
        
        distances: dict[str, float] = {source_id: 0.0}
        previous: dict[str, tuple[str, RelationEdge] | None] = {source_id: None}
        visited = set()
        
        pq = [(0.0, source_id)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == target_id:
                break
            
            for edge in self._edges_from.get(current, []):
                neighbor = edge.target_id
                distance = current_dist + edge.weight
                
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = (current, edge)
                    heapq.heappush(pq, (distance, neighbor))
        
        if target_id not in previous or previous[target_id] is None:
            return None
        
        nodes = []
        edges = []
        current = target_id
        
        while current is not None:
            nodes.insert(0, current)
            if previous[current] is not None:
                _, edge = previous[current]
                edges.insert(0, edge)
            current = previous[current][0] if previous[current] else None
        
        return Path(
            nodes=nodes,
            edges=edges,
            total_weight=distances.get(target_id, 0.0),
        )
    
    async def search_by_type(
        self,
        concept_type: ConceptType,
    ) -> list[ConceptNode]:
        """Search nodes by concept type."""
        node_ids = self._type_index.get(concept_type, [])
        return [
            self._nodes[nid] for nid in node_ids
            if nid in self._nodes and isinstance(self._nodes[nid], ConceptNode)
        ]
    
    async def search_by_code(
        self,
        code: str,
        code_system: str,
    ) -> ConceptNode | None:
        """Search node by code system and code."""
        node_id = self._code_index.get((code_system, code))
        if node_id:
            node = self._nodes.get(node_id)
            if isinstance(node, ConceptNode):
                return node
        return None
    
    async def search_by_name(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ConceptNode]:
        """Search nodes by name (exact and partial match)."""
        query_lower = query.lower()
        results: list[tuple[str, ConceptNode]] = []
        
        for node in self._nodes.values():
            if isinstance(node, ConceptNode):
                if query_lower == node.name.lower():
                    results.insert(0, (node.node_id, node))
                elif query_lower in node.name.lower():
                    results.append((node.node_id, node))
                else:
                    for syn in node.synonyms:
                        if query_lower in syn.lower():
                            results.append((node.node_id, node))
                            break
        
        results.sort(key=lambda x: x[0])
        return [node for _, node in results[:limit]]
    
    async def subgraph(
        self,
        center_id: str,
        depth: int = 2,
        relation_types: list[RelationType] | None = None,
    ) -> Subgraph:
        """Extract subgraph centered on a node."""
        visited = {center_id}
        nodes = {center_id: self._nodes.get(center_id)}
        edges = []
        
        current_level = {center_id}
        
        for _ in range(depth):
            next_level = set()
            
            for node_id in current_level:
                for edge in self._edges_from.get(node_id, []):
                    if relation_types and edge.relation_type not in relation_types:
                        continue
                    
                    edges.append(edge)
                    
                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        next_level.add(edge.target_id)
                        nodes[edge.target_id] = self._nodes.get(edge.target_id)
                    
                    if edge.bidirectional and edge.source_id not in visited:
                        visited.add(edge.source_id)
                        next_level.add(edge.source_id)
                        nodes[edge.source_id] = self._nodes.get(edge.source_id)
            
            current_level = next_level
        
        valid_nodes = [n for n in nodes.values() if n is not None]
        
        return Subgraph(
            nodes=valid_nodes,
            edges=edges,
            center_id=center_id,
            depth=depth,
        )
    
    async def get_concept_hierarchy(
        self,
        concept_id: str,
        max_depth: int = 10,
    ) -> dict[str, list[ConceptNode]]:
        """Get complete hierarchy for a concept (ancestors and descendants)."""
        ancestors: dict[str, list[ConceptNode]] = {"direct": [], "all": []}
        descendants: dict[str, list[ConceptNode]] = {"direct": [], "all": []}
        
        visited_ancestors = set()
        visited_descendants = set()
        
        current_ancestors = {concept_id}
        current_descendants = {concept_id}
        
        for _ in range(max_depth):
            next_ancestors = set()
            next_descendants = set()
            
            for node_id in current_ancestors:
                if node_id in visited_ancestors:
                    continue
                visited_ancestors.add(node_id)
                
                for edge in self._edges_to.get(node_id, []):
                    if edge.relation_type in (RelationType.IS_A, RelationType.PART_OF):
                        target = self._nodes.get(edge.target_id)
                        if target and isinstance(target, ConceptNode):
                            next_ancestors.add(edge.target_id)
                            ancestors["all"].append(target)
            
            for node_id in current_descendants:
                if node_id in visited_descendants:
                    continue
                visited_descendants.add(node_id)
                
                for edge in self._edges_from.get(node_id, []):
                    if edge.relation_type in (RelationType.IS_A, RelationType.PART_OF):
                        target = self._nodes.get(edge.target_id)
                        if target and isinstance(target, ConceptNode):
                            next_descendants.add(edge.target_id)
                            descendants["all"].append(target)
            
            if not next_ancestors:
                break
            if not next_descendants:
                break
            
            current_ancestors = next_ancestors
            current_descendants = next_descendants
        
        center_node = self._nodes.get(concept_id)
        if center_node and isinstance(center_node, ConceptNode):
            ancestors["direct"] = [
                self._nodes[nid] for nid in current_ancestors
                if nid != concept_id and isinstance(self._nodes.get(nid), ConceptNode)
            ]
            descendants["direct"] = [
                self._nodes[nid] for nid in current_descendants
                if nid != concept_id and isinstance(self._nodes.get(nid), ConceptNode)
            ]
        
        return {"ancestors": ancestors, "descendants": descendants}
    
    async def get_related_concepts(
        self,
        concept_id: str,
        relation_types: list[RelationType] | None = None,
        limit: int = 20,
    ) -> list[tuple[ConceptNode, RelationEdge]]:
        """Get all related concepts for a given concept."""
        results: list[tuple[ConceptNode, RelationEdge]] = []
        
        for edge in self._edges_from.get(concept_id, []):
            if relation_types and edge.relation_type not in relation_types:
                continue
            target = self._nodes.get(edge.target_id)
            if target and isinstance(target, ConceptNode):
                results.append((target, edge))
        
        for edge in self._edges_to.get(concept_id, []):
            if relation_types and edge.relation_type not in relation_types:
                continue
            source = self._nodes.get(edge.source_id)
            if source and isinstance(source, ConceptNode):
                results.append((source, edge))
        
        results.sort(key=lambda x: x[1].weight * x[1].confidence, reverse=True)
        return results[:limit]
    
    async def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its edges."""
        if node_id not in self._nodes:
            return False
        
        for edge in self._edges_from.get(node_id, []):
            self._edges_to[edge.target_id] = [
                e for e in self._edges_to.get(edge.target_id, [])
                if e.source_id != node_id
            ]
        
        for edge in self._edges_to.get(node_id, []):
            self._edges_from[edge.source_id] = [
                e for e in self._edges_from.get(edge.source_id, [])
                if e.target_id != node_id
            ]
        
        del self._nodes[node_id]
        self._edges_from.pop(node_id, None)
        self._edges_to.pop(node_id, None)
        
        return True
    
    async def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge by ID."""
        for source, edges in list(self._edges_from.items()):
            for i, edge in enumerate(edges):
                if edge.edge_id == edge_id:
                    self._edges_from[source].pop(i)
                    self._edges_to[edge.target_id] = [
                        e for e in self._edges_to.get(edge.target_id, [])
                        if e.edge_id != edge_id and e.edge_id != f"{edge_id}_reverse"
                    ]
                    return True
        return False
    
    def _get_node_id(self, node: ConceptNode | EntityNode | StandardNode | DeviceNode) -> str:
        """Extract node ID from various node types."""
        if isinstance(node, ConceptNode):
            return node.node_id
        elif isinstance(node, EntityNode):
            return node.entity_id
        elif isinstance(node, StandardNode):
            return node.standard_id
        elif isinstance(node, DeviceNode):
            return node.device_id
        return str(node)
    
    def _get_reverse_relation(self, relation: RelationType) -> RelationType:
        """Get the reverse relation type."""
        reverse_map = {
            RelationType.CAUSES: RelationType.CAUSES,
            RelationType.PREVENTS: RelationType.PREVENTS,
            RelationType.TREATS: RelationType.TREATS,
            RelationType.DIAGNOSES: RelationType.DIAGNOSES,
            RelationType.USES_DEVICE: RelationType.USES_DEVICE,
            RelationType.HAS_FAILURE_MODE: RelationType.HAS_FAILURE_MODE,
            RelationType.COMPLIES_WITH: RelationType.COMPLIES_WITH,
            RelationType.REFERENCES: RelationType.REFERENCES,
        }
        return reverse_map.get(relation, relation)


__all__ = [
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
]
