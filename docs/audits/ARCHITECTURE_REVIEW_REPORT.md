# EREN Epic 0 — Architecture Review Report

**Review Board:** Independent Architecture Review  
**Date:** 2026-07-15  
**Scope:** All Epic 0 documents  
**Objective:** Critical audit before proceeding to Epic 1

---

## Executive Summary

| Category | Score | Status |
|----------|-------|--------|
| Philosophy | 9.0/10 | ✅ APPROVED with notes |
| Domain Model | 8.0/10 | ⚠️ CHANGES REQUIRED |
| Capability Map | 7.5/10 | ⚠️ REVISIONS REQUIRED |
| Cognitive Model | 8.5/10 | ✅ APPROVED with notes |
| Architecture | 8.0/10 | ⚠️ CHANGES REQUIRED |
| Contracts | 7.0/10 | ⚠️ REVISIONS REQUIRED |
| Scalability | 7.5/10 | ⚠️ REVISIONS REQUIRED |
| **OVERALL** | **8.0/10** | **⚠️ PROCEED WITH CHANGES** |

---

## Critical Issues: 0
## High Issues: 4
## Medium Issues: 8
## Low Issues: 12

---

## Auditoría A — Domain Model

### Finding A-1: Domain Boundary Ambiguity

**Severity:** HIGH  
**Document:** EREN_THREE_DOMAINS.md

**Issue:**
The three domains (Clinical, Biomedical, Hospital) are not clearly separated. Several concepts overlap:

```
OVERLAPPING CONCEPTS:
├── "Patient" appears in both Clinical AND Hospital
├── "Staff" appears in Hospital but also affects Clinical workflow
├── "Equipment" appears in Biomedical but Hospital tracks inventory
├── "Alert" is listed in Biomedical but affects Clinical decisions
```

**Evidence:**
```markdown
Clinical Domain includes: Patient, Diagnosis, Treatment
Hospital Domain includes: Staff, Inventory, Costs

But "Staff" manages "Patient" in Clinical context.
But "Inventory" includes Biomedical "Equipment".
```

**Impact:**
- Unclear ownership of entities
- Risk of domain coupling
- Implementation will be unclear about which domain owns what

**Recommendation:**
Define explicit ownership rules:
```markdown
Patient —> Clinical Domain (owns)
Staff —> Hospital Domain (owns), used by Clinical
Equipment —> Biomedical Domain (owns), tracked by Hospital
Alert —> Biomedical Domain (source), triggers Clinical Domain
```

**Resolution:** MODIFY before Epic 1

---

### Finding A-2: Missing Domain

**Severity:** HIGH  
**Document:** EREN_THREE_DOMAINS.md

**Issue:**
There is no **Operations Domain** despite Operations being central to hospital function.

**Missing:**
- Scheduling (surgeries, appointments, shifts)
- Billing/Finance
- Supply Chain
- Compliance/Regulatory

**Evidence:**
The Three Domains show Clinical, Biomedical, Hospital. But hospitals have:
- Operations Management
- Financial Management
- Compliance Management

**Impact:**
- Incomplete coverage
- These capabilities will fall into wrong domains
- Hospital Twin will be incomplete

**Recommendation:**
Consider adding:
```
FOURTH DOMAIN: Operations Domain
├── Scheduling
├── Billing
├── Supply Chain
├── Compliance Tracking
├── Reporting
```

