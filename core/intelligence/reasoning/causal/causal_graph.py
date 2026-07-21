"""
Causal Graph Module

Complete implementation for representing and analyzing
causal relationships between events and conditions.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import defaultdict, deque


class CausalType(Enum):
    """Types of causal relationships."""
    DIRECT = "direct"              # A directly causes B
    CONTRIBUTING = "contributing"  # A contributes to B (needs other factors)
    ENABLING = "enabling"        # A enables B (B won't happen without A)
    PREVENTING = "preventing"     # A prevents B
    MITIGATING = "mitigating"     # A mitigates B
    TRIGGERING = "triggering"     # A triggers B


class CausalNodeType(Enum):
    """Types of nodes in causal graph."""
    EVENT = "event"              # Observed event
    FACTOR = "factor"            # Contributing factor
    CONDITION = "condition"       # Background condition
    MECHANISM = "mechanism"      # Mechanism
    OUTCOME = "outcome"          # Outcome


class TemporalRelation(Enum):
    """Temporal relationships."""
    OCCURS_BEFORE = "occurs_before"
    OCCURS_AFTER = "occurs_after"
    SIMULTANEOUS = "simultaneous"
    OVERLAPPING = "overlapping"


@dataclass(frozen=True)
class CausalNode:
    """Node in causal graph."""
    node_id: str
    node_type: CausalNodeType
    description: str
    probability: float = 1.0
    evidence: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.node_type, str):
            object.__setattr__(self, 'node_type', CausalNodeType(self.node_type))


@dataclass(frozen=True)
class CausalEdge:
    """Causal relationship edge."""
    edge_id: str
    source_id: str
    target_id: str
    causal_type: CausalType
    strength: float  # 0.0 - 1.0
    temporal_relation: Optional[TemporalRelation] = None
    conditions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 1.0

    def __post_init__(self):
        if isinstance(self.causal_type, str):
            object.__setattr__(self, 'causal_type', CausalType(self.causal_type))
        if isinstance(self.temporal_relation, str):
            object.__setattr__(self, 'temporal_relation', TemporalRelation(self.temporal_relation))


@dataclass
class CausalPath:
    """Path in causal graph."""
    path_id: str
    nodes: list[CausalNode]
    edges: list[CausalEdge]
    total_strength: float
    probability: float


@dataclass
class CausalAnalysis:
    """Complete causal analysis result."""
    analysis_id: str
    start_node: CausalNode
    effects: list[CausalNode]
    causes: list[CausalNode]
    causal_paths: list[CausalPath]
    confidence_scores: dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)


class CausalGraph:
    """
    Graph for representing and analyzing causal relationships.
    """
    
    def __init__(self):
        self._nodes: dict[str, CausalNode] = {}
        self._edges: dict[str, list[CausalEdge]] = defaultdict(list)
        self._reverse_edges: dict[str, list[CausalEdge]] = defaultdict(list)
    
    async def add_node(self, node: CausalNode) -> None:
        """Add a node to the graph."""
        self._nodes[node.node_id] = node
    
    async def add_edge(self, edge: CausalEdge) -> None:
        """Add a causal edge."""
        self._edges[edge.source_id].append(edge)
        self._reverse_edges[edge.target_id].append(edge)
    
    async def add_causal_relation(
        self,
        source: CausalNode,
        target: CausalNode,
        causal_type: CausalType,
        strength: float,
        temporal_relation: TemporalRelation | None = None,
    ) -> CausalEdge:
        """Add a causal relationship between nodes."""
        # Ensure nodes exist
        await self.add_node(source)
        await self.add_node(target)
        
        edge = CausalEdge(
            edge_id=f"ce_{len(self._edges)}",
            source_id=source.node_id,
            target_id=target.node_id,
            causal_type=causal_type,
            strength=strength,
            temporal_relation=temporal_relation,
        )
        
        await self.add_edge(edge)
        return edge
    
    async def infer_effects(
        self,
        cause_node_id: str,
        max_depth: int = 10,
    ) -> list[CausalNode]:
        """Infer all effects of a cause."""
        effects = []
        visited = set()
        queue = deque([(cause_node_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            
            for edge in self._edges.get(current_id, []):
                target = self._nodes.get(edge.target_id)
                if target and edge.target_id not in visited:
                    effects.append(target)
                    queue.append((edge.target_id, depth + 1))
        
        return effects
    
    async def infer_causes(
        self,
        effect_node_id: str,
        max_depth: int = 10,
    ) -> list[CausalNode]:
        """Infer all causes of an effect."""
        causes = []
        visited = set()
        queue = deque([(effect_node_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            
            for edge in self._reverse_edges.get(current_id, []):
                source = self._nodes.get(edge.source_id)
                if source and edge.source_id not in visited:
                    causes.append(source)
                    queue.append((edge.source_id, depth + 1))
        
        return causes
    
    async def find_paths(
        self,
        source_id: str,
        target_id: str,
        max_paths: int = 5,
    ) -> list[CausalPath]:
        """Find causal paths between two nodes."""
        paths = []
        
        def dfs(
            current: str,
            target: str,
            path_nodes: list[CausalNode],
            path_edges: list[CausalEdge],
            visited: set[str],
        ):
            if len(paths) >= max_paths:
                return
            
            if current == target:
                strength = 1.0
                for edge in path_edges:
                    strength *= edge.strength
                
                paths.append(CausalPath(
                    path_id=f"path_{len(paths)}",
                    nodes=list(path_nodes),
                    edges=list(path_edges),
                    total_strength=strength,
                    probability=strength,
                ))
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            for edge in self._edges.get(current, []):
                target_node = self._nodes.get(edge.target_id)
                if target_node and edge.target_id not in visited:
                    dfs(
                        edge.target_id,
                        target,
                        path_nodes + [target_node],
                        path_edges + [edge],
                        visited.copy(),
                    )
            
            visited.discard(current)
        
        source_node = self._nodes.get(source_id)
        if source_node:
            dfs(source_id, target_id, [source_node], [], set())
        
        return paths
    
    async def calculate_causal_strength(
        self,
        source_id: str,
        target_id: str,
    ) -> float:
        """Calculate total causal strength between two nodes."""
        paths = await self.find_paths(source_id, target_id)
        
        if not paths:
            return 0.0
        
        # Return strongest path
        return max(p.total_strength for p in paths)
    
    async def propagate_confidence(
        self,
        node_id: str,
        initial_confidence: float,
    ) -> dict[str, float]:
        """Propagate confidence through the graph."""
        confidences = {node_id: initial_confidence}
        queue = deque([(node_id, initial_confidence)])
        visited = {node_id}
        
        while queue:
            current_id, conf = queue.popleft()
            
            for edge in self._edges.get(current_id, []):
                if edge.target_id not in visited:
                    new_conf = conf * edge.strength * edge.confidence
                    confidences[edge.target_id] = new_conf
                    queue.append((edge.target_id, new_conf))
                    visited.add(edge.target_id)
        
        return confidences
    
    async def analyze_causal_network(
        self,
        start_node_id: str,
    ) -> CausalAnalysis:
        """Perform complete causal network analysis."""
        start_node = self._nodes.get(start_node_id)
        if not start_node:
            return CausalAnalysis(
                analysis_id=f"ca_{datetime.now().timestamp()}",
                start_node=start_node,
                effects=[],
                causes=[],
                causal_paths=[],
                confidence_scores={},
            )
        
        effects = await self.infer_effects(start_node_id)
        causes = await self.infer_causes(start_node_id)
        
        # Find all paths to outcomes
        paths = []
        for effect in effects:
            if effect.node_type == CausalNodeType.OUTCOME:
                effect_paths = await self.find_paths(start_node_id, effect.node_id)
                paths.extend(effect_paths)
        
        # Calculate confidence scores
        confidence_scores = await self.propagate_confidence(start_node_id, 1.0)
        
        return CausalAnalysis(
            analysis_id=f"ca_{datetime.now().timestamp()}",
            start_node=start_node,
            effects=effects,
            causes=causes,
            causal_paths=paths,
            confidence_scores=confidence_scores,
        )
    
    def get_node(self, node_id: str) -> CausalNode | None:
        """Get node by ID."""
        return self._nodes.get(node_id)
    
    def get_neighbors(
        self,
        node_id: str,
        direction: str = "outgoing",
    ) -> list[tuple[CausalNode, CausalEdge]]:
        """Get neighboring nodes with edges."""
        neighbors = []
        
        if direction in ("outgoing", "both"):
            for edge in self._edges.get(node_id, []):
                neighbor = self._nodes.get(edge.target_id)
                if neighbor:
                    neighbors.append((neighbor, edge))
        
        if direction in ("incoming", "both"):
            for edge in self._reverse_edges.get(node_id, []):
                neighbor = self._nodes.get(edge.source_id)
                if neighbor:
                    neighbors.append((neighbor, edge))
        
        return neighbors


class CausalReasoner:
    """
    High-level causal reasoning engine.
    """
    
    def __init__(self):
        self.graph = CausalGraph()
    
    async def reason_about(
        self,
        problem: str,
        symptoms: list[str],
    ) -> CausalAnalysis:
        """Perform causal reasoning about a problem."""
        # Create problem node
        problem_node = CausalNode(
            node_id="problem",
            node_type=CausalNodeType.EVENT,
            description=problem,
        )
        
        # Create symptom nodes
        symptom_nodes = []
        for i, symptom in enumerate(symptoms):
            node = CausalNode(
                node_id=f"symptom_{i}",
                node_type=CausalNodeType.EVENT,
                description=symptom,
            )
            symptom_nodes.append(node)
            await self.graph.add_node(node)
            
            # Link problem to symptoms
            await self.graph.add_causal_relation(
                problem_node,
                node,
                CausalType.DIRECT,
                strength=0.8,
            )
        
        await self.graph.add_node(problem_node)
        
        # Perform analysis
        return await self.graph.analyze_causal_network("problem")
    
    async def find_root_cause(
        self,
        effect_description: str,
    ) -> list[CausalNode]:
        """Find potential root causes of an effect."""
        # Search for effect node
        effect_node = None
        for node in self.graph._nodes.values():
            if effect_description.lower() in node.description.lower():
                effect_node = node
                break
        
        if not effect_node:
            return []
        
        # Trace back causes
        causes = await self.graph.infer_causes(effect_node.node_id)
        
        # Filter for likely root causes (no incoming edges from non-event nodes)
        root_causes = []
        for cause in causes:
            incoming = self.graph._reverse_edges.get(cause.node_id, [])
            if len(incoming) == 0 or all(
                e.causal_type == CausalType.TRIGGERING
                for e in incoming
            ):
                root_causes.append(cause)
        
        return root_causes


__all__ = [
    "CausalType",
    "CausalNodeType",
    "TemporalRelation",
    "CausalNode",
    "CausalEdge",
    "CausalPath",
    "CausalAnalysis",
    "CausalGraph",
    "CausalReasoner",
]
