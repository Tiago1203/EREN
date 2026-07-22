"""
Tests for core.intelligence.confidence module.

These tests verify the confidence calculation and scoring functionality.
"""

import pytest
from datetime import datetime
from core.intelligence.confidence import (
    ConfidenceLevel,
    RiskLevel,
    UncertaintyType,
    ConfidenceQualityDimension,
    ConfidenceScore,
    RiskFactor,
    RiskAssessment,
    UncertaintyFactor,
    UncertaintyReport,
    QualityScore,
    CoverageAnalysis,
    AmbiguityReport,
    ConfidenceResult,
    EvidenceBasedCalculator,
    KnowledgeBasedCalculator,
    ReasoningBasedCalculator,
    EnsembleCalculator,
    ConfidenceCalculator,
    ConfidenceEngine,
)


class TestConfidenceScore:
    """Tests for ConfidenceScore dataclass."""

    def test_confidence_score_creation(self):
        """Test ConfidenceScore can be created."""
        score = ConfidenceScore(
            score=0.85,
            level=ConfidenceLevel.HIGH,
            components={"evidence": 0.9, "knowledge": 0.8},
            uncertainty_factors=[],
            supporting_factors=["Strong evidence"],
            recommendation="Proceed"
        )
        
        assert score.score == 0.85
        assert score.level == ConfidenceLevel.HIGH
        assert score.components["evidence"] == 0.9

    def test_confidence_score_is_uncertain(self):
        """Test is_uncertain property."""
        uncertain_score = ConfidenceScore(
            score=0.3,
            level=ConfidenceLevel.VERY_LOW,
            components={},
            uncertainty_factors=["Limited data"],
            supporting_factors=[],
            recommendation="More investigation needed"
        )
        
        assert uncertain_score.is_uncertain is True
        assert uncertain_score.is_certain is False

    def test_confidence_score_is_certain(self):
        """Test is_certain property."""
        certain_score = ConfidenceScore(
            score=0.95,
            level=ConfidenceLevel.VERY_HIGH,
            components={},
            uncertainty_factors=[],
            supporting_factors=["Strong evidence"],
            recommendation="Proceed"
        )
        
        assert certain_score.is_certain is True
        assert certain_score.is_uncertain is False

    def test_confidence_score_percentage(self):
        """Test percentage property."""
        score = ConfidenceScore(
            score=0.75,
            level=ConfidenceLevel.MODERATE,
            components={},
            uncertainty_factors=[],
            supporting_factors=[],
            recommendation=""
        )
        
        assert score.percentage == 75


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum usage."""

    def test_confidence_level_from_foundation(self):
        """Test ConfidenceLevel is imported from foundation."""
        # Verify it matches foundation enum
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MODERATE.value == "moderate"

    def test_all_confidence_levels_available(self):
        """Test all confidence levels are available."""
        levels = [
            ConfidenceLevel.VERY_HIGH,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MODERATE,
            ConfidenceLevel.LOW,
            ConfidenceLevel.VERY_LOW,
            ConfidenceLevel.UNCERTAIN,
        ]
        assert len(levels) == 6


class TestRiskLevel:
    """Tests for RiskLevel enum usage."""

    def test_risk_level_from_foundation(self):
        """Test RiskLevel is imported from foundation."""
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.LOW.value == "low"


class TestUncertaintyType:
    """Tests for UncertaintyType enum usage."""

    def test_uncertainty_type_from_foundation(self):
        """Test UncertaintyType is imported from foundation."""
        assert UncertaintyType.EPISTEMIC.value == "epistemic"
        assert UncertaintyType.ALEATORY.value == "aleatory"
        assert UncertaintyType.MODEL.value == "model"
        assert UncertaintyType.MEASUREMENT.value == "measurement"


class TestRiskFactor:
    """Tests for RiskFactor dataclass."""

    def test_risk_factor_creation(self):
        """Test RiskFactor can be created."""
        factor = RiskFactor(
            factor_id="rf001",
            name="Equipment Failure",
            description="Risk of equipment failure during procedure",
            category="equipment",
            probability=0.3,
            severity=0.7
        )
        
        assert factor.factor_id == "rf001"
        assert factor.probability == 0.3
        assert factor.severity == 0.7

    def test_risk_factor_risk_score(self):
        """Test risk_score property calculation."""
        factor = RiskFactor(
            factor_id="rf001",
            name="Test",
            description="Test",
            category="test",
            probability=0.5,
            severity=0.8,
            detectability=0.5
        )
        
        # risk_score = probability * severity * (1 - detectability * 0.5)
        expected = 0.5 * 0.8 * (1 - 0.5 * 0.5)
        assert factor.risk_score == expected


class TestRiskAssessment:
    """Tests for RiskAssessment dataclass."""

    def test_risk_assessment_creation(self):
        """Test RiskAssessment can be created."""
        assessment = RiskAssessment(
            overall_risk=RiskLevel.HIGH,
            risk_factors=[],
            recommendations=["Monitor closely"],
            immediate_actions=["Stop procedure"]
        )
        
        assert assessment.overall_risk == RiskLevel.HIGH
        assert "Monitor closely" in assessment.recommendations


class TestEvidenceBasedCalculator:
    """Tests for EvidenceBasedCalculator."""

    @pytest.fixture
    def calculator(self):
        return EvidenceBasedCalculator()

    @pytest.mark.asyncio
    async def test_calculate_no_evidence(self, calculator):
        """Test calculator returns low score with no evidence."""
        result = await calculator.calculate({})
        assert result == 0.2

    @pytest.mark.asyncio
    async def test_calculate_with_supporting_evidence(self, calculator):
        """Test calculator with supporting evidence."""
        evidence_bundle = {
            "supporting": [
                {"quality_score": 0.9, "relevance_score": 0.8},
                {"quality_score": 0.8, "relevance_score": 0.7},
            ],
            "contradicting": []
        }
        
        result = await calculator.calculate(evidence_bundle)
        assert 0 <= result <= 1

    @pytest.mark.asyncio
    async def test_calculate_with_contradicting_evidence(self, calculator):
        """Test calculator penalty for contradicting evidence."""
        evidence_bundle = {
            "supporting": [
                {"quality_score": 0.9, "relevance_score": 0.8},
            ],
            "contradicting": [
                {"quality_score": 0.8, "relevance_score": 0.7},
                {"quality_score": 0.8, "relevance_score": 0.7},
            ]
        }
        
        result = await calculator.calculate(evidence_bundle)
        assert result < 0.9  # Should be penalized


class TestKnowledgeBasedCalculator:
    """Tests for KnowledgeBasedCalculator."""

    @pytest.fixture
    def calculator(self):
        return KnowledgeBasedCalculator()

    @pytest.mark.asyncio
    async def test_calculate_full_knowledge(self, calculator):
        """Test calculator with full knowledge coverage."""
        context = {
            "knowledge_coverage": 1.0,
            "knowledge_quality": 1.0,
            "knowledge_recency": 1.0
        }
        
        result = await calculator.calculate(context)
        assert result == 1.0

    @pytest.mark.asyncio
    async def test_calculate_no_knowledge(self, calculator):
        """Test calculator with no knowledge."""
        context = {
            "knowledge_coverage": 0.0,
            "knowledge_quality": 0.0,
            "knowledge_recency": 0.0
        }
        
        result = await calculator.calculate(context)
        assert result == 0.0


class TestEnsembleCalculator:
    """Tests for EnsembleCalculator."""

    def test_combine_weights(self):
        """Test weighted combination of scores."""
        calc = EnsembleCalculator(
            evidence_weight=0.5,
            knowledge_weight=0.3,
            reasoning_weight=0.2
        )
        
        result = calc.combine(evidence=1.0, knowledge=1.0, reasoning=1.0)
        assert result == 1.0

    def test_combine_partial_scores(self):
        """Test combination with partial scores."""
        calc = EnsembleCalculator(
            evidence_weight=0.5,
            knowledge_weight=0.3,
            reasoning_weight=0.2
        )
        
        result = calc.combine(evidence=0.8, knowledge=0.6, reasoning=0.4)
        expected = 0.8 * 0.5 + 0.6 * 0.3 + 0.4 * 0.2
        assert result == expected

    def test_combine_bounded(self):
        """Test result is bounded between 0 and 1."""
        calc = EnsembleCalculator()
        
        result = calc.combine(evidence=2.0, knowledge=2.0, reasoning=2.0)
        assert result == 1.0


class TestConfidenceCalculator:
    """Tests for ConfidenceCalculator."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceCalculator()

    @pytest.mark.asyncio
    async def test_calculate_full(self, calculator):
        """Test full confidence calculation."""
        evidence_bundle = {
            "supporting": [{"quality_score": 0.9, "relevance_score": 0.9}],
            "contradicting": []
        }
        knowledge_context = {
            "knowledge_coverage": 1.0,
            "knowledge_quality": 1.0,
            "knowledge_recency": 1.0
        }
        reasoning_chain = {
            "strength": 1.0,
            "steps": [{"supported": True}, {"supported": True}]
        }
        
        result = await calculator.calculate(evidence_bundle, knowledge_context, reasoning_chain)
        
        assert isinstance(result, ConfidenceScore)
        assert 0 <= result.score <= 1

    @pytest.mark.asyncio
    async def test_get_level_very_high(self, calculator):
        """Test _get_level returns VERY_HIGH for high scores."""
        level = calculator._get_level(0.98)
        assert level == ConfidenceLevel.VERY_HIGH

    @pytest.mark.asyncio
    async def test_get_level_uncertain(self, calculator):
        """Test _get_level returns UNCERTAIN for low scores."""
        level = calculator._get_level(0.2)
        assert level == ConfidenceLevel.UNCERTAIN


class TestConfidenceEngine:
    """Tests for ConfidenceEngine."""

    @pytest.fixture
    def engine(self):
        return ConfidenceEngine()

    @pytest.mark.asyncio
    async def test_assess_confidence(self, engine):
        """Test confidence assessment."""
        result = await engine.assess_confidence(
            evidence_bundle={"supporting": []},
            knowledge_context={"knowledge_coverage": 0.5},
            reasoning_chain={"strength": 0.5, "steps": []}
        )
        
        assert isinstance(result, ConfidenceScore)

    def test_explain_confidence(self, engine):
        """Test confidence explanation generation."""
        score = ConfidenceScore(
            score=0.85,
            level=ConfidenceLevel.HIGH,
            components={},
            uncertainty_factors=[],
            supporting_factors=["Strong evidence"],
            recommendation="Proceed"
        )
        
        explanation = engine.explain_confidence(score)
        assert isinstance(explanation, str)
        assert "Confidence" in explanation
