"""Repository interface for AI Recommendation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import DeviceId, EngineerId, IncidentId, RecommendationId, Result, TenantId

from ..entities import AIRecommendation

if TYPE_CHECKING:
    pass


class RecommendationRepository(ABC):
    """Repository interface for AIRecommendation aggregate."""

    @abstractmethod
    async def save(self, recommendation: AIRecommendation) -> Result[AIRecommendation, str]:
        """Save a recommendation."""

    @abstractmethod
    async def get_by_id(self, recommendation_id: RecommendationId) -> Result[AIRecommendation | None, str]:
        """Get a recommendation by ID."""

    @abstractmethod
    async def get_by_incident(
        self,
        incident_id: IncidentId,
        tenant_id: TenantId,
    ) -> Result[list[AIRecommendation], str]:
        """Get all recommendations for an incident."""

    @abstractmethod
    async def get_by_device(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        limit: int = 50,
    ) -> Result[list[AIRecommendation], str]:
        """Get all recommendations for a device."""

    @abstractmethod
    async def get_pending_for_engineer(
        self,
        engineer_id: EngineerId,
        tenant_id: TenantId,
        limit: int = 20,
    ) -> Result[list[AIRecommendation], str]:
        """Get pending recommendations for an engineer to review."""

    @abstractmethod
    async def get_high_confidence(
        self,
        tenant_id: TenantId,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> Result[list[AIRecommendation], str]:
        """Get high confidence recommendations."""

    @abstractmethod
    async def get_accepted(
        self,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[AIRecommendation], str]:
        """Get accepted recommendations."""

    @abstractmethod
    async def delete(self, recommendation_id: RecommendationId) -> Result[bool, str]:
        """Delete a recommendation (soft delete)."""
