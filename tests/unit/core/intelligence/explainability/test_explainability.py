"""
Tests for core.intelligence.explainability module.

These tests verify the explainability and visualization functionality.
"""

import pytest
from datetime import datetime
from core.intelligence.explainability import (
    LanguageStyle,
    NodeType,
    EdgeType,
    TreeNodeType,
    GraphNode,
    GraphEdge,
    ReasoningGraph,
    TreeNode,
    EvidenceTree,
    PathStep,
    DecisionPath,
    Citation,
    SourceTrace,
    Explanation,
    ReasoningGraphGenerator,
    EvidenceTreeBuilder,
    DecisionPathTracer,
    SourceTracer,
    NaturalLanguageExplainer,
    ExplainabilityEngine,
)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_type_values(self):
        """Test NodeType enum has correct values."""
        assert NodeType.SYMPTOM.value == "symptom"
        assert NodeType.EVIDENCE.value == "evidence"
        assert NodeType.RULE.value == "rule"
        assert NodeType.HYPOTHESIS.value == "hypothesis"
        assert NodeType.CONCLUSION.value == "conclusion"
        assert NodeType.ACTION.value == "action"

    def test_node_type_count(self):
        """Test NodeType enum has correct number of values."""
        assert len(NodeType) == 6


class TestEdgeType:
    """Tests for EdgeType enum."""

    def test_edge_type_values(self):
        """Test EdgeType enum has correct values."""
        assert EdgeType.SUPPORTS.value == "supports"
        assert EdgeType.CONTRADICTS.value == "contradicts"
        assert EdgeType.CAUSES.value == "causes"
        assert EdgeType.IMPLIES.value == "implies"
        assert EdgeType.LEADS_TO.value == "leads_to"


class TestLanguageStyle:
    """Tests for LanguageStyle enum."""

    def test_language_style_from_foundation(self):
        """Test LanguageStyle is imported from foundation."""
        assert LanguageStyle.TECHNICAL.value == "technical"
        assert LanguageStyle.CLINICAL.value == "clinical"
        assert LanguageStyle.PATIENT_FRIENDLY.value == "patient_friendly"
        assert LanguageStyle.ADMINISTRATIVE.value == "administrative"

    def test_language_style_count(self):
        """Test LanguageStyle enum has correct number of values."""
        assert len(LanguageStyle) == 4


class TestGraphNode:
    """Tests for GraphNode dataclass."""

    def test_graph_node_creation(self):
        """Test GraphNode can be created."""
        node = GraphNode(
            node_id="n001",
            label="Test Node",
            node_type=NodeType.EVIDENCE,
            properties={"weight": 0.8},
            confidence=0.95,
            source="TestSource"
        )
        
        assert node.node_id == "n001"
        assert node.node_type == NodeType.EVIDENCE
        assert node.confidence == 0.95


class TestGraphEdge:
    """Tests for GraphEdge dataclass."""

    def test_graph_edge_creation(self):
        """Test GraphEdge can be created."""
        edge = GraphEdge(
            edge_id="e001",
            source_id="n001",
            target_id="n002",
            edge_type=EdgeType.SUPPORTS,
            weight=0.9,
            label="supports"
        )
        
        assert edge.edge_id == "e001"
        assert edge.source_id == "n001"
        assert edge.target_id == "n002"
        assert edge.weight == 0.9


class TestReasoningGraph:
    """Tests for ReasoningGraph dataclass."""

    def test_reasoning_graph_creation(self):
        """Test ReasoningGraph can be created."""
        graph = ReasoningGraph(
            graph_id="g001",
            nodes=[],
            edges=[],
            root_nodes=["n001"],
            leaf_nodes=["n003"],
            critical_path=["n001", "n002", "n003"]
        )
        
        assert graph.graph_id == "g001"
        assert "n001" in graph.root_nodes


class TestTreeNode:
    """Tests for TreeNode dataclass."""

    def test_tree_node_creation(self):
        """Test TreeNode can be created."""
        node = TreeNode(
            node_id="t001",
            label="Test Tree Node",
            node_type=TreeNodeType.ROOT,
            children=[],
            confidence=0.9
        )
        
        assert node.node_id == "t001"
        assert node.node_type == TreeNodeType.ROOT


class TestEvidenceTree:
    """Tests for EvidenceTree dataclass."""

    def test_evidence_tree_creation(self):
        """Test EvidenceTree can be created."""
        tree = EvidenceTree(
            tree_id="et001",
            root=TreeNode(
                node_id="root",
                label="Root",
                node_type=TreeNodeType.ROOT,
                children=[]
            ),
            supporting_evidence=[],
            contradicting_evidence=[],
            total_evidence_count=0,
            overall_weight=0.5
        )
        
        assert tree.tree_id == "et001"


class TestPathStep:
    """Tests for PathStep dataclass."""

    def test_path_step_creation(self):
        """Test PathStep can be created."""
        step = PathStep(
            step_id="s001",
            description="Test step",
            step_type="reasoning",
            evidence=[],
            conclusion="Test conclusion"
        )
        
        assert step.step_id == "s001"
        assert step.conclusion == "Test conclusion"


