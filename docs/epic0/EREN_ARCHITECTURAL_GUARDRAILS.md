# EREN Architectural Guardrails
## Engineering Constitution — Rules That Cannot Be Broken

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial - Epic 0.1 |

---

## Purpose

This document defines **architectural guardrails** — rules that must NEVER be violated in EREN development.

These are not guidelines. These are not suggestions. These are **architectural laws**.

Breaking a guardrail requires:
1. Architecture Board approval
2. ADR documenting the exception
3. Explicit waiver with expiration date

---

## Guardrail Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHITECTURAL GUARDRAILS                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CONTRACTS & DEPENDENCIES                                │
│  2. SECURITY & COMPLIANCE                                    │
│  3. DATA INTEGRITY                                           │
│  4. OBSERVABILITY                                           │
│  5. COGNITIVE INTEGRITY                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Category 1: Contracts & Dependencies

### Guardrail G1.1: No Direct Capability-to-Capability Access

```
RULE: No capability accesses another capability directly.

✅ CORRECT:
Capability A → Contract → Capability B

❌ WRONG:
Capability A → imports → Capability B
```

**Rationale:** Direct dependencies prevent capability replacement and testing.

**Enforcement:** Architecture review, dependency analysis tools.

---

### Guardrail G1.2: No Knowledge of Implementation Details

```
RULE: Core modules must never import or reference concrete implementations.

✅ CORRECT:
from core.contracts.security import AuthenticationProvider
provider: AuthenticationProvider

❌ WRONG:
from integrations.supabase import SupabaseAuth
auth: SupabaseAuth
```

**Rationale:** Core must remain agnostic to how contracts are implemented.

**Enforcement:** Linting rules, architecture tests.

---

### Guardrail G1.3: All Changes Require ADR

```
RULE: Any architectural decision must be documented in an ADR.

Scope of "architectural decision":
- New capability
- New domain
- Contract changes (v1, v2, v3)
- New infrastructure component
- Dependency direction changes
- New integration

✅ CORRECT:
ADR-0012: Adding Trust as a Cross-Cutting Service
Status: Accepted
Decision: Trust is a service, not a capability

❌ WRONG:
"We'll just add this module and document it later"
```

**Rationale:** Without ADRs, architectural decisions are invisible and impossible to trace.

**Enforcement:** PR cannot be merged without ADR for architectural changes.

---

### Guardrail G1.4: Contracts Are Versioned

```
RULE: All contracts must be versioned.

✅ CORRECT:
AuthenticationProviderV1
AuthenticationProviderV2

❌ WRONG:
AuthenticationProvider (assumed permanent)
```

**Rationale:** Breaking contracts in production is catastrophic. Versioning allows evolution without breaking existing implementations.

**Versioning Policy:**
- v1: Initial release
- Breaking changes → new major version
- Additive changes → new minor version
- Bug fixes → patch version

---

### Guardrail G1.5: Contract Compatibility Tests Required

```
RULE: Every contract must have compatibility tests.

For each contract:
✅ MUST have unit tests proving compliance
✅ MUST have breaking change detection tests
✅ MUST have backward compatibility tests

❌ WRONG:
Contract exists but has no tests proving implementations work
```

**Rationale:** Contracts without tests are assumptions, not guarantees.

---

## Category 2: Security & Compliance

### Guardrail G2.1: Audit Events Are Immutable

```
RULE: Once logged, audit events CANNOT be modified or deleted.

Implementation requirements:
✅ Append-only storage
✅ Cryptographic integrity verification
✅ No UPDATE or DELETE operations on audit tables
✅ Chain integrity verification

❌ ABSOLUTELY FORBIDDEN:
DELETE FROM audit_events WHERE event_id = '...'
UPDATE audit_events SET ... WHERE event_id = '...'
```

**Rationale:** HIPAA requires immutable audit trails.

**Enforcement:** Database constraints, application-level enforcement, automated tests.

---

### Guardrail G2.2: Tenant Context Is Mandatory

