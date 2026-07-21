"""Recommendation Domain - Repository."""

from .repository import (
    RecommendationRepository,
    RecommendationRepositoryImpl,
    SQLAlchemyRecommendationRepository,
)

__all__ = [
    "RecommendationRepository",
    "RecommendationRepositoryImpl",
    "SQLAlchemyRecommendationRepository",
]
