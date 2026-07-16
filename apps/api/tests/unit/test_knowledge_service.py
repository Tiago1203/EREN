"""Unit tests for KnowledgeService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.knowledge.domain.services.knowledge_service import KnowledgeService
from core.knowledge.domain.entities import KnowledgeArticle
from core.shared import EngineerId, Ok, Err, TenantId


@pytest.fixture
def mock_repository():
    """Create a mock KnowledgeRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    """Create KnowledgeService with mock repository."""
    return KnowledgeService(repository=mock_repository)


@pytest.mark.asyncio
class TestCreateArticle:
    """Test KnowledgeService.create_article()."""

    async def test_create_article_success(self, service, mock_repository):
        """Article is created successfully when ID is unique."""
        mock_repository.get_by_article_id.return_value = Ok(None)

        result = await service.create_article(
            tenant_id=TenantId(value="tenant-1"),
            article_id="KB-001",
            title="How to calibrate device X",
            summary="Step-by-step guide",
            body="Detailed calibration steps...",
            category="maintenance_procedure",
            author_id=EngineerId(value="eng-1"),
            author_name="John Doe",
        )

        assert result.is_ok()
        article = result.unwrap()
        assert article.title == "How to calibrate device X"
        assert article.category.value == "maintenance_procedure"
        mock_repository.save.assert_called_once()

    async def test_create_article_duplicate_id(self, service, mock_repository):
        """Article creation fails when article ID already exists."""
        mock_repository.get_by_article_id.return_value = Ok(MagicMock())

        result = await service.create_article(
            tenant_id=TenantId(value="tenant-1"),
            article_id="KB-001",
            title="Duplicate",
            summary="Summary",
            body="Body",
            category="troubleshooting",
            author_id=EngineerId(value="eng-1"),
            author_name="John Doe",
        )

        assert result.is_err()
        assert "already exists" in result.unwrap_err()


@pytest.mark.asyncio
class TestSearchKnowledgeBase:
    """Test KnowledgeService.search_knowledge_base()."""

    async def test_search_knowledge_base_returns_results(self, service, mock_repository):
        """Search returns matching articles."""
        mock_article = MagicMock(spec=KnowledgeArticle)
        mock_repository.search.return_value = Ok([mock_article])

        result = await service.search_knowledge_base(
            tenant_id=TenantId(value="tenant-1"),
            query="calibration",
        )

        assert result.is_ok()
        articles = result.unwrap()
        assert len(articles) == 1
        mock_repository.search.assert_called_once()


@pytest.mark.asyncio
class TestPublishArticle:
    """Test KnowledgeService.publish_article()."""

    async def test_publish_article_not_found(self, service, mock_repository):
        """Publish fails when article not found."""
        mock_repository.get_by_id.return_value = Ok(None)

        result = await service.publish_article(
            tenant_id=TenantId(value="tenant-1"),
            article_id="KB-NONEXISTENT",
            published_by=EngineerId(value="eng-1"),
        )

        assert result.is_err()
