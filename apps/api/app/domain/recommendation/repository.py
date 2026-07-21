"""Recommendation repository interface and SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.recommendation import RecommendationModel


class RecommendationRepository(Protocol):
    """Protocol for recommendation persistence operations."""

    async def save(
        self,
        tenant_id: str,
        recommendation_id: str,
        device_id: str,
        title: str,
        description: str,
        rationale: str,
        category: str,
        confidence_score: float,
        model_version: str,
        incident_id: str | None = None,
        urgency: str = "scheduled",
        status: str = "generated",
        **kwargs: Any,
    ) -> RecommendationModel: ...

    async def get_by_id(self, recommendation_id: str, tenant_id: str) -> RecommendationModel | None: ...

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        device_id_filter: str | None = None,
        incident_id_filter: str | None = None,
        min_confidence: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[RecommendationModel], int]: ...

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 20) -> list[RecommendationModel]: ...

    async def get_pending(self, tenant_id: str, limit: int = 20) -> list[RecommendationModel]: ...

    async def update(
        self,
        recommendation: RecommendationModel,
        expected_version: int,
        **updates: Any,
    ) -> RecommendationModel | None: ...

    async def delete(self, recommendation_id: str, tenant_id: str) -> bool: ...


@dataclass
class SQLAlchemyRecommendationRepository:
    """SQLAlchemy implementation of RecommendationRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(
        self,
        tenant_id: str,
        recommendation_id: str,
        device_id: str,
        title: str,
        description: str,
        rationale: str,
        category: str,
        confidence_score: float,
        model_version: str,
        incident_id: str | None = None,
        urgency: str = "scheduled",
        status: str = "generated",
        **kwargs: Any,
    ) -> RecommendationModel:
        from app.infrastructure.models.recommendation import RecommendationModel

        model = RecommendationModel(
            id=UUID(recommendation_id),
            tenant_id=tenant_id,
            device_id=device_id,
            title=title,
            description=description,
            rationale=rationale,
            category=category,
            confidence_score=confidence_score,
            model_version=model_version,
            incident_id=incident_id,
            urgency=urgency,
            status=status,
        )
        self._db.add(model)
        await self._db.flush()
        return model

    async def get_by_id(self, recommendation_id: str, tenant_id: str) -> RecommendationModel | None:
        from app.infrastructure.models.recommendation import RecommendationModel

        result = await self._db.execute(
            select(RecommendationModel).where(
                RecommendationModel.id == UUID(recommendation_id),
                RecommendationModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        device_id_filter: str | None = None,
        incident_id_filter: str | None = None,
        min_confidence: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[RecommendationModel], int]:
        from app.infrastructure.models.recommendation import RecommendationModel

        base = select(RecommendationModel).where(RecommendationModel.tenant_id == tenant_id)

        if status_filter:
            base = base.where(RecommendationModel.status == status_filter)
        if device_id_filter:
            base = base.where(RecommendationModel.device_id == device_id_filter)
        if incident_id_filter:
            base = base.where(RecommendationModel.incident_id == incident_id_filter)
        if min_confidence is not None:
            base = base.where(RecommendationModel.confidence_score >= min_confidence)

        # Count
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        sort_col = getattr(RecommendationModel, sort_by, RecommendationModel.created_at)
        if sort_order.lower() == "desc":
            base = base.order_by(sort_col.desc())
        else:
            base = base.order_by(sort_col.asc())
        base = base.offset(offset).limit(page_size)

        result = await self._db.execute(base)
        return list(result.scalars().all()), total

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 20) -> list[RecommendationModel]:
        from app.infrastructure.models.recommendation import RecommendationModel

        result = await self._db.execute(
            select(RecommendationModel).where(
                RecommendationModel.tenant_id == tenant_id,
                RecommendationModel.device_id == device_id,
            ).order_by(RecommendationModel.confidence_score.desc(), RecommendationModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(self, tenant_id: str, limit: int = 20) -> list[RecommendationModel]:
        from app.infrastructure.models.recommendation import RecommendationModel

        result = await self._db.execute(
            select(RecommendationModel).where(
                RecommendationModel.tenant_id == tenant_id,
                RecommendationModel.status == "pending",
            ).order_by(RecommendationModel.urgency.desc(), RecommendationModel.confidence_score.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        recommendation: RecommendationModel,
        expected_version: int,
        **updates: Any,
    ) -> RecommendationModel | None:
        if hasattr(recommendation, 'version') and recommendation.version != expected_version:
            return None

        for field_name, value in updates.items():
            if hasattr(recommendation, field_name) and value is not None:
                setattr(recommendation, field_name, value)

        if hasattr(recommendation, 'version'):
            recommendation.version = expected_version + 1
        await self._db.flush()
        return recommendation

    async def delete(self, recommendation_id: str, tenant_id: str) -> bool:
        model = await self.get_by_id(recommendation_id, tenant_id)
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.flush()
        return True


# Alias for compatibility with EPIC 10 imports
RecommendationRepositoryImpl = SQLAlchemyRecommendationRepository
