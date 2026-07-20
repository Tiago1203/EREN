"""Prompt Versioning - Versionado de prompts."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VersionStatus(str, Enum):
    """Estado de una versión de prompt."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class PromptVersion:
    """Una versión específica de un template de prompt."""
    id: str
    template_id: str
    version: int
    
    # Contenido
    system_template: str
    user_template: str
    
    # Metadatos
    status: VersionStatus = VersionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str | None = None
    description: str = ""
    
    # Analytics
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_quality: float = 0.0
    
    # Tags y notas
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    changelog: str = ""


@dataclass
class PromptVersionHistory:
    """Historial de versiones de un prompt."""
    template_id: str
    versions: list[PromptVersion] = field(default_factory=list)
    
    def get_active_version(self) -> PromptVersion | None:
        """Obtiene la versión activa."""
        for v in self.versions:
            if v.status == VersionStatus.ACTIVE:
                return v
        return None
    
    def get_latest_version(self) -> PromptVersion | None:
        """Obtiene la última versión."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version)
    
    def get_version(self, version: int) -> PromptVersion | None:
        """Obtiene una versión específica."""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_version_history(
        self,
        status: VersionStatus | None = None,
    ) -> list[PromptVersion]:
        """Obtiene historial de versiones."""
        if status:
            return [v for v in self.versions if v.status == status]
        return sorted(self.versions, key=lambda v: v.version, reverse=True)


class PromptVersioningManager:
    """
    Gestor de versionado de prompts.
    
    Maneja el ciclo de vida de las versiones
    de templates de prompt.
    """

    def __init__(self) -> None:
        self._histories: dict[str, PromptVersionHistory] = {}

    def create_version(
        self,
        template_id: str,
        system_template: str,
        user_template: str,
        created_by: str | None = None,
        description: str = "",
        set_active: bool = False,
    ) -> PromptVersion:
        """
        Crea una nueva versión de un prompt.
        
        Args:
            template_id: ID del template
            system_template: Template de sistema
            user_template: Template de usuario
            created_by: Usuario que crea
            description: Descripción del cambio
            set_active: Si es true, activa esta versión
            
        Returns:
            Nueva versión creada
        """
        # Obtener o crear historial
        if template_id not in self._histories:
            self._histories[template_id] = PromptVersionHistory(
                template_id=template_id,
            )
        
        history = self._histories[template_id]
        latest_version = history.get_latest_version()
        new_version_num = (latest_version.version + 1) if latest_version else 1
        
        # Crear nueva versión
        version = PromptVersion(
            id=str(uuid.uuid4()),
            template_id=template_id,
            version=new_version_num,
            system_template=system_template,
            user_template=user_template,
            status=VersionStatus.ACTIVE if set_active else VersionStatus.DRAFT,
            created_by=created_by,
            description=description,
            changelog=f"v{new_version_num}: {description}" if description else "",
        )
        
        # Si se activa, desactivar las anteriores
        if set_active:
            for v in history.versions:
                if v.status == VersionStatus.ACTIVE:
                    v.status = VersionStatus.DEPRECATED
        
        history.versions.append(version)
        
        return version

    def activate_version(
        self,
        template_id: str,
        version: int,
    ) -> PromptVersion | None:
        """
        Activa una versión específica.
        
        Args:
            template_id: ID del template
            version: Número de versión
            
        Returns:
            Versión activada o None
        """
        if template_id not in self._histories:
            return None
        
        history = self._histories[template_id]
        target_version = history.get_version(version)
        
        if not target_version:
            return None
        
        # Desactivar versión activa actual
        active = history.get_active_version()
        if active:
            active.status = VersionStatus.DEPRECATED
        
        # Activar nueva versión
        target_version.status = VersionStatus.ACTIVE
        
        return target_version

    def deprecate_version(
        self,
        template_id: str,
        version: int,
    ) -> PromptVersion | None:
        """Marca una versión como deprecada."""
        if template_id not in self._histories:
            return None
        
        history = self._histories[template_id]
        target_version = history.get_version(version)
        
        if not target_version:
            return None
        
        target_version.status = VersionStatus.DEPRECATED
        return target_version

    def archive_version(
        self,
        template_id: str,
        version: int,
    ) -> PromptVersion | None:
        """Archiva una versión."""
        if template_id not in self._histories:
            return None
        
        history = self._histories[template_id]
        target_version = history.get_version(version)
        
        if not target_version:
            return None
        
        target_version.status = VersionStatus.ARCHIVED
        return target_version

    def get_history(self, template_id: str) -> PromptVersionHistory | None:
        """Obtiene el historial de un template."""
        return self._histories.get(template_id)

    def record_usage(
        self,
        template_id: str,
        version: int,
        success: bool = True,
        response_quality: float | None = None,
    ) -> None:
        """
        Registra el uso de una versión.
        
        Args:
            template_id: ID del template
            version: Número de versión
            success: Si la interacción fue exitosa
            response_quality: Calidad de respuesta (0-1)
        """
        if template_id not in self._histories:
            return
        
        history = self._histories[template_id]
        target_version = history.get_version(version)
        
        if not target_version:
            return
        
        target_version.usage_count += 1
        
        # Actualizar tasa de éxito
        total = target_version.usage_count
        current_successes = target_version.success_rate * (total - 1)
        target_version.success_rate = (current_successes + (1 if success else 0)) / total
        
        # Actualizar calidad de respuesta
        if response_quality is not None:
            current_quality_sum = target_version.avg_response_quality * (total - 1)
            target_version.avg_response_quality = (
                current_quality_sum + response_quality
            ) / total

    def compare_versions(
        self,
        template_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """
        Compara dos versiones.
        
        Args:
            template_id: ID del template
            version_a: Primera versión
            version_b: Segunda versión
            
        Returns:
            Comparación de versiones
        """
        if template_id not in self._histories:
            return {}
        
        history = self._histories[template_id]
        v_a = history.get_version(version_a)
        v_b = history.get_version(version_b)
        
        if not v_a or not v_b:
            return {}
        
        return {
            "template_id": template_id,
            "version_a": {
                "version": v_a.version,
                "status": v_a.status.value,
                "usage_count": v_a.usage_count,
                "success_rate": v_a.success_rate,
                "avg_response_quality": v_a.avg_response_quality,
            },
            "version_b": {
                "version": v_b.version,
                "status": v_b.status.value,
                "usage_count": v_b.usage_count,
                "success_rate": v_b.success_rate,
                "avg_response_quality": v_b.avg_response_quality,
            },
            "comparison": {
                "usage_diff": v_b.usage_count - v_a.usage_count,
                "success_rate_diff": v_b.success_rate - v_a.success_rate,
                "quality_diff": v_b.avg_response_quality - v_a.avg_response_quality,
            },
        }

    def get_best_version(
        self,
        template_id: str,
        metric: str = "success_rate",
    ) -> PromptVersion | None:
        """
        Obtiene la mejor versión según una métrica.
        
        Args:
            template_id: ID del template
            metric: Métrica a usar (success_rate, avg_response_quality, usage_count)
            
        Returns:
            Mejor versión o None
        """
        if template_id not in self._histories:
            return None
        
        history = self._histories[template_id]
        active_versions = [
            v for v in history.versions
            if v.status in (VersionStatus.ACTIVE, VersionStatus.DEPRECATED)
            and v.usage_count > 0
        ]
        
        if not active_versions:
            return None
        
        if metric == "success_rate":
            return max(active_versions, key=lambda v: v.success_rate)
        elif metric == "avg_response_quality":
            return max(active_versions, key=lambda v: v.avg_response_quality)
        elif metric == "usage_count":
            return max(active_versions, key=lambda v: v.usage_count)
        else:
            return None
