"""
PHASE 7 - EPIC 0: HIPAA Compliance Checker

Verificador de compliance HIPAA:
- Gap analysis
- Compliance validation
- Violation detection
- Remediation tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ViolationSeverity(str, Enum):
    """Severidad de violaciones."""
    CRITICAL = "critical"      # Breach potencial
    HIGH = "high"             # No compliance
    MEDIUM = "medium"          # Partial compliance
    LOW = "low"               # Best practice


class ViolationCategory(str, Enum):
    """Categorías de violaciones."""
    ENCRYPTION = "encryption"
    ACCESS_CONTROL = "access_control"
    AUDIT_LOGGING = "audit_logging"
    AUTHENTICATION = "authentication"
    DATA_INTEGRITY = "data_integrity"
    TRANSMISSION_SECURITY = "transmission_security"
    CONTINGENCY_PLAN = "contingency_plan"
    WORKFORCE_TRAINING = "workforce_training"
    BUSINESS_ASSOCIATE = "business_associate"
    PATIENT_RIGHTS = "patient_rights"


@dataclass
class HIPAAViolation:
    """Violación identificada."""
    violation_id: str
    category: ViolationCategory
    severity: ViolationSeverity
    title: str
    description: str
    control_reference: str        # e.g., "164.312(a)(1)"
    detected_at: datetime
    affected_records: int = 0
    affected_systems: list[str] = field(default_factory=list)
    remediation_required: str = ""
    remediation_deadline: Optional[datetime] = None
    remediated: bool = False
    remediated_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class ComplianceGap:
    """Gap de compliance."""
    gap_id: str
    category: ViolationCategory
    title: str
    description: str
    control_reference: str
    current_state: str = ""
    required_state: str = ""
    risk_level: str = ""
    remediation_steps: list[str] = field(default_factory=list)
    estimated_effort: str = ""
    priority: int = 1  # 1 = highest


@dataclass
class ComplianceStatus:
    """Estado general de compliance."""
    assessment_date: datetime
    overall_score: float           # 0-100
    hipaa_score: float             # 0-100
    controls_passed: int = 0
    controls_failed: int = 0
    controls_partial: int = 0
    critical_violations: int = 0
    open_violations: int = 0
    remediated_violations: int = 0
    next_review_date: Optional[datetime] = None


class HIPAAComplianceChecker:
    """Verificador de compliance HIPAA."""

    def __init__(self):
        self._violations: list[HIPAAViolation] = []
        self._gaps: list[ComplianceGap] = []

    def check_encryption(self, data: dict) -> list[HIPAAViolation]:
        """Verifica cumplimiento de encriptación."""
        violations = []

        # Check PHI fields are encrypted
        phi_fields = ["patient_name", "diagnosis", "treatment", "medications",
                      "ssn", "mrn", "date_of_birth"]
        unencrypted_phi = []

        for field_name, value in data.items():
            if any(phi in field_name.lower() for phi in phi_fields):
                if isinstance(value, str) and not self._is_encrypted(value):
                    unencrypted_phi.append(field_name)

        if unencrypted_phi:
            violations.append(HIPAAViolation(
                violation_id=f"enc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                category=ViolationCategory.ENCRYPTION,
                severity=ViolationSeverity.CRITICAL,
                title="PHI sin encriptación detectado",
                description=f"Campos PHI sin cifrar: {', '.join(unencrypted_phi)}",
                control_reference="164.312(a)(1)",
                detected_at=datetime.utcnow(),
                affected_records=1,
                remediation_required="Encriptar todos los campos PHI con AES-256",
            ))

        return violations

    def check_access_control(self, user_permissions: set, resource: str) -> list[HIPAAViolation]:
        """Verifica controles de acceso."""
        violations = []

        # Shared account check
        if "shared_account" in str(user_permissions):
            violations.append(HIPAAViolation(
                violation_id=f"acc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                category=ViolationCategory.ACCESS_CONTROL,
                severity=ViolationSeverity.HIGH,
                title="Cuenta compartida detectada",
                description="Uso de cuenta compartida viola principio de mínimo privilegio",
                control_reference="164.312(a)(1)",
                detected_at=datetime.utcnow(),
                remediation_required="Implementar autenticación individual",
            ))

        return violations

    def check_audit_logging(self, access_log: list) -> list[HIPAAViolation]:
        """Verifica que PHI access esté loggeado."""
        violations = []

        phi_access_without_log = [
            entry for entry in access_log
            if entry.get("accessed_phi") and not entry.get("logged")
        ]

        if phi_access_without_log:
            violations.append(HIPAAViolation(
                violation_id=f"aud-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                category=ViolationCategory.AUDIT_LOGGING,
                severity=ViolationSeverity.HIGH,
                title="Acceso PHI sin registro de auditoría",
                description=f"{len(phi_access_without_log)} accesos PHI sin log",
                control_reference="164.312(b)",
                detected_at=datetime.utcnow(),
                affected_records=len(phi_access_without_log),
                remediation_required="Implementar logging de auditoría para todos los accesos PHI",
            ))

        return violations

    def check_transmission_security(self, connections: list) -> list[HIPAAViolation]:
        """Verifica seguridad de transmisión."""
        violations = []

        for conn in connections:
            if not conn.get("encrypted"):
                violations.append(HIPAAViolation(
                    violation_id=f"trs-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    category=ViolationCategory.TRANSMISSION_SECURITY,
                    severity=ViolationSeverity.HIGH,
                    title="Transmisión no cifrada",
                    description=f"Comunicación {conn.get('from')} -> {conn.get('to')} sin TLS",
                    control_reference="164.312(e)(1)",
                    detected_at=datetime.utcnow(),
                    affected_systems=[conn.get("system", "unknown")],
                    remediation_required="Implementar TLS 1.2+ para todas las transmisiones",
                ))

        return violations

    def identify_gaps(self) -> list[ComplianceGap]:
        """Identifica gaps de compliance."""
        gaps = [
            ComplianceGap(
                gap_id="gap-001",
                category=ViolationCategory.ENCRYPTION,
                title="Encriptación de PHI en base de datos",
                description="Verificar que todos los campos PHI usen AES-256",
                control_reference="164.312(a)(1)",
                current_state="Revisar estado actual",
                required_state="100% campos PHI encriptados",
                risk_level="Critical",
                remediation_steps=[
                    "1. Inventariar todos los campos PHI",
                    "2. Implementar encriptación a nivel de campo",
                    "3. Rotar claves de encriptación",
                    "4. Validar desencriptación correcta",
                ],
                priority=1,
            ),
            ComplianceGap(
                gap_id="gap-002",
                category=ViolationCategory.AUDIT_LOGGING,
                title="Sistema de auditoría HIPAA",
                description="Registrar todos los accesos PHI con timestamp e identidad",
                control_reference="164.312(b)",
                current_state="Revisar estado actual",
                required_state="100% accesos PHI loggeados",
                risk_level="High",
                remediation_steps=[
                    "1. Diseñar schema de auditoría",
                    "2. Implementar middleware de auditoría",
                    "3. Crear dashboard de auditoría",
                    "4. Configurar retención de logs (6 años)",
                ],
                priority=2,
            ),
        ]
        self._gaps = gaps
        return gaps

    def get_compliance_status(self) -> ComplianceStatus:
        """Obtiene estado de compliance."""
        total_controls = 16  # HIPAA controls principales
        passed = total_controls - len(self._violations)
        failed = len([v for v in self._violations if v.severity == ViolationSeverity.CRITICAL])

        return ComplianceStatus(
            assessment_date=datetime.utcnow(),
            overall_score=max(0, (passed / total_controls) * 100),
            hipaa_score=max(0, (passed / total_controls) * 100),
            controls_passed=passed,
            controls_failed=failed,
            controls_partial=len(self._violations) - failed,
            critical_violations=failed,
            open_violations=len(self._violations),
            remediated_violations=sum(1 for v in self._violations if v.remediated),
        )

    def _is_encrypted(self, value: str) -> bool:
        """Verifica si un valor parece encriptado."""
        # Basic check: base64-like string that decodes to binary
        if len(value) > 20 and ":" not in value:
            try:
                import base64
                decoded = base64.b64decode(value)
                return len(decoded) > 10
            except Exception:
                pass
        return False
