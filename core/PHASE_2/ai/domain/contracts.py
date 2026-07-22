"""
Domain Contracts for AI Core.

This module defines the interfaces (ABCs) that AI Core uses to interact
with the Business Domain. These contracts ensure dependency inversion:
AI Core depends on abstractions, not implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    pass

# =============================================================================
# DTOs (Data Transfer Objects)
# =============================================================================

@dataclass(frozen=True)
class DeviceDTO:
    """DTO for Device - exposed to AI."""
    id: str
    serial_number: str
    name: str
    device_type: str
    status: str
    manufacturer: str
    model: str
    is_critical: bool
    location: dict = field(default_factory=dict)
    last_maintenance: datetime | None = None
    next_maintenance: datetime | None = None
    created_at: datetime | None = None

@dataclass(frozen=True)
class IncidentDTO:
    """DTO for Incident - exposed to AI."""
    id: str
    title: str
    description: str
    severity: str
    status: str
    device_id: str | None = None
    device_name: str | None = None
    assigned_to: str | None = None
    reported_at: datetime | None = None
    resolved_at: datetime | None = None

@dataclass(frozen=True)
class KnowledgeArticleDTO:
    """DTO for Knowledge Article - exposed to AI."""
    id: str
    title: str
    content: str
    category: str
    tags: list[str] = field(default_factory=list)
    views: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

@dataclass(frozen=True)
class RecommendationDTO:
    """DTO for Recommendation - exposed to AI."""
    id: str
    title: str
    description: str
    priority: str
    confidence: float
    device_id: str | None = None
    incident_id: str | None = None
    actions: list[str] = field(default_factory=list)
    created_at: datetime | None = None

@dataclass(frozen=True)
class HospitalDTO:
    """DTO for Hospital/Campus - exposed to AI."""
    id: str
    name: str
    address: str
    departments: list[dict] = field(default_factory=list)
    total_beds: int = 0
    available_beds: int = 0

@dataclass(frozen=True)
class DepartmentDTO:
    """DTO for Department - exposed to AI."""
    id: str
    name: str
    floor: str | None = None
    building: str | None = None
    beds: int = 0
    available_beds: int = 0

@dataclass(frozen=True)
class WorkOrderDTO:
    """DTO for Work Order - exposed to AI."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    device_id: str | None = None
    assigned_to: str | None = None
    scheduled_date: datetime | None = None
    completed_at: datetime | None = None

@dataclass(frozen=True)
class CapacityDTO:
    """DTO for Capacity info - exposed to AI."""
    campus_id: str
    campus_name: str
    total_beds: int
    occupied_beds: int
    available_beds: int
    occupancy_rate: float
    departments: list[dict] = field(default_factory=list)


# =============================================================================
# Gateway Interfaces
# =============================================================================

T = TypeVar("T")

class IDomainGateway(ABC, Generic[T]):
    """Base interface for all domain gateways."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Gateway name for identification."""
        raise NotImplementedError


class IDeviceGateway(IDomainGateway[DeviceDTO]):
    """Gateway interface for Device domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        device_id: str,
        tenant_id: str,
    ) -> DeviceDTO | None:
        """Get device by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[DeviceDTO]:
        """Search devices by name, type, or serial."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_status(
        self,
        tenant_id: str,
        status: str,
        limit: int = 50,
    ) -> list[DeviceDTO]:
        """Get devices by status."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_critical_devices(
        self,
        tenant_id: str,
    ) -> list[DeviceDTO]:
        """Get all critical devices."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_needing_maintenance(
        self,
        tenant_id: str,
    ) -> list[DeviceDTO]:
        """Get devices needing maintenance."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_history(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Get device maintenance/incident history."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_location(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Get device location details."""
        raise NotImplementedError


class IIncidentGateway(IDomainGateway[IncidentDTO]):
    """Gateway interface for Incident domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> IncidentDTO | None:
        """Get incident by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[IncidentDTO]:
        """Search incidents."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_open_incidents(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[IncidentDTO]:
        """Get all open incidents."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list[IncidentDTO]:
        """Get incidents for a device."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_engineer(
        self,
        engineer_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list[IncidentDTO]:
        """Get incidents assigned to an engineer."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_history(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Get incident history/timeline."""
        raise NotImplementedError
    
    @abstractmethod
    async def analyze(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Analyze incident for root cause."""
        raise NotImplementedError


class IKnowledgeGateway(IDomainGateway[KnowledgeArticleDTO]):
    """Gateway interface for Knowledge domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        article_id: str,
        tenant_id: str,
    ) -> KnowledgeArticleDTO | None:
        """Get article by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search knowledge articles."""
        raise NotImplementedError
    
    @abstractmethod
    async def search_manuals(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search user manuals."""
        raise NotImplementedError
    
    @abstractmethod
    async def search_procedures(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search procedures."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[KnowledgeArticleDTO]:
        """Get articles related to a device."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_related(
        self,
        article_id: str,
        tenant_id: str,
        limit: int = 5,
    ) -> list[KnowledgeArticleDTO]:
        """Get related articles."""
        raise NotImplementedError


class IRecommendationGateway(IDomainGateway[RecommendationDTO]):
    """Gateway interface for Recommendation domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        recommendation_id: str,
        tenant_id: str,
    ) -> RecommendationDTO | None:
        """Get recommendation by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_pending(
        self,
        tenant_id: str,
        engineer_id: str | None = None,
        limit: int = 20,
    ) -> list[RecommendationDTO]:
        """Get pending recommendations."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_confidence(
        self,
        tenant_id: str,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> list[RecommendationDTO]:
        """Get high confidence recommendations."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[RecommendationDTO]:
        """Get recommendations for a device."""
        raise NotImplementedError
    
    @abstractmethod
    async def generate(
        self,
        device_id: str | None,
        incident_id: str | None,
        tenant_id: str,
    ) -> list[RecommendationDTO]:
        """Generate new recommendations."""
        raise NotImplementedError


class IHospitalGateway(IDomainGateway[HospitalDTO]):
    """Gateway interface for Hospital/Capacity domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> HospitalDTO | None:
        """Get campus/hospital by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_departments(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> list[DepartmentDTO]:
        """Get departments for a campus."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_capacity(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> CapacityDTO:
        """Get capacity information."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_available_beds(
        self,
        tenant_id: str,
        department_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get available beds."""
        raise NotImplementedError


class IWorkOrderGateway(IDomainGateway[WorkOrderDTO]):
    """Gateway interface for WorkOrder domain."""
    
    @abstractmethod
    async def get_by_id(
        self,
        work_order_id: str,
        tenant_id: str,
    ) -> WorkOrderDTO | None:
        """Get work order by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_pending(
        self,
        tenant_id: str,
        technician_id: str | None = None,
        limit: int = 20,
    ) -> list[WorkOrderDTO]:
        """Get pending work orders."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_sla_breached(
        self,
        tenant_id: str,
    ) -> list[WorkOrderDTO]:
        """Get SLA-breached work orders."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[WorkOrderDTO]:
        """Get work orders for a device."""
        raise NotImplementedError
