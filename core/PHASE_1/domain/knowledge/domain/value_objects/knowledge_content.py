"""Knowledge-specific value objects."""

from __future__ import annotations

from dataclasses import dataclass

from core.PHASE_1.infrastructure.shared import ValueObject


@dataclass(frozen=True)
class KnowledgeStatus(ValueObject):
    """Status of a knowledge article."""

    value: str

    def __post_init__(self) -> None:
        valid_statuses = {
            "draft",
            "review",
            "published",
            "archived",
            "deprecated",
        }
        if self.value.lower() not in valid_statuses:
            msg = f"Invalid knowledge status: {self.value}. Must be one of {valid_statuses}"
            raise ValueError(msg)

    @classmethod
    def draft(cls) -> KnowledgeStatus:
        return cls(value="draft")

    @classmethod
    def review(cls) -> KnowledgeStatus:
        return cls(value="review")

    @classmethod
    def published(cls) -> KnowledgeStatus:
        return cls(value="published")

    @classmethod
    def archived(cls) -> KnowledgeStatus:
        return cls(value="archived")

    @classmethod
    def deprecated(cls) -> KnowledgeStatus:
        return cls(value="deprecated")

    def is_editable(self) -> bool:
        """Check if article can be edited."""
        return self.value in {"draft", "review"}

    def is_active(self) -> bool:
        """Check if article is currently active/visible."""
        return self.value == "published"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class KnowledgeCategory(ValueObject):
    """Category for organizing knowledge articles."""

    value: str
    parent: str | None = None

    def __post_init__(self) -> None:
        valid_categories = {
            "troubleshooting",
            "maintenance_procedure",
            "safety_guideline",
            "device_manual",
            "incident_report",
            "best_practice",
            "training_material",
            "regulatory_compliance",
            "emergency_protocol",
        }
        if self.value.lower() not in valid_categories:
            msg = f"Invalid category: {self.value}"
            raise ValueError(msg)

    @classmethod
    def troubleshooting(cls) -> KnowledgeCategory:
        return cls(value="troubleshooting")

    @classmethod
    def maintenance_procedure(cls) -> KnowledgeCategory:
        return cls(value="maintenance_procedure")

    @classmethod
    def safety_guideline(cls) -> KnowledgeCategory:
        return cls(value="safety_guideline")

    @classmethod
    def device_manual(cls) -> KnowledgeCategory:
        return cls(value="device_manual")

    @classmethod
    def incident_report(cls) -> KnowledgeCategory:
        return cls(value="incident_report")

    @classmethod
    def best_practice(cls) -> KnowledgeCategory:
        return cls(value="best_practice")

    def is_regulatory(self) -> bool:
        """Check if category is regulatory/compliance related."""
        return self.value in {"safety_guideline", "regulatory_compliance", "emergency_protocol"}


@dataclass(frozen=True)
class ArticleContent(ValueObject):
    """Content of a knowledge article."""

    title: str
    summary: str
    body: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            msg = "Title cannot be empty"
            raise ValueError(msg)
        if not self.body or not self.body.strip():
            msg = "Body cannot be empty"
            raise ValueError(msg)

    @property
    def word_count(self) -> int:
        """Get approximate word count."""
        return len(self.body.split())

    @property
    def preview(self, length: int = 200) -> str:
        """Get preview of content."""
        if len(self.body) <= length:
            return self.body
        return self.body[:length] + "..."

    def has_tag(self, tag: str) -> bool:
        """Check if content has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]


@dataclass(frozen=True)
class KnowledgeReference(ValueObject):
    """Reference to another knowledge article or external source."""

    reference_type: str  # internal, external, device_manual, standard
    reference_id: str
    description: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        valid_types = {"internal", "external", "device_manual", "standard", "regulation"}
        if self.reference_type.lower() not in valid_types:
            msg = f"Invalid reference type: {self.reference_type}"
            raise ValueError(msg)

        if self.reference_type == "external" and not self.url:
            msg = "External references must have a URL"
            raise ValueError(msg)

    @classmethod
    def internal(cls, article_id: str, description: str | None = None) -> KnowledgeReference:
        return cls(reference_type="internal", reference_id=article_id, description=description)

    @classmethod
    def external(cls, url: str, description: str | None = None) -> KnowledgeReference:
        return cls(reference_type="external", reference_id=url, description=description, url=url)

    @classmethod
    def device_manual(cls, device_model: str, page: str | None = None) -> KnowledgeReference:
        ref_id = f"{device_model}:{page}" if page else device_model
        return cls(reference_type="device_manual", reference_id=ref_id, description=f"Manual for {device_model}")

    def is_internal(self) -> bool:
        return self.reference_type == "internal"


@dataclass(frozen=True)
class ReviewInfo(ValueObject):
    """Review and approval information."""

    reviewed_by: str
    reviewed_at: str
    approval_status: str  # approved, rejected, needs_revision
    comments: str | None = None

    def __post_init__(self) -> None:
        valid_statuses = {"approved", "rejected", "needs_revision"}
        if self.approval_status.lower() not in valid_statuses:
            msg = f"Invalid approval status: {self.approval_status}"
            raise ValueError(msg)

    @classmethod
    def approved(cls, reviewed_by: str, comments: str | None = None) -> ReviewInfo:
        return cls(
            reviewed_by=reviewed_by,
            reviewed_at="",  # Would be set in actual implementation
            approval_status="approved",
            comments=comments,
        )

    @classmethod
    def rejected(cls, reviewed_by: str, reason: str) -> ReviewInfo:
        return cls(
            reviewed_by=reviewed_by,
            reviewed_at="",
            approval_status="rejected",
            comments=reason,
        )

    def is_approved(self) -> bool:
        return self.approval_status == "approved"


@dataclass(frozen=True)
class UsageStatistics(ValueObject):
    """Usage statistics for a knowledge article."""

    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    last_accessed: str | None = None

    @property
    def helpfulness_ratio(self) -> float:
        """Calculate helpfulness ratio."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total

    @property
    def total_feedback(self) -> int:
        """Total feedback count."""
        return self.helpful_count + self.not_helpful_count
