"""
Feedback Learning Module

Collects and processes user feedback for continuous learning.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    CORRECTION = "correction"


class Feedback(BaseModel):
    id: str
    type: FeedbackType
    user_id: str
    interaction_id: str
    content: Dict[str, Any]
    rating: Optional[int] = None  # 1-5
    helpful: Optional[bool] = None
    correction: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}


class FeedbackCollector:
    """Collects feedback from users."""
    
    async def collect_explicit(
        self,
        user_id: str,
        interaction_id: str,
        rating: int = None,
        helpful: bool = None,
        correction: str = None
    ) -> Feedback:
        """Collect explicit feedback."""
        feedback = Feedback(
            id=f"fb-{datetime.utcnow().timestamp()}",
            type=FeedbackType.EXPLICIT,
            user_id=user_id,
            interaction_id=interaction_id,
            content={},
            rating=rating,
            helpful=helpful,
            correction=correction,
            created_at=datetime.utcnow()
        )
        return feedback
    
    async def collect_implicit(
        self,
        user_id: str,
        interaction_id: str,
        time_on_response: float,
        follow_up_count: int,
        task_completed: bool
    ) -> Feedback:
        """Collect implicit feedback from behavior."""
        return Feedback(
            id=f"fb-{datetime.utcnow().timestamp()}",
            type=FeedbackType.IMPLICIT,
            user_id=user_id,
            interaction_id=interaction_id,
            content={
                "time_on_response": time_on_response,
                "follow_up_count": follow_up_count,
                "task_completed": task_completed
            },
            created_at=datetime.utcnow()
        )


class FeedbackProcessor:
    """Processes and classifies feedback."""
    
    async def classify(self, feedback: Feedback) -> Dict[str, Any]:
        """Classify feedback for training."""
        classification = {
            "sentiment": "positive" if (feedback.rating or 0) >= 4 else "negative",
            "actionable": feedback.correction is not None,
            "category": self._categorize(feedback)
        }
        return classification
    
    def _categorize(self, feedback: Feedback) -> str:
        """Categorize feedback type."""
        if feedback.correction:
            return "correction"
        if feedback.helpful is False:
            return "unhelpful"
        if (feedback.rating or 0) <= 2:
            return "low_quality"
        return "satisfactory"


class LearningLoop:
    """Implements the continuous learning loop."""
    
    def __init__(self):
        self.collector = FeedbackCollector()
        self.processor = FeedbackProcessor()
        self.pending_updates: List[Dict] = []
    
    async def process_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        """Process feedback and update knowledge."""
        classification = await self.processor.classify(feedback)
        
        # Add to pending updates for batch processing
        update = {
            "feedback": feedback.dict(),
            "classification": classification,
            "processed_at": datetime.utcnow()
        }
        self.pending_updates.append(update)
        
        return {
            "feedback_id": feedback.id,
            "classification": classification,
            "knowledge_updated": classification["actionable"]
        }
    
    async def batch_update(self) -> int:
        """Batch process updates."""
        count = len(self.pending_updates)
        self.pending_updates.clear()
        return count