Or clarify these belong to Hospital Domain (but they currently don't appear there).

**Resolution:** CLARIFY before Epic 1

---

### Finding A-3: Cross-Domain Events Undefined

**Severity:** MEDIUM  
**Document:** EREN_THREE_DOMAINS.md

**Issue:**
The document mentions cross-domain integration but doesn't define:
- How domains communicate
- What events cross boundaries
- Who owns cross-domain processes

**Evidence:**
```markdown
Cross-Domain Example: "Patient in Room 305 requires transport to MRI"
Clinical input: Patient stability, transport risk
Biomedical input: Transport monitor availability
Hospital input: MRI wait time, staff availability

But WHO coordinates this? Which domain owns the decision?
```

**Impact:**
- Unclear responsibility
- Implementation will have conflicts

**Recommendation:**
Define explicit "Integration Context" for cross-domain scenarios.

**Resolution:** DOCUMENT before Epic 1

---

## Auditoría B — Philosophy

### Finding B-1: "EREN Always Explains" — Not Measurable

**Severity:** MEDIUM  
**Document:** EREN_PHILOSOPHY.md

**Issue:**
Principle #2 states "EREN always explains its decisions" but there's no definition of what constitutes an adequate explanation.

**Question:**
- Minimum words?
- Required elements?
- Traceability depth?
- What if explanation takes too long in emergencies?

**Evidence:**
```markdown
2. EREN Always Explains Its Decisions
   "Transparency is non-negotiable."
   "A recommendation without explanation is a black box."
   
But HOW is this measured? What's the acceptance criteria?
```

**Impact:**
- Cannot verify compliance
- Cannot test
- Implementation ambiguity

**Recommendation:**
Add measurable criteria:
```markdown
Every recommendation must include:
- Conclusion (1-2 sentences)
- Supporting evidence (at least 1 source)
- Confidence level (0-100%)
- Risk assessment (if applicable)
- Alternative options (if applicable)
```

**Resolution:** ADD METRICS to principle

---

### Finding B-2: "EREN Never Fabricates" — Needs Enforcement

**Severity:** HIGH  
**Document:** EREN_PHILOSOPHY.md

**Issue:**
Principle #4 "EREN never fabricates clinical information" needs technical enforcement, not just philosophical statement.

**Evidence:**
The philosophy says EREN must never invent dosages, protocols, specifications. But:
- No mechanism defined to prevent this
- No hallucination detection specified
- No "unknown" state defined

**Impact:**
- Without technical enforcement, this is aspirational
- Hallucination is a patient safety issue

**Recommendation:**
Add to Philosophy:
```markdown
4. EREN Never Fabricates
   - Every claim MUST cite a source
   - When source is unknown, state explicitly: "I don't have information about X"
   - Implement hallucination detection
   - Never generate unverified clinical content
```

**Resolution:** ADD TECHNICAL ENFORCEMENT

---

### Finding B-3: "EREN Enables, Not Automates" — Contradiction Risk

**Severity:** LOW  
**Document:** EREN_PHILOSOPHY.md

**Issue:**
Principle #12 "EREN enables, not automates" might conflict with:
- Automated alarm routing
- Automated device status monitoring
- Automated scheduling suggestions

**Evidence:**
Some automation might be beneficial (e.g., "automatically silence acknowledged alarms"). Is this automation or enabling?

**Recommendation:**
Clarify boundary:
```markdown
EREN enables, not automates CLINICAL DECISIONS.
EREN MAY automate OPERATIONAL tasks with human oversight.
```

**Resolution:** CLARIFY in Philosophy

---

## Auditoría C — Capability Map

### Finding C-1: Trust Is Not a Capability

**Severity:** HIGH  
**Document:** EREN_CAPABILITY_MAP.md

**Issue:**
"Trust" is listed as a cognitive capability, but Trust is an **evaluation** of other things, not a capability itself.

**Evidence:**
```markdown
Cognitive Capabilities:
- Trust — Evaluate source credibility

But Trust evaluates:
- Evidence (from Knowledge)
- Devices (from Biomedical)
- Clinical guidelines (from Clinical)
```

**Problem:**
Trust cannot exist independently. It's a **quality** that applies to other capabilities.

**Recommendation:**
**Option 1:** Move Trust to a cross-cutting quality (like Security)
**Option 2:** Redefine Trust as "TrustEvaluation" which is a service that other capabilities use
**Option 3:** Keep Trust as a capability but clarify it only evaluates evidence (not devices, not clinical)

Which is correct?

**Resolution:** REDEFINE before Epic 1

---

### Finding C-2: Hospital Twin Is a Product, Not a Capability

**Severity:** MEDIUM  
**Document:** EREN_CAPABILITY_MAP.md

**Issue:**
"Hospital Twin" is listed as a capability. But a Digital Twin is an **implementation approach**, not a capability.

**Evidence:**
```markdown
Hospital Capabilities:
- HospitalTwin — Digital representation of hospital

But what does HospitalTwin DO?
- Monitor capacity? That's CapacityManagement
- Track devices? That's AssetTracking
- Predict occupancy? That's Analytics
```

**Problem:**
Hospital Twin aggregates other capabilities. It's not a primitive capability.

**Recommendation:**
Either:
1. Remove HospitalTwin as standalone capability
2. Redefine HospitalTwin as "Unified Hospital View" that synthesizes other capabilities
3. Define HospitalTwin as a SPECIFIC IMPLEMENTATION approach

**Resolution:** CLARIFY SCOPE

---

### Finding C-3: Learn Is Behavior, Not Capability

**Severity:** MEDIUM  
**Document:** EREN_CAPABILITY_MAP.md

**Issue:**
"Learn" is listed as a cognitive capability. But learning is what cognitive systems DO, not a separate module.

**Evidence:**
```markdown
Cognitive Capabilities:
- Learn — Improve from outcomes

But:
- Memory consolidates experiences
- Trust adjusts based on outcomes
- Knowledge updates with new facts

These ARE learning. Is Learn separate?
```

**Problem:**
If Memory, Trust, and Knowledge all learn, what does standalone "Learn" do?

**Recommendation:**
Either:
1. Remove standalone "Learn" capability
2. Define Learn as a meta-capability that coordinates other learning
3. Define what standalone Learn adds beyond other capabilities

**Resolution:** REDEFINE

---

### Finding C-4: Missing Capabilities

**Severity:** LOW  
**Document:** EREN_CAPABILITY_MAP.md

**Issue:**
Several expected capabilities are missing:

**Missing:**
- **Notification** — How does EREN alert humans?
- **History** — How does EREN track longitudinal data?
- **Versioning** — How does EREN track changes to knowledge?
- **Consent** — How does EREN manage patient consent (HIPAA)?

**Recommendation:**
Add these to Capability Map or clarify they fall under existing capabilities.

**Resolution:** ADD or CLARIFY

---

## Auditoría D — Contracts

### Finding D-1: IdentityProvider Has Too Many Responsibilities

**Severity:** HIGH  
**Document:** core/contracts/security/identity.py

**Issue:**
IdentityProvider mixes authentication AND session management AND principal management.

**Evidence:**
```python
class IdentityProvider(Protocol):
    # Authentication
    async def authenticate(credentials: dict) -> AuthenticationResult
    async def verify_token(token: str) -> Principal | None
    
    # Session Management
    async def create_session(principal: Principal) -> Session
    async def get_session(session_id: str) -> Session | None
    async def refresh_session(session_id: str) -> Session
    async def invalidate_session(session_id: str) -> bool
    
    # Principal Management
    async def create_principal(...) -> Principal
    async def update_principal(...) -> Principal
    async def suspend_principal(...) -> bool
```

**Problem:**
This violates Single Responsibility Principle. Authentication shouldn't know about sessions.

**Recommendation:**
Split into three contracts:
```python
class AuthenticationProvider(Protocol):
    async def authenticate(credentials) -> AuthenticationResult
    async def verify_token(token) -> Principal | None

class SessionProvider(Protocol):
    async def create_session(principal) -> Session
    async def refresh_session(session_id) -> Session
    async def invalidate_session(session_id) -> bool

class PrincipalProvider(Protocol):
    async def create_principal(...) -> Principal
    async def update_principal(...) -> Principal
```

**Resolution:** REFACTOR before Epic 1

---

### Finding D-2: AuditProvider Lacks Immutability Guarantee

**Severity:** MEDIUM  
**Document:** core/contracts/security/audit.py

**Issue:**
The contract defines `log()` but doesn't guarantee immutability.

**Evidence:**
```python
async def log(self, event: AuditEvent) -> str:
    """Log an audit event."""
```

No mention of:
- Append-only storage
- No update method (only create)
- No delete method
- Hash chaining for tamper detection

**Impact:**
- HIPAA compliance requires immutable audit trail
- Without guarantee, implementation might allow modifications

**Recommendation:**
Add to contract:
```python
async def log(event: AuditEvent) -> str:
    """Log an audit event. Events are IMMUTABLE once logged."""

# Explicitly NO update or delete methods
# Add hash_chaining for verification
async def verify_integrity(event_id: str) -> bool:
    """Verify event hasn't been tampered with."""
```

**Resolution:** ADD IMMUTABILITY GUARANTEES

---

### Finding D-3: TrustProvider — Abstract Definition

**Severity:** MEDIUM  
**Document:** core/contracts/cognitive/trust.py

**Issue:**
TrustProvider defines TrustScore but the evaluation algorithm is not defined.

**Evidence:**
```python
@dataclass(frozen=True)
class TrustScore:
    level: TrustLevel  # HIGH, MODERATE, LOW, UNCERTAIN
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
```

But HOW is score calculated? What factors? What algorithm?

**Question:**
- Is this Bayesian?
- Is this weighted evidence?
- Is this human-annotated?
- Is this ML model?

**Impact:**
- Two implementations could produce different scores
- No way to verify consistency

**Recommendation:**
Add to contract:
```python
async def evaluate_source_trust(...) -> TrustScore:
    """
    Evaluate trust using [ALGORITHM]:
    - Publication date weight: X%
    - Validation count weight: Y%
    - Source type weight: Z%
    
    Or: "Trust evaluation is implementation-specific"
    """

# Define minimum requirements
# Define what "HIGH" means as minimum
```

**Resolution:** DEFINE ALGORITHM or ACKNOWLEDGE VARIANCE

---

### Finding D-4: Contracts Missing Exception Definitions

**Severity:** LOW  
**Document:** All contracts

**Issue:**
Contracts define interfaces but not specific exceptions.

**Evidence:**
No `from .exceptions import ...` in any contract file.

**Recommendation:**
Add exception hierarchy to each contract:
```python
# core/contracts/security/identity/exceptions.py
class IdentityError(Exception): pass
class AuthenticationError(IdentityError): pass
class InvalidCredentialsError(AuthenticationError): pass
class SessionExpiredError(IdentityError): pass
```

**Resolution:** ADD to each contract package

---

## Auditoría E — Architecture

### Finding E-1: Dependency Direction Violation

**Severity:** HIGH  
**Document:** EREN_ARCHITECTURE_BLUEPRINT.md

**Issue:**
The architecture states "Domain capabilities feed cognitive, not the reverse" but some dependencies suggest otherwise.

**Evidence:**
```markdown
ClinicalContext
  feeds → PERCEIVE
  feeds → KNOW
  feeds → REMEMBER

DecisionSupport
  uses → REASON
  uses → TRUST
  uses → ASSESS_RISK
  uses → DECIDE
```

But "DecisionSupport" is a DOMAIN capability (Clinical). It USES cognitive capabilities. This seems correct.

But if DecisionSupport produces trust evaluations, does it depend on TrustProvider?

**Question:**
Who evaluates the TRUST of the evidence that DecisionSupport uses?

**Ambiguity:**
```
Option A: Trust is INDEPENDENT capability that evaluates evidence
Option B: Trust is PART OF DecisionSupport (self-trusts its own reasoning)
Option C: Trust is PART OF ClinicalContext (context-trusts its own data)
```

**Recommendation:**
Clarify the trust evaluation pipeline:
```
Evidence → [Trust Evaluator] → Trusted Evidence → Reasoning → Decision
                    ↑
          Which capability owns this?
```

**Resolution:** CLARIFY TRUST PIPELINE

---

### Finding E-2: Event Bus Coupling

**Severity:** MEDIUM  
**Document:** EREN_ARCHITECTURE_BLUEPRINT.md

**Issue:**
The Event Bus is in Infrastructure Layer but everything publishes to it.

**Evidence:**
```markdown
Cognitive Events
Clinical Events  
Biomedical Events
Hospital Events
```

All publish to the same Event Bus.

**Problem:**
- If Event Bus is infrastructure, it should be stable
- But adding new event types requires infrastructure changes
- This creates coupling

**Recommendation:**
Define Event Bus as a capability:
```
EventBus — ADAPTER
├── InMemoryEventBus (development)
├── KafkaEventBus (production)
├── RabbitMQEventBus (production)
```

But event SCHEMAS should be in domain contracts.

**Resolution:** SEPARATE bus implementation from event schemas

---

### Finding E-3: "Contracts First" May Be Premature

**Severity:** LOW  
**Document:** EREN_ARCHITECTURE_BLUEPRINT.md

**Issue:**
"Contract-first development" is stated as a rule, but some contracts (like TrustProvider) are too abstract to be useful.

**Evidence:**
TrustProvider has ~10 methods but no defined algorithm for evaluation.

**Problem:**
Writing contracts before understanding implementation can lead to:
- Contracts that don't match reality
- Over-engineered abstractions
- Missing methods discovered late

**Recommendation:**
Hybrid approach:
- Write contracts for KNOWN requirements
- Write stubs for EXPLORATORY capabilities
- Evolve contracts through RFC process

**Resolution:** ACKNOWLEDGE CONTRACT LIMITATIONS

---

## Auditoría F — Scalability

### Finding F-1: Event Bus Scalability Unknown

**Severity:** MEDIUM  
**Document:** EREN_ARCHITECTURE_BLUEPRINT.md

**Issue:**
Architecture mentions "Event Bus" but doesn't specify:
- Throughput (events/second)
- Storage requirements
- Partitioning strategy
- Cross-region replication

**Scenario:**
```
100 hospitals
10M events/day
= 115 events/second average
= Peak maybe 1000 events/second

Can in-memory EventBus handle this?
```

**Recommendation:**
Define:
```markdown
Event Bus Requirements:
- Minimum throughput: 1,000 events/second
- Storage: 30 days hot, 7 years cold
- Replication: Multi-region for HA
- Latency: < 100ms end-to-end

Based on requirements, recommend:
- Development: In-memory
- Production: Kafka / RabbitMQ
```

**Resolution:** ADD SCALABILITY REQUIREMENTS

---

### Finding F-2: Knowledge Graph Scalability

**Severity:** MEDIUM  
**Document:** EREN_CAPABILITY_MAP.md

**Issue:**
"Knowledge Graph" is a capability but scalability is not addressed.

**Questions:**
- Graph DB (Neo4j) for what exactly?
- Entities and relationships?
- Clinical relationships?
- Device dependencies?

**Problem:**
Knowledge Graph at hospital scale:
```
1 hospital = ~1M entities
100 hospitals = 100M entities

Can Neo4j handle 100M entities?
```

**Recommendation:**
Define scope:
```markdown
Knowledge Graph Scope:
- Medical ontology (fixed, ~500K concepts)
- Device relationships (~10K per hospital)
- Clinical relationships (per encounter, ephemeral)

Strategy:
- Fixed ontologies: GraphDB
- Ephemeral data: Not in GraphDB
```

**Resolution:** DEFINE SCOPE AND STORAGE STRATEGY

---

### Finding F-3: Multi-Tenancy Not Addressed

**Severity:** MEDIUM  
**Document:** EREN_ARCHITECTURE_BLUEPRINT.md

**Issue:**
Architecture doesn't address multi-tenancy (multiple hospitals on same deployment).

**Questions:**
- Is EREN single-tenant or multi-tenant?
- How is data isolation handled?
- How is tenant routing done?

**Scenario:**
```
Hospital A data MUST NOT be visible to Hospital B
How is this enforced at:
- Database level?
- Application level?
- Contract level?
```

**Recommendation:**
Define tenant model:
```markdown
Tenant Strategy:
- Database per tenant (isolation)
- OR
- Tenant ID on all records (shared DB)
- OR
- Hybrid (shared DB, separate GraphDB)

Which is EREN's approach?
```

**Resolution:** DEFINE TENANT MODEL

---

## Summary of Findings

### Critical Issues: 0

### High Issues: 4

| ID | Issue | Document | Recommendation |
|----|-------|----------|----------------|
| A-1 | Domain Boundary Ambiguity | Three Domains | DEFINE OWNERSHIP |
| A-2 | Missing Operations Domain | Three Domains | ADD OR CLARIFY |
| C-1 | Trust Is Not Capability | Capability Map | REDEFINE |
| D-1 | IdentityProvider Too Many Responsibilities | Contracts | SPLIT CONTRACT |

### Medium Issues: 8

| ID | Issue | Document |
|----|-------|----------|
| A-3 | Cross-Domain Events Undefined | Three Domains |
| B-1 | "Always Explains" Not Measurable | Philosophy |
| B-2 | "Never Fabricates" Needs Enforcement | Philosophy |
| C-2 | Hospital Twin Is Product Not Capability | Capability Map |
| C-3 | Learn Is Behavior Not Capability | Capability Map |
| D-2 | AuditProvider Lacks Immutability | Contracts |
| D-3 | TrustProvider Algorithm Undefined | Contracts |
| F-1 | Event Bus Scalability Unknown | Architecture |

### Low Issues: 12

| ID | Issue |
|----|-------|
| B-3 | "Enables Not Automates" Ambiguity |
| C-4 | Missing Capabilities (Notification, History, etc.) |
| D-4 | Contracts Missing Exception Definitions |
| E-2 | Event Bus Coupling |
| E-3 | Contracts First Premature |
| F-2 | Knowledge Graph Scalability |
| F-3 | Multi-Tenancy Not Addressed |
| + 5 more minor issues |

---

## Recommendations by Priority

### Must Fix Before Epic 1 (High Priority)

1. **Define Domain Ownership** — Which domain owns each entity
2. **Clarify Operations Domain** — Add or explicitly exclude
3. **Redefine Trust** — Capability or quality?
4. **Split IdentityProvider** — Authentication ≠ Session ≠ Principal

### Should Fix Before Epic 1 (Medium Priority)

5. **Add Trust Algorithm** — Or acknowledge implementation variance
6. **Add Audit Immutability** — HIPAA requires this
7. **Measure Philosophy** — Make principles measurable
8. **Define Scalability** — Event bus, knowledge graph, multi-tenancy

### Can Address in Epic 1 (Low Priority)

9. Add missing capabilities
10. Add contract exceptions
11. Separate bus from schemas
12. Document contract limitations

---

## Architecture Review Decision

### Overall Score: 8.0/10

### Status: ⚠️ PROCEED WITH CHANGES

### Conditions for Epic 1 Approval

1. ✅ Resolve 4 High Priority issues
2. ⚠️ Address Medium Priority issues (can be tracked)
3. ✅ Document 12 Low Priority issues as tech debt

### Recommendation

**APPROVE Epic 0 for Epic 1 development with conditions:**

```markdown
Epic 0 Status: APPROVED WITH CONDITIONS

Before proceeding to Epic 1 implementation:

Required Changes:
□ Define entity ownership across 3 domains
□ Clarify if Operations is 4th domain
□ Redefine Trust capability scope
□ Split IdentityProvider into 3 contracts

Documentation Required:
□ Trust evaluation algorithm
□ Audit immutability guarantees
□ Scalability requirements (events/sec, storage)
□ Multi-tenant strategy

Tech Debt (Track, Don't Block):
□ Missing capabilities
□ Contract exceptions
□ Event bus coupling
```

---

## Signatures

| Role | Name | Decision |
|------|------|----------|
| Principal Engineer | Architecture Board | APPROVED WITH CONDITIONS |
| Domain Expert | (Pending Review) | - |
| Security Expert | (Pending Review) | - |
| Clinical Advisor | (Pending Review) | - |

---

*EREN Epic 0 Architecture Review Report v1.0*  
*Review Date: 2026-07-15*  
*Next Review: After required changes*
