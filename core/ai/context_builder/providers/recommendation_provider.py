"""
Recommendation Context Provider.

Provides recommendation context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.ai.domain import RecommendationGateway


class RecommendationContextProvider(BaseContextProvider):
    """
    Provides recommendation context for the AI.
    
    Retrieves pending recommendations and high-confidence suggestions.
    """
    
    def __init__(
        self,
        recommendation_gateway: RecommendationGateway | None = None,
    ):
        self._recommendation = recommendation_gateway
    
    @property
    def name(self) -> str:
        return "recommendation"
    
    @property
    def priority(self) -> int:
        return 65  # Low priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get recommendation context."""
        items = []
        
        # Get high confidence recommendations
        recommendations = await self._get_high_confidence_safe(query.tenant_id)
        if recommendations:
            items.append(self._create_recommendations_context(recommendations))
        
        return items
    
    async def _get_high_confidence_safe(self, tenant_id: str) -> list[dict]:
        """Safely get recommendations."""
        if self._recommendation is None:
            return self._mock_get_high_confidence()
        try:
            results = await self._recommendation.get_by_confidence(tenant_id, min_confidence=0.7, limit=5)
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "confidence": r.confidence,
                    "priority": r.priority,
                }
                for r in results
            ]
        except Exception:
            return []
    
    def _create_recommendations_context(self, recommendations: list[dict]) -> ContextItem:
        """Create recommendations context."""
        lines = ["Active Recommendations:"]
        for rec in recommendations:
            lines.append(f"- [{rec['priority'].upper()}] {rec['title']} (confidence: {rec['confidence']:.0%})")
            lines.append(f"  {rec['description'][:100]}")
        
        return self._create_item(
            content="\n".join(lines),
            relevance_score=0.6,
            metadata={"type": "recommendations", "count": len(recommendations)},
        )
    
    def _mock_get_high_confidence(self) -> list[dict]:
        """Mock recommendations for testing."""
        return [
            {
                "id": "rec-001",
                "title": "Replace air filters in Ventilator",
                "description": "Filters at 95% capacity, replace within 7 days",
                "confidence": 0.92,
                "priority": "high",
            },
        ]
