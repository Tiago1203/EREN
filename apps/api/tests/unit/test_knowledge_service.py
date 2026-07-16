"""Unit tests for KnowledgeService."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.knowledge.domain.services.knowledge_service import KnowledgeService
from core.knowledge.domain.entities.knowledge_article import KnowledgeArticle
from core.knowledge.domain.value_objects import (
    ArticleContent,
    KnowledgeCategory,
    KnowledgeStatus,
)
from core.knowledge.domain.repositories.knowledge_repository import KnowledgeRepository
from core.shared import (
    EngineerId,
    KnowledgeId,
    Ok,
    Err,
    TenantId,
)


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock repository."""
    repo = MagicMock(spec=KnowledgeRepository)
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_article_id = AsyncMock()
    repo.search_by_keywords = AsyncMock()
    repo.get_by_tenant = AsyncMock()
    repo.get_active_articles = AsyncMock()
    return repo


@pytest.fixture
def knowledge_service(mock_repository: MagicMock) -> KnowledgeService:
    """Create a KnowledgeService with mock repository."""
    return KnowledgeService(mock_repository)


@pytest.fixture
def sample_article() -> KnowledgeArticle:
    """Create a sample knowledge article."""
    return KnowledgeArticle(
        id=KnowledgeId.generate(),
        tenant_id=TenantId.generate(),
        article_id="KB-001",
        content=ArticleContent(
            title="Test Article",
            summary="Test summary",
            body="Test body content",
            tags=("test",),
        ),
        category=KnowledgeCategory(value="maintenance_procedure"),
        author_id=EngineerId.generate(),
        author_name="Test Engineer",
        device_ids=(),
        status=KnowledgeStatus.draft(),
    )


class TestCreateArticle:
    """Tests for KnowledgeService.create_article."""

    @pytest.mark.asyncio
    async def test_create_article_success(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
        sample_article: KnowledgeArticle,
    ) -> None:
        """Should return Ok(article) when article is created successfully."""
        mock_repository.get_by_article_id.return_value = Ok(None)
        mock_repository.save.return_value = Ok(sample_article)

        tenant_id = TenantId.generate()
        result = await knowledge_service.create_article(
            tenant_id=tenant_id,
            article_id="KB-001",
            title="Test Article",
            summary="Test summary",
            body="Test body content",
            category="maintenance_procedure",
            author_id=EngineerId.generate(),
            author_name="Test Engineer",
        )

        assert result.is_ok()
        assert result.unwrap() == sample_article
        mock_repository.get_by_article_id.assert_called_once_with("KB-001")
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_article_duplicate_id(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
        sample_article: KnowledgeArticle,
    ) -> None:
        """Should return Err when article_id already exists."""
        mock_repository.get_by_article_id.return_value = Ok(sample_article)

        tenant_id = TenantId.generate()
        result = await knowledge_service.create_article(
            tenant_id=tenant_id,
            article_id="KB-001",
            title="Test Article",
            summary="Test summary",
            body="Test body content",
            category="maintenance_procedure",
            author_id=EngineerId.generate(),
            author_name="Test Engineer",
        )

        assert result.is_err()
        assert "already exists" in result.unwrap_err()


class TestPublishArticle:
    """Tests for KnowledgeService.publish_article."""

    @pytest.mark.asyncio
    async def test_publish_article_success(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
        sample_article: KnowledgeArticle,
    ) -> None:
        """Should return Ok(published_article) when article is published."""
        published_article = KnowledgeArticle(
            id=sample_article.id,
            tenant_id=sample_article.tenant_id,
            article_id=sample_article.article_id,
            content=sample_article.content,
            category=sample_article.category,
            author_id=sample_article.author_id,
            author_name=sample_article.author_name,
            device_ids=sample_article.device_ids,
            status=KnowledgeStatus.published(),
        )
        mock_repository.get_by_id.return_value = Ok(sample_article)
        mock_repository.save.return_value = Ok(published_article)

        result = await knowledge_service.publish_article(
            article_id=sample_article.id,
            published_by=sample_article.author_id,
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_article_not_found(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
    ) -> None:
        """Should return Err when article is not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await knowledge_service.publish_article(
            article_id=KnowledgeId.generate(),
            published_by=EngineerId.generate(),
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()


class TestArchiveArticle:
    """Tests for KnowledgeService.archive_article."""

    @pytest.mark.asyncio
    async def test_archive_article_success(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
    ) -> None:
        """Should return Ok(archived_article) when archived."""
        published_article = KnowledgeArticle(
            id=KnowledgeId.generate(),
            tenant_id=TenantId.generate(),
            article_id="KB-002",
            content=ArticleContent(
                title="Test Article",
                summary="Test summary",
                body="Test body",
                tags=("test",),
            ),
            category=KnowledgeCategory(value="maintenance_procedure"),
            author_id=EngineerId.generate(),
            author_name="Test Engineer",
            device_ids=(),
            status=KnowledgeStatus.published(),
        )
        mock_repository.get_by_id.return_value = Ok(published_article)
        mock_repository.save.return_value = Ok(published_article)

        result = await knowledge_service.archive_article(
            article_id=published_article.id,
            reason="Outdated",
        )

        assert result.is_ok()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_article_not_found(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
    ) -> None:
        """Should return Err when article is not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await knowledge_service.archive_article(
            article_id=KnowledgeId.generate(),
        )

        assert result.is_err()
        assert "not found" in result.unwrap_err()


class TestSearchKnowledgeBase:
    """Tests for KnowledgeService.search_knowledge_base."""

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
        sample_article: KnowledgeArticle,
    ) -> None:
        """Should return Ok(list) when search finds articles."""
        mock_repository.search_by_keywords.return_value = Ok([sample_article])

        result = await knowledge_service.search_knowledge_base(
            tenant_id=sample_article.tenant_id,
            keywords=["test"],
        )

        assert result.is_ok()
        articles = result.unwrap()
        assert len(articles) == 1
        assert articles[0].article_id == "KB-001"

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
        sample_article: KnowledgeArticle,
    ) -> None:
        """Should filter results by category when specified."""
        mock_repository.search_by_keywords.return_value = Ok([sample_article])

        result = await knowledge_service.search_knowledge_base(
            tenant_id=sample_article.tenant_id,
            keywords=["test"],
            category="maintenance_procedure",
        )

        assert result.is_ok()
        articles = result.unwrap()
        assert len(articles) == 1

    @pytest.mark.asyncio
    async def test_search_repository_error(
        self,
        knowledge_service: KnowledgeService,
        mock_repository: MagicMock,
    ) -> None:
        """Should propagate repository errors."""
        mock_repository.search_by_keywords.return_value = Err("Database error")

        result = await knowledge_service.search_knowledge_base(
            tenant_id=TenantId.generate(),
            keywords=["test"],
        )

        assert result.is_err()
        assert "Database error" in result.unwrap_err()
