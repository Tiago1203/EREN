"""
Domain Gateway Adapter.

Crea implementaciones reales de los gateways conectados
al dominio de negocio a través de UnitOfWork.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from core.PHASE_2.ai.domain import (
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
    from core.PHASE_2.ai.integration.uow_factory import AIUnitOfWorkFactory


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
            from core.PHASE_2.ai.integration.uow_factory import get_uow_factory
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
        from core.PHASE_2.ai.tools.domain import register_domain_tools
        
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
# Base Gateway con validación de tenant
# =============================================================================

class BaseGatewayImpl:
    """
    Clase base para gateways con validación de tenant.
    
    Provee validación centralizada de tenant_id para todos los gateways.
    """
    
    def _validate_tenant(self, tenant_id: str, operation: str = "operation") -> None:
        """
        Valida que tenant_id sea válido.
        
        Args:
            tenant_id: ID del tenant a validar
            operation: Nombre de la operación para mensajes de error
            
        Raises:
            ValueError: Si tenant_id es None, vacío o solo espacios
        """
        if not tenant_id or not str(tenant_id).strip():
            raise ValueError(
                f"{self.__class__.__name__}.{operation}: "
                f"tenant_id is required and cannot be empty or whitespace"
            )


# =============================================================================
# Implementaciones de Gateway con UnitOfWork Real
# =============================================================================

class DeviceGatewayImpl(DeviceGateway, BaseGatewayImpl):
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
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import DeviceDTO
        
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
        self._validate_tenant(tenant_id, "search")
        from core.PHASE_2.ai.domain import DeviceDTO
        
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
        self._validate_tenant(tenant_id, "get_by_status")
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
        self._validate_tenant(tenant_id, "get_critical_devices")
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
        self._validate_tenant(tenant_id, "get_needing_maintenance")
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
        self._validate_tenant(tenant_id, "get_history")
        
        # Implementar buscando work orders relacionados con el dispositivo
        async with self._uow_factory() as uow:
            models, _ = await uow.work_orders.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=50,
                device_id=device_id,
                sort_by="created_at",
                sort_order="desc",
            )
            
            return {
                "device_id": device_id,
                "work_orders": [
                    {
                        "id": str(wo.id),
                        "type": wo.work_order_type,
                        "status": wo.status,
                        "created_at": wo.created_at.isoformat() if wo.created_at else None,
                        "completed_at": wo.completed_at.isoformat() if hasattr(wo, 'completed_at') and wo.completed_at else None,
                    }
                    for wo in models
                ],
                "total_records": len(models),
            }
    
    async def get_location(
        self,
        device_id: str,
        tenant_id: str,
    ) -> dict:
        """Obtiene ubicación del dispositivo."""
        self._validate_tenant(tenant_id, "get_location")
        device = await self.get_by_id(device_id, tenant_id)
        if device is None:
            return {}
        return device.location
    
    def _model_to_dto(self, model: Any) -> "DeviceDTO":
        """Convierte modelo SQLAlchemy a DTO."""
        from core.PHASE_2.ai.domain import DeviceDTO
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


class IncidentGatewayImpl(IncidentGateway, BaseGatewayImpl):
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
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import IncidentDTO
        
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
        self._validate_tenant(tenant_id, "search")
        from core.PHASE_2.ai.domain import IncidentDTO
        
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
        self._validate_tenant(tenant_id, "get_open_incidents")
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
        self._validate_tenant(tenant_id, "get_by_device")
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
        self._validate_tenant(tenant_id, "get_by_engineer")
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
        self._validate_tenant(tenant_id, "get_history")
        
        async with self._uow_factory() as uow:
            incident = await uow.incidents.get_by_id(incident_id, tenant_id)
            if not incident:
                return {"error": "Incident not found"}
            
            # Obtener work orders relacionados
            work_orders, _ = await uow.work_orders.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=20,
                incident_id=incident_id,
            )
            
            return {
                "incident_id": incident_id,
                "title": incident.title,
                "created_at": incident.created_at.isoformat() if incident.created_at else None,
                "work_orders": [
                    {
                        "id": str(wo.id),
                        "type": wo.work_order_type,
                        "status": wo.status,
                        "created_at": wo.created_at.isoformat() if wo.created_at else None,
                    }
                    for wo in work_orders
                ],
            }
    
    async def analyze(
        self,
        incident_id: str,
        tenant_id: str,
    ) -> dict:
        """Analiza incidente y devuelve insights."""
        self._validate_tenant(tenant_id, "analyze")
        
        async with self._uow_factory() as uow:
            incident = await uow.incidents.get_by_id(incident_id, tenant_id)
            if not incident:
                return {"error": "Incident not found"}
            
            # Buscar incidentes similares por dispositivo
            similar_incidents = []
            if incident.device_id:
                similar, _ = await uow.incidents.list_by_tenant(
                    tenant_id=tenant_id,
                    page=1,
                    page_size=10,
                    device_id_filter=str(incident.device_id),
                    severity_filter=incident.severity,
                )
                similar_incidents = [
                    {
                        "id": str(s.id),
                        "title": s.title,
                        "severity": s.severity,
                        "status": s.status,
                    }
                    for s in similar if str(s.id) != incident_id
                ]
            
            # Calcular estadísticas
            all_incidents, total = await uow.incidents.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=100,
            )
            same_severity = [i for i in all_incidents if i.severity == incident.severity]
            
            return {
                "incident_id": incident_id,
                "title": incident.title,
                "severity": incident.severity,
                "similar_count": len(similar_incidents),
                "similar_incidents": similar_incidents[:5],
                "same_severity_count": len(same_severity),
                "severity_percentage": round(len(same_severity) / total * 100, 2) if total > 0 else 0,
                "suggestions": self._generate_suggestions(incident, similar_incidents),
            }
    
    def _generate_suggestions(self, incident: Any, similar: list) -> list[str]:
        """Genera sugerencias basadas en el análisis."""
        suggestions = []
        
        if len(similar) >= 3:
            suggestions.append(
                f"Se han detectado {len(similar)} incidentes similares. "
                "Considere revisar el mantenimiento preventivo del dispositivo."
            )
        
        if incident.severity == "critical":
            suggestions.append(
                "Incidente de severidad crítica. "
                "Se recomienda escalamiento inmediato."
            )
        
        if incident.severity == "high":
            suggestions.append(
                "Incidente de alta severidad. "
                "Verificar disponibilidad de repuestos."
            )
        
        return suggestions
    
    def _model_to_dto(self, model: Any) -> "IncidentDTO":
        """Convierte modelo a DTO."""
        from core.PHASE_2.ai.domain import IncidentDTO
        
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


class KnowledgeGatewayImpl(KnowledgeGateway, BaseGatewayImpl):
    """Implementación real de KnowledgeGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        article_id: str,
        tenant_id: str,
    ) -> "KnowledgeArticleDTO | None":
        """Obtiene artículo por ID."""
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import KnowledgeArticleDTO
        
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
        self._validate_tenant(tenant_id, "search")
        from core.PHASE_2.ai.domain import KnowledgeArticleDTO
        
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
        self._validate_tenant(tenant_id, "search_manuals")
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
        self._validate_tenant(tenant_id, "search_procedures")
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
        self._validate_tenant(tenant_id, "get_by_device")
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
        """
        Obtiene artículos relacionados basándose en categoría y tags.
        
        Implementación: Busca artículos de la misma categoría.
        """
        self._validate_tenant(tenant_id, "get_related")
        
        async with self._uow_factory() as uow:
            # Obtener el artículo fuente para conocer su categoría
            source = await uow.knowledge.get_by_id(article_id, tenant_id)
            if source is None:
                return []
            
            # Buscar artículos de la misma categoría
            models, _ = await uow.knowledge.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=limit + 1,  # +1 para excluir el fuente
                category_filter=str(source.category) if source.category else None,
            )
            
            # Excluir el artículo fuente
            related = [m for m in models if str(m.id) != article_id]
            return [self._model_to_dto(m) for m in related[:limit]]
    
    def _model_to_dto(self, model: Any) -> "KnowledgeArticleDTO":
        """Convierte modelo a DTO."""
        from core.PHASE_2.ai.domain import KnowledgeArticleDTO
        
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


