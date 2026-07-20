"""Feedback Engine - processes user feedback and improves AI."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FeedbackType(str, Enum):
    """Type of user feedback."""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    SAFE = "safe"
    UNSAFE = "unsafe"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    CITATION_HELPFUL = "citation_helpful"
    CITATION_MISSING = "citation_missing"
    CUSTOM = "custom"


@dataclass
class Feedback:
    """User feedback on AI response."""
    feedback_id: str
    conversation_id: str
    message_id: str
    feedback_type: FeedbackType
    rating: int  # 1-5 scale
    comment: str | None
    user_id: str
    created_at: datetime


@dataclass
class FeedbackSummary:
    """Summary of feedback for a response or topic."""
    total_feedback: int
    average_rating: float
    helpful_count: int
    not_helpful_count: int
    accurate_count: int
    inaccurate_count: int
    common_issues: list[str]
    improvement_suggestions: list[str]


class FeedbackEngine:
    """
    Processes user feedback and generates insights for improvement.
    
    Handles:
    - Feedback collection
    - Feedback analysis
    - Learning loop integration
    - A/B testing support
    """
    
    def __init__(self, store: Any | None = None):  # FeedbackStore
        self.store = store
    
    async def record_feedback(
        self,
        conversation_id: str,
        message_id: str,
        feedback_type: FeedbackType,
        rating: int,
        user_id: str,
        comment: str | None = None,
    ) -> Feedback:
        """
        Record user feedback.
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID that was feedbacked
            feedback_type: Type of feedback
            rating: Rating 1-5
            user_id: User who gave feedback
            comment: Optional comment
        
        Returns:
            Created feedback record
        """
        feedback = Feedback(
            feedback_id=f"fb_{datetime.utcnow().timestamp()}",
            conversation_id=conversation_id,
            message_id=message_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        
        if self.store:
            await self.store.save(feedback)
        
        # Update metrics
        await self._update_metrics(feedback)
        
        return feedback
    
    async def analyze_feedback(
        self,
        entity_id: str,
        entity_type: str = "message",
    ) -> FeedbackSummary:
        """
        Analyze feedback for an entity.
        
        Args:
            entity_id: ID of entity to analyze
            entity_type: Type of entity (message, topic, domain)
        
        Returns:
            Feedback summary with insights
        """
        if not self.store:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                helpful_count=0,
                not_helpful_count=0,
                accurate_count=0,
                inaccurate_count=0,
                common_issues=[],
                improvement_suggestions=[],
            )
        
        feedback_list = await self.store.get_feedback(entity_id, entity_type)
        
        if not feedback_list:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                helpful_count=0,
                not_helpful_count=0,
                accurate_count=0,
                inaccurate_count=0,
                common_issues=[],
                improvement_suggestions=[],
            )
        
        # Calculate metrics
        total = len(feedback_list)
        ratings = [f.rating for f in feedback_list]
        avg_rating = sum(ratings) / total if total > 0 else 0.0
        
        helpful = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.HELPFUL)
        not_helpful = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.NOT_HELPFUL)
        accurate = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.ACCURATE)
        inaccurate = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.INACCURATE)
        
        # Extract issues from comments
        issues = self._extract_issues([f.comment for f in feedback_list if f.comment])
        
        # Generate suggestions
        suggestions = self._generate_suggestions(feedback_list)
        
        return FeedbackSummary(
            total_feedback=total,
            average_rating=avg_rating,
            helpful_count=helpful,
            not_helpful_count=not_helpful,
            accurate_count=accurate,
            inaccurate_count=inaccurate,
            common_issues=issues,
            improvement_suggestions=suggestions,
        )
    
    def _extract_issues(self, comments: list[str]) -> list[str]:
        """Extract common issues from comments."""
        # Simple keyword-based extraction
        issue_keywords = {
            "unclear": ["unclear", "confusing", "vague"],
            "missing context": ["missing", "need more", "doesn't explain"],
            "too technical": ["technical", "jargon", "complex"],
            "incomplete": ["incomplete", "missing", "doesn't answer"],
            "incorrect": ["wrong", "incorrect", "mistake"],
        }
        
        issues = []
        for comment in comments:
            comment_lower = comment.lower()
            for issue, keywords in issue_keywords.items():
                if any(kw in comment_lower for kw in keywords):
                    if issue not in issues:
                        issues.append(issue)
        
        return issues[:5]  # Top 5 issues
    
    def _generate_suggestions(self, feedback_list: list[Feedback]) -> list[str]:
        """Generate improvement suggestions based on feedback."""
        suggestions = []
        
        # Analyze patterns
        ratings = [f.rating for f in feedback_list]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        if avg_rating < 3:
            suggestions.append("Overall rating is low. Consider reviewing response quality.")
        
        low_ratings = [f for f in feedback_list if f.rating <= 2]
        if low_ratings:
            suggestions.append(f"{len(low_ratings)} responses rated as low quality. Review these cases.")
        
        inaccurate_count = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.INACCURATE)
        if inaccurate_count > 0:
            suggestions.append("Some responses marked as inaccurate. Verify information sources.")
        
        citation_issues = sum(
            1 for f in feedback_list 
            if f.feedback_type in [FeedbackType.CITATION_HELPFUL, FeedbackType.CITATION_MISSING]
        )
        if citation_issues > 0:
            suggestions.append("Review citation quality and availability.")
        
        return suggestions
    
    async def _update_metrics(self, feedback: Feedback) -> None:
        """Update aggregate metrics when new feedback is recorded."""
        # In production, would update:
        # - Running averages
        # - Topic-specific metrics
        # - User-specific metrics
        pass
    
    async def get_topic_insights(self, topic: str) -> dict[str, Any]:
        """Get insights for a specific topic."""
        # In production, would query by topic keyword
        return {
            "topic": topic,
            "total_feedback": 0,
            "average_rating": 0.0,
            "suggestions": [],
        }


def create_feedback_engine(store: Any | None = None) -> FeedbackEngine:
    """Create a feedback engine."""
    return FeedbackEngine(store=store)
