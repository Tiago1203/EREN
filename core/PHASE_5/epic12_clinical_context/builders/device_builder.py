"""
DeviceContextBuilder: Constructor de contexto de dispositivo
"""

from datetime import datetime
from typing import Optional

from core.PHASE_5.epic12_clinical_context.domain import (
    DeviceContext,
    MaintenanceRecord,
    Incident,
    CalibrationStatus,
)


class DeviceContextBuilder:
    """Constructor de contexto de dispositivo."""
    
    async def build(
        self,
        device_id: str,
        include_maintenance: bool = True,
        include_incidents: bool = True,
    ) -> DeviceContext:
        """
        Construye contexto de dispositivo.
        
        Args:
            device_id: ID del dispositivo
            include_maintenance: Incluir historial de mantenimiento
            include_incidents: Incluir historial de incidentes
        
        Returns:
            DeviceContext construido
        """
        # En implementación real, esto consultaría FASE 1/Device
        device_context = DeviceContext(
            device_id=device_id,
            device_type="infusion_pump",
            manufacturer="Baxter",
            model="Sigma Spectrum",
            maintenance_history=[] if include_maintenance else None,
            incident_history=[] if include_incidents else None,
            calibration_status=CalibrationStatus.VALID,
            risk_classification="CLASS_B",
        )
        
        return device_context
    
    async def get_device_history(
        self,
        device_id: str,
    ) -> list[MaintenanceRecord]:
        """Obtiene historial de dispositivo."""
        return [
            MaintenanceRecord(
                record_id=f"maint_{device_id}_1",
                date=datetime(2026, 6, 15),
                type="preventive",
                description="Annual preventive maintenance",
                technician="John Smith",
            ),
        ]
    
    async def get_incident_history(
        self,
        device_id: str,
    ) -> list[Incident]:
        """Obtiene historial de incidentes."""
        return [
            Incident(
                incident_id=f"inc_{device_id}_1",
                date=datetime(2026, 5, 10),
                type="alarm_fault",
                severity="medium",
                resolution="Replaced alarm module",
            ),
        ]
