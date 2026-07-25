"""
PHASE 7 - EPIC 0: HIPAA Controls

Controles de seguridad HIPAA:
- Administrative Safeguards
- Physical Safeguards
- Technical Safeguards
- Breach Notification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class HIPAA_SafeguardType(str, Enum):
    """Tipos de safeguards HIPAA."""
    ADMINISTRATIVE = "administrative"
    PHYSICAL = "physical"
    TECHNICAL = "technical"


class SafeguardCategory(str, Enum):
    """Categorías de safeguards."""
    # Administrative (164.308)
    ACCESS_MANAGEMENT = "access_management"
    WORKFORCE_SECURITY = "workforce_security"
    INFORMATION_ACCESS = "information_access"
    SECURITY_AWARENESS = "security_awareness"
    SECURITY_INCIDENT = "security_incident"
    CONTINGENCY = "contingency"
    EVALUATION = "evaluation"
    BUSINESS_ASSOCIATE = "business_associate"

    # Physical (164.310)
    FACILITY_ACCESS = "facility_access"
    WORKSTATION_USE = "workstation_use"
    DEVICE_MEDIA = "device_media"

    # Technical (164.312)
    ACCESS_CONTROL = "access_control"
    AUDIT_CONTROLS = "audit_controls"
    INTEGRITY = "integrity"
    TRANSMISSION = "transmission"
    AUTHENTICATION = "authentication"
    PERSON_ENTITY = "person_entity_authentication"


@dataclass
class HIPAAControl:
    """Control individual HIPAA."""
    control_id: str                    # e.g., "164.308(a)(1)"
    title: str
    category: SafeguardCategory
    safeguard_type: HIPAA_SafeguardType
    description: str = ""
    implementation: str = ""
    is_required: bool = True
    is_addressable: bool = False       # Addressable = puede implementar alternativa


# Catálogo de controles HIPAA
HIPAA_CONTROLS = [
    # Administrative (§164.308)
    HIPAAControl(
        control_id="164.308(a)(1)",
        title="Security Management Process",
        category=SafeguardCategory.ACCESS_MANAGEMENT,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Risk analysis and management",
    ),
    HIPAAControl(
        control_id="164.308(a)(3)",
        title="Workforce Security",
        category=SafeguardCategory.WORKFORCE_SECURITY,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Authorization and supervision of workforce members",
    ),
    HIPAAControl(
        control_id="164.308(a)(4)",
        title="Information Access Management",
        category=SafeguardCategory.INFORMATION_ACCESS,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Access authorization based on role",
    ),
    HIPAAControl(
        control_id="164.308(a)(5)",
        title="Security Awareness and Training",
        category=SafeguardCategory.SECURITY_AWARENESS,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Security awareness program",
    ),
    HIPAAControl(
        control_id="164.308(a)(6)",
        title="Security Incident Procedures",
        category=SafeguardCategory.SECURITY_INCIDENT,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Incident response procedures",
    ),
    HIPAAControl(
        control_id="164.308(a)(7)",
        title="Contingency Plan",
        category=SafeguardCategory.CONTINGENCY,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Data backup, disaster recovery, emergency operations",
    ),
    HIPAAControl(
        control_id="164.308(b)(1)",
        title="Business Associate Contracts",
        category=SafeguardCategory.BUSINESS_ASSOCIATE,
        safeguard_type=HIPAA_SafeguardType.ADMINISTRATIVE,
        description="Contracts with business associates",
    ),

    # Physical (§164.310)
    HIPAAControl(
        control_id="164.310(a)(1)",
        title="Facility Access Controls",
        category=SafeguardCategory.FACILITY_ACCESS,
        safeguard_type=HIPAA_SafeguardType.PHYSICAL,
        description="Physical access restrictions",
    ),
    HIPAAControl(
        control_id="164.310(b)",
        title="Workstation Use",
        category=SafeguardCategory.WORKSTATION_USE,
        safeguard_type=HIPAA_SafeguardType.PHYSICAL,
        description="Policies for workstation use",
    ),
    HIPAAControl(
        control_id="164.310(d)(1)",
        title="Device and Media Controls",
        category=SafeguardCategory.DEVICE_MEDIA,
        safeguard_type=HIPAA_SafeguardType.PHYSICAL,
        description="Receipt and removal of hardware/media",
    ),

    # Technical (§164.312)
    HIPAAControl(
        control_id="164.312(a)(1)",
        title="Access Control",
        category=SafeguardCategory.ACCESS_CONTROL,
        safeguard_type=HIPAA_SafeguardType.TECHNICAL,
        description="Unique user identification, emergency access, automatic logoff, encryption",
    ),
    HIPAAControl(
        control_id="164.312(b)",
        title="Audit Controls",
        category=SafeguardCategory.AUDIT_CONTROLS,
        safeguard_type=HIPAA_SafeguardType.TECHNICAL,
        description="Hardware/software audit trails",
    ),
    HIPAAControl(
        control_id="164.312(c)(1)",
        title="Integrity Controls",
        category=SafeguardCategory.INTEGRITY,
        safeguard_type=HIPAA_SafeguardType.TECHNICAL,
        description="Electronic mechanisms to authenticate ePHI",
    ),
    HIPAAControl(
        control_id="164.312(e)(1)",
        title="Transmission Security",
        category=SafeguardCategory.TRANSMISSION,
        safeguard_type=HIPAA_SafeguardType.TECHNICAL,
        description="Integrity controls and encryption for transmission",
    ),
    HIPAAControl(
        control_id="164.312(d)",
        title="Person or Entity Authentication",
        category=SafeguardCategory.AUTHENTICATION,
        safeguard_type=HIPAA_SafeguardType.TECHNICAL,
        description="Procedures to verify identity",
    ),
]


@dataclass
class SafeguardImplementation:
    """Implementación de un safeguard."""
    control_id: str
    implemented: bool
    implementation_details: str = ""
    implementation_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    responsible_party: str = ""
    evidence: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


class HIPAAComplianceManager:
    """Gestor de compliance HIPAA."""

    def __init__(self):
        self._implementations: dict[str, SafeguardImplementation] = {}
        self._initialize_controls()

    def _initialize_controls(self) -> None:
        """Inicializa todos los controles."""
        for control in HIPAA_CONTROLS:
            self._implementations[control.control_id] = SafeguardImplementation(
                control_id=control.control_id,
                implemented=False,
            )

    def get_control(self, control_id: str) -> Optional[HIPAAControl]:
        """Obtiene control por ID."""
        for control in HIPAA_CONTROLS:
            if control.control_id == control_id:
                return control
        return None

    def get_controls_by_category(self, category: SafeguardCategory) -> list[HIPAAControl]:
        """Obtiene controles por categoría."""
        return [c for c in HIPAA_CONTROLS if c.category == category]

    def get_controls_by_type(self, safeguard_type: HIPAA_SafeguardType) -> list[HIPAAControl]:
        """Obtiene controles por tipo."""
        return [c for c in HIPAA_CONTROLS if c.safeguard_type == safeguard_type]

    def implement_control(
        self,
        control_id: str,
        details: str,
        responsible_party: str,
    ) -> bool:
        """Registra implementación de un control."""
        impl = self._implementations.get(control_id)
        if not impl:
            return False

        impl.implemented = True
        impl.implementation_details = details
        impl.implementation_date = datetime.utcnow()
        impl.last_reviewed = datetime.utcnow()
        impl.responsible_party = responsible_party
        return True

    def get_implementation_status(self) -> dict:
        """Obtiene estado de implementación."""
        total = len(HIPAA_CONTROLS)
        implemented = sum(1 for impl in self._implementations.values() if impl.implemented)
        required = sum(1 for c in HIPAA_CONTROLS if c.is_required and not c.is_addressable)
        required_implemented = sum(
            1 for c in HIPAA_CONTROLS
            if c.is_required and not c.is_addressable
            and self._implementations[c.control_id].implemented
        )

        by_type = {}
        for safeguard_type in HIPAA_SafeguardType:
            controls = self.get_controls_by_type(safeguard_type)
            implemented_count = sum(
                1 for c in controls
                if self._implementations[c.control_id].implemented
            )
            by_type[safeguard_type.value] = {
                "total": len(controls),
                "implemented": implemented_count,
                "percentage": (implemented_count / len(controls) * 100) if controls else 0,
            }

        return {
            "total_controls": total,
            "implemented": implemented,
            "percentage": (implemented / total * 100) if total else 0,
            "required_controls": required,
            "required_implemented": required_implemented,
            "required_percentage": (required_implemented / required * 100) if required else 0,
            "by_type": by_type,
        }

    def identify_gaps(self) -> list[dict]:
        """Identifica gaps en la implementación."""
        gaps = []
        for control in HIPAA_CONTROLS:
            impl = self._implementations.get(control.control_id)
            if control.is_required and not impl.implemented:
                gaps.append({
                    "control_id": control.control_id,
                    "title": control.title,
                    "category": control.category.value,
                    "type": control.safeguard_type.value,
                    "severity": "critical" if control.is_required else "medium",
                })
        return gaps
