"""
Recommendation Domain Tools.

Tools for accessing recommendation data from the domain.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext

if TYPE_CHECKING:
    from core.PHASE_2.ai.domain import RecommendationGateway


class GetRecommendationHistoryTool(BaseDomainTool):
    """
    Tool for getting recommendation history.
    
    Usage:
        get_recommendation_history(device_id="dev-001")
    """
    
    config = DomainToolConfig(
        name="get_recommendation_history",
        description="Get history of recommendations for a specific device.",
        category="domain.recommendation",
        parameters_schema={
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID to get recommendations for",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                },
            },
        },
    )
    
    def __init__(self, recommendation_gateway: RecommendationGateway):
        self._gateway = recommendation_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get recommendation history."""
        try:
            device_id = parameters.get("device_id")
            if not device_id:
                return self._format_error("device_id is required")
            
            recommendations = await self._gateway.get_by_device(
                device_id,
                context.tenant_id,
            )
            
            return self._format_success([
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "confidence": r.confidence,
                    "actions": r.actions,
                }
                for r in recommendations
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class GenerateRecommendationTool(BaseDomainTool):
    """
    Tool for generating new recommendations.
    
    Usage:
        generate_recommendation(device_id="dev-001", incident_id="inc-001")
    """
    
    config = DomainToolConfig(
        name="generate_recommendation",
        description="Generate AI recommendations based on device or incident context.",
        category="domain.recommendation",
        parameters_schema={
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID for context",
                },
                "incident_id": {
                    "type": "string",
                    "description": "Incident ID for context",
                },
            },
        },
    )
    
    def __init__(self, recommendation_gateway: RecommendationGateway):
        self._gateway = recommendation_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Generate recommendations."""
        try:
            device_id = parameters.get("device_id")
            incident_id = parameters.get("incident_id")
            
            if not device_id and not incident_id:
                return self._format_error("Either device_id or incident_id is required")
            
            recommendations = await self._gateway.generate(
                device_id=device_id,
                incident_id=incident_id,
                tenant_id=context.tenant_id,
            )
            
            return self._format_success([
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "confidence": r.confidence,
                    "actions": r.actions,
                }
                for r in recommendations
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class GetPendingRecommendationsTool(BaseDomainTool):
    """
    Tool for getting pending recommendations.
    
    Usage:
        get_pending_recommendations(engineer_id="eng-001")
    """
    
    config = DomainToolConfig(
        name="get_pending_recommendations",
        description="Get pending recommendations for review, optionally filtered by engineer.",
        category="domain.recommendation",
        parameters_schema={
            "type": "object",
            "properties": {
                "engineer_id": {
                    "type": "string",
                    "description": "Engineer ID to filter by",
                },
                "min_confidence": {
                    "type": "number",
                    "description": "Minimum confidence threshold (0-1)",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                },
            },
        },
    )
    
    def __init__(self, recommendation_gateway: RecommendationGateway):
        self._gateway = recommendation_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Get pending recommendations."""
        try:
            if min_confidence := parameters.get("min_confidence"):
                recommendations = await self._gateway.get_by_confidence(
                    context.tenant_id,
                    min_confidence=min_confidence,
                    limit=parameters.get("limit", 20),
                )
            else:
                recommendations = await self._gateway.get_pending(
                    context.tenant_id,
                    engineer_id=parameters.get("engineer_id"),
                    limit=parameters.get("limit", 20),
                )
            
            return self._format_success([
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "confidence": r.confidence,
                    "device_id": r.device_id,
                    "incident_id": r.incident_id,
                }
                for r in recommendations
            ])
            
        except Exception as e:
            return self._format_error(str(e))
