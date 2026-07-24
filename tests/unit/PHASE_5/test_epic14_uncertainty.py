"""
Tests para EPIC 14: Uncertainty Quantification Model
"""

import pytest
from datetime import datetime

from core.PHASE_5.epic14_uncertainty.domain import (
    Uncertainty,
    ConfidenceLevel,
    UncertaintySource,
    UncertaintyStatement,
    UncertaintyType,
    ProbabilityDistribution,
    AudienceType,
)
from core.PHASE_5.epic14_uncertainty.agent import UncertaintyAgent


class TestUncertainty:
    """Tests para Uncertainty."""
    
    def test_uncertainty_creation(self):
        """Test creación de incertidumbre."""
        uncertainty = Uncertainty(
            uncertainty_id="unc_1",
            uncertainty_type=UncertaintyType.EPISTEMIC,
            value=0.75,
            distribution=ProbabilityDistribution(
                distribution_type="normal",
                parameters={},
                mean=0.75,
                std_dev=0.15,
            ),
        )
        
        assert uncertainty.uncertainty_id == "unc_1"
        assert uncertainty.uncertainty_type == UncertaintyType.EPISTEMIC
        assert uncertainty.value == 0.75
    
    def test_get_confidence_interval(self):
        """Test obtener intervalo de confianza."""
        uncertainty = Uncertainty(
            uncertainty_id="unc_1",
            uncertainty_type=UncertaintyType.EPISTEMIC,
            value=0.75,
            distribution=ProbabilityDistribution(
                distribution_type="normal",
                parameters={},
                mean=0.75,
                std_dev=0.15,
            ),
        )
        
        ci = uncertainty.get_confidence_interval(level=0.95)
        assert ci[0] < ci[1]
        assert uncertainty.value in ci
    
    def test_get_variance(self):
        """Test obtener varianza."""
        uncertainty = Uncertainty(
            uncertainty_id="unc_1",
            uncertainty_type=UncertaintyType.EPISTEMIC,
            value=0.75,
        )
        
        variance = uncertainty.get_variance()
        assert variance >= 0


class TestConfidenceLevel:
    """Tests para ConfidenceLevel."""
    
    def test_is_high_confidence(self):
        """Test verificar si es alta confianza."""
        confidence = ConfidenceLevel(
            level=0.85,
            is_calibrated=True,
            calibration_error=0.05,
        )
        
        assert confidence.is_high_confidence() is True
    
    def test_requires_qualification(self):
        """Test verificar si requiere cualificación."""
        confidence = ConfidenceLevel(
            level=0.6,
            is_calibrated=True,
            calibration_error=0.15,
        )
        
        assert confidence.requires_qualification() is True


class TestUncertaintySource:
    """Tests para UncertaintySource."""
    
    def test_get_mitigation_strategy(self):
        """Test obtener estrategia de mitigación."""
        source = UncertaintySource(
            source_id="src_1",
            source_type=UncertaintyType.EPISTEMIC,
            description="Limited evidence",
            estimated_impact=0.3,
            mitigatable=True,
        )
        
        strategy = source.get_mitigation_strategy()
        assert strategy is not None


class TestUncertaintyStatement:
    """Tests para UncertaintyStatement."""
    
    def test_format_for_clinical(self):
        """Test formatear para contexto clínico."""
        statement = UncertaintyStatement(
            statement="Test statement",
            probability=0.75,
            confidence_interval=(0.6, 0.85),
            caveats=["Based on limited evidence"],
            audience=AudienceType.CLINICAL,
        )
        
        formatted = statement.format_for_clinical()
        assert "75%" in formatted
        assert "Limited evidence" in formatted


class TestProbabilityDistribution:
    """Tests para ProbabilityDistribution."""
    
    def test_get_confidence_interval(self):
        """Test obtener intervalo de confianza."""
        dist = ProbabilityDistribution(
            distribution_type="normal",
            parameters={},
            mean=0.75,
            std_dev=0.15,
        )
        
        ci = dist.get_confidence_interval(level=0.95)
        assert ci[0] < dist.mean < ci[1]


class TestUncertaintyAgent:
    """Tests para UncertaintyAgent."""
    
    @pytest.mark.asyncio
    async def test_quantify_uncertainty(self):
        """Test cuantificar incertidumbre."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = UncertaintyAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_1",
            agent_id="test_agent",
            task_type="uncertainty",
            input={
                "action": "quantify",
                "value": 0.75,
                "uncertainty_type": "epistemic",
                "evidence_ids": ["ev_1", "ev_2"],
            },
        )
        
        result = await agent.execute(task)
        
        assert "uncertainty_id" in result
        assert result["value"] == 0.75
        assert result["uncertainty_type"] == "epistemic"
    
    @pytest.mark.asyncio
    async def test_calibrate_confidence(self):
        """Test calibrar confianza."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = UncertaintyAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_2",
            agent_id="test_agent",
            task_type="uncertainty",
            input={
                "action": "calibrate",
                "confidence_level": 0.9,
                "predictions": [0.9, 0.85, 0.88],
                "outcomes": [True, True, False],
            },
        )
        
        result = await agent.execute(task)
        
        assert "confidence_level" in result
        assert result["is_calibrated"] is True
    
    @pytest.mark.asyncio
    async def test_detect_sources(self):
        """Test detectar fuentes."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = UncertaintyAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_3",
            agent_id="test_agent",
            task_type="uncertainty",
            input={
                "action": "detect_sources",
                "decision_type": "diagnostic",
            },
        )
        
        result = await agent.execute(task)
        
        assert "sources" in result
        assert result["total_sources"] > 0
