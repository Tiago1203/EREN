"""
Recommendation Gateway.

Gateway implementation for Recommendation domain.
Provides AI Core with access to AI recommendations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .contracts import RecommendationDTO, IRecommendationGateway
from .exceptions import RecommendationNotFoundError

if TYPE_CHECKING:
    from core.recommendation.domain.repositories import RecommendationRepository


class RecommendationGateway(IRecommendationGateway):
    """
    Gateway for Recommendation domain.
    
    AI Core uses this gateway to access recommendations.
    """
    
    def __init__(
        self,
        repository: RecommendationRepository | None = None,
    ):
        self._repository = repository
    
    @property
    def name(self) -> str:
        return "recommendation"
    
    async def get_by_id(
        self,
        recommendation_id: str,
        tenant_id: str,
    ) -> RecommendationDTO | None:
        """Get recommendation by ID."""
        if self._repository is None:
            return self._mock_get_by_id(recommendation_id)
        
        from core.shared import RecommendationId
        result = await self._repository.get_by_id(
            RecommendationId(recommendation_id),
        )
        
        if result.is_ok() and result.value:
            return self._entity_to_dto(result.value)
        return None
    
    async def get_pending(
        self,
        tenant_id: str,
        engineer_id: str | None = None,
        limit: int = 20,
    ) -> list[RecommendationDTO]:
        """Get pending recommendations."""
        if self._repository is None:
            return self._mock_get_pending(engineer_id, limit)
        
        from core.shared import EngineerId, TenantId
        
        if engineer_id:
            result = await self._repository.get_pending_for_engineer(
                EngineerId(engineer_id),
                TenantId(tenant_id),
                limit,
            )
        else:
            result = await self._repository.get_pending_for_engineer(
                EngineerId(""),  # Get all
                TenantId(tenant_id),
                limit,
            )
        
        if result.is_ok():
            return [self._entity_to_dto(r) for r in result.value]
        return []
    
    async def get_by_confidence(
        self,
        tenant_id: str,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> list[RecommendationDTO]:
        """Get high confidence recommendations."""
        if self._repository is None:
            return self._mock_get_by_confidence(min_confidence, limit)
        
        from core.shared import TenantId
        result = await self._repository.get_high_confidence(
            TenantId(tenant_id),
            min_confidence,
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(r) for r in result.value]
        return []
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[RecommendationDTO]:
        """Get recommendations for a device."""
        if self._repository is None:
            return self._mock_get_by_device(device_id)
        
        from core.shared import DeviceId, TenantId
        result = await self._repository.get_by_device(
            DeviceId(device_id),
            TenantId(tenant_id),
        )
        
        if result.is_ok():
            return [self._entity_to_dto(r) for r in result.value]
        return []
    
    async def generate(
        self,
        device_id: str | None,
        incident_id: str | None,
        tenant_id: str,
    ) -> list[RecommendationDTO]:
        """Generate new recommendations."""
        # Mock implementation - in production would call recommendation service
        recommendations = []
        
        if device_id:
            recommendations.append(RecommendationDTO(
                id=f"rec-{device_id}-001",
                title=f"Maintenance due for device {device_id}",
                description="Recommended preventive maintenance based on usage patterns",
                priority="high",
                confidence=0.85,
                device_id=device_id,
                actions=["Schedule maintenance", "Replace filters"],
            ))
        
        if incident_id:
            recommendations.append(RecommendationDTO(
                id=f"rec-{incident_id}-001",
                title=f"Investigation needed for incident {incident_id}",
                description="Root cause analysis recommended",
                priority="medium",
                confidence=0.75,
                incident_id=incident_id,
                actions=["Conduct RCA", "Update documentation"],
            ))
        
        return recommendations
    
    def _entity_to_dto(self, entity: Any) -> RecommendationDTO:
        """Convert Recommendation entity to RecommendationDTO."""
        return RecommendationDTO(
            id=str(entity.id),
            title=entity.title,
            description=entity.description,
            priority=str(entity.priority),
            confidence=entity.confidence,
            device_id=str(entity.device_id) if entity.device_id else None,
            incident_id=str(entity.incident_id) if entity.incident_id else None,
            actions=list(entity.actions) if entity.actions else [],
            created_at=entity.created_at,
        )
    
    # =============================================================================
    # Mock implementations
    # =============================================================================
    
    def _mock_get_by_id(self, recommendation_id: str) -> RecommendationDTO | None:
        """Mock implementation."""
        mock_recs = {
            "rec-001": RecommendationDTO(
                id="rec-001",
                title="Replace air filters in Ventilator",
                description="Filters are at 95% capacity, replace within 7 days",
                priority="high",
                confidence=0.92,
                device_id="dev-001",
                actions=["Order filters", "Schedule replacement"],
            ),
        }
        return mock_recs.get(recommendation_id)
    
    def _mock_get_pending(self, engineer_id: str | None, limit: int) -> list[RecommendationDTO]:
        """Mock get pending."""
        all_recs = [
            RecommendationDTO(
                id="rec-001",
                title="Replace air filters in Ventilator",
                description="Filters at 95% capacity",
                priority="high",
                confidence=0.92,
                device_id="dev-001",
            ),
            RecommendationDTO(
                id="rec-002",
                title="Calibrate infusion pump",
                description="Calibration due in 5 days",
                priority="medium",
                confidence=0.78,
                device_id="dev-002",
            ),
        ]
        return all_recs[:limit]
    
    def _mock_get_by_confidence(self, min_confidence: float, limit: int) -> list[RecommendationDTO]:
        """Mock get by confidence."""
        return [r for r in self._mock_get_pending(None, 100) if r.confidence >= min_confidence][:limit]
    
    def _mock_get_by_device(self, device_id: str) -> list[RecommendationDTO]:
        """Mock get by device."""
        return [r for r in self._mock_get_pending(None, 100) if r.device_id == device_id]
