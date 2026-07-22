"""SQLAlchemy implementation of KnowledgeRepository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.PHASE_1.domain.knowledge.domain.entities import KnowledgeArticle
from core.PHASE_1.domain.knowledge.domain.repositories import (
    KnowledgeRepository as AbstractKnowledgeRepository,
)
from core.PHASE_1.domain.knowledge.domain.value_objects import (
    ArticleContent,
    KnowledgeCategory,
    KnowledgeStatus,
    UsageStatistics,
)
from core.PHASE_1.infrastructure.shared import EngineerId, KnowledgeId, Ok, Result, TenantId
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.knowledge import KnowledgeArticleModel

if TYPE_CHECKING:
    pass


def _model_to_entity(model: KnowledgeArticleModel) -> KnowledgeArticle:
    """Convert SQLAlchemy model to domain entity."""
    content = ArticleContent(
        title=model.title,
        summary=model.summary or "",
        body=model.body,
        tags=tuple(model.tags) if model.tags else (),
    )

    article = KnowledgeArticle.__new__(KnowledgeArticle)
    article.id = model.id
    article.tenant_id = TenantId(value=model.tenant_id)
    article.article_id = model.article_id
    article.content = content
    article.category = KnowledgeCategory(value=model.category)
    article.author_id = EngineerId(value=model.author_id)
    article.author_name = model.author_name
    article.status = KnowledgeStatus(value=model.status)
    article.device_ids = ()
    article.incident_type_tags = ()
    article.references = ()
    article.related_articles = tuple(m for m in (model.to_dict().get("related_articles") or []))
    article.published_at = model.published_at
    article.review_info = None
    article.statistics = UsageStatistics(
        view_count=model.view_count,
        helpful_count=model.helpful_count,
        not_helpful_count=model.not_helpful_count,
        last_accessed=model.last_accessed,
    )
    article.version = model.version
    article.created_at = model.created_at
    article.updated_at = model.updated_at
    article._pending_events = []
    article._locked = True
    return article


def _entity_to_model(entity: KnowledgeArticle) -> dict[str, Any]:
    return {
        "tenant_id": str(entity.tenant_id),
        "article_id": entity.article_id,
        "title": entity.content.title,
        "summary": entity.content.summary,
        "body": entity.content.body,
        "tags": list(entity.content.tags),
        "category": str(entity.category),
        "status": str(entity.status),
        "author_id": str(entity.author_id),
        "author_name": entity.author_name,
        "published_at": entity.published_at,
        "view_count": entity.statistics.view_count,
        "helpful_count": entity.statistics.helpful_count,
        "not_helpful_count": entity.statistics.not_helpful_count,
        "last_accessed": entity.statistics.last_accessed,
        "version": entity.version,
    }


class KnowledgeRepositoryImpl(AbstractKnowledgeRepository):
    """SQLAlchemy implementation of KnowledgeRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, article: KnowledgeArticle) -> Result[KnowledgeArticle, str]:
        try:
            existing = await self._session.get(KnowledgeArticleModel, article.id)
            data = _entity_to_model(article)
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.version = article.version
            else:
                model = KnowledgeArticleModel(id=article.id, **data)
                self._session.add(model)
            await self._session.flush()
            return Ok(article)
        except Exception as e:
            return Ok(str(e))

    async def get_by_id(self, article_id: KnowledgeId) -> Result[KnowledgeArticle | None, str]:
        try:
            model = await self._session.get(KnowledgeArticleModel, article_id)
            return Ok(_model_to_entity(model) if model else None)
        except Exception:
            return Ok(None)

    async def get_by_article_id(self, article_id: str) -> Result[KnowledgeArticle | None, str]:
        try:
            stmt = select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.article_id == article_id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return Ok(_model_to_entity(model) if model else None)
        except Exception:
            return Ok(None)

    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .limit(limit)
                .offset(offset)
                .order_by(KnowledgeArticleModel.created_at.desc())
            )
            if status:
                stmt = stmt.where(KnowledgeArticleModel.status == status)
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_category(
        self, tenant_id: TenantId, category: str, limit: int = 50
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .where(KnowledgeArticleModel.category == category)
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_active_articles(
        self, tenant_id: TenantId, limit: int = 50
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .where(KnowledgeArticleModel.status == "published")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def search_by_keywords(
        self, tenant_id: TenantId, keywords: list[str], limit: int = 20
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .where(KnowledgeArticleModel.status == "published")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_device(
        self, tenant_id: TenantId, device_id: str
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.tenant_id == str(tenant_id),
                KnowledgeArticleModel.status == "published",
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_by_tag(
        self, tenant_id: TenantId, tag: str, limit: int = 50
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .where(KnowledgeArticleModel.status == "published")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_popular_articles(
        self, tenant_id: TenantId, limit: int = 10
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.tenant_id == str(tenant_id))
                .where(KnowledgeArticleModel.status == "published")
                .order_by(KnowledgeArticleModel.view_count.desc())
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_related_articles(
        self, article_id: str, limit: int = 5
    ) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = (
                select(KnowledgeArticleModel)
                .where(KnowledgeArticleModel.article_id != article_id)
                .where(KnowledgeArticleModel.status == "published")
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def get_needing_review(self, tenant_id: TenantId) -> Result[list[KnowledgeArticle], str]:
        try:
            stmt = select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.tenant_id == str(tenant_id),
                KnowledgeArticleModel.status == "review",
            )
            result = await self._session.execute(stmt)
            return Ok([_model_to_entity(m) for m in result.scalars().all()])
        except Exception:
            return Ok([])

    async def delete(self, article_id: KnowledgeId) -> Result[bool, str]:
        try:
            model = await self._session.get(KnowledgeArticleModel, article_id)
            if model:
                await self._session.delete(model)
                await self._session.flush()
            return Ok(True)
        except Exception:
            return Ok(False)
