"""
Context Providers Module.

Provides context from various sources for the AI.
"""

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery
from .conversation_provider import ConversationContextProvider
from .memory_provider import MemoryContextProvider
from .device_provider import DeviceContextProvider
from .incident_provider import IncidentContextProvider
from .knowledge_provider import KnowledgeContextProvider
from .recommendation_provider import RecommendationContextProvider
from .hospital_provider import HospitalContextProvider
from .session_provider import SessionContextProvider

if TYPE_CHECKING:
    from core.ai.domain import (
        DeviceGateway,
        IncidentGateway,
        KnowledgeGateway,
        RecommendationGateway,
        IHospitalGateway,
    )

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
    # Factory
    "get_all_providers",
    "get_providers_with_gateways",
    "create_provider",
]


# Lazy-loaded gateways for provider creation
_gateways: dict[str, object] = {}


def set_gateways(gateways: dict[str, object]) -> None:
    """
    Set the gateways to be used by providers.
    
    Args:
        gateways: Dict mapping gateway names to instances
                  e.g., {"device": DeviceGatewayImpl, "incident": IncidentGatewayImpl}
    """
    global _gateways
    _gateways = gateways


def get_all_providers(
    gateways: dict[str, object] | None = None,
) -> list[BaseContextProvider]:
    """
    Get all context providers in priority order.
    
    Args:
        gateways: Optional dict of gateways to inject into providers.
                  If provided, providers will be connected to real gateways.
                  If None, uses any previously set gateways via set_gateways().

    Returns:
        Providers sorted by priority (lower = higher priority).
    """
    # Use provided gateways or fall back to global state
    active_gateways = gateways or _gateways
    
    providers = [
        ConversationContextProvider(),
        SessionContextProvider(),
        MemoryContextProvider(),
        # Domain providers with optional gateway injection
        DeviceContextProvider(
            device_gateway=active_gateways.get("device"),
            incident_gateway=active_gateways.get("incident"),
        ) if "device" in active_gateways else DeviceContextProvider(),
        IncidentContextProvider(
            incident_gateway=active_gateways.get("incident"),
            device_gateway=active_gateways.get("device"),
        ) if "incident" in active_gateways else IncidentContextProvider(),
        KnowledgeContextProvider(
            knowledge_gateway=active_gateways.get("knowledge"),
        ) if "knowledge" in active_gateways else KnowledgeContextProvider(),
        RecommendationContextProvider(
            recommendation_gateway=active_gateways.get("recommendation"),
        ) if "recommendation" in active_gateways else RecommendationContextProvider(),
        HospitalContextProvider(
            hospital_gateway=active_gateways.get("hospital"),
        ) if "hospital" in active_gateways else HospitalContextProvider(),
    ]

    return sorted(providers, key=lambda p: p.priority)


def get_providers_with_gateways(
    device_gateway: "DeviceGateway | None" = None,
    incident_gateway: "IncidentGateway | None" = None,
    knowledge_gateway: "KnowledgeGateway | None" = None,
    recommendation_gateway: "RecommendationGateway | None" = None,
    hospital_gateway: "IHospitalGateway | None" = None,
) -> list[BaseContextProvider]:
    """
    Create providers with explicitly injected gateways.
    
    This is the preferred method for production use.
    
    Args:
        device_gateway: Gateway for device context
        incident_gateway: Gateway for incident context
        knowledge_gateway: Gateway for knowledge context
        recommendation_gateway: Gateway for recommendation context
        hospital_gateway: Gateway for hospital/capacity context
    
    Returns:
        List of providers with injected gateways
    """
    providers = [
        ConversationContextProvider(),
        SessionContextProvider(),
        MemoryContextProvider(),
        DeviceContextProvider(
            device_gateway=device_gateway,
            incident_gateway=incident_gateway,
        ),
        IncidentContextProvider(
            incident_gateway=incident_gateway,
            device_gateway=device_gateway,
        ),
        KnowledgeContextProvider(
            knowledge_gateway=knowledge_gateway,
        ),
        RecommendationContextProvider(
            recommendation_gateway=recommendation_gateway,
        ),
        HospitalContextProvider(
            hospital_gateway=hospital_gateway,
        ),
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
        **kwargs: Additional arguments for the provider (e.g., gateway)

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
