"""Domain service for AI Recommendation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.shared import (
    DeviceId,
    EngineerId,
    IncidentId,
    RecommendationId,
    Result,
    TenantId,
)

from ..entities import AIRecommendation
from ..repositories.recommendation_repository import RecommendationRepository
from ..value_objects import (
    AcceptanceNote,
    RecommendationCategory,
    RecommendationConfidence as RecConfidence,
    RecommendationStatus,
    RecommendationUrgency,
    RejectionReason,
)

if TYPE_CHECKING:
    pass


class RecommendationService:
    """Domain service for AIRecommendation operations."""

    def __init__(self, repository: RecommendationRepository) -> None:
        self._repository = repository

    async def create_recommendation(
        self,
        tenant_id: TenantId,
        device_id: DeviceId,
        title: str,
        description: str,
        rationale: str,
        category: RecommendationCategory,
        confidence: RecConfidence,
        model_version: str,
        incident_id: IncidentId | None = None,
        urgency: RecommendationUrgency | None = None,
    ) -> Result[AIRecommendation, str]:
        """Create a new AI recommendation."""
        recommendation = AIRecommendation(
            id=RecommendationId.generate(),
            tenant_id=tenant_id,
            incident_id=incident_id,
            device_id=device_id,
            title=title,
            description=description,
            rationale=rationale,
            category=category,
            confidence=confidence,
            model_version=model_version,
            urgency=urgency or RecommendationUrgency.scheduled(),
        )

        return await self._repository.save(recommendation)

    async def accept_recommendation(
        self,
        recommendation_id: RecommendationId,
        engineer_id: EngineerId,
        note: str | None = None,
        modifications: str | None = None,
    ) -> Result[AIRecommendation, str]:
        """Accept a recommendation."""
        result = await self._repository.get_by_id(recommendation_id)
        if result.is_err():
            return result

        recommendation = result.unwrap()
        if recommendation is None:
            return Result.Err(f"Recommendation {recommendation_id} not found")

        acceptance_note = None
        if note:
            acceptance_note = AcceptanceNote(content=note)

        try:
            recommendation.accept(
                engineer_id=engineer_id,
                note=acceptance_note,
                modifications=modifications,
                expected_version=recommendation.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(recommendation)

    async def reject_recommendation(
        self,
        recommendation_id: RecommendationId,
        engineer_id: EngineerId,
        reason_code: str,
        reason_description: str,
        feedback: str | None = None,
    ) -> Result[AIRecommendation, str]:
        """Reject a recommendation."""
        result = await self._repository.get_by_id(recommendation_id)
        if result.is_err():
            return result

        recommendation = result.unwrap()
        if recommendation is None:
            return Result.Err(f"Recommendation {recommendation_id} not found")

        reason = RejectionReason(reason_code=reason_code, description=reason_description)

        try:
            recommendation.reject(
                engineer_id=engineer_id,
                reason=reason,
                feedback=feedback,
                expected_version=recommendation.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(recommendation)

    async def provide_feedback(
        self,
        recommendation_id: RecommendationId,
        engineer_id: EngineerId,
        feedback: str,
    ) -> Result[AIRecommendation, str]:
        """Provide feedback on a recommendation."""
        result = await self._repository.get_by_id(recommendation_id)
        if result.is_err():
            return result

        recommendation = result.unwrap()
        if recommendation is None:
            return Result.Err(f"Recommendation {recommendation_id} not found")

        try:
            recommendation.provide_feedback(
                engineer_id=engineer_id,
                feedback=feedback,
                expected_version=recommendation.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(recommendation)

    async def get_pending_recommendations(
        self,
        tenant_id: TenantId,
        engineer_id: EngineerId | None = None,
        limit: int = 20,
    ) -> Result[list[AIRecommendation], str]:
        """Get pending recommendations."""
        if engineer_id:
            return await self._repository.get_pending_for_engineer(engineer_id, tenant_id, limit)

        # Get all pending for tenant
        result = await self._repository.get_by_device(
            DeviceId(value="all"),  # This is a placeholder
            tenant_id,
            limit,
        )
        if result.is_err():
            return result

        recommendations = result.unwrap()
        pending = [r for r in recommendations if r.status == RecommendationStatus.pending_review()]
        return Result.Ok(pending[:limit])

    async def get_high_confidence_recommendations(
        self,
        tenant_id: TenantId,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> Result[list[AIRecommendation], str]:
        """Get high confidence recommendations."""
        return await self._repository.get_high_confidence(tenant_id, min_confidence, limit)

    async def get_recommendations_for_incident(
        self,
        incident_id: IncidentId,
        tenant_id: TenantId,
    ) -> Result[list[AIRecommendation], str]:
        """Get all recommendations for an incident."""
        return await self._repository.get_by_incident(incident_id, tenant_id)