```
RULE: Every data operation MUST include tenant context.

✅ CORRECT:
tenant_id = get_current_tenant()
patient = await patient_repo.find(patient_id, tenant_id)

❌ WRONG:
patient = await patient_repo.find(patient_id)
-- No tenant context!
```

**Rationale:** Multi-tenant isolation is non-negotiable for patient data.

**Enforcement:**
- Database RLS policies
- Repository layer enforcement
- Automated tests for tenant isolation

---

### Guardrail G2.3: No SQL Outside Repositories

```
RULE: Raw SQL queries are FORBIDDEN outside of Repository classes.

✅ CORRECT:
class PatientRepository:
    async def find_by_id(self, patient_id, tenant_id):
        return await self.db.fetch_one(
            "SELECT * FROM patients WHERE id = $1 AND tenant_id = $2",
            patient_id, tenant_id
        )

❌ WRONG:
async def get_patient(patient_id):
    result = await db.execute(f"SELECT * FROM patients WHERE id = {patient_id}")
```

**Rationale:** Direct SQL bypasses tenant filtering, security checks, and audit logging.

**Enforcement:** Linting rules, architecture tests.

---

### Guardrail G2.4: All PHI Access Is Audited

```
RULE: Every access to Protected Health Information must be logged.

PHI includes:
- Patient demographics
- Medical history
- Diagnoses
- Treatments
- Vital signs
- Lab results

✅ CORRECT:
phi_access = PHIAccessEvent(
    principal_id=user.principal_id,
    patient_id=patient.patient_id,
    action="read",
    fields_accessed=["diagnoses", "medications"]
)
await audit.log_phi_access(phi_access)

❌ WRONG:
patient = await patient_repo.find(patient_id)
-- No PHI audit!
```

**Rationale:** HIPAA requires accounting of all PHI disclosures.

**Enforcement:** Automated tests, architecture tests.

---

### Guardrail G2.5: No Secrets in Code

```
RULE: Secrets must NEVER be committed to version control.

Allowed secret storage:
✅ Environment variables
✅ Secrets managers (Vault, AWS Secrets Manager)
✅ Configuration files (excluded from git)

❌ WRONG:
password = "admin123"  # In code!
api_key = "sk-xxxxx"   # In code!
```

**Rationale:** Secret exposure is a security breach.

**Enforcement:** Pre-commit hooks, automated scanning.

---

## Category 3: Data Integrity

### Guardrail G3.1: All Events Are Versioned

```
RULE: Every domain event must include a version field.

✅ CORRECT:
@dataclass
class PatientCreated(DomainEvent):
    event_version: str = "1.0"
    patient_id: str
    tenant_id: str

❌ WRONG:
@dataclass
class PatientCreated(DomainEvent):
    patient_id: str
    -- No version!
```

**Rationale:** Event schemas evolve. Without versioning, consumers cannot handle evolution.

**Enforcement:** Schema validation, contract tests.

---

### Guardrail G3.2: Strong Type Validation

```
RULE: All domain objects must use frozen dataclasses with validated types.

✅ CORRECT:
@dataclass(frozen=True)
class PatientId:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Patient ID cannot be empty")

❌ WRONG:
patient_id: str  # No type validation
```

**Rationale:** Invalid state must be impossible to represent.

**Enforcement:** Type checking (mypy, pyright), validation tests.

---

### Guardrail G3.3: No Null References in Domain Logic

```
RULE: Null values must be handled explicitly in domain objects.

✅ CORRECT:
@dataclass(frozen=True)
class CalibrationRecord:
    calibration_date: datetime
    next_calibration: datetime | None = None  # Explicit optional
    
    def is_overdue(self) -> bool:
        if self.next_calibration is None:
            return False
        return datetime.now() > self.next_calibration

❌ WRONG:
calibration_date: datetime = None  # Implicit optional!
if calibration_date is not None:  # Null checks everywhere
```

**Rationale:** Null checks scatter throughout code indicate design problems.

**Enforcement:** Type checking, code review.

---

## Category 4: Observability

### Guardrail G4.1: Every Capability Emits Metrics

