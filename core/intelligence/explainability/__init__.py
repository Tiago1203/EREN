"""
Explainability Engine Module

Complete implementation of EPIC 5 for EREN PHASE 3.

This module provides explainability capabilities:
- Reasoning Graph Generator
- Evidence Tree Builder
- Decision Path Tracer
- Source Tracer
- Natural Language Explainer
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any


# Version
__version__ = "1.0.0"


# Enums
class NodeType(Enum):
    """Types of nodes in reasoning graph."""
    SYMPTOM = "symptom"
    EVIDENCE = "evidence"
    RULE = "rule"
    HYPOTHESIS = "hypothesis"
    CONCLUSION = "conclusion"
    ACTION = "action"


class EdgeType(Enum):
    """Types of edges."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CAUSES = "causes"
    IMPLIES = "implies"
    LEADS_TO = "leads_to"


class TreeNodeType(Enum):
    """Types of tree nodes."""
    ROOT = "root"
    CATEGORY = "category"
    EVIDENCE = "evidence"
    CONCLUSION = "conclusion"


class LanguageStyle(Enum):
    """Styles for natural language generation."""
    TECHNICAL = "technical"
    CLINICAL = "clinical"
    SIMPLE = "simple"
    FORMAL = "formal"


# Data Classes
@dataclass(frozen=True)
class GraphNode:
    """Node in reasoning graph."""
    node_id: str
    label: str
    node_type: NodeType
    properties: dict
    confidence: Optional[float] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class GraphEdge:
    """Edge in reasoning graph."""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float
    label: Optional[str] = None


@dataclass(frozen=True)
class ReasoningGraph:
    """Graph representation of reasoning."""
    graph_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    root_nodes: list[str]
    leaf_nodes: list[str]
    critical_path: list[str]


@dataclass(frozen=True)
class TreeNode:
    """Node in evidence tree."""
    node_id: str
    label: str
    node_type: TreeNodeType
    children: list
    annotation: Optional[dict] = None
    confidence: Optional[float] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class EvidenceTree:
    """Tree representation of evidence."""
    tree_id: str
    root: TreeNode
    supporting_evidence: list
    contradicting_evidence: list
    total_evidence_count: int
    overall_weight: float


@dataclass(frozen=True)
class PathStep:
    """Step in decision path."""
    step_id: str
    description: str
    step_type: str
    evidence: list
    conclusion: str


@dataclass(frozen=True)
class DecisionPath:
    """Path through decision space."""
    path_id: str
    steps: list[PathStep]
    alternatives: list
    selected_path: list[str]


@dataclass(frozen=True)
class Citation:
    """Citation for a source."""
    citation_id: str
    text: str
    source_type: str
    source_name: str
    url: Optional[str] = None
    page: Optional[str] = None


@dataclass(frozen=True)
class SourceTrace:
    """Trace of all sources."""
    trace_id: str
    citations: list[Citation]
    provenance: list
    references: list[str]


