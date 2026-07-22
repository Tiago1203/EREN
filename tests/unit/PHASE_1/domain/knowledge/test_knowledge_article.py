"""Tests for KnowledgeArticle."""

from __future__ import annotations

import pytest

from core.PHASE_1.domain.knowledge.domain import (
    ArticleContent,
    KnowledgeArticle,
    KnowledgeCategory,
    KnowledgeReference,
    KnowledgeStatus,
)
from core.PHASE_1.infrastructure.shared import EngineerId, KnowledgeId, TenantId


class TestKnowledgeArticle:
    """Tests for KnowledgeArticle aggregate."""

    @pytest.fixture
    def tenant_id(self) -> TenantId:
        return TenantId(value="tenant_001")

    @pytest.fixture
    def article_id(self) -> KnowledgeId:
        return KnowledgeId.generate()

    @pytest.fixture
    def author_id(self) -> EngineerId:
        return EngineerId(value="engineer_001")

    @pytest.fixture
    def content(self) -> ArticleContent:
        return ArticleContent(
            title="How to calibrate MRI scanner",
            summary="Step by step guide for MRI calibration",
            body="First, ensure the device is powered off...",
            tags=("mri", "calibration", "maintenance"),
        )

    @pytest.fixture
    def category(self) -> KnowledgeCategory:
        return KnowledgeCategory.maintenance_procedure()

    def test_create_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test creating a new article."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )

        assert article.tenant_id == tenant_id
        assert article.article_id == "KB-001"
        assert article.content.title == "How to calibrate MRI scanner"
        assert article.status == KnowledgeStatus.draft()
        assert article.version == 1

    def test_article_is_editable_when_draft(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test that draft articles are editable."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )

        assert article.status.is_editable()

        # Can update content
        article.update_content(
            title="Updated title",
            summary="Updated summary",
            body="Updated body",
            expected_version=1,
        )

        assert article.content.title == "Updated title"
        assert article.version == 2

    def test_cannot_edit_published_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test that published articles cannot be edited."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        # Publish the article
        article.submit_for_review(expected_version=1)
        article.approve(reviewed_by=author_id, expected_version=2)

        assert not article.status.is_editable()

        # Cannot update content
        with pytest.raises(Exception):
            article.update_content(
                title="New title",
                summary="New summary",
                body="New body",
                expected_version=3,
            )

    def test_submit_for_review(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test submitting article for review."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.submit_for_review(expected_version=1)

        assert article.status == KnowledgeStatus.review()
        assert article.version == 2

    def test_approve_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test approving article."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.submit_for_review(expected_version=1)
        article.approve(reviewed_by=author_id, expected_version=2)

        assert article.status == KnowledgeStatus.published()
        assert article.published_at is not None
        assert article.review_info is not None
        assert article.review_info.is_approved()

    def test_reject_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test rejecting article."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.submit_for_review(expected_version=1)
        article.reject(reviewed_by=author_id, reason="Missing critical steps", expected_version=2)

        assert article.status == KnowledgeStatus.draft()
        assert article.review_info is not None
        assert not article.review_info.is_approved()

    def test_archive_published_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test archiving a published article."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        # Publish
        article.submit_for_review(expected_version=1)
        article.approve(reviewed_by=author_id, expected_version=2)

        # Archive
        article.archive(reason="Outdated procedure", expected_version=3)

        assert article.status == KnowledgeStatus.archived()

    def test_cannot_archive_draft(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test that draft articles cannot be archived."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        with pytest.raises(Exception):
            article.archive(expected_version=1)

    def test_deprecate_article(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test deprecating an article."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.deprecate(
            replacement_article_id="KB-002",
            reason="Replaced by updated procedure",
            expected_version=1,
        )

        assert article.status == KnowledgeStatus.deprecated()

    def test_add_device_link(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test linking article to a device."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.add_device_link("device_001", expected_version=1)

        assert "device_001" in article.device_ids

    def test_add_reference(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test adding a reference."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        ref = KnowledgeReference.internal("KB-002", "Related procedure")
        article.add_reference(ref, expected_version=1)

        assert len(article.references) == 1
        assert article.references[0].is_internal()

    def test_record_view(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test recording article view."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        initial_views = article.statistics.view_count

        article.record_view(expected_version=1)

        assert article.statistics.view_count == initial_views + 1

    def test_record_feedback(
        self,
        article_id,
        tenant_id,
        author_id,
        content,
        category,
    ):
        """Test recording article feedback."""
        article = KnowledgeArticle(
            id=article_id,
            tenant_id=tenant_id,
            article_id="KB-001",
            content=content,
            category=category,
            author_id=author_id,
            author_name="John Doe",
        )
        article.pop_events()

        article.record_feedback(is_helpful=True, expected_version=1)
        article.record_feedback(is_helpful=True, expected_version=2)
        article.record_feedback(is_helpful=False, expected_version=3)

        assert article.statistics.helpful_count == 2
        assert article.statistics.not_helpful_count == 1
        assert article.statistics.helpfulness_ratio == pytest.approx(0.666, rel=0.01)


class TestKnowledgeValueObjects:
    """Tests for Knowledge value objects."""

    def test_knowledge_status_factory_methods(self):
        """Test status factory methods."""
        assert KnowledgeStatus.draft().value == "draft"
        assert KnowledgeStatus.review().value == "review"
        assert KnowledgeStatus.published().value == "published"

    def test_knowledge_status_is_editable(self):
        """Test editable checks."""
        assert KnowledgeStatus.draft().is_editable()
        assert KnowledgeStatus.review().is_editable()
        assert not KnowledgeStatus.published().is_editable()

    def test_knowledge_status_is_active(self):
        """Test active checks."""
        assert KnowledgeStatus.published().is_active()
        assert not KnowledgeStatus.draft().is_active()

    def test_knowledge_category_factory_methods(self):
        """Test category factory methods."""
        assert KnowledgeCategory.troubleshooting().value == "troubleshooting"
        assert KnowledgeCategory.safety_guideline().is_regulatory()
        assert not KnowledgeCategory.best_practice().is_regulatory()

    def test_article_content(self):
        """Test article content value object."""
        content = ArticleContent(
            title="Test",
            summary="Summary",
            body="This is the body text",
            tags=("tag1", "tag2"),
        )

        assert content.word_count == 5
        assert content.has_tag("tag1")
        assert not content.has_tag("tag3")

    def test_knowledge_reference(self):
        """Test knowledge reference."""
        internal = KnowledgeReference.internal("KB-001", "Related")
        assert internal.is_internal()

        external = KnowledgeReference.external("https://example.com", "External source")
        assert not external.is_internal()
