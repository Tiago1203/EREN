"""Unit tests for RecommendationService."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.PHASE_3.recommendation.domain.services.recommendation_service import RecommendationService
from core.PHASE_3.recommendation.domain.entities.recommendation import AIRecommendation
from core.PHASE_3.recommendation.domain.value_objects import (
    RecommendationCategory,
    RecommendationConfidence,
    RecommendationStatus,
    RecommendationUrgency,
    RejectionReason,
)
from core.PHASE_3.recommendation.domain.repositories.recommendation_repository import RecommendationRepository
from core.PHASE_1.infrastructure.shared import (
    DeviceId,
    EngineerId,
    IncidentId,
    Ok,
    Err,
    RecommendationId,
    TenantId,
)


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock repository."""
    repo = MagicMock(spec=RecommendationRepository)
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_incident = AsyncMock()
    repo.get_by_device = AsyncMock()
    return repo


@pytest.fixture
def recommendation_service(mock_repository: MagicMock) -> RecommendationService:
    """Create a RecommendationService with mock repository."""
    return RecommendationService(mock_repository)


@pytest.fixture
def sample_recommendation() -> AIRecommendation:
    """Create a sample AIRecommendation."""
    return AIRecommendation(
        id=RecommendationId.generate(),
        tenant_id=TenantId.generate(),
        incident_id=IncidentId.generate(),
        device_id=DeviceId.generate(),
        title="Replace filter",
        description="Replace the HEPA filter on Unit 3",
        rationale="Filter lifespan exceeded 90 days",
        category=RecommendationCategory(value="preventive_maintenance"),
        confidence=RecommendationConfidence(score=0.85, evidence_count=5, model_version="v1.0"),
        model_version="v1.0",
        urgency=RecommendationUrgency.scheduled(),
        status=RecommendationStatus.generated(),
    )


class TestCreateRecommendation:
    """Tests for RecommendationService.create_recommendation."""

    @pytest.mark.asyncio
    async def test_create_recommendation_success(
        self,
        recommendation_service: RecommendationService,
        mock_repository: MagicMock,
        sample_recommendation: AIRecommendation,
    ) -> None:
        """Should return Ok(recommendation) when created successfully."""
        mock_repository.save.return_value = Ok(sample_recommendation)

        result = await recommendation_service.create_recommendation(
            tenant_id=sample_recommendation.tenant_id,
            device_id=sample_recommendation.device_id,
            title="Replace filter",
            description="Replace the HEPA filter on Unit 3",
            rationale="Filter lifespan exceeded 90 days",
            category=RecommendationCategory(value="preventive_maintenance"),
            confidence=RecommendationConfidence(score=0.85, evidence_count=5, model_version="v1.0"),
            model_version="v1.0",
        )

        assert result.is_ok()
        assert result.unwrap() == sample_recommendation
        mock_repository.save.assert_called_once()


class TestAcceptRecommendation:
    """Tests for RecommendationService.accept_recommendation."""

    @pytest.mark.asyncio
    async def test_accept_recommendation_success(
        self,
        recommendation_service: RecommendationService,
        mock_repository: MagicMock,
        sample_recommendation: AIRecommendation,
    ) -> None:
        """Should return Ok(accepted_recommendation) when accepted."""
        mock_repository.get_by_id.return_value = Ok(sample_recommendation)
        mock_repository.save.return_value = Ok(sample_recommendation)

        result = await recommendation_service.accept_recommendation(
            recommendation_id=sample_recommendation.id,
            engineer_id=EngineerId.generate(),
            note="Accepted and scheduled",
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_recommendation_not_found(
        self,
        recommendation_service: RecommendationService,
        mock_repository: MagicMock,
    ) -> None:
        """Should return Err when recommendation is not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await recommendation_service.accept_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId.generate(),
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()


class TestRejectRecommendation:
    """Tests for RecommendationService.reject_recommendation."""

    @pytest.mark.asyncio
    async def test_reject_recommendation_success(
        self,
        recommendation_service: RecommendationService,
        mock_repository: MagicMock,
        sample_recommendation: AIRecommendation,
    ) -> None:
        """Should return Ok(rejected_recommendation) when rejected."""
        mock_repository.get_by_id.return_value = Ok(sample_recommendation)
        mock_repository.save.return_value = Ok(sample_recommendation)

        result = await recommendation_service.reject_recommendation(
            recommendation_id=sample_recommendation.id,
            engineer_id=EngineerId.generate(),
            reason_code="not_applicable",
            reason_description="This recommendation does not apply to our device model",
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_recommendation_not_found(
        self,
        recommendation_service: RecommendationService,
        mock_repository: MagicMock,
    ) -> None:
        """Should return Err when recommendation is not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await recommendation_service.reject_recommendation(
            recommendation_id=RecommendationId.generate(),
            engineer_id=EngineerId.generate(),
            reason_code="not_applicable",
            reason_description="Not applicable",
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()
