"""Repository implementations for all bounded contexts.

These implementations satisfy the abstract repository interfaces
defined in the domain layer (core/).
"""
from app.infrastructure.repositories.device import DeviceRepositoryImpl
from app.infrastructure.repositories.incident import IncidentRepositoryImpl
from app.infrastructure.repositories.knowledge import KnowledgeRepositoryImpl
from app.infrastructure.repositories.recommendation import RecommendationRepositoryImpl

__all__ = [
    "IncidentRepositoryImpl",
    "DeviceRepositoryImpl",
    "RecommendationRepositoryImpl",
    "KnowledgeRepositoryImpl",
]