```
RULE: Every capability must expose standard metrics.

Required metrics per capability:
✅ request_count_total
✅ request_duration_seconds (histogram)
✅ error_count_total
✅ active_requests (gauge)

✅ CORRECT:
metrics.increment("auth.authentication.success", {"method": "password"})
metrics.observe("auth.authentication.duration", duration, {"method": "password"})

❌ WRONG:
# No metrics emitted
```

**Rationale:** Without metrics, system health is invisible.

**Enforcement:** Architecture tests.

---

### Guardrail G4.2: Every Capability Emits Traces

```
RULE: Every capability must propagate OpenTelemetry traces.

✅ CORRECT:
with tracer.start_as_current_span("decision_support.evaluate") as span:
    span.set_attribute("patient.id", patient_id)
    result = await evaluate_decision(...)

❌ WRONG:
result = await evaluate_decision(...)  # No trace context
```

**Rationale:** Distributed tracing is required for debugging production issues.

**Enforcement:** Instrumentation tests.

---

### Guardrail G4.3: Structured Logging Only

```
RULE: All logging must use structured (JSON) format.

✅ CORRECT:
logger.info(
    "Authentication successful",
    extra={
        "principal_id": str(principal_id),
        "method": "password",
        "tenant_id": str(tenant_id),
        "duration_ms": duration_ms
    }
)

❌ WRONG:
logger.info(f"User {user_id} logged in successfully")  # Unstructured
```

**Rationale:** Structured logs enable log aggregation and analysis.

**Enforcement:** Logging tests, linting.

---

## Category 5: Cognitive Integrity

### Guardrail G5.1: Clinical Responses Require Evidence

```
RULE: Any clinical recommendation must cite evidence.

This is a PATIENT SAFETY requirement.

✅ CORRECT:
recommendation = Decision(
    conclusion="Consider beta-blocker therapy",
    evidence=[
        Evidence(source="AHA Guidelines 2023", trust_score=0.95),
        Evidence(source="Meta-analysis JACC 2022", trust_score=0.88)
    ],
    confidence=0.82,
    uncertainty="Limited evidence for specific patient population"
)

❌ WRONG:
recommendation = Decision(
    conclusion="Consider beta-blocker therapy"
    # No evidence!
)
```

**Rationale:** EREN Philosophy: "EREN never fabricates clinical information."

**Enforcement:** Architecture tests that verify evidence is present for clinical decisions.

---

### Guardrail G5.2: Trust Evaluation for All Evidence

```
RULE: Any evidence used in reasoning must have a trust evaluation.

Evidence → TrustEngine → Trusted Evidence → Reasoning → Decision

✅ CORRECT:
trust_score = await trust_engine.evaluate(evidence)
if trust_score.level == TrustLevel.UNCERTAIN:
    # Must be explicitly marked as uncertain
    conclusion.uncertainty_level = "HIGH"

❌ WRONG:
# Evidence used without trust evaluation
reasoning.use(evidence)
```

**Rationale:** EREN Philosophy: "EREN expresses trust in sources."

**Enforcement:** Architecture tests.

---

### Guardrail G5.3: Risk Assessment for All Decisions

```
RULE: Any clinical or operational decision must include risk assessment.

✅ CORRECT:
decision = Decision(
    action="Schedule maintenance now",
    risk_assessment=RiskAssessment(
        risk_level="HIGH",
        probability=0.15,
        severity="Patient monitoring gap",
        mitigation="Ensure backup monitoring available"
    )
)

❌ WRONG:
decision = Decision(action="Schedule maintenance now")
# No risk assessment!
```

**Rationale:** EREN Philosophy: "EREN expresses risk."

**Enforcement:** Architecture tests.

---

### Guardrail G5.4: All Recommendations Include Uncertainty

```
RULE: Any recommendation must quantify uncertainty.

✅ CORRECT:
recommendation = Recommendation(
    action="Increase monitoring frequency",
    confidence=0.72,  # Explicit confidence
    uncertainty="Evidence based on similar cases, not this patient's data",
    alternatives=["Maintain current frequency"]
)

❌ WRONG:
recommendation = Recommendation(
    action="Increase monitoring frequency"
    # No confidence, no uncertainty!
)
```