@dataclass(frozen=True)
class Explanation:
    """Complete explanation of a recommendation."""
    explanation_id: str
    recommendation_id: str
    summary: str
    reasoning_graph: ReasoningGraph
    evidence_tree: EvidenceTree
    decision_path: DecisionPath
    source_trace: SourceTrace
    natural_language: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class ReasoningGraphGenerator:
    """Generates reasoning graphs."""
    
    def generate(self, reasoning_chain: dict) -> ReasoningGraph:
        """Generate reasoning graph from chain."""
        nodes = []
        edges = []
        
        steps = reasoning_chain.get("steps", [])
        
        # Create nodes from steps
        for i, step in enumerate(steps):
            node_type = self._get_node_type(step.get("type", "unknown"))
            node = GraphNode(
                node_id=f"node_{i}",
                label=step.get("description", f"Step {i+1}"),
                node_type=node_type,
                properties=step.get("properties", {}),
                confidence=step.get("confidence"),
                source=step.get("source"),
            )
            nodes.append(node)
        
        # Create edges
        for i in range(len(nodes) - 1):
            edge = GraphEdge(
                edge_id=f"edge_{i}",
                source_id=nodes[i].node_id,
                target_id=nodes[i + 1].node_id,
                edge_type=EdgeType.IMPLIES,
                weight=0.9,
                label=None,
            )
            edges.append(edge)
        
        return ReasoningGraph(
            graph_id=f"graph_{datetime.now().timestamp()}",
            nodes=nodes,
            edges=edges,
            root_nodes=[nodes[0].node_id] if nodes else [],
            leaf_nodes=[nodes[-1].node_id] if nodes else [],
            critical_path=[n.node_id for n in nodes],
        )
    
    def _get_node_type(self, step_type: str) -> NodeType:
        """Get node type from step type."""
        type_map = {
            "symptom": NodeType.SYMPTOM,
            "evidence": NodeType.EVIDENCE,
            "rule": NodeType.RULE,
            "hypothesis": NodeType.HYPOTHESIS,
            "conclusion": NodeType.CONCLUSION,
            "action": NodeType.ACTION,
        }
        return type_map.get(step_type, NodeType.HYPOTHESIS)
    
    def to_dot(self, graph: ReasoningGraph) -> str:
        """Export to DOT format."""
        lines = [
            "digraph ReasoningGraph {",
            "  rankdir=TB;",
            "  node [shape=box];",
        ]
        
        for node in graph.nodes:
            lines.append(
                f'  {node.node_id} [label="{node.label}"];'
            )
        
        for edge in graph.edges:
            lines.append(
                f"  {edge.source_id} -> {edge.target_id};"
            )
        
        lines.append("}")
        return "\n".join(lines)


class EvidenceTreeBuilder:
    """Builds evidence trees."""
    
    def build(self, evidence_bundle: dict) -> EvidenceTree:
        """Build evidence tree from bundle."""
        supporting = evidence_bundle.get("supporting", [])
        contradicting = evidence_bundle.get("contradicting", [])
        
        # Create root
        root = TreeNode(
            node_id="root",
            label="Recommendation",
            node_type=TreeNodeType.ROOT,
            children=[],
        )
        
        # Create supporting branch
        supporting_node = TreeNode(
            node_id="supporting",
            label=f"Supporting Evidence ({len(supporting)})",
            node_type=TreeNodeType.CATEGORY,
            children=[],
        )
        
        for i, e in enumerate(supporting[:5]):
            child = TreeNode(
                node_id=f"supp_{i}",
                label=e.get("content", "")[:80],
                node_type=TreeNodeType.EVIDENCE,
                children=[],
                annotation={"weight": e.get("quality_score", 0.5)},
                confidence=e.get("quality_score"),
                source=e.get("source_name"),
            )
            supporting_node.children.append(child)
        
        # Create contradicting branch
        contradicting_node = TreeNode(
            node_id="contradicting",
            label=f"Contradicting Evidence ({len(contradicting)})",
            node_type=TreeNodeType.CATEGORY,
            children=[],
        )
        
        for i, e in enumerate(contradicting[:5]):
            child = TreeNode(
                node_id=f"contra_{i}",
                label=e.get("content", "")[:80],
                node_type=TreeNodeType.EVIDENCE,
                children=[],
                annotation={"weight": e.get("quality_score", 0.5)},
                confidence=e.get("quality_score"),
                source=e.get("source_name"),
            )
            contradicting_node.children.append(child)
        
        root.children = [supporting_node, contradicting_node]
        
        return EvidenceTree(
            tree_id=f"tree_{datetime.now().timestamp()}",
            root=root,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            total_evidence_count=len(supporting) + len(contradicting),
            overall_weight=0.8,
        )


class DecisionPathTracer:
    """Traces decision paths."""
    
    def trace(self, reasoning_chain: dict) -> DecisionPath:
        """Trace decision path from chain."""
        steps = []
        
        for i, step in enumerate(reasoning_chain.get("steps", [])):
            path_step = PathStep(
                step_id=f"step_{i}",
                description=step.get("description", f"Step {i+1}"),
                step_type=step.get("type", "reasoning"),
                evidence=step.get("evidence", []),
                conclusion=step.get("conclusion", ""),
            )
            steps.append(path_step)
        
        return DecisionPath(
            path_id=f"path_{datetime.now().timestamp()}",
            steps=steps,
            alternatives=[],
            selected_path=[s.step_id for s in steps],
        )


