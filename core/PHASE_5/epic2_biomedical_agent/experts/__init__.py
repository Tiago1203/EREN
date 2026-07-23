"""
PHASE 5 - EPIC 2: Biomedical Experts

Expertos especializados en Ingeniería Clínica:
- EquipmentExpert: Análisis de equipos médicos
- MaintenanceExpert: Asesoría de mantenimiento
- ManufacturerExpert: Información de fabricantes
- StandardsExpert: Normas y estándares (IEC, ISO)
- CalibrationExpert: Calibraciones
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentCapability,
    AgentCapabilityVO,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

# =============================================================================
# IMPORTS FROM EPIC 2 DOMAIN
# =============================================================================

from core.PHASE_5.epic2_biomedical_agent.domain import (
    BiomedicalTask,
    BiomedicalTaskType,
    DeviceAssessment,
    AssessmentSeverity,
    MaintenanceRecommendation,
    MaintenancePriority,
    MaintenanceType,
)


# =============================================================================
# EQUIPMENT EXPERT - Experto en equipos médicos
# =============================================================================

@dataclass
class EquipmentAnalysis:
    """Resultado del análisis de equipo."""
    device_id: str
    device_type: str
    
    # Análisis
    specifications: dict = field(default_factory=dict)
    technical_details: dict = field(default_factory=dict)
    
    # Compatibilidad
    compatible_accessories: list[str] = field(default_factory=list)
    incompatible_devices: list[str] = field(default_factory=list)
    
    # Requisitos
    power_requirements: dict = field(default_factory=dict)
    environmental_requirements: dict = field(default_factory=dict)
    
    # Estado
    condition_assessment: str = ""
    expected_lifetime_years: float = 0.0
    end_of_life_date: datetime | None = None
    
    # Metadatos
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    confidence: float = 0.0


class EquipmentExpert:
    """
    Experto en análisis de equipos médicos.
    
    Responsabilidades:
    - Analizar especificaciones técnicas
    - Evaluar estado de equipos
    - Identificar compatibilidad
    - Predecir fallas
    """
    
    def __init__(self):
        self.expertise_areas = [
            "diagnostic_equipment",
            "therapeutic_equipment",
            "monitoring_equipment",
            "life_support",
            "laboratory",
            "imaging",
        ]
    
    async def analyze_device(
        self,
        device_id: str,
        context: dict | None = None,
    ) -> EquipmentAnalysis:
        """
        Analiza un dispositivo médico.
        
        Args:
            device_id: ID del dispositivo
            context: Contexto adicional
        
        Returns:
            EquipmentAnalysis con el análisis completo
        """
        logger.info(f"Analyzing device: {device_id}")
        
        # Placeholder - en producción usaría PHASE 4 para búsqueda
        analysis = EquipmentAnalysis(
            device_id=device_id,
            device_type="general",
            specifications={
                "manufacturer": context.get("manufacturer", "Unknown"),
                "model": context.get("model", "Unknown"),
                "serial": context.get("serial", "N/A"),
            },
            technical_details={},
            compatible_accessories=[],
            condition_assessment="Operational",
            expected_lifetime_years=7.0,
            confidence=0.85,
        )
        
        return analysis
    
    async def get_similar_devices(
        self,
        device_type: str,
        manufacturer: str | None = None,
    ) -> list[dict]:
        """Obtiene dispositivos similares."""
        # Placeholder
        return []
    
    async def predict_failures(
        self,
        device_id: str,
        usage_hours: int,
        age_years: float,
    ) -> list[dict]:
        """Predice fallas potenciales."""
        failures = []
        
        # Lógica de predicción simplificada
        if age_years > 5:
            failures.append({
                "type": "component_wear",
                "probability": 0.7,
                "recommended_action": "Preventive maintenance",
            })
        
        if usage_hours > 10000:
            failures.append({
                "type": "calibration_drift",
                "probability": 0.5,
                "recommended_action": "Calibration check",
            })
        
        return failures


# =============================================================================
# MAINTENANCE EXPERT - Experto en mantenimiento
# =============================================================================

@dataclass
class MaintenanceAdvice:
    """Resultado de asesoría de mantenimiento."""
    device_id: str
    
    # Recomendaciones
    recommendations: list[MaintenanceRecommendation] = field(default_factory=list)
    
    # Historial
    maintenance_history: list[dict] = field(default_factory=list)
    
    # Análisis
    current_condition: str = ""
    maintenance_gaps: list[str] = field(default_factory=list)
    
    # Scheduling
    next_maintenance_date: datetime | None = None
    suggested_schedule: list[dict] = field(default_factory=list)
    
    # Metadatos
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class MaintenanceExpert:
    """
    Experto en asesoría de mantenimiento.
    
    Responsabilidades:
    - Generar recomendaciones de mantenimiento
    - Analizar historial de mantenimiento
    - Identificar gaps
    - Sugerir scheduling
    """
    
    def __init__(self):
        self.maintenance_types = list(MaintenanceType)
    
    async def generate_recommendations(
        self,
        device_id: str,
        device_type: str,
        age_years: float,
        usage_hours: int,
        last_maintenance: datetime | None = None,
    ) -> list[MaintenanceRecommendation]:
        """Genera recomendaciones de mantenimiento."""
        recommendations = []
        
        # Preventive maintenance
        if age_years > 1:
            recommendations.append(MaintenanceRecommendation(
                recommendation_id="",
                device_id=device_id,
                maintenance_type=MaintenanceType.PREVENTIVE,
                priority=MaintenancePriority.MEDIUM if age_years < 5 else MaintenancePriority.HIGH,
                title="Preventive Maintenance",
                description=f"Standard preventive maintenance for {device_type}",
                estimated_duration_minutes=60,
                frequency_days=365,
            ))
        
        # Calibration
        if "monitoring" in device_type.lower() or "diagnostic" in device_type.lower():
            recommendations.append(MaintenanceRecommendation(
                recommendation_id="",
                device_id=device_id,
                maintenance_type=MaintenanceType.CALIBRATION,
                priority=MaintenancePriority.HIGH,
                title="Calibration Verification",
                description="Verify calibration accuracy",
                estimated_duration_minutes=30,
                frequency_days=180,
            ))
        
        # Safety inspection
        recommendations.append(MaintenanceRecommendation(
            recommendation_id="",
            device_id=device_id,
            maintenance_type=MaintenanceType.SAFETY,
            priority=MaintenancePriority.HIGH,
            title="Safety Inspection",
            description="Comprehensive safety inspection per IEC standards",
            estimated_duration_minutes=45,
            frequency_days=365,
        ))
        
        return recommendations
    
    async def analyze_maintenance_history(
        self,
        device_id: str,
        history: list[dict],
    ) -> dict:
        """Analiza historial de mantenimiento."""
        if not history:
            return {
                "status": "no_history",
                "gaps": ["No maintenance history available"],
                "recommendation": "Establish maintenance schedule",
            }
        
        completed_types = {h.get("type") for h in history}
        missing_types = [t for t in self.maintenance_types if t.value not in completed_types]
        
        return {
            "status": "analyzed",
            "completed_count": len(history),
            "missing_types": [m.value for m in missing_types],
            "gaps": [f"Missing {m.value} maintenance" for m in missing_types],
        }


# =============================================================================
# MANUFACTURER EXPERT - Experto en fabricantes
# =============================================================================

@dataclass
class ManufacturerInfo:
    """Información de fabricante."""
    manufacturer_name: str
    manufacturer_code: str = ""
    
    # Contacto
    website: str = ""
    support_phone: str = ""
    support_email: str = ""
    
    # Productos
    product_lines: list[str] = field(default_factory=list)
    device_types: list[str] = field(default_factory=list)
    
    # Soporte
    warranty_years: int = 0
    support_tier: str = ""
    
    # Certificaciones
    certifications: list[str] = field(default_factory=list)
    iso_certifications: list[str] = field(default_factory=list)


class ManufacturerExpert:
    """
    Experto en información de fabricantes.
    
    Responsabilidades:
    - Proporcionar información de contacto
    - Detallar productos
    - Verificar certificaciones
    - Obtener soporte técnico
    """
    
    def __init__(self):
        self.known_manufacturers = [
            "GE Healthcare",
            "Siemens Healthineers",
            "Philips Healthcare",
            "Medtronic",
            "Abbott",
            "Johnson & Johnson",
            "Boston Scientific",
            "Stryker",
        ]
    
    async def get_manufacturer_info(
        self,
        manufacturer_name: str,
    ) -> ManufacturerInfo | None:
        """Obtiene información de un fabricante."""
        # Placeholder - en producción consultaría base de datos
        if manufacturer_name in self.known_manufacturers:
            return ManufacturerInfo(
                manufacturer_name=manufacturer_name,
                website=f"https://www.{manufacturer_name.lower().replace(' ', '')}.com",
                certifications=["FDA", "CE", "ISO 13485"],
                iso_certifications=["ISO 13485:2016"],
            )
        return None
    
    async def get_device_manual(
        self,
        manufacturer: str,
        model: str,
    ) -> dict | None:
        """Obtiene manual de dispositivo."""
        # Placeholder
        return None
    
    async def get_spare_parts(
        self,
        manufacturer: str,
        model: str,
    ) -> list[dict]:
        """Obtiene lista de repuestos."""
        # Placeholder
        return []


# =============================================================================
# STANDARDS EXPERT - Experto en normas
# =============================================================================

@dataclass
class StandardReference:
    """Referencia a estándar técnico."""
    standard_id: str  # e.g., "IEC 60601-1"
    title: str
    category: str = ""
    
    # Versión
    version: str = ""
    publication_date: str = ""
    
    # Alcance
    scope: str = ""
    applicability: list[str] = field(default_factory=list)
    
    # Requisitos
    key_requirements: list[str] = field(default_factory=list)
    
    # Cumplimiento
    is_mandatory: bool = False
    enforcement_body: str = ""


class StandardsExpert:
    """
    Experto en normas y estándares técnicos.
    
    Responsabilidades:
    - Identificar normas aplicables (IEC, ISO, AAMI)
    - Detallar requisitos
    - Verificar cumplimiento
    - Proporcionar guidance
    """
    
    def __init__(self):
        # Estándares comunes en ingeniería clínica
        self.common_standards = {
            "IEC 60601-1": "Medical electrical equipment - General requirements",
            "IEC 60601-1-2": "Electromagnetic compatibility",
            "IEC 60601-1-6": "Usability",
            "IEC 60601-1-8": "Alarm systems",
            "IEC 62353": "Recurrent test and test after repair",
            "ISO 14971": "Risk management for medical devices",
            "AAMI HE75": "Human factors engineering",
        }
    
    async def find_applicable_standards(
        self,
        device_type: str,
        device_class: str,
    ) -> list[StandardReference]:
        """Encuentra estándares aplicables a un dispositivo."""
        standards = []
        
        # IEC 60601-1 siempre aplica
        standards.append(StandardReference(
            standard_id="IEC 60601-1",
            title="Medical electrical equipment - General requirements",
            category="Electrical Safety",
            version="3rd Edition",
            key_requirements=[
                "General requirements",
                "Classification",
                "Protection against electrical hazards",
                "Protection against mechanical hazards",
            ],
            is_mandatory=True,
        ))
        
        # EMC para dispositivos electrónicos
        standards.append(StandardReference(
            standard_id="IEC 60601-1-2",
            title="Electromagnetic compatibility",
            category="EMC",
            version="4th Edition",
            key_requirements=[
                "Emissions testing",
                "Immunity testing",
                "Risk analysis",
            ],
            is_mandatory=True,
        ))
        
        return standards
    
    async def check_compliance(
        self,
        standard_id: str,
        device_requirements: dict,
    ) -> dict:
        """Verifica cumplimiento de un estándar."""
        # Placeholder
        return {
            "standard": standard_id,
            "compliant": True,
            "issues": [],
            "recommendations": [],
        }
    
    async def get_test_requirements(
        self,
        standard_id: str,
    ) -> list[dict]:
        """Obtiene requisitos de prueba para un estándar."""
        # Placeholder
        return []


# =============================================================================
# CALIBRATION EXPERT - Experto en calibraciones
# =============================================================================

@dataclass
class CalibrationRecord:
    """Registro de calibración."""
    calibration_id: str
    device_id: str
    
    # Fechas
    calibration_date: datetime
    next_calibration_date: datetime
    due_date: datetime
    
    # Resultados
    passed: bool
    accuracy: float  # 0.0 - 1.0
    
    # Detalles
    measurements: list[dict] = field(default_factory=list)
    deviations: list[dict] = field(default_factory=list)
    adjustments: list[str] = field(default_factory=list)
    
    # metadatos
    calibrator_id: str = ""
    equipment_used: str = ""
    temperature: float = 0.0
    humidity: float = 0.0


class CalibrationExpert:
    """
    Experto en calibraciones.
    
    Responsabilidades:
    - Gestionar historial de calibraciones
    - Verificar fechas de vencimiento
    - Generar record de calibración
    - Recomendar intervals
    """
    
    def __init__(self):
        self.default_intervals = {
            "high_precision": 30,    # días
            "standard": 180,          # días
            "low_precision": 365,     # días
        }
    
    async def get_calibration_status(
        self,
        device_id: str,
    ) -> dict:
        """Obtiene estado de calibración."""
        # Placeholder
        return {
            "device_id": device_id,
            "is_calibrated": True,
            "last_calibration": datetime.now(UTC),
            "next_due": datetime.now(UTC),
            "days_until_due": 30,
            "is_overdue": False,
        }
    
    async def calculate_interval(
        self,
        device_type: str,
        usage_hours: int,
        accuracy_required: float,
    ) -> int:
        """Calcula intervalo de calibración recomendado."""
        if accuracy_required > 0.95:
            return self.default_intervals["high_precision"]
        elif accuracy_required > 0.85:
            return self.default_intervals["standard"]
        else:
            return self.default_intervals["low_precision"]
    
    async def create_calibration_record(
        self,
        device_id: str,
        measurements: list[dict],
        passed: bool,
    ) -> CalibrationRecord:
        """Crea un registro de calibración."""
        accuracy = 0.9 if passed else 0.0
        
        record = CalibrationRecord(
            calibration_id="",
            device_id=device_id,
            calibration_date=datetime.now(UTC),
            next_calibration_date=datetime.now(UTC),
            due_date=datetime.now(UTC),
            passed=passed,
            accuracy=accuracy,
            measurements=measurements,
        )
        
        return record


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Equipment Expert
    "EquipmentExpert",
    "EquipmentAnalysis",
    # Maintenance Expert
    "MaintenanceExpert",
    "MaintenanceAdvice",
    # Manufacturer Expert
    "ManufacturerExpert",
    "ManufacturerInfo",
    # Standards Expert
    "StandardsExpert",
    "StandardReference",
    # Calibration Expert
    "CalibrationExpert",
    "CalibrationRecord",
]