**Rationale:** EREN Philosophy: "EREN measures and expresses uncertainty."

**Enforcement:** Architecture tests.

---

### Guardrail G5.5: Explainability for All CDS

```
RULE: Clinical Decision Support must include explanation.

Every CDS recommendation must include:
✅ What EREN concluded
✅ Why EREN concluded it
✅ What evidence supported it
✅ What risks were considered
✅ What alternatives exist

✅ CORRECT:
explanation = Explanation(
    conclusion="Patient at risk of sepsis",
    reasoning_chain=[
        "Temperature elevated (>38°C)",
        "Heart rate elevated (>90 bpm)",
        "WBC elevated (>12,000)",
        "qSOFA score = 2",
        "High risk of sepsis"
    ],
    evidence=["Vital signs", "Lab results"],
    risks=["Missed early intervention", "Deterioration"],
    alternatives=["Monitor closely", "Order lactate"]
)

❌ WRONG:
recommendation = "Patient at risk"
# No explanation!
```

**Rationale:** EREN Philosophy: "EREN always explains its decisions."

**Enforcement:** Architecture tests.

---

## Guardrail Violations: Response Protocol

### When a Guardrail is Violated

```
Step 1: STOP
Do not proceed with the change.

Step 2: DOCUMENT
Create an ADR explaining:
- What guardrail was violated
- Why it was necessary
- What the risk is
- What mitigation exists

Step 3: REQUEST WAIVER
Submit to Architecture Board for review.

Step 4: WAIT FOR APPROVAL
No merge until Architecture Board approves or rejects.

Step 5: IF APPROVED
Add waiver to ADR with expiration date.
Track as technical debt.
```

---

## Guardrail Compliance Checklist

For every PR, verify:

```
CONTRACTS & DEPENDENCIES
□ G1.1: No direct capability access
□ G1.2: No implementation knowledge
□ G1.3: ADR for architectural changes
□ G1.4: Contracts versioned
□ G1.5: Contract compatibility tests

SECURITY & COMPLIANCE
□ G2.1: Audit events immutable
□ G2.2: Tenant context mandatory
□ G2.3: No raw SQL outside repositories
□ G2.4: PHI access audited
□ G2.5: No secrets in code

DATA INTEGRITY
□ G3.1: Events versioned
□ G3.2: Strong type validation
□ G3.3: No null references

OBSERVABILITY
□ G4.1: Metrics emitted
□ G4.2: Traces propagated
□ G4.3: Structured logging

COGNITIVE INTEGRITY
□ G5.1: Clinical evidence cited
□ G5.2: Trust evaluated
□ G5.3: Risk assessed
□ G5.4: Uncertainty quantified
□ G5.5: Explanation provided
```

---

## Enforcement Tools

| Guardrail | Tool | Enforcement |
|-----------|------|-------------|
| G1.1, G1.2 | Dependency analysis | CI/CD check |
| G1.3 | ADR requirement | PR template |
| G1.4, G1.5 | Contract tests | CI/CD |
| G2.1 | DB constraints | Database |
| G2.2, G2.3 | Repository layer | Architecture tests |
| G2.4 | Auto-audit | Architecture tests |
| G2.5 | Secret scanner | Pre-commit, CI/CD |
| G3.1, G3.2, G3.3 | Type checking | mypy, pyright |
| G4.1, G4.2, G4.3 | Observability tests | CI/CD |
| G5.1-G5.5 | Architecture tests | CI/CD |

---

## Review and Evolution

This document is part of Epic 0 and subject to Architecture Board governance.

**Changes to this document:**
- Require Architecture Board approval
- Must be documented in ADR
- Require stakeholder review (clinical, security, legal)

**Review frequency:**
- Quarterly review
- Before major version releases
- After significant incidents

---

*EREN Architectural Guardrails v1.0*
*Architecture Board - 2026-07-15*
*These rules are the constitution of EREN engineering.*
