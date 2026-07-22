"""
AI Domain Integration Layer.

This module provides the official facade between AI Core (FASE 2) and
Business Domain (FASE 1). AI Core uses these gateways to access
business data without coupling to domain implementations.
"""

from .contracts import (
    # DTOs
    DeviceDTO,
    IncidentDTO,
    KnowledgeArticleDTO,
    RecommendationDTO,
    HospitalDTO,
    DepartmentDTO,
    WorkOrderDTO,
    CapacityDTO,
    # Gateway Interfaces
    IDomainGateway,
    IDeviceGateway,
    IIncidentGateway,
    IKnowledgeGateway,
    IRecommendationGateway,
    IHospitalGateway,
    IWorkOrderGateway,
)
from .device_gateway import DeviceGateway
from .incident_gateway import IncidentGateway
from .knowledge_gateway import KnowledgeGateway
from .recommendation_gateway import RecommendationGateway
from .hospital_gateway import HospitalGateway
from .workorder_gateway import WorkOrderGateway
from .exceptions import (
    GatewayError,
    DeviceNotFoundError,
    IncidentNotFoundError,
    KnowledgeNotFoundError,
    RecommendationNotFoundError,
    HospitalNotFoundError,
    WorkOrderNotFoundError,
)

__all__ = [
    # DTOs
    "DeviceDTO",
    "IncidentDTO",
    "KnowledgeArticleDTO",
    "RecommendationDTO",
    "HospitalDTO",
    "DepartmentDTO",
    "WorkOrderDTO",
    "CapacityDTO",
    # Gateway Interfaces
    "IDomainGateway",
    "IDeviceGateway",
    "IIncidentGateway",
    "IKnowledgeGateway",
    "IRecommendationGateway",
    "IHospitalGateway",
    "IWorkOrderGateway",
    # Gateway Implementations
    "DeviceGateway",
    "IncidentGateway",
    "KnowledgeGateway",
    "RecommendationGateway",
    "HospitalGateway",
    "WorkOrderGateway",
    # Exceptions
    "GatewayError",
    "DeviceNotFoundError",
    "IncidentNotFoundError",
    "KnowledgeNotFoundError",
    "RecommendationNotFoundError",
    "HospitalNotFoundError",
    "WorkOrderNotFoundError",
]
