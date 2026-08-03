"""
AI Domain Integration Layer.

This module provides the official facade between AI Core (FASE 2) and
Business Domain (FASE 1) and Clinical Intelligence (FASE 3).

ARCHITECTURE FLOW:
    PHASE_1 (Business Domain)
            │
            ▼
    PHASE_2 (AI Core)
            │
            ├── AI Kernel
            ├── Context Builder
            └── Domain Gateways
                    │
                    ├── DeviceGateway ──────→ PHASE_1 Device
                    ├── IncidentGateway ────→ PHASE_1 Incident
                    ├── KnowledgeGateway ────→ PHASE_1 Knowledge
                    ├── HospitalGateway ─────→ PHASE_1 Capacity
                    ├── WorkOrderGateway ────→ PHASE_1 WorkOrder
                    ├── RecommendationGateway ─→ PHASE_3 Recommendation
                    └── ClinicalIntelligenceGateway ─→ PHASE_3 Clinical Intelligence
                            │
                            ▼
                    PHASE_3 (Clinical Intelligence)
                            │
                            ├── Reasoning Engine
                            ├── Evidence Retrieval
                            ├── Confidence Engine
                            ├── Decision Engine
                            ├── Safety Engine
                            └── Validation Engine
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
from .clinical_intelligence_gateway import (
    ClinicalIntelligenceGateway,
    ClinicalQueryDTO,
    ClinicalResponseDTO,
)
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
    # Gateway Implementations - PHASE_1
    "DeviceGateway",
    "IncidentGateway",
    "KnowledgeGateway",
    "HospitalGateway",
    "WorkOrderGateway",
    # Gateway Implementations - PHASE_3
    "RecommendationGateway",
    "ClinicalIntelligenceGateway",
    "ClinicalQueryDTO",
    "ClinicalResponseDTO",
    # Exceptions
    "GatewayError",
    "DeviceNotFoundError",
    "IncidentNotFoundError",
    "KnowledgeNotFoundError",
    "RecommendationNotFoundError",
    "HospitalNotFoundError",
    "WorkOrderNotFoundError",
]
