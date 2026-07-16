"""Unit tests for RecommendationService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.recommendation.domain.services.recommendation_service import RecommendationService
from core.recommendation.domain.entities import AIRecommendation
from core.recommendation.domain.value_objects import (
    RecommendationCategory,
    RecommendationConfidence,
    RecommendationStatus,
    RecommendationUrgency,
)
from core.shared import DeviceId, EngineerId, IncidentId, Ok, Result, TenantId, RecommendationId


@pytest.fixture
def mock_repository():
    """Create a mock RecommendationRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    """Create RecommendationService with mock repository."""
    return RecommendationService(repository=mock_repository)


@pytest.mark.asyncio
class TestCreateRecommendation:
    """Test RecommendationService.create_recommendation()."""

    async def test_create_recommendation_success(self, service, mock_repository):
        """Recommendation is created successfully."""
        mock_repository.save.return_value = Ok(MagicMock())

        result = await service.create_recommendation(
            tenant_id=TenantId(value="tenant-1"),
            device_id=DeviceId(value="device-1"),
            title="Replace filter",
            description="Replace the HEPA filter every 6 months",
            rationale="Filter lifespan exceeded based on usage hours",
            category=RecommendationCategory.maintenance,
            confidence=RecommendationConfidence(high=0.85, medium=0.10, low=0.05),
            model_version="v1.0",
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()

    async def test_create_recommendation_with_incident(self, service, mock_repository):
        """Recommendation can be linked to an incident."""
        mock_repository.save.return_value = Ok(MagicMock())

        result = await service.create_recommendation(
            tenant_id=TenantId(value="tenant-1"),
            device_id=DeviceId(value="device-1"),
            title="Calibrate sensor",
            description="Perform sensor calibration",
            rationale="Recalibration recommended by manufacturer",
            category=RecommendationCategory.calibration,
            confidence=RecommendationConfidence(high=0.90, medium=0.08, low=0.02),
            model_version="v1.0",
            incident_id=IncidentId(value="incident-1"),
            urgency=RecommendationUrgency.urgent(),
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()


@pytest.mark.asyncio
class TestAcceptRecommendation:
    """Test RecommendationService.accept_recommendation()."""

    async def test_accept_recommendation_success(self, service, mock_repository):
        """Recommendation is accepted successfully."""
        mock_rec = MagicMock(spec=AIRecommendation)
        mock_rec.version = 1
        mock_repository.get_by_id.return_value = Ok(mock_rec)
        mock_repository.save.return_value = Ok(mock_rec)

        result = await service.accept_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId(value="eng-1"),
            note="Will do this next week",
        )

        assert result.is_ok()
        mock_rec.accept.assert_called_once()

    async def test_accept_recommendation_not_found(self, service, mock_repository):
        """Accept fails when recommendation not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await service.accept_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId(value="eng-1"),
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()


@pytest.mark.asyncio
class TestRejectRecommendation:
    """Test RecommendationService.reject_recommendation()."""

    async def test_reject_recommendation_success(self, service, mock_repository):
        """Recommendation is rejected successfully."""
        mock_rec = MagicMock(spec=AIRecommendation)
        mock_rec.version = 1
        mock_repository.get_by_id.return_value = Ok(mock_rec)
        mock_repository.save.return_value = Ok(mock_rec)

        result = await service.reject_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId(value="eng-1"),
            reason_code="NOT_RELEVANT",
            reason_description="This device does not need this",
        )

        assert result.is_ok()
        mock_rec.reject.assert_called_once()

    async def test_reject_recommendation_not_found(self, service, mock_repository):
        """Reject fails when recommendation not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await service.reject_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId(value="eng-1"),
            reason_code="NOT_RELEVANT",
            reason_description="Description",
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()


@pytest.mark.asyncio
class TestProvideFeedback:
    """Test RecommendationService.provide_feedback()."""

    async def test_provide_feedback_success(self, service, mock_repository):
        """Feedback is recorded successfully."""
        mock_rec = MagicMock(spec=AIRecommendation)
        mock_rec.version = 1
        mock_repository.get_by_id.return_value = Ok(mock_rec)
        mock_repository.save.return_value = Ok(mock_rec)

        result = await service.provide_feedback(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId(value="eng-1"),
            feedback="This recommendation helped identify the issue.",
        )

        assert result.is_ok()
        mock_rec.provide_feedback.assert_called_once()


@pytest.mark.asyncio
class TestGetHighConfidenceRecommendations:
    """Test RecommendationService.get_high_confidence_recommendations()."""

    async def test_get_high_confidence_returns_recommendations(self, service, mock_repository):
        """High confidence recommendations are returned."""
        mock_rec = MagicMock(spec=AIRecommendation)
        mock_repository.get_high_confidence.return_value = Ok([mock_rec])

        result = await service.get_high_confidence_recommendations(
            tenant_id=TenantId(value="tenant-1"),
            min_confidence=0.7,
        )

        assert result.is_ok()
        recs = result.unwrap()
        assert len(recs) == 1
        mock_repository.get_high_confidence.assert_called_once()