class SourceTracer:
    """Traces source citations."""
    
    def trace(self, evidence_bundle: dict) -> SourceTrace:
        """Trace sources from evidence."""
        citations = []
        references = []
        
        for e in evidence_bundle.get("supporting", []) + evidence_bundle.get("contradicting", []):
            citation = Citation(
                citation_id=f"cite_{len(citations)}",
                text=e.get("content", "")[:100],
                source_type=e.get("source_type", "unknown"),
                source_name=e.get("source_name", "Unknown"),
                url=e.get("url"),
                page=e.get("citation"),
            )
            citations.append(citation)
            
            if e.get("citation"):
                references.append(e.get("citation"))
            elif e.get("source_name"):
                references.append(e.get("source_name"))
        
        return SourceTrace(
            trace_id=f"trace_{datetime.now().timestamp()}",
            citations=citations,
            provenance=[],
            references=list(set(references)),
        )


class NaturalLanguageExplainer:
    """Generates natural language explanations."""
    
    def __init__(self):
        self.style = LanguageStyle.CLINICAL
    
    def generate(
        self,
        recommendation: dict,
        evidence_bundle: dict,
        confidence: dict,
        style: LanguageStyle = LanguageStyle.CLINICAL,
    ) -> str:
        """Generate natural language explanation."""
        
        lines = []
        
        # Header
        action = recommendation.get("action", "Unknown action")
        lines.append(f"EREN recommends: {action.upper()}")
        lines.append("")
        lines.append("Why?")
        lines.append("━" * 50)
        lines.append("")
        
        # Evidence
        supporting = evidence_bundle.get("supporting", [])
        for i, e in enumerate(supporting[:3], 1):
            lines.append(f"{i}. {e.get('content', '')}")
            lines.append(f"   Source: {e.get('source_name', 'Unknown')}")
            if e.get("citation"):
                lines.append(f"   Reference: {e.get('citation')}")
            lines.append("")
        
        # Confidence
        conf_level = confidence.get("level", "unknown")
        conf_score = confidence.get("score", 0.5)
        lines.append(f"Confidence: {int(conf_score * 100)}% ({conf_level.upper()})")
        
        return "\n".join(lines)


class ExplainabilityEngine:
    """
    Main explainability engine that provides the external interface.
    """
    
    def __init__(self):
        self.graph_generator = ReasoningGraphGenerator()
        self.tree_builder = EvidenceTreeBuilder()
        self.path_tracer = DecisionPathTracer()
        self.source_tracer = SourceTracer()
        self.nl_explainer = NaturalLanguageExplainer()
    
    async def explain(
        self,
        recommendation: dict,
        reasoning_chain: dict,
        evidence_bundle: dict,
        confidence: dict,
    ) -> Explanation:
        """Generate complete explanation."""
        
        # Generate components
        graph = self.graph_generator.generate(reasoning_chain)
        tree = self.tree_builder.build(evidence_bundle)
        path = self.path_tracer.trace(reasoning_chain)
        trace = self.source_tracer.trace(evidence_bundle)
        nl = self.nl_explainer.generate(
            recommendation, evidence_bundle, confidence
        )
        
        # Generate summary
        summary = f"EREN recommends: {recommendation.get('action', 'action')}. Confidence: {int(confidence.get('score', 0.5) * 100)}%."
        
        return Explanation(
            explanation_id=f"exp_{datetime.now().timestamp()}",
            recommendation_id=recommendation.get("id", "unknown"),
            summary=summary,
            reasoning_graph=graph,
            evidence_tree=tree,
            decision_path=path,
            source_trace=trace,
            natural_language=nl,
            confidence=confidence.get("score", 0.5),
        )


__all__ = [
    # Version
    "__version__",
    # Enums
    "NodeType",
    "EdgeType",
    "TreeNodeType",
    "LanguageStyle",
    # Data Classes
    "GraphNode",
    "GraphEdge",
    "ReasoningGraph",
    "TreeNode",
    "EvidenceTree",
    "PathStep",
    "DecisionPath",
    "Citation",
    "SourceTrace",
    "Explanation",
    # Generators
    "ReasoningGraphGenerator",
    "EvidenceTreeBuilder",
    "DecisionPathTracer",
    "SourceTracer",
    "NaturalLanguageExplainer",
    "ExplainabilityEngine",
]
