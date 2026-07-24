"""
ContextLifecycleManager: Gestor de ciclo de vida de contexto
"""

from datetime import datetime
from typing import Optional, Dict

from core.PHASE_5.epic12_clinical_context.domain import (
    ClinicalContext,
    ContextMetadata,
    ClinicalContextConfig,
)


class ContextLifecycleManager:
    """Gestor de ciclo de vida de contexto."""
    
    def __init__(self, config: Optional[ClinicalContextConfig] = None):
        """Inicializa el gestor."""
        self.config = config or ClinicalContextConfig()
        self._contexts: Dict[str, ClinicalContext] = {}
        self._snapshots: Dict[str, list[ClinicalContext]] = {}
    
    async def create_context(
        self,
        session_id: str,
        patient_id: str,
        device_id: str,
    ) -> ClinicalContext:
        """
        Crea nuevo contexto.
        
        Args:
            session_id: ID de sesión
            patient_id: ID de paciente
            device_id: ID de dispositivo
        
        Returns:
            ClinicalContext creado
        """
        from core.PHASE_5.epic12_clinical_context.builders import (
            PatientContextBuilder,
            DeviceContextBuilder,
            HospitalContextBuilder,
            ClinicalContextAggregator,
        )
        
        # Construir contextos individuales
        patient_builder = PatientContextBuilder()
        patient_context = await patient_builder.build(
            patient_id=patient_id,
            include_history=self.config.include_history,
            include_conditions=self.config.include_conditions,
        )
        
        device_builder = DeviceContextBuilder()
        device_context = await device_builder.build(
            device_id=device_id,
            include_maintenance=self.config.include_maintenance,
            include_incidents=self.config.include_incidents,
        )
        
        hospital_builder = HospitalContextBuilder()
        hospital_context = await hospital_builder.build(
            hospital_id="default_hospital",
            include_departments=True,
            include_capacity=True,
        )
        
        # Agregar contextos
        aggregator = ClinicalContextAggregator()
        clinical_context = await aggregator.aggregate(
            patient_context=patient_context,
            device_context=device_context,
            hospital_context=hospital_context,
        )
        
        # Actualizar metadata
        clinical_context.metadata.session_id = session_id
        clinical_context.metadata.created_by = "context_lifecycle_manager"
        
        # Guardar contexto
        self._contexts[clinical_context.context_id] = clinical_context
        
        return clinical_context
    
    async def update_context(
        self,
        context_id: str,
        updates: dict,
    ) -> ClinicalContext:
        """
        Actualiza contexto existente.
        
        Args:
            context_id: ID del contexto
            updates: Diccionario de actualizaciones
        
        Returns:
            ClinicalContext actualizado
        """
        context = self._contexts.get(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")
        
        # Aplicar actualizaciones
        context.metadata.updated_at = datetime.now()
        context.metadata.version += 1
        
        self._contexts[context_id] = context
        return context
    
    async def snapshot(
        self,
        context_id: str,
    ) -> ClinicalContext:
        """
        Guarda snapshot de contexto.
        
        Args:
            context_id: ID del contexto
        
        Returns:
            Snapshot del contexto
        """
        context = self._contexts.get(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")
        
        # Crear snapshot (copia profunda)
        import copy
        snapshot = copy.deepcopy(context)
        
        # Guardar snapshot
        if context_id not in self._snapshots:
            self._snapshots[context_id] = []
        self._snapshots[context_id].append(snapshot)
        
        return snapshot
    
    async def restore(
        self,
        context_id: str,
        snapshot_index: int = -1,
    ) -> ClinicalContext:
        """
        Restaura desde snapshot.
        
        Args:
            context_id: ID del contexto
            snapshot_index: Índice del snapshot (-1 para el último)
        
        Returns:
            ClinicalContext restaurado
        """
        snapshots = self._snapshots.get(context_id, [])
        if not snapshots:
            raise ValueError(f"No snapshots found for context: {context_id}")
        
        if snapshot_index < 0:
            snapshot_index = len(snapshots) + snapshot_index
        
        if snapshot_index < 0 or snapshot_index >= len(snapshots):
            raise ValueError(f"Snapshot index out of range: {snapshot_index}")
        
        # Restaurar snapshot
        restored = snapshots[snapshot_index]
        self._contexts[context_id] = restored
        
        return restored
    
    async def get_context(
        self,
        context_id: str,
    ) -> Optional[ClinicalContext]:
        """Obtiene contexto por ID."""
        return self._contexts.get(context_id)
    
    async def delete_context(
        self,
        context_id: str,
    ) -> bool:
        """Elimina contexto."""
        if context_id in self._contexts:
            del self._contexts[context_id]
            if context_id in self._snapshots:
                del self._snapshots[context_id]
            return True
        return False
