"""Knowledge repository interface and SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.knowledge import KnowledgeArticleModel


class KnowledgeRepository(Protocol):
    """Protocol for knowledge article persistence operations."""

    async def save(
        self,
        tenant_id: str,
        article_id: str,
        title: str,
        body: str,
        category: str,
        author_id: str,
        author_name: str,
        summary: str | None = None,
        tags: list[str] | None = None,
        status: str = "draft",
        **kwargs: Any,
    ) -> KnowledgeArticleModel: ...

    async def get_by_id(self, article_id: str, tenant_id: str) -> KnowledgeArticleModel | None: ...

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        category_filter: str | None = None,
        status_filter: str | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[KnowledgeArticleModel], int]: ...

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 20) -> list[KnowledgeArticleModel]: ...

    async def get_related(self, article_id: str, tenant_id: str, limit: int = 5) -> list[KnowledgeArticleModel]: ...

    async def update(
        self,
        article: KnowledgeArticleModel,
        expected_version: int,
        **updates: Any,
    ) -> KnowledgeArticleModel | None: ...

    async def delete(self, article_id: str, tenant_id: str) -> bool: ...


@dataclass
class SQLAlchemyKnowledgeRepository:
    """SQLAlchemy implementation of KnowledgeRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(
        self,
        tenant_id: str,
        article_id: str,
        title: str,
        body: str,
        category: str,
        author_id: str,
        author_name: str,
        summary: str | None = None,
        tags: list[str] | None = None,
        status: str = "draft",
        **kwargs: Any,
    ) -> KnowledgeArticleModel:
        from app.infrastructure.models.knowledge import KnowledgeArticleModel

        model = KnowledgeArticleModel(
            id=UUID(article_id),
            tenant_id=tenant_id,
            article_id=article_id,
            title=title,
            body=body,
            category=category,
            author_id=author_id,
            author_name=author_name,
            summary=summary,
            tags=tags or [],
            status=status,
        )
        self._db.add(model)
        await self._db.flush()
        return model

    async def get_by_id(self, article_id: str, tenant_id: str) -> KnowledgeArticleModel | None:
        from app.infrastructure.models.knowledge import KnowledgeArticleModel

        result = await self._db.execute(
            select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.article_id == article_id,
                KnowledgeArticleModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        category_filter: str | None = None,
        status_filter: str | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[KnowledgeArticleModel], int]:
        from app.infrastructure.models.knowledge import KnowledgeArticleModel

        base = select(KnowledgeArticleModel).where(KnowledgeArticleModel.tenant_id == tenant_id)

        if category_filter:
            base = base.where(KnowledgeArticleModel.category == category_filter)
        if status_filter:
            base = base.where(KnowledgeArticleModel.status == status_filter)
        if search_query:
            base = base.where(
                KnowledgeArticleModel.title.ilike(f"%{search_query}%") |
                KnowledgeArticleModel.body.ilike(f"%{search_query}%") |
                KnowledgeArticleModel.summary.ilike(f"%{search_query}%")
            )

        # Count
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        sort_col = getattr(KnowledgeArticleModel, sort_by, KnowledgeArticleModel.created_at)
        if sort_order.lower() == "desc":
            base = base.order_by(sort_col.desc())
        else:
            base = base.order_by(sort_col.asc())
        base = base.offset(offset).limit(page_size)

        result = await self._db.execute(base)
        return list(result.scalars().all()), total

    async def get_by_device(self, device_id: str, tenant_id: str, limit: int = 20) -> list[KnowledgeArticleModel]:
        from app.infrastructure.models.knowledge import KnowledgeArticleModel

        # Search for articles mentioning the device
        result = await self._db.execute(
            select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.tenant_id == tenant_id,
                KnowledgeArticleModel.status == "published",
                KnowledgeArticleModel.body.ilike(f"%{device_id}%"),
            ).order_by(KnowledgeArticleModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_related(self, article_id: str, tenant_id: str, limit: int = 5) -> list[KnowledgeArticleModel]:
        from app.infrastructure.models.knowledge import KnowledgeArticleModel

        # Get the source article to find related tags
        source = await self.get_by_id(article_id, tenant_id)
        if source is None:
            return []

        # Find articles with similar tags or category
        result = await self._db.execute(
            select(KnowledgeArticleModel).where(
                KnowledgeArticleModel.tenant_id == tenant_id,
                KnowledgeArticleModel.article_id != article_id,
                KnowledgeArticleModel.status == "published",
                KnowledgeArticleModel.category == source.category,
            ).order_by(KnowledgeArticleModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        article: KnowledgeArticleModel,
        expected_version: int,
        **updates: Any,
    ) -> KnowledgeArticleModel | None:
        if hasattr(article, 'version') and article.version != expected_version:
            return None

        for field_name, value in updates.items():
            if hasattr(article, field_name) and value is not None:
                setattr(article, field_name, value)

        if hasattr(article, 'version'):
            article.version = expected_version + 1
        await self._db.flush()
        return article

    async def delete(self, article_id: str, tenant_id: str) -> bool:
        model = await self.get_by_id(article_id, tenant_id)
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.flush()
        return True


# Alias for compatibility with EPIC 10 imports
KnowledgeRepositoryImpl = SQLAlchemyKnowledgeRepository
