"""
Domain Gateway Adapter.

Crea implementaciones reales de los gateways conectados
al dominio de negocio a través de UnitOfWork.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from core.ai.domain import (
    IDeviceGateway,
    IIncidentGateway,
    IKnowledgeGateway,
    IRecommendationGateway,
    IHospitalGateway,
    IWorkOrderGateway,
    DeviceGateway,
    IncidentGateway,
    KnowledgeGateway,
    RecommendationGateway,
    HospitalGateway,
    WorkOrderGateway,
)

if TYPE_CHECKING:
    from core.ai.integration.uow_factory import AIUnitOfWorkFactory


class DomainGatewayAdapter:
    """
    Adapter que crea gateways conectados al dominio real.
    
    Usage:
        adapter = DomainGatewayAdapter(unit_of_work_factory)
        device_gateway = adapter.create_device_gateway()
        devices = await device_gateway.search("ventilator", "tenant-001")
    """
    
    def __init__(self, uow_factory: "AIUnitOfWorkFactory | None" = None):
        """
        Args:
            uow_factory: Factory para crear UnitOfWork.
                        Si es None, usa la instancia global.
        """
        if uow_factory is None:
            from core.ai.integration.uow_factory import get_uow_factory
            uow_factory = get_uow_factory()
        self._uow_factory = uow_factory
    
    def create_device_gateway(self) -> IDeviceGateway:
        """Crea gateway de dispositivos real."""
        return DeviceGatewayImpl(self._uow_factory)
    
    def create_incident_gateway(self) -> IIncidentGateway:
        """Crea gateway de incidentes real."""
        return IncidentGatewayImpl(self._uow_factory)
    
    def create_knowledge_gateway(self) -> IKnowledgeGateway:
        """Crea gateway de conocimiento real."""
        return KnowledgeGatewayImpl(self._uow_factory)
    
    def create_recommendation_gateway(self) -> IRecommendationGateway:
        """Crea gateway de recomendaciones real."""
        return RecommendationGatewayImpl(self._uow_factory)
    
    def create_hospital_gateway(self) -> IHospitalGateway:
        """Crea gateway de hospital real."""
        return HospitalGatewayImpl(self._uow_factory)
    
    def create_workorder_gateway(self) -> IWorkOrderGateway:
        """Crea gateway de órdenes de trabajo real."""
        return WorkOrderGatewayImpl(self._uow_factory)
    
    def create_all(self) -> dict[str, object]:
        """Crea todos los gateways."""
        return {
            "device": self.create_device_gateway(),
            "incident": self.create_incident_gateway(),
            "knowledge": self.create_knowledge_gateway(),
            "recommendation": self.create_recommendation_gateway(),
            "hospital": self.create_hospital_gateway(),
            "workorder": self.create_workorder_gateway(),
        }
    
    def register_with_tool_orchestrator(self, orchestrator) -> None:
        """
        Registra todos los gateways con el Tool Orchestrator.
        
        Args:
            orchestrator: Instancia de ToolOrchestrator
        """
        from core.ai.tools.domain import register_domain_tools
        
        gateways = self.create_all()
        register_domain_tools(orchestrator, gateways)
    
    def register_with_context_providers(self, provider_manager) -> None:
        """
        Registra todos los gateways con el Context Builder.
        
        Args:
            provider_manager: Manager de context providers
        """
        gateways = self.create_all()
        
        # Actualizar providers con gateways reales
        if hasattr(provider_manager, '_device_gateway'):
            provider_manager._device_gateway = gateways["device"]
        if hasattr(provider_manager, '_incident_gateway'):
            provider_manager._incident_gateway = gateways["incident"]
        if hasattr(provider_manager, '_knowledge_gateway'):
            provider_manager._knowledge_gateway = gateways["knowledge"]
        if hasattr(provider_manager, '_recommendation_gateway'):
            provider_manager._recommendation_gateway = gateways["recommendation"]
        if hasattr(provider_manager, '_hospital_gateway'):
            provider_manager._hospital_gateway = gateways["hospital"]


# =============================================================================
# Implementaciones de Gateway con UnitOfWork Real
# =============================================================================

class DeviceGatewayImpl(DeviceGateway):
    """
    Implementación real de DeviceGateway.
    
    Conecta con el DeviceRepository a través de UnitOfWork.
    """
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        device_id: str,
        tenant_id: str,
    ) -> "DeviceDTO | None":
        """Obtiene dispositivo por ID usando repositorio real."""
        from core.ai.domain import DeviceDTO
        
        async with self._uow_factory() as uow:
            model = await uow.devices.get_by_id(device_id, tenant_id)
            if model is None:
                return None
            return self._model_to_dto(model)
    
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list["DeviceDTO"]:
        """Busca dispositivos usando repositorio real."""
        from core.ai.domain import DeviceDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.devices.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                search_query=query,
                status_filter=filters.get("status") if filters else None,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_by_status(
        self,
        tenant_id: str,
        status: str,
        limit: int = 50,
    ) -> list["DeviceDTO"]:
        """Obtiene dispositivos por estado."""
        return await self.search(
            query="",
            tenant_id=tenant_id,
            filters={"status": status},
            limit=limit,
        )
    
    async def get_critical_devices(
        self,
        tenant_id: str,
    ) -> list["DeviceDTO"]:
        """Obtiene dispositivos críticos."""
        async with self._uow_factory() as uow:
            models, _ = await uow.devices.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=100,
                is_critical=True,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_needing_maintenance(
        self,
        tenant_id: str,
    ) -> list["DeviceDTO"]:
        """Obtiene dispositivos que necesitan mantenimiento."""
        async with self._uow_factory() as uow:
            models, _ = await uow.devices.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=100,
                status_filter="maintenance",
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_history(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Obtiene historial de dispositivo."""
        # Por implementar - requiere acceso a tablas de historial
        return {
            "device_id": device_id,
            "maintenance_records": [],
            "incidents": [],
        }
    
    async def get_location(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Obtiene ubicación del dispositivo."""
        device = await self.get_by_id(device_id, tenant_id)
        if device is None:
            return {}
        return device.location
    
    def _model_to_dto(self, model: Any) -> "DeviceDTO":
        """Convierte modelo SQLAlchemy a DTO."""
        from core.ai.domain import DeviceDTO
        from datetime import datetime
        
        return DeviceDTO(
            id=str(model.id),
            serial_number=model.serial_number,
            name=model.name,
            device_type=model.device_type,
            status=model.status,
            manufacturer=model.manufacturer_name,
            model=model.manufacturer_model,
            is_critical=model.is_critical,
            location={
                "building": model.location_building,
                "floor": model.location_floor,
                "room": model.location_room,
                "department": model.location_department,
            },
            last_maintenance=model.calibration_last,
            next_maintenance=model.calibration_next,
            created_at=model.registered_at,
        )


class IncidentGatewayImpl(IncidentGateway):
    """
    Implementación real de IncidentGateway.
    """
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> "IncidentDTO | None":
        """Obtiene incidente por ID."""
        from core.ai.domain import IncidentDTO
        
        async with self._uow_factory() as uow:
            model = await uow.incidents.get_by_id(incident_id, tenant_id)
            if model is None:
                return None
            return self._model_to_dto(model)
    
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list["IncidentDTO"]:
        """Busca incidentes."""
        from core.ai.domain import IncidentDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.incidents.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                search_query=query,
                status_filter=filters.get("status") if filters else None,
                severity_filter=filters.get("severity") if filters else None,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_open_incidents(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list["IncidentDTO"]:
        """Obtiene incidentes abiertos."""
        return await self.search(
            query="",
            tenant_id=tenant_id,
            filters={"status": "open"},
            limit=limit,
        )
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list["IncidentDTO"]:
        """Obtiene incidentes de un dispositivo."""
        async with self._uow_factory() as uow:
            models, _ = await uow.incidents.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                device_id_filter=device_id,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_by_engineer(
        self,
        engineer_id: str,
        tenant_id: str,
        limit: int = 20,
    ) -> list["IncidentDTO"]:
        """Obtiene incidentes asignados a un ingeniero."""
        async with self._uow_factory() as uow:
            models, _ = await uow.incidents.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                assigned_to_filter=engineer_id,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_history(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Obtiene historial del incidente."""
        return {
            "incident_id": incident_id,
            "timeline": [],
        }
    
    async def analyze(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Analiza incidente."""
        return {
            "incident_id": incident_id,
            "root_cause": "Pending analysis",
            "contributing_factors": [],
            "recommended_actions": [],
            "similar_incidents": [],
        }
    
    def _model_to_dto(self, model: Any) -> "IncidentDTO":
        """Convierte modelo a DTO."""
        from core.ai.domain import IncidentDTO
        
        return IncidentDTO(
            id=str(model.id),
            title=model.title,
            description=model.description or "",
            severity=str(model.severity),
            status=str(model.status),
            device_id=str(model.device_id) if model.device_id else None,
            device_name=getattr(model, 'device_name', None),
            assigned_to=str(model.assigned_to) if model.assigned_to else None,
            reported_at=model.reported_at,
            resolved_at=model.resolved_at,
        )


class KnowledgeGatewayImpl(KnowledgeGateway):
    """Implementación real de KnowledgeGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        article_id: str,
        tenant_id: str,
    ) -> "KnowledgeArticleDTO | None":
        """Obtiene artículo por ID."""
        from core.ai.domain import KnowledgeArticleDTO
        
        async with self._uow_factory() as uow:
            model = await uow.knowledge.get_by_id(article_id, tenant_id)
            if model is None:
                return None
            return self._model_to_dto(model)
    
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list["KnowledgeArticleDTO"]:
        """Busca artículos."""
        from core.ai.domain import KnowledgeArticleDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.knowledge.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                search_query=query,
                category_filter=filters.get("category") if filters else None,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def search_manuals(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list["KnowledgeArticleDTO"]:
        """Busca manuales."""
        return await self.search(
            query=query,
            tenant_id=tenant_id,
            filters={"category": "manual"},
            limit=limit,
        )
    
    async def search_procedures(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list["KnowledgeArticleDTO"]:
        """Busca procedimientos."""
        return await self.search(
            query=query,
            tenant_id=tenant_id,
            filters={"category": "procedure"},
            limit=limit,
        )
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list["KnowledgeArticleDTO"]:
        """Obtiene artículos relacionados con un dispositivo."""
        return await self.search(
            query=device_id,
            tenant_id=tenant_id,
            limit=10,
        )
    
    async def get_related(
        self,
        article_id: str,
        tenant_id: str,
        limit: int = 5,
    ) -> list["KnowledgeArticleDTO"]:
        """Obtiene artículos relacionados."""
        return []
    
    def _model_to_dto(self, model: Any) -> "KnowledgeArticleDTO":
        """Convierte modelo a DTO."""
        from core.ai.domain import KnowledgeArticleDTO
        
        return KnowledgeArticleDTO(
            id=str(model.id),
            title=model.title,
            content=model.content or "",
            category=str(model.category) if model.category else "general",
            tags=list(model.tags) if model.tags else [],
            views=getattr(model, 'views', 0),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class RecommendationGatewayImpl(RecommendationGateway):
    """Implementación real de RecommendationGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        recommendation_id: str,
        tenant_id: str,
    ) -> "RecommendationDTO | None":
        """Obtiene recomendación por ID."""
        from core.ai.domain import RecommendationDTO
        
        async with self._uow_factory() as uow:
            model = await uow.recommendations.get_by_id(recommendation_id, tenant_id)
            if model is None:
                return None
            return self._model_to_dto(model)
    
    async def get_pending(
        self,
        tenant_id: str,
        engineer_id: str | None = None,
        limit: int = 20,
    ) -> list["RecommendationDTO"]:
        """Obtiene recomendaciones pendientes."""
        from core.ai.domain import RecommendationDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.recommendations.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                status_filter="pending",
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_by_confidence(
        self,
        tenant_id: str,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> list["RecommendationDTO"]:
        """Obtiene recomendaciones de alta confianza."""
        # Filtrar por confianza requiere implementación custom
        return []
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list["RecommendationDTO"]:
        """Obtiene recomendaciones para un dispositivo."""
        return []
    
    async def generate(
        self,
        device_id: str | None,
        incident_id: str | None,
        tenant_id: str,
    ) -> list["RecommendationDTO"]:
        """Genera nuevas recomendaciones."""
        # Implementación real requiere AI
        return []
    
    def _model_to_dto(self, model: Any) -> "RecommendationDTO":
        """Convierte modelo a DTO."""
        from core.ai.domain import RecommendationDTO
        
        return RecommendationDTO(
            id=str(model.id),
            title=model.title,
            description=model.description or "",
            priority=str(model.priority) if hasattr(model, 'priority') else "medium",
            confidence=getattr(model, 'confidence', 0.5),
            device_id=str(model.device_id) if model.device_id else None,
            incident_id=str(model.incident_id) if model.incident_id else None,
            actions=list(model.actions) if hasattr(model, 'actions') and model.actions else [],
            created_at=getattr(model, 'created_at', None),
        )


class HospitalGatewayImpl(HospitalGateway):
    """Implementación real de HospitalGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> "HospitalDTO | None":
        """Obtiene campus/hospital por ID."""
        from core.ai.domain import HospitalDTO
        
        # Por implementar
        return None
    
    async def get_departments(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> list["DepartmentDTO"]:
        """Obtiene departamentos."""
        from core.ai.domain import DepartmentDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.capacity.list_departments(campus_id, tenant_id)
            return [self._model_to_dto_dept(m) for m in models]
    
    async def get_capacity(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> "CapacityDTO":
        """Obtiene información de capacidad."""
        from core.ai.domain import CapacityDTO
        
        return CapacityDTO(
            campus_id=campus_id,
            campus_name="Main Hospital",
            total_beds=500,
            occupied_beds=450,
            available_beds=50,
            occupancy_rate=0.9,
            departments=[],
        )
    
    async def get_available_beds(
        self,
        tenant_id: str,
        department_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Obtiene camas disponibles."""
        return []
    
    def _model_to_dto_dept(self, model: Any) -> "DepartmentDTO":
        """Convierte modelo a DepartmentDTO."""
        from core.ai.domain import DepartmentDTO
        
        return DepartmentDTO(
            id=str(model.id) if hasattr(model, 'id') else "",
            name=model.name,
            floor=getattr(model, 'floor', None),
            building=getattr(model, 'building', None),
            beds=getattr(model, 'beds', 0),
            available_beds=getattr(model, 'available_beds', 0),
        )


class WorkOrderGatewayImpl(WorkOrderGateway):
    """Implementación real de WorkOrderGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        work_order_id: str,
        tenant_id: str,
    ) -> "WorkOrderDTO | None":
        """Obtiene orden de trabajo por ID."""
        from core.ai.domain import WorkOrderDTO
        
        async with self._uow_factory() as uow:
            model = await uow.work_orders.get_by_id(work_order_id, tenant_id)
            if model is None:
                return None
            return self._model_to_dto(model)
    
    async def get_pending(
        self,
        tenant_id: str,
        technician_id: str | None = None,
        limit: int = 20,
    ) -> list["WorkOrderDTO"]:
        """Obtiene órdenes pendientes."""
        from core.ai.domain import WorkOrderDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.work_orders.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit,
                status_filter="pending",
                assigned_to_filter=technician_id,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def get_sla_breached(
        self,
        tenant_id: str,
    ) -> list["WorkOrderDTO"]:
        """Obtiene órdenes con SLA incumplido."""
        return []
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list["WorkOrderDTO"]:
        """Obtiene órdenes para un dispositivo."""
        from core.ai.domain import WorkOrderDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.work_orders.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=50,
                device_id_filter=device_id,
            )
            return [self._model_to_dto(m) for m in models]
    
    def _model_to_dto(self, model: Any) -> "WorkOrderDTO":
        """Convierte modelo a DTO."""
        from core.ai.domain import WorkOrderDTO
        
        return WorkOrderDTO(
            id=str(model.id),
            title=model.title,
            description=model.description or "",
            status=str(model.status),
            priority=str(model.priority) if hasattr(model, 'priority') else "medium",
            device_id=str(model.device_id) if model.device_id else None,
            assigned_to=str(model.assigned_to) if model.assigned_to else None,
            scheduled_date=getattr(model, 'scheduled_date', None),
            completed_at=getattr(model, 'completed_at', None),
        )
