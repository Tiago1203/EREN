"""Tests for Clinical Intelligence Gateway."""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from datetime import datetime
from typing import Any

from core.PHASE_2.ai.domain.clinical_intelligence_gateway import (
    ClinicalIntelligenceGateway,
    ClinicalQueryDTO,
    ClinicalResponseDTO,
)


class TestClinicalIntelligenceGateway:
    """Tests for ClinicalIntelligenceGateway."""

    def test_gateway_exists(self):
        """Test that ClinicalIntelligenceGateway can be imported."""
        from core.PHASE_2.ai.domain import ClinicalIntelligenceGateway
        
        assert ClinicalIntelligenceGateway is not None

    def test_gateway_can_be_instantiated(self):
        """Test that gateway can be instantiated."""
        gateway = ClinicalIntelligenceGateway()
        assert gateway is not None

    def test_gateway_has_name(self):
        """Test that gateway has correct name."""
        gateway = ClinicalIntelligenceGateway()
        assert gateway.name == "clinical_intelligence"

    def test_gateway_with_custom_pipelines(self):
        """Test that gateway can be initialized with custom pipelines."""
        mock_reasoning = Mock()
        mock_evidence = Mock()
        mock_safety = Mock()
        
        gateway = ClinicalIntelligenceGateway(
            reasoning_pipeline=mock_reasoning,
            evidence_retrieval=mock_evidence,
            safety_validation=mock_safety,
        )
        
        assert gateway._reasoning_pipeline is mock_reasoning
        assert gateway._evidence_retrieval is mock_evidence
        assert gateway._safety_validation is mock_safety


class TestClinicalQueryDTO:
    """Tests for ClinicalQueryDTO."""

    def test_query_dto_can_be_created(self):
        """Test that ClinicalQueryDTO can be created."""
        query = ClinicalQueryDTO(
            query_id="q-001",
            device_id="dev-123",
            incident_id="inc-456",
            symptoms=["high_temperature", "error_code_5E"],
            context={"key": "value"},
            tenant_id="hospital-001",
            requested_at=datetime.now(),
        )
        
        assert query.query_id == "q-001"
        assert query.device_id == "dev-123"
        assert query.incident_id == "inc-456"
        assert len(query.symptoms) == 2
        assert query.tenant_id == "hospital-001"

    def test_query_dto_is_frozen(self):
        """Test that ClinicalQueryDTO is immutable."""
        query = ClinicalQueryDTO(
            query_id="q-001",
            device_id="dev-123",
            incident_id=None,
            symptoms=[],
            context={},
            tenant_id="hospital-001",
            requested_at=datetime.now(),
        )
        
        with pytest.raises(AttributeError):
            query.query_id = "modified"


class TestClinicalResponseDTO:
    """Tests for ClinicalResponseDTO."""

    def test_response_dto_can_be_created(self):
        """Test that ClinicalResponseDTO can be created."""
        response = ClinicalResponseDTO(
            query_id="q-001",
            reasoning_chain=["step1", "step2", "step3"],
            hypotheses=[{"id": "h-001", "cause": "sensor_failure"}],
            evidence_bundle={"evidence_count": 5},
            confidence_score=0.85,
            recommendations=[{"action": "replace_sensor"}],
            safety_validated=True,
            validation_status="VALIDATED",
            generated_at=datetime.now(),
        )
        
        assert response.query_id == "q-001"
        assert len(response.reasoning_chain) == 3
        assert len(response.hypotheses) == 1
        assert response.confidence_score == 0.85
        assert response.safety_validated is True

    def test_response_dto_is_frozen(self):
        """Test that ClinicalResponseDTO is immutable."""
        response = ClinicalResponseDTO(
            query_id="q-001",
            reasoning_chain=[],
            hypotheses=[],
            evidence_bundle={},
            confidence_score=0.5,
            recommendations=[],
            safety_validated=False,
            validation_status="PENDING",
            generated_at=datetime.now(),
        )
        
        with pytest.raises(AttributeError):
            response.confidence_score = 1.0


