"""Repository interface for Knowledge."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.shared import KnowledgeId, Result, TenantId

from ..entities import KnowledgeArticle

if TYPE_CHECKING:
    pass


class KnowledgeRepository(ABC):
    """Repository interface for KnowledgeArticle aggregate."""

    @abstractmethod
    async def save(self, article: KnowledgeArticle) -> Result[KnowledgeArticle, str]:
        """Save a knowledge article."""

    @abstractmethod
    async def get_by_id(self, article_id: KnowledgeId) -> Result[KnowledgeArticle | None, str]:
        """Get an article by ID."""

    @abstractmethod
    async def get_by_article_id(self, article_id: str) -> Result[KnowledgeArticle | None, str]:
        """Get an article by human-readable article ID (e.g., KB-001)."""

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get all articles for a tenant."""

    @abstractmethod
    async def get_by_category(
        self,
        tenant_id: TenantId,
        category: str,
        limit: int = 50,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get articles by category."""

    @abstractmethod
    async def get_active_articles(
        self,
        tenant_id: TenantId,
        limit: int = 50,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get all active (published) articles."""

    @abstractmethod
    async def search_by_keywords(
        self,
        tenant_id: TenantId,
        keywords: list[str],
        limit: int = 20,
    ) -> Result[list[KnowledgeArticle], str]:
        """Search articles by keywords."""

    @abstractmethod
    async def get_by_device(
        self,
        tenant_id: TenantId,
        device_id: str,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get articles related to a device."""

    @abstractmethod
    async def get_by_tag(
        self,
        tenant_id: TenantId,
        tag: str,
        limit: int = 50,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get articles by tag."""

    @abstractmethod
    async def get_popular_articles(
        self,
        tenant_id: TenantId,
        limit: int = 10,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get most viewed articles."""

    @abstractmethod
    async def get_related_articles(
        self,
        article_id: str,
        limit: int = 5,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get articles related to an article."""

    @abstractmethod
    async def get_needing_review(
        self,
        tenant_id: TenantId,
    ) -> Result[list[KnowledgeArticle], str]:
        """Get articles pending review."""

    @abstractmethod
    async def delete(self, article_id: KnowledgeId) -> Result[bool, str]:
        """Delete an article (soft delete)."""
