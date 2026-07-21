"""
Memory Bridge - Almacena referencias a entidades del dominio.

Permite que las memorias del AI Core referencien
entidades reales del Business Domain.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.ai.memory.manager import MemoryManager
    from core.ai.integration.domain_adapter import DomainGatewayAdapter


class EntityType(str, Enum):
    """Tipos de entidades del dominio que pueden ser referenciadas."""
    DEVICE = "device"
    INCIDENT = "incident"
    KNOWLEDGE = "knowledge"
    RECOMMENDATION = "recommendation"
    HOSPITAL = "hospital"
    DEPARTMENT = "department"
    WORK_ORDER = "work_order"
    STAFF = "staff"


@dataclass(frozen=True)
class DomainReference:
    """
    Referencia a una entidad del dominio.
    
    Permite que la memoria referencie entidades reales
    sin copiar todos sus datos.
    """
    entity_type: EntityType
    entity_id: str
    display_name: str
    metadata: dict = field(default_factory=dict)
    
    def to_string(self) -> str:
        """Convierte a representación string para almacenamiento."""
        return json.dumps({
            "type": self.entity_type.value,
            "id": self.entity_id,
            "name": self.display_name,
            "metadata": self.metadata,
        })
    
    @classmethod
    def from_string(cls, data: str) -> DomainReference:
        """Crea desde string."""
        parsed = json.loads(data)
        return cls(
            entity_type=EntityType(parsed["type"]),
            entity_id=parsed["id"],
            display_name=parsed["name"],
            metadata=parsed.get("metadata", {}),
        )
    
    @staticmethod
    def from_dto(dto: Any) -> DomainReference:
        """Crea referencia desde un DTO."""
        # Mapear tipo de DTO a EntityType
        dto_type = type(dto).__name__
        entity_type_map = {
            "DeviceDTO": EntityType.DEVICE,
            "IncidentDTO": EntityType.INCIDENT,
            "KnowledgeArticleDTO": EntityType.KNOWLEDGE,
            "RecommendationDTO": EntityType.RECOMMENDATION,
            "HospitalDTO": EntityType.HOSPITAL,
            "DepartmentDTO": EntityType.DEPARTMENT,
            "WorkOrderDTO": EntityType.WORK_ORDER,
        }
        entity_type = entity_type_map.get(dto_type, EntityType.DEVICE)
        
        return DomainReference(
            entity_type=entity_type,
            entity_id=dto.id,
            display_name=getattr(dto, 'name', getattr(dto, 'title', str(dto.id))),
            metadata={
                "dto_type": dto_type,
            },
        )


@dataclass
class MemoryWithReferences:
    """Memoria con sus referencias a dominio."""
    memory_id: str
    content: str
    references: list[DomainReference]
    tenant_id: str | None
    user_id: str | None


class MemoryBridge:
    """
    Bridge entre MemoryManager y Domain.
    
    Permite almacenar y recuperar referencias a entidades
    del dominio asociadas a memorias.
    
    Usage:
        bridge = MemoryBridge(memory_manager, domain_adapter)
        
        # Almacenar con referencia
        memory_id = bridge.store_with_reference(
            content="Device needs maintenance",
            reference=DomainReference(
                entity_type=EntityType.DEVICE,
                entity_id="dev-001",
                display_name="Ventilator ICU-1",
            ),
            tenant_id="tenant-001",
        )
        
        # Recuperar con referencias
        memory = bridge.get_with_references(memory_id)
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        domain_adapter: DomainGatewayAdapter | None = None,
    ):
        self._memory = memory_manager
        self._adapter = domain_adapter
    
    def store_with_reference(
        self,
        content: str,
        reference: DomainReference,
        tenant_id: str | None = None,
        user_id: str | None = None,
        memory_type: str = "semantic",
        importance: str = "medium",
        tags: list[str] | None = None,
    ) -> str:
        """
        Almacena una memoria con referencia a dominio.
        
        Args:
            content: Contenido textual de la memoria
            reference: Referencia a entidad del dominio
            tenant_id: ID del tenant
            user_id: ID del usuario
            memory_type: Tipo de memoria
            importance: Importancia
            tags: Etiquetas adicionales
            
        Returns:
            ID de la memoria creada
        """
        from core.ai.memory.models import MemoryImportance, MemoryType
        
        # Mapear strings a enums
        type_map = {
            "working": MemoryType.WORKING,
            "short": MemoryType.SHORT,
            "long": MemoryType.LONG,
            "semantic": MemoryType.SEMANTIC,
            "episodic": MemoryType.EPISODIC,
        }
        mem_type = type_map.get(memory_type.lower(), MemoryType.SEMANTIC)
        
        importance_map = {
            "low": MemoryImportance.LOW,
            "medium": MemoryImportance.MEDIUM,
            "high": MemoryImportance.HIGH,
            "critical": MemoryImportance.CRITICAL,
        }
        mem_importance = importance_map.get(importance.lower(), MemoryImportance.MEDIUM)
        
        # Combinar contenido con referencia serializada
        full_content = f"{content}\n\n[Reference: {reference.to_string()}]"
        
        # Crear tags con referencia
        reference_tags = list(tags) if tags else []
        reference_tags.append(f"ref:{reference.entity_type.value}")
        reference_tags.append(f"id:{reference.entity_id}")
        
        # Almacenar en memoria
        item = self._memory.store(
            content=full_content,
            memory_type=mem_type,
            tenant_id=tenant_id,
            user_id=user_id,
            importance=mem_importance,
            tags=reference_tags,
            metadata={
                "has_domain_reference": True,
                "entity_type": reference.entity_type.value,
                "entity_id": reference.entity_id,
            },
        )
        
        return item.id
    
    def store_with_references(
        self,
        content: str,
        references: list[DomainReference],
        **kwargs,
    ) -> str:
        """Almacena memoria con múltiples referencias."""
        # Crear contenido combinado
        ref_strings = [ref.to_string() for ref in references]
        full_content = f"{content}\n\n[References: {json.dumps(ref_strings)}]"
        
        # Extraer todos los tags
        all_tags = list(kwargs.get("tags", []))
        for ref in references:
            all_tags.append(f"ref:{ref.entity_type.value}")
        
        # Agregar metadata
        metadata = kwargs.get("metadata", {})
        metadata["has_domain_reference"] = True
        metadata["entity_types"] = list(set(r.entity_type.value for r in references))
        kwargs["metadata"] = metadata
        
        return self._memory.store(
            content=full_content,
            tags=all_tags,
            **kwargs,
        ).id
    
    async def get_with_references(
        self,
        memory_id: str,
        resolve: bool = True,
        tenant_id: str | None = None,
    ) -> MemoryWithReferences | None:
        """
        Obtiene memoria con sus referencias.
        
        Args:
            memory_id: ID de la memoria
            resolve: Si True, resuelve las referencias a entidades reales
            tenant_id: Tenant ID para resolver referencias
            
        Returns:
            Memoria con referencias o None
        """
        item = self._memory.retrieve(memory_id)
        if not item:
            return None
        
        # Extraer referencias del contenido
        references = self._extract_references(item.content)
        
        # Usar tenant_id del item o el proporcionado
        effective_tenant_id = tenant_id or item.tenant_id or ""
        
        if resolve and references and self._adapter and effective_tenant_id:
            references = await self._resolve_references(references, effective_tenant_id)
        
        return MemoryWithReferences(
            memory_id=memory_id,
            content=item.content,
            references=references,
            tenant_id=item.tenant_id,
            user_id=item.user_id,
        )
    
    def search_by_reference(
        self,
        entity_type: EntityType,
        entity_id: str | None = None,
        tenant_id: str | None = None,
    ) -> list[MemoryWithReferences]:
        """
        Busca memorias por referencia de entidad.
        
        Args:
            entity_type: Tipo de entidad a buscar
            entity_id: ID específico (opcional)
            tenant_id: Filtrar por tenant
            
        Returns:
            Lista de memorias que referencian la entidad
        """
        # Buscar por tags
        tags = [f"ref:{entity_type.value}"]
        if entity_id:
            tags.append(f"id:{entity_id}")
        
        result = self._memory.search(
            tags=tags,
            tenant_id=tenant_id,
        )
        
        memories = []
        for item in result.items:
            references = self._extract_references(item.content)
            memories.append(MemoryWithReferences(
                memory_id=item.id,
                content=item.content,
                references=references,
                tenant_id=item.tenant_id,
                user_id=item.user_id,
            ))
        
        return memories
    
    def _extract_references(self, content: str) -> list[DomainReference]:
        """Extrae referencias del contenido."""
        references = []
        seen_ids = set()  # Evitar duplicados
        
        # Patrón más robusto que busca cualquier JSON válido después de [Reference o [References
        patterns = [
            # Patrón para [Reference: {"type": ..., "id": ...}]
            r'\[Reference:\s*(\{.*?\})\s*\]',
            # Patrón para [References: [ {"type": ...}, ... ] ]
            r'\[References:\s*(\[.*?\])\s*\]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    # Intentar parsear como JSON
                    data = json.loads(match)
                    if isinstance(data, list):
                        # Múltiples referencias
                        for ref_data in data:
                            ref = self._parse_ref_data(ref_data)
                            if ref and ref.entity_id not in seen_ids:
                                references.append(ref)
                                seen_ids.add(ref.entity_id)
                    elif isinstance(data, dict):
                        # Una sola referencia
                        ref = self._parse_ref_data(data)
                        if ref and ref.entity_id not in seen_ids:
                            references.append(ref)
                            seen_ids.add(ref.entity_id)
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue
        
        return references
    
    def _parse_ref_data(self, data: dict | str) -> DomainReference | None:
        """Parsea datos de referencia."""
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return DomainReference(
                entity_type=EntityType(data["type"]),
                entity_id=data["id"],
                display_name=data["name"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return None
    
    async def _resolve_references(
        self,
        references: list[DomainReference],
        tenant_id: str,
    ) -> list[DomainReference]:
        """Resuelve referencias a entidades reales usando el adapter."""
        if self._adapter is None:
            return references
        
        resolved = []
        
        for ref in references:
            resolved_ref = await self._resolve_reference(ref, tenant_id)
            if resolved_ref:
                resolved.append(resolved_ref)
            else:
                # Mantener la referencia sin resolver
                resolved.append(ref)
        
        return resolved
    
    async def _resolve_reference(
        self,
        ref: DomainReference,
        tenant_id: str,
    ) -> DomainReference | None:
        """Resuelve una referencia individual de forma async."""
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            if ref.entity_type == EntityType.DEVICE:
                gateway = self._adapter.create_device_gateway()
            elif ref.entity_type == EntityType.INCIDENT:
                gateway = self._adapter.create_incident_gateway()
            else:
                return None
            
            # Usar await correctamente en contexto async
            entity = await gateway.get_by_id(ref.entity_id, tenant_id)
            if entity:
                return DomainReference(
                    entity_type=ref.entity_type,
                    entity_id=ref.entity_id,
                    display_name=getattr(entity, 'name', getattr(entity, 'title', ref.display_name)),
                    metadata={
                        **ref.metadata,
                        "resolved": True,
                        "current_status": getattr(entity, 'status', None),
                    },
                )
        except Exception as e:
            logger.warning(
                f"Failed to resolve reference {ref.entity_type.value}:{ref.entity_id}: {e}"
            )
        
        return None


def create_memory_bridge(
    memory_manager: MemoryManager,
    domain_adapter: DomainGatewayAdapter | None = None,
) -> MemoryBridge:
    """
    Factory para crear MemoryBridge.
    
    Args:
        memory_manager: Instancia de MemoryManager
        domain_adapter: Adapter de dominios (opcional)
        
    Returns:
        Nueva instancia de MemoryBridge
    """
    return MemoryBridge(memory_manager, domain_adapter)
