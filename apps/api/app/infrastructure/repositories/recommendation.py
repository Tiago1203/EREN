"""SQLAlchemy implementation of RecommendationRepository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.recommendation.domain.entities import AIRecommendation
from core.recommendation.domain.repositories import (
    RecommendationRepository as AbstractRecommendationRepository,
)
from core.recommendation.domain.value_objects import (
    AcceptanceNote,
    RecommendationCategory,
    RecommendationConfidence,
    RecommendationStatus,
    RecommendationUrgency,
    RejectionReason,
)
from core.shared import (
    DeviceId,
    EngineerId,
    IncidentId,
    Ok,
    Result,
    TenantId,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.recommendation import RecommendationModel

if TYPE_CHECKING:
    pass


def _model_to_entity(model: RecommendationModel) -> AIRecommendation:
    """Convert SQLAlchemy model to domain entity."""
    rec = AIRecommendation.__new__(AIRecommendation)
    rec.id = model.id
    rec.tenant_id = TenantId(value=model.tenant_id)
    rec.incident_id = IncidentId(value=model.incident_id) if model.incident_id else None
    rec.device_id = DeviceId(value=model.device_id)
    rec.title = model.title
    rec.description = model.description
    rec.rationale = model.rationale
    rec.category = RecommendationCategory(value=model.category)
    rec.confidence = RecommendationConfidence(score=model.confidence_score)
    rec.model_version = model.model_version
    rec.urgency = RecommendationUrgency(value=model.urgency)
    rec.status = RecommendationStatus(value=model.status)
    rec.rejection_reason = (
        RejectionReason(value=model.rejection_reason)
        if model.rejection_reason
        else None
    )
    rec.acceptance_note = (
        AcceptanceNote(value=model.acceptance_note)
        if model.acceptance_note
        else None
    )
    rec.engineer_feedback = model.engineer_feedback
    rec.expires_at = model.expires_at
    rec.reviewed_at = model.reviewed_at
    rec.reviewed_by = (
        EngineerId(value=model.reviewed_by) if model.reviewed_by else None
    )
    rec.superseded_by = model.superseded_by
    rec.supersedes = list(model.supersedes) if model.supersedes else []
    rec.version = model.version
    rec.created_at = model.created_at
    rec.updated_at = model.updated_at
    rec._pending_events = []
    rec._locked = True
    return rec


def _entity_to_model(entity: AIRecommendation) -> dict[str, Any]:
    return {
        "tenant_id": str(entity.tenant_id),
        "incident_id": str(entity.incident_id) if entity.incident_id else None,
        "device_id": str(entity.device_id),
        "title": entity.title,
        "description": entity.description,
        "rationale": entity.rationale,
        "category": str(entity.category),
        "confidence_score": entity.confidence.score,
        "model_version": entity.model_version,
        "urgency": str(entity.urgency),
        "status": str(entity.status),
        "rejection_reason": str(entity.rejection_reason) if entity.rejection_reason else None,
        "acceptance_note": str(entity.acceptance_note) if entity.acceptance_note else None,
        "engineer_feedback": entity.engineer_feedback,
        "expires_at": entity.expires_at,
        "reviewed_at": entity.reviewed_at,
        "reviewed_by": str(entity.reviewed_by) if entity.reviewed_by else None,
        "superseded_by": str(entity.superseded_by) if entity.superseded_by else None,
        "supersedes": [str(r) for r in entity.supersedes],
        "version": entity.version,
    }


class RecommendationRepositoryImpl(AbstractRecommendationRepository):
    """SQLAlchemy implementation of RecommendationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, recommendation: AIRecommendation) -> Result[AIRecommendation, str]:
        try:
            existing = await self._session.get(RecommendationModel, recommendation.id)
            data = _entity_to_model(recommendation)
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.version = recommendation.version
            else:
                model = RecommendationModel(id=recommendation.id, **data)
                self._session.add(model)
            await self._session.flush()
            return Ok(recommendation)
        except Exception as e:
            return Ok(str(e))

    async def get_by_id(
        self, recommendation_id: Any
    ) -> Result[AIRecommendation | None, str]:
        try:
            model = await self._session.get(RecommendationModel, recommendation_id)
            return Ok(_model_to_entity(model) if model else None)
        except Exception:
            return Ok(None)

    async def get_by_incident(
        self, incident_id: IncidentId, tenant_id: TenantId
    ) -> Result[list[AIRecommendation], str]:
        try:
            stmt = select(RecommendationModel).where(
                RecommendationModel.incident_id == str(incident_id),
                RecommendationModel.tenant_id == str(tenant_id),
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_device(
        self, device_id: DeviceId, tenant_id: TenantId, limit: int = 50
    ) -> Result[list[AIRecommendation], str]:
        try:
            stmt = (
                select(RecommendationModel)
                .where(RecommendationModel.device_id == str(device_id))
                .where(RecommendationModel.tenant_id == str(tenant_id))
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_pending_for_engineer(
        self, engineer_id: EngineerId, tenant_id: TenantId, limit: int = 20
    ) -> Result[list[AIRecommendation], str]:
        try:
            stmt = (
                select(RecommendationModel)
                .where(RecommendationModel.tenant_id == str(tenant_id))
                .where(RecommendationModel.status == "pending_review")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_high_confidence(
        self, tenant_id: TenantId, min_confidence: float = 0.7, limit: int = 20
    ) -> Result[list[AIRecommendation], str]:
        try:
            stmt = (
                select(RecommendationModel)
                .where(RecommendationModel.tenant_id == str(tenant_id))
                .where(RecommendationModel.confidence_score >= min_confidence)
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_accepted(
        self, tenant_id: TenantId, limit: int = 100
    ) -> Result[list[AIRecommendation], str]:
        try:
            stmt = (
                select(RecommendationModel)
                .where(RecommendationModel.tenant_id == str(tenant_id))
                .where(RecommendationModel.status == "accepted")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def delete(self, recommendation_id: Any) -> Result[bool, str]:
        try:
            model = await self._session.get(RecommendationModel, recommendation_id)
            if model:
                await self._session.delete(model)
                await self._session.flush()
            return Ok(True)
        except Exception:
            return Ok(False)
