"""Domain service for Knowledge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.shared import EngineerId, KnowledgeId, Result, TenantId

from ..entities import KnowledgeArticle
from ..repositories.knowledge_repository import KnowledgeRepository
from ..value_objects import (
    ArticleContent,
    KnowledgeCategory,
    KnowledgeReference,
    KnowledgeStatus,
)

if TYPE_CHECKING:
    pass


class KnowledgeService:
    """Domain service for Knowledge operations."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self._repository = repository

    async def create_article(
        self,
        tenant_id: TenantId,
        article_id: str,
        title: str,
        summary: str,
        body: str,
        category: str,
        author_id: EngineerId,
        author_name: str,
        tags: list[str] | None = None,
        device_ids: list[str] | None = None,
    ) -> Result[KnowledgeArticle, str]:
        """Create a new knowledge article."""
        # Check for duplicate article ID
        existing = await self._repository.get_by_article_id(article_id)
        if existing.is_ok() and existing.unwrap() is not None:
            return Result.Err(f"Article with ID {article_id} already exists")

        # Create content
        content = ArticleContent(
            title=title,
            summary=summary,
            body=body,
            tags=tuple(tags) if tags else (),
        )

        # Create category
        category_vo = KnowledgeCategory(value=category)

        # Create article
        article = KnowledgeArticle(
            id=KnowledgeId.generate(),
            tenant_id=tenant_id,
            article_id=article_id,
            content=content,
            category=category_vo,
            author_id=author_id,
            author_name=author_name,
            device_ids=tuple(device_ids) if device_ids else (),
        )

        return await self._repository.save(article)

    async def publish_article(
        self,
        article_id: KnowledgeId,
        published_by: EngineerId,
    ) -> Result[KnowledgeArticle, str]:
        """Submit and publish an article."""
        result = await self._repository.get_by_id(article_id)
        if result.is_err():
            return result

        article = result.unwrap()
        if article is None:
            return Result.Err(f"Article {article_id} not found")

        try:
            # Submit for review then approve
            article.submit_for_review(expected_version=article.version)
            article.approve(
                reviewed_by=published_by,
                expected_version=article.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(article)

    async def archive_article(
        self,
        article_id: KnowledgeId,
        reason: str | None = None,
    ) -> Result[KnowledgeArticle, str]:
        """Archive an article."""
        result = await self._repository.get_by_id(article_id)
        if result.is_err():
            return result

        article = result.unwrap()
        if article is None:
            return Result.Err(f"Article {article_id} not found")

        try:
            article.archive(reason=reason, expected_version=article.version)
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(article)

    async def search_knowledge_base(
        self,
        tenant_id: TenantId,
        keywords: list[str],
        category: str | None = None,
    ) -> Result[list[KnowledgeArticle], str]:
        """Search the knowledge base."""
        result = await self._repository.search_by_keywords(tenant_id, keywords)
        if result.is_err():
            return result

        articles = result.unwrap()

        # Filter by category if specified
        if category:
            articles = [a for a in articles if str(a.category) == category]

        return Result.Ok(articles)

    async def get_device_knowledge(
        self,
        tenant_id: TenantId,
        device_id: str,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get all knowledge related to a device."""
        return await self._repository.get_by_device(tenant_id, device_id)

    async def get_popular_troubleshooting(
        self,
        tenant_id: TenantId,
        limit: int = 10,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get popular troubleshooting articles."""
        result = await self._repository.get_by_category(
            tenant_id, "troubleshooting", limit
        )
        if result.is_err():
            return result

        articles = result.unwrap()
        # Sort by view count
        articles.sort(key=lambda a: a.statistics.view_count, reverse=True)
        return Result.Ok(articles[:limit])

    async def link_article_to_device(
        self,
        article_id: KnowledgeId,
        device_id: str,
    ) -> Result[KnowledgeArticle, str]:
        """Link an article to a device."""
        result = await self._repository.get_by_id(article_id)
        if result.is_err():
            return result

        article = result.unwrap()
        if article is None:
            return Result.Err(f"Article {article_id} not found")

        try:
            article.add_device_link(device_id, expected_version=article.version)
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(article)

    async def add_cross_reference(
        self,
        source_article_id: KnowledgeId,
        target_article_id: str,
        description: str | None = None,
    ) -> Result[KnowledgeArticle, str]:
        """Add a reference from one article to another."""
        result = await self._repository.get_by_id(source_article_id)
        if result.is_err():
            return result

        article = result.unwrap()
        if article is None:
            return Result.Err(f"Article {source_article_id} not found")

        reference = KnowledgeReference.internal(target_article_id, description)

        try:
            article.add_reference(reference, expected_version=article.version)
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(article)
