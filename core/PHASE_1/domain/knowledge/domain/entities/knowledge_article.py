"""Knowledge Article aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, EngineerId, KnowledgeId, TenantId

from ..value_objects import (
    ArticleContent,
    KnowledgeCategory,
    KnowledgeReference,
    KnowledgeStatus,
    ReviewInfo,
    UsageStatistics,
)

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class KnowledgeArticle(AggregateRoot):
    """Knowledge Article aggregate root.

    Represents a knowledge article in the system.
    Articles go through a lifecycle: draft → review → published → archived

    Invariants:
    1. Title must not be empty
    2. Body must not be empty
    3. Only draft articles can be edited
    4. Archived articles cannot be unpublished
    """

    # Required fields (kw_only to avoid conflict with parent defaults)
    tenant_id: TenantId = field(kw_only=True)
    article_id: str = field(kw_only=True)  # Human-readable ID like "KB-001"
    content: ArticleContent = field(kw_only=True)
    category: KnowledgeCategory = field(kw_only=True)
    author_id: EngineerId = field(kw_only=True)
    author_name: str = field(kw_only=True)

    # Optional fields with defaults
    status: KnowledgeStatus = field(default_factory=KnowledgeStatus.draft, kw_only=True)
    device_ids: tuple[str, ...] = field(default=(), kw_only=True)
    incident_type_tags: tuple[str, ...] = field(default=(), kw_only=True)
    references: tuple[KnowledgeReference, ...] = field(default=(), kw_only=True)
    related_articles: tuple[str, ...] = field(default=(), kw_only=True)
    published_at: datetime | None = field(default=None, kw_only=True)
    review_info: ReviewInfo | None = field(default=None, kw_only=True)
    statistics: UsageStatistics = field(default_factory=UsageStatistics, kw_only=True)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate()

    def _validate(self) -> None:
        """Validate article invariants."""
        if not self.content.title.strip():
            msg = "Article title cannot be empty"
            raise ValueError(msg)
        if not self.content.body.strip():
            msg = "Article body cannot be empty"
            raise ValueError(msg)

    def update_content(
        self,
        title: str,
        summary: str,
        body: str,
        tags: list[str] | None = None,
        expected_version: int = 1,
    ) -> None:
        """Update article content."""
        self._assert_version(expected_version)

        if not self.status.is_editable():
            msg = f"Cannot edit article in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.content = ArticleContent(
            title=title,
            summary=summary,
            body=body,
            tags=tuple(tags) if tags else self.content.tags,
        )
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def change_category(
        self,
        new_category: KnowledgeCategory,
        expected_version: int = 1,
    ) -> None:
        """Change article category."""
        self._assert_version(expected_version)

        if not self.status.is_editable():
            msg = "Cannot change category of non-editable article"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.category = new_category
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def submit_for_review(
        self,
        expected_version: int = 1,
    ) -> None:
        """Submit article for review."""
        self._assert_version(expected_version)

        if self.status != KnowledgeStatus.draft():
            msg = f"Cannot submit article in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.status = KnowledgeStatus.review()
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def approve(
        self,
        reviewed_by: EngineerId,
        comments: str | None = None,
        expected_version: int = 1,
    ) -> None:
        """Approve article for publication."""
        self._assert_version(expected_version)

        if self.status != KnowledgeStatus.review():
            msg = f"Cannot approve article in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.status = KnowledgeStatus.published()
        self.published_at = datetime.now(UTC)
        self.review_info = ReviewInfo.approved(str(reviewed_by), comments)
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def reject(
        self,
        reviewed_by: EngineerId,
        reason: str,
        expected_version: int = 1,
    ) -> None:
        """Reject article."""
        self._assert_version(expected_version)

        if self.status != KnowledgeStatus.review():
            msg = f"Cannot reject article in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.status = KnowledgeStatus.draft()
        self.review_info = ReviewInfo.rejected(str(reviewed_by), reason)
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def archive(
        self,
        reason: str | None = None,
        expected_version: int = 1,
    ) -> None:
        """Archive the article."""
        self._assert_version(expected_version)

        if not self.status.is_active():
            msg = f"Cannot archive article in status {self.status}"
            raise ValueError(msg)

        self._unlock_for_mutation()
        self.status = KnowledgeStatus.archived()
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def deprecate(
        self,
        replacement_article_id: str | None = None,
        reason: str | None = None,
        expected_version: int = 1,
    ) -> None:
        """Deprecate article in favor of another."""
        self._assert_version(expected_version)

        self._unlock_for_mutation()
        self.status = KnowledgeStatus.deprecated()
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def add_device_link(
        self,
        device_id: str,
        expected_version: int = 1,
    ) -> None:
        """Link article to a device."""
        self._assert_version(expected_version)

        if device_id not in self.device_ids:
            self._unlock_for_mutation()
            self.device_ids = (*self.device_ids, device_id)
            self.updated_at = datetime.now(UTC)
            self._relock_after_mutation()

    def add_reference(
        self,
        reference: KnowledgeReference,
        expected_version: int = 1,
    ) -> None:
        """Add a reference to another article or source."""
        self._assert_version(expected_version)

        if reference not in self.references:
            self._unlock_for_mutation()
            self.references = (*self.references, reference)
            self.updated_at = datetime.now(UTC)
            self._relock_after_mutation()

    def record_view(
        self,
        expected_version: int = 1,
    ) -> None:
        """Record a view of this article."""
        self._assert_version(expected_version)

        self._unlock_for_mutation()
        self.statistics = UsageStatistics(
            view_count=self.statistics.view_count + 1,
            helpful_count=self.statistics.helpful_count,
            not_helpful_count=self.statistics.not_helpful_count,
            last_accessed=datetime.now(UTC).isoformat(),
        )
        self._relock_after_mutation()

    def record_feedback(
        self,
        is_helpful: bool,
        expected_version: int = 1,
    ) -> None:
        """Record user feedback on this article."""
        self._assert_version(expected_version)

        self._unlock_for_mutation()
        if is_helpful:
            self.statistics = UsageStatistics(
                view_count=self.statistics.view_count,
                helpful_count=self.statistics.helpful_count + 1,
                not_helpful_count=self.statistics.not_helpful_count,
                last_accessed=self.statistics.last_accessed,
            )
        else:
            self.statistics = UsageStatistics(
                view_count=self.statistics.view_count,
                helpful_count=self.statistics.helpful_count,
                not_helpful_count=self.statistics.not_helpful_count + 1,
                last_accessed=self.statistics.last_accessed,
            )
        self._relock_after_mutation()

    def add_related_article(
        self,
        related_article_id: str,
        expected_version: int = 1,
    ) -> None:
        """Add a related article."""
        self._assert_version(expected_version)

        if related_article_id not in self.related_articles:
            self._unlock_for_mutation()
            self.related_articles = (*self.related_articles, related_article_id)
            self.updated_at = datetime.now(UTC)
            self._relock_after_mutation()

    def is_active(self) -> bool:
        """Check if article is active and visible."""
        return self.status.is_active()

    def is_searchable(self) -> bool:
        """Check if article can be found in searches."""
        return self.status in {KnowledgeStatus.published(), KnowledgeStatus.archived()}

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update(
            {
                "tenant_id": str(self.tenant_id),
                "article_id": self.article_id,
                "title": self.content.title,
                "summary": self.content.summary,
                "body": self.content.body,
                "tags": list(self.content.tags),
                "category": str(self.category),
                "status": str(self.status),
                "author_id": str(self.author_id),
                "author_name": self.author_name,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "published_at": self.published_at.isoformat() if self.published_at else None,
                "view_count": self.statistics.view_count,
                "helpful_count": self.statistics.helpful_count,
            },
        )
        return base