@pytest.mark.asyncio
class TestClinicalIntelligenceGatewayMethods:
    """Tests for ClinicalIntelligenceGateway async methods."""

    async def test_process_clinical_query_returns_response(self):
        """Test that process_clinical_query returns a valid response."""
        gateway = ClinicalIntelligenceGateway()
        
        query = ClinicalQueryDTO(
            query_id="q-001",
            device_id="dev-123",
            incident_id=None,
            symptoms=["error_code_5E"],
            context={},
            tenant_id="hospital-001",
            requested_at=datetime.now(),
        )
        
        response = await gateway.process_clinical_query(query)
        
        assert isinstance(response, ClinicalResponseDTO)
        assert response.query_id == "q-001"
        assert len(response.reasoning_chain) > 0
        assert 0 <= response.confidence_score <= 1

    async def test_get_reasoning_context_returns_dict(self):
        """Test that get_reasoning_context returns a dictionary."""
        gateway = ClinicalIntelligenceGateway()
        
        context = await gateway.get_reasoning_context(
            device_id="dev-123",
            incident_id="inc-456",
        )
        
        assert isinstance(context, dict)
        assert "device_id" in context
        assert context["device_id"] == "dev-123"

    async def test_validate_safety_returns_bool(self):
        """Test that validate_safety returns a boolean."""
        gateway = ClinicalIntelligenceGateway()
        
        recommendation = {"action": "Replace sensor"}
        result = await gateway.validate_safety(recommendation)
        
        assert isinstance(result, bool)

    async def test_validate_safety_blocks_unsafe_actions(self):
        """Test that unsafe actions are blocked."""
        gateway = ClinicalIntelligenceGateway()
        
        unsafe_recommendation = {"action": "Open the defibrillator"}
        result = await gateway.validate_safety(unsafe_recommendation)
        
        assert result is False

    async def test_validate_safety_allows_safe_actions(self):
        """Test that safe actions are allowed."""
        gateway = ClinicalIntelligenceGateway()
        
        safe_recommendation = {"action": "Replace the sensor"}
        result = await gateway.validate_safety(safe_recommendation)
        
        assert result is True

    async def test_get_confidence_returns_float(self):
        """Test that get_confidence returns a float between 0 and 1."""
        gateway = ClinicalIntelligenceGateway()
        
        reasoning_result = {
            "evidence_score": 0.8,
            "consistency_score": 0.7,
            "coverage_score": 0.6,
        }
        
        confidence = await gateway.get_confidence(reasoning_result)
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1


@pytest.mark.asyncio
class TestClinicalIntelligenceIntegration:
    """Integration tests for ClinicalIntelligenceGateway with PHASE_3."""

    async def test_gateway_connects_to_phase3_intelligence(self):
        """Test that gateway can connect to PHASE_3 intelligence modules."""
        # Verify PHASE_3 modules are accessible
        from core.PHASE_3.intelligence import reasoning, evidence, confidence
        
        assert reasoning is not None
        assert evidence is not None
        assert confidence is not None

    async def test_mock_response_has_expected_structure(self):
        """Test that mock response has expected structure."""
        gateway = ClinicalIntelligenceGateway()
        
        query = ClinicalQueryDTO(
            query_id="test-q-001",
            device_id="test-dev",
            incident_id=None,
            symptoms=["symptom1"],
            context={},
            tenant_id="test-tenant",
            requested_at=datetime.now(),
        )
        
        response = await gateway.process_clinical_query(query)
        
        # Verify structure
        assert hasattr(response, 'query_id')
        assert hasattr(response, 'reasoning_chain')
        assert hasattr(response, 'hypotheses')
        assert hasattr(response, 'evidence_bundle')
        assert hasattr(response, 'confidence_score')
        assert hasattr(response, 'recommendations')
        assert hasattr(response, 'safety_validated')
        assert hasattr(response, 'validation_status')
        assert hasattr(response, 'generated_at')

    async def test_reasoning_chain_contains_clinical_steps(self):
        """Test that reasoning chain contains clinical analysis steps."""
        gateway = ClinicalIntelligenceGateway()
        
        query = ClinicalQueryDTO(
            query_id="test-q-002",
            device_id="test-dev",
            incident_id="test-inc",
            symptoms=["temperature_high", "error_5E"],
            context={},
            tenant_id="test-tenant",
            requested_at=datetime.now(),
        )
        
        response = await gateway.process_clinical_query(query)
        
        # Verify reasoning chain has clinical steps
        assert len(response.reasoning_chain) >= 3
        assert any("symptom" in step.lower() for step in response.reasoning_chain)

    async def test_hypotheses_have_required_fields(self):
        """Test that hypotheses have required fields."""
        gateway = ClinicalIntelligenceGateway()
        
        query = ClinicalQueryDTO(
            query_id="test-q-003",
            device_id="test-dev",
            incident_id=None,
            symptoms=["error"],
            context={},
            tenant_id="test-tenant",
            requested_at=datetime.now(),
        )
        
        response = await gateway.process_clinical_query(query)
        
        for hypothesis in response.hypotheses:
            assert "id" in hypothesis or "cause" in hypothesis
            assert "confidence" in hypothesis or "recommended_action" in hypothesis