class TestCitation:
    """Tests for Citation dataclass."""

    def test_citation_creation(self):
        """Test Citation can be created."""
        citation = Citation(
            citation_id="c001",
            text="Test citation text",
            source_type="journal",
            source_name="Test Journal",
            url="https://example.com",
            page="42"
        )
        
        assert citation.citation_id == "c001"
        assert citation.source_name == "Test Journal"


class TestReasoningGraphGenerator:
    """Tests for ReasoningGraphGenerator."""

    @pytest.fixture
    def generator(self):
        return ReasoningGraphGenerator()

    def test_generate_empty_chain(self, generator):
        """Test generator with empty reasoning chain."""
        graph = generator.generate({})
        
        assert isinstance(graph, ReasoningGraph)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_generate_with_steps(self, generator):
        """Test generator with reasoning steps."""
        chain = {
            "steps": [
                {"type": "symptom", "description": "Patient has fever", "confidence": 0.9},
                {"type": "evidence", "description": "Temperature 38.5C", "confidence": 0.95},
                {"type": "hypothesis", "description": "Possible infection", "confidence": 0.8},
            ]
        }
        
        graph = generator.generate(chain)
        
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2  # 3 nodes = 2 edges

    def test_to_dot_format(self, generator):
        """Test DOT format export."""
        chain = {
            "steps": [
                {"type": "symptom", "description": "Step 1"},
                {"type": "evidence", "description": "Step 2"},
            ]
        }
        
        graph = generator.generate(chain)
        dot = generator.to_dot(graph)
        
        assert "digraph" in dot
        assert "node_" in dot


class TestEvidenceTreeBuilder:
    """Tests for EvidenceTreeBuilder."""

    @pytest.fixture
    def builder(self):
        return EvidenceTreeBuilder()

    def test_build_empty_bundle(self, builder):
        """Test builder with empty evidence bundle.
        
        OPTION 4: TreeNodes are created with children from the start,
        maintaining immutability (frozen=True).
        """
        tree = builder.build({})
        
        assert isinstance(tree, EvidenceTree)
        assert tree.total_evidence_count == 0
        # Verify root has both branches even with empty evidence
        assert len(tree.root.children) == 2

    def test_build_with_supporting_evidence(self, builder):
        """Test builder with supporting evidence.
        
        OPTION 4: All children are created at once as lists,
        no post-creation modification of frozen dataclasses.
        """
        bundle = {
            "supporting": [
                {"content": "Evidence 1", "quality_score": 0.8, "source_name": "Source 1"},
                {"content": "Evidence 2", "quality_score": 0.7, "source_name": "Source 2"},
            ],
            "contradicting": []
        }
        
        tree = builder.build(bundle)
        
        assert isinstance(tree, EvidenceTree)
        assert tree.total_evidence_count == 2
        # Verify supporting branch has children
        supporting_branch = tree.root.children[0]
        assert len(supporting_branch.children) == 2


class TestSourceTracer:
    """Tests for SourceTracer."""

    @pytest.fixture
    def tracer(self):
        return SourceTracer()

    def test_trace_empty_bundle(self, tracer):
        """Test tracer with empty evidence bundle."""
        trace = tracer.trace({})
        
        assert isinstance(trace, SourceTrace)
        assert len(trace.citations) == 0

    def test_trace_with_evidence(self, tracer):
        """Test tracer with evidence."""
        bundle = {
            "supporting": [
                {"content": "Test", "source_type": "journal", "source_name": "Test Journal", "citation": "Ref 1"}
            ]
        }
        
        trace = tracer.trace(bundle)
        
        assert len(trace.citations) == 1
        assert trace.citations[0].source_name == "Test Journal"


class TestNaturalLanguageExplainer:
    """Tests for NaturalLanguageExplainer."""

    @pytest.fixture
    def explainer(self):
        return NaturalLanguageExplainer()

    def test_explainer_default_style(self, explainer):
        """Test explainer uses CLINICAL style by default."""
        assert explainer.style == LanguageStyle.CLINICAL

    def test_generate_recommendation(self, explainer):
        """Test natural language generation."""
        recommendation = {"action": "Replace sensor"}
        evidence_bundle = {
            "supporting": [
                {"content": "Sensor readings are inconsistent", "source_name": "Test"}
            ]
        }
        confidence = {"score": 0.85, "level": "high"}
        
        result = explainer.generate(recommendation, evidence_bundle, confidence)
        
        assert isinstance(result, str)
        # Note: The code uppercases the action, so check for uppercase version
        assert "REPLACE SENSOR" in result


class TestExplainabilityEngine:
    """Tests for ExplainabilityEngine."""

    @pytest.fixture
    def engine(self):
        return ExplainabilityEngine()

    @pytest.mark.asyncio
    async def test_explain(self, engine):
        """Test complete explanation generation.
        
        Uses OPTION 4 for EvidenceTree construction,
        maintaining immutability throughout.
        """
        recommendation = {"id": "r001", "action": "Calibrate device"}
        reasoning_chain = {"steps": []}
        evidence_bundle = {"supporting": [], "contradicting": []}
        confidence = {"score": 0.8, "level": "high"}
        
        result = await engine.explain(
            recommendation,
            reasoning_chain,
            evidence_bundle,
            confidence
        )
        
        assert isinstance(result, Explanation)
        assert result.recommendation_id == "r001"