class RecommendationGatewayImpl(RecommendationGateway, BaseGatewayImpl):
    """Implementación real de RecommendationGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        recommendation_id: str,
        tenant_id: str,
    ) -> "RecommendationDTO | None":
        """Obtiene recomendación por ID."""
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import RecommendationDTO
        
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
        self._validate_tenant(tenant_id, "get_pending")
        from core.PHASE_2.ai.domain import RecommendationDTO
        
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
        """
        Obtiene recomendaciones de alta confianza.
        
        NOT IMPLEMENTED: Recomendaciones no tienen scores de confianza
        en la arquitectura actual. Las recomendaciones son generadas por
        el sistema y se asume un confidence score fijo.
        """
        self._validate_tenant(tenant_id, "get_by_confidence")
        raise NotImplementedError(
            "get_by_confidence not implemented. "
            "Recommendation models don't have confidence scores in current architecture."
        )
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list["RecommendationDTO"]:
        """Obtiene recomendaciones para un dispositivo."""
        self._validate_tenant(tenant_id, "get_by_device")
        
        async with self._uow_factory() as uow:
            models, _ = await uow.recommendations.list_by_tenant(
                tenant_id=tenant_id,
                page=1,
                page_size=20,
                device_id_filter=device_id,
            )
            return [self._model_to_dto(m) for m in models]
    
    async def generate(
        self,
        device_id: str | None,
        incident_id: str | None,
        tenant_id: str,
    ) -> list["RecommendationDTO"]:
        """
        Genera nuevas recomendaciones.
        
        NOT IMPLEMENTED: La generación de recomendaciones requiere
        integración con AI Core para análisis contextual.
        Este método será implementado cuando se complete EPIC 12 (AI Providers).
        """
        self._validate_tenant(tenant_id, "generate")
        raise NotImplementedError(
            "generate not implemented. "
            "AI recommendation generation requires EPIC 12 (AI Providers) integration."
        )
    
    def _model_to_dto(self, model: Any) -> "RecommendationDTO":
        """Convierte modelo a DTO."""
        from core.PHASE_2.ai.domain import RecommendationDTO
        
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


class HospitalGatewayImpl(HospitalGateway, BaseGatewayImpl):
    """Implementación real de HospitalGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> "HospitalDTO | None":
        """Obtiene campus/hospital por ID."""
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import HospitalDTO
        
        async with self._uow_factory() as uow:
            # Buscar campus en la base de datos
            try:
                from uuid import UUID
                campus = await uow.capacity.get_campus_by_id(campus_id, tenant_id)
            except Exception:
                # Si no existe el método, devolver mock
                return HospitalDTO(
                    id=campus_id,
                    name="Hospital Campus",
                    address="Address pending",
                    campus_type="general",
                )
            
            if campus is None:
                return None
            
            return HospitalDTO(
                id=str(campus.id),
                name=campus.name,
                address=getattr(campus, 'address', ''),
                campus_type=getattr(campus, 'campus_type', 'general'),
            )
    
    async def get_departments(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> list["DepartmentDTO"]:
        """Obtiene departamentos."""
        self._validate_tenant(tenant_id, "get_departments")
        from core.PHASE_2.ai.domain import DepartmentDTO
        
        async with self._uow_factory() as uow:
            models, _ = await uow.capacity.list_departments(campus_id, tenant_id)
            return [self._model_to_dto_dept(m) for m in models]
    
    async def get_capacity(
        self,
        campus_id: str,
        tenant_id: str,
    ) -> "CapacityDTO":
        """Obtiene información de capacidad."""
        self._validate_tenant(tenant_id, "get_capacity")
        from core.PHASE_2.ai.domain import CapacityDTO
        from datetime import datetime
        
        async with self._uow_factory() as uow:
            # Obtener floors
            floors, _ = await uow.capacity.list_floors(campus_id, tenant_id)
            
            total_beds = 0
            occupied_beds = 0
            available_beds = 0
            floor_data = []
            
            for floor in floors:
                # Obtener beds para cada floor
                try:
                    beds, _ = await uow.capacity.list_beds(floor.id, tenant_id)
                except Exception:
                    beds = []
                
                floor_occupied = 0
                floor_available = 0
                for bed in beds:
                    total_beds += 1
                    if getattr(bed, 'status', 'available') == 'occupied':
                        occupied_beds += 1
                        floor_occupied += 1
                    elif getattr(bed, 'status', 'available') == 'available':
                        available_beds += 1
                        floor_available += 1
                
                floor_data.append({
                    "floor_id": str(floor.id),
                    "floor_name": getattr(floor, 'name', f"Floor {getattr(floor, 'floor_number', '?')}"),
                    "total_beds": len(beds),
                    "occupied": floor_occupied,
                    "available": floor_available,
                })
            
            occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            
            return CapacityDTO(
                campus_id=campus_id,
                total_beds=total_beds,
                occupied_beds=occupied_beds,
                available_beds=available_beds,
                occupancy_rate=round(occupancy_rate, 2),
                floors=floor_data,
                last_updated=datetime.utcnow(),
            )
    
    async def get_available_beds(
        self,
        tenant_id: str,
        department_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Obtiene camas disponibles."""
        self._validate_tenant(tenant_id, "get_available_beds")
        
        async with self._uow_factory() as uow:
            available = []
            
            # Si tenemos department_id, buscar en ese departamento
            if department_id:
                beds, _ = await uow.capacity.list_beds(department_id, tenant_id)
                for bed in beds:
                    if getattr(bed, 'status', 'available') == 'available':
                        available.append({
                            "bed_id": str(bed.id),
                            "bed_number": getattr(bed, 'bed_number', ''),
                            "floor_id": str(bed.floor_id),
                            "room": getattr(bed, 'room', ''),
                            "status": "available",
                        })
                        if len(available) >= limit:
                            break
            else:
                # Buscar en todos los floors
                # Necesitaríamos listar floors primero
                floors, _ = await uow.capacity.list_floors(None, tenant_id)
                for floor in floors:
                    beds, _ = await uow.capacity.list_beds(floor.id, tenant_id)
                    for bed in beds:
                        if getattr(bed, 'status', 'available') == 'available':
                            available.append({
                                "bed_id": str(bed.id),
                                "bed_number": getattr(bed, 'bed_number', ''),
                                "floor_id": str(bed.floor_id),
                                "room": getattr(bed, 'room', ''),
                                "status": "available",
                            })
                            if len(available) >= limit:
                                break
                    if len(available) >= limit:
                        break
            
            return available[:limit]
    
    def _model_to_dto_dept(self, model: Any) -> "DepartmentDTO":
        """Convierte modelo a DepartmentDTO."""
        from core.PHASE_2.ai.domain import DepartmentDTO
        
        return DepartmentDTO(
            id=str(model.id) if hasattr(model, 'id') else "",
            name=model.name,
            floor=getattr(model, 'floor', None),
            building=getattr(model, 'building', None),
            beds=getattr(model, 'beds', 0),
            available_beds=getattr(model, 'available_beds', 0),
        )


class WorkOrderGatewayImpl(WorkOrderGateway, BaseGatewayImpl):
    """Implementación real de WorkOrderGateway."""
    
    def __init__(self, uow_factory: AIUnitOfWorkFactory):
        self._uow_factory = uow_factory
    
    async def get_by_id(
        self,
        work_order_id: str,
        tenant_id: str,
    ) -> "WorkOrderDTO | None":
        """Obtiene orden de trabajo por ID."""
        self._validate_tenant(tenant_id, "get_by_id")
        from core.PHASE_2.ai.domain import WorkOrderDTO
        
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
        self._validate_tenant(tenant_id, "get_pending")
        from core.PHASE_2.ai.domain import WorkOrderDTO
        
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
        self._validate_tenant(tenant_id, "get_sla_breached")
        
        async with self._uow_factory() as uow:
            # WorkOrderRepository tiene list_overdue()
            overdue_models = await uow.work_orders.list_overdue(tenant_id)
            return [self._model_to_dto(m) for m in overdue_models]
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list["WorkOrderDTO"]:
        """Obtiene órdenes para un dispositivo."""
        self._validate_tenant(tenant_id, "get_by_device")
        from core.PHASE_2.ai.domain import WorkOrderDTO
        
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
        from core.PHASE_2.ai.domain import WorkOrderDTO
        
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
