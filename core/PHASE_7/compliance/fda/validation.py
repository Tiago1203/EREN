"""
PHASE 7 - EPIC 0: FDA Software Validation

Validación de software médico FDA 21 CFR Part 820 e IEC 62304:
- Validation planning
- Installation qualification
- Operational qualification
- Performance qualification
- Requirements traceability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ValidationPhase(str, Enum):
    """Fases de validación."""
    PLANNING = "planning"
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


class QualificationType(str, Enum):
    """Tipos de calificación."""
    IQ = "IQ"     # Installation Qualification
    OQ = "OQ"    # Operational Qualification
    PQ = "PQ"    # Performance Qualification


class ValidationStatus(str, Enum):
    """Estados de validación."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"
    ON_HOLD = "on_hold"


@dataclass
class ValidationRequirement:
    """Requisito de validación."""
    requirement_id: str
    title: str
    description: str
    source: str                    # user_need, design_input, regulatory
    software_requirement: str      # IEEE 830
    test_case_id: str = ""
    test_result: str = ""
    passed: bool = False
    verified_by: str = ""
    verified_at: Optional[datetime] = None


@dataclass
class ValidationTest:
    """Test de validación."""
    test_id: str
    title: str
    requirement_ids: list[str] = field(default_factory=list)
    test_procedure: str = ""
    expected_result: str = ""
    actual_result: str = ""
    status: ValidationStatus = ValidationStatus.NOT_STARTED
    executed_by: str = ""
    executed_at: Optional[datetime] = None
    evidence: list[str] = field(default_factory=list)


@dataclass
class Qualification:
    """Calificación IQ/OQ/PQ."""
    qualification_id: str
    qualification_type: QualificationType
    test_cases: list[ValidationTest] = field(default_factory=list)
    status: ValidationStatus = ValidationStatus.NOT_STARTED
    completed_by: str = ""
    completed_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class ValidationPlan:
    """Plan de validación."""
    plan_id: str
    project_name: str
    software_name: str
    software_version: str
    risk_class: str                # Class A, B, C (IEC 62304)
    current_phase: ValidationPhase = ValidationPhase.PLANNING
    created_at: datetime = field(default_factory=datetime.utcnow)
    requirements: list[ValidationRequirement] = field(default_factory=list)
    iq: Optional[Qualification] = None
    oq: Optional[Qualification] = None
    pq: Optional[Qualification] = None
    overall_status: ValidationStatus = ValidationStatus.NOT_STARTED


class FDAValidationManager:
    """Gestor de validación FDA/IEC 62304."""

    def __init__(self):
        self._plans: dict[str, ValidationPlan] = {}
        self._test_results: dict[str, list] = {}

    def create_validation_plan(
        self,
        project_name: str,
        software_name: str,
        version: str,
        risk_class: str = "B",
    ) -> ValidationPlan:
        """Crea plan de validación."""
        plan_id = f"val-{project_name.lower().replace(' ', '-')}-{datetime.utcnow().strftime('%Y%m%d')}"

        plan = ValidationPlan(
            plan_id=plan_id,
            project_name=project_name,
            software_name=software_name,
            software_version=version,
            risk_class=risk_class,
            iq=Qualification(
                qualification_id=f"{plan_id}-IQ",
                qualification_type=QualificationType.IQ,
            ),
            oq=Qualification(
                qualification_id=f"{plan_id}-OQ",
                qualification_type=QualificationType.OQ,
            ),
            pq=Qualification(
                qualification_id=f"{plan_id}-PQ",
                qualification_type=QualificationType.PQ,
            ),
        )

        self._plans[plan_id] = plan
        return plan

    def add_requirement(
        self,
        plan_id: str,
        title: str,
        description: str,
        source: str,
        software_requirement: str,
    ) -> ValidationRequirement:
        """Agrega requisito de validación."""
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        req_id = f"{plan_id}-req-{len(plan.requirements) + 1:03d}"
        requirement = ValidationRequirement(
            requirement_id=req_id,
            title=title,
            description=description,
            source=source,
            software_requirement=software_requirement,
        )
        plan.requirements.append(requirement)
        return requirement

    def trace_requirement_to_test(
        self,
        plan_id: str,
        requirement_id: str,
        test_id: str,
    ) -> bool:
        """Vincula requisito a test (trazabilidad)."""
        plan = self._plans.get(plan_id)
        if not plan:
            return False

        for req in plan.requirements:
            if req.requirement_id == requirement_id:
                req.test_case_id = test_id
                return True
        return False

    def execute_test(
        self,
        plan_id: str,
        test_id: str,
        result: str,
        executed_by: str,
        evidence: Optional[list[str]] = None,
    ) -> ValidationStatus:
        """Ejecuta test de validación."""
        plan = self._plans.get(plan_id)
        if not plan:
            return ValidationStatus.NOT_STARTED

        # Find test in IQ/OQ/PQ
        test_found = None
        for qual in [plan.iq, plan.oq, plan.pq]:
            if qual:
                for test in qual.test_cases:
                    if test.test_id == test_id:
                        test_found = test
                        break

        if not test_found:
            return ValidationStatus.NOT_STARTED

        test_found.actual_result = result
        test_found.executed_by = executed_by
        test_found.executed_at = datetime.utcnow()
        if evidence:
            test_found.evidence.extend(evidence)

        # Determine status
        if "pass" in result.lower():
            test_found.status = ValidationStatus.PASSED
        elif "fail" in result.lower():
            test_found.status = ValidationStatus.FAILED
        else:
            test_found.status = ValidationStatus.IN_PROGRESS

        return test_found.status

    def get_traceability_matrix(self, plan_id: str) -> list[dict]:
        """Genera matriz de trazabilidad requisitos -> tests."""
        plan = self._plans.get(plan_id)
        if not plan:
            return []

        matrix = []
        for req in plan.requirements:
            matrix.append({
                "requirement_id": req.requirement_id,
                "title": req.title,
                "source": req.source,
                "test_case_id": req.test_case_id,
                "test_status": req.test_result or "not_executed",
                "passed": req.passed,
            })
        return matrix

    def get_validation_status(self, plan_id: str) -> dict:
        """Obtiene estado de validación completo."""
        plan = self._plans.get(plan_id)
        if not plan:
            return {}

        all_tests = []
        for qual in [plan.iq, plan.oq, plan.pq]:
            if qual:
                all_tests.extend(qual.test_cases)

        passed = sum(1 for t in all_tests if t.status == ValidationStatus.PASSED)
        failed = sum(1 for t in all_tests if t.status == ValidationStatus.FAILED)

        return {
            "plan_id": plan_id,
            "project_name": plan.project_name,
            "risk_class": plan.risk_class,
            "current_phase": plan.current_phase.value,
            "total_requirements": len(plan.requirements),
            "total_tests": len(all_tests),
            "tests_passed": passed,
            "tests_failed": failed,
            "completion_percentage": (passed / len(all_tests) * 100) if all_tests else 0,
            "overall_status": plan.overall_status.value,
        }
