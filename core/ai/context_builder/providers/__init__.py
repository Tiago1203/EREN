"""
Context Providers Module.

Provides context from various sources for the AI.
"""

from .base import BaseContextProvider, ContextItem, ContextQuery
from .conversation_provider import ConversationContextProvider
from .memory_provider import MemoryContextProvider
from .device_provider import DeviceContextProvider
from .incident_provider import IncidentContextProvider
from .knowledge_provider import KnowledgeContextProvider
from .recommendation_provider import RecommendationContextProvider
from .hospital_provider import HospitalContextProvider
from .session_provider import SessionContextProvider

__all__ = [
    # Base
    "BaseContextProvider",
    "ContextItem",
    "ContextQuery",
    # Providers
    "ConversationContextProvider",
    "MemoryContextProvider",
    "DeviceContextProvider",
    "IncidentContextProvider",
    "KnowledgeContextProvider",
    "RecommendationContextProvider",
    "HospitalContextProvider",
    "SessionContextProvider",
]


def get_all_providers() -> list[BaseContextProvider]:
    """
    Get all context providers in priority order.
    
    Returns providers sorted by priority (lower = higher priority).
    """
    providers = [
        ConversationContextProvider(),
        SessionContextProvider(),
        MemoryContextProvider(),
        DeviceContextProvider(),
        IncidentContextProvider(),
        KnowledgeContextProvider(),
        RecommendationContextProvider(),
        HospitalContextProvider(),
    ]
    
    return sorted(providers, key=lambda p: p.priority)


def create_provider(
    name: str,
    **kwargs,
) -> BaseContextProvider | None:
    """
    Create a specific provider by name.
    
    Args:
        name: Provider name (e.g., "device", "incident")
        **kwargs: Additional arguments for the provider
        
    Returns:
        The provider instance or None if not found
    """
    provider_map = {
        "conversation": ConversationContextProvider,
        "memory": MemoryContextProvider,
        "device": DeviceContextProvider,
        "incident": IncidentContextProvider,
        "knowledge": KnowledgeContextProvider,
        "recommendation": RecommendationContextProvider,
        "hospital": HospitalContextProvider,
        "session": SessionContextProvider,
    }
    
    provider_class = provider_map.get(name.lower())
    if provider_class:
        return provider_class(**kwargs)
    return None
