# EREN Capability Dependencies
## How capabilities relate to each other

---

## Dependency Principles

1. **Cognitive capabilities** form the core processing layer
2. **Security capabilities** are foundational (no other capability should work without them)
3. **Domain capabilities** depend on both cognitive and security
4. **Integration capabilities** are adapters to external systems

---

## Dependency Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                          │
│  (FHIR, HL7, DICOM, MQTT, REST, Webhooks)                   │
│  These are adapters. They adapt external systems.            │
└────────────────────────────┬────────────────────────────────┘
                             │ feeds
┌────────────────────────────▼────────────────────────────────┐
│                    DOMAIN LAYER                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   CLINICAL   │  │ BIOMEDICAL   │  │   HOSPITAL   │       │
│  │              │  │              │  │              │       │
│  │ClinicalContext│ DeviceRegistry│ CapacityMgmt │       │
│  │DecisionSupport│ AlarmMgmt    │ HospitalTwin │       │
│  │DrugInteraction│ Calibration   │ Maintenance  │       │
│  │EvidenceRetrieval│AssetTracking│ Staffing    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                   COGNITIVE LAYER                            │
│                                                              │
│          ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│          │  TRUST   │  │RISK_ASSESS│  │  REASON  │          │
│          └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│               │              │              │               │
│          ┌────▼──────────────▼──────────────▼─────┐         │
│          │              DECIDE                    │         │
│          └────────────────┬───────────────────────┘         │
│                           │                                 │
│     ┌─────────────────────┼─────────────────────┐          │
│     │                     │                     │          │
│ ┌───▼───┐          ┌────▼────┐         ┌────▼────┐      │
│ │ PERCEIVE│         │ REMEMBER │         │   KNOW  │      │
│ └───────┘          └────┬────┘         └────┬────┘      │
│                         │                     │             │
└─────────────────────────┼─────────────────────┼─────────────┘
                          │                     │
┌─────────────────────────▼─────────────────────▼─────────────┐
│                    SECURITY LAYER                            │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌──────┐  ┌─────────┐          │
│  │IDENTITY │  │AUTHORIZE │  │AUDIT │  │ENCRYPT  │          │
│  └─────────┘  └──────────┘  └──────┘  └─────────┘          │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌──────┐                      │
│  │ SECRETS │  │  POLICY  │  │TRUST │                      │
│  └─────────┘  └──────────┘  └──────┘                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Detailed Dependencies

### Cognitive → Cognitive

```
PERCEIVE
  ↑
  │ (context from perception)
  └→ REMEMBER (encodes perceptions)
  └→ KNOW (feeds knowledge)
  
REMEMBER
  ↑ (retrieves memories)
  └→ REASON (feeds reasoning)
  └→ TRUST (historical trust)
  └→ KNOW (reinforces knowledge)
  
KNOW
  ↑ (provides evidence)
  └→ REASON (feeds reasoning)
  └→ TRUST (source information)
  └→ DECIDE (informs decisions)
  
TRUST
  ↑ (trusts sources)
  └→ REASON (weights evidence)
  └→ DECIDE (affects options)
  └→ ASSESS_RISK (trust affects risk)
  
ASSESS_RISK
  ↑ (risks evaluated)
  └→ DECIDE (risk in decisions)
  └→ REASON (risk in reasoning)
  
REASON
  ↑ (inferences)
  └→ DECIDE (basis for decisions)
  └→ TRUST (validates trust)
  
DECIDE
  ↑ (decisions made)
  └→ EXPLAIN (explains decisions)
  └→ LEARN (learns from outcomes)
  └→ PLAN (informs planning)
  
EXPLAIN
  ↑ (explanations generated)
  └→ LEARN (feedback from humans)
  
LEARN
  ↑ (learning updates)
  └→ REMEMBER (consolidates memories)
  └→ TRUST (adjusts trust)
  └→ KNOW (adds knowledge)
  
PLAN
  ↑ (plans created)
  └→ DECIDE (informs decisions)
```

### Domain → Cognitive

```
CLINICAL_CONTEXT
  feeds → PERCEIVE (clinical signals)
  feeds → KNOW (clinical knowledge)
  feeds → REMEMBER (patient history)
  
DECISION_SUPPORT
  uses → REASON
  uses → TRUST
  uses → ASSESS_RISK
  uses → DECIDE
  produces → EXPLAIN
  
DRUG_INTERACTION
  uses → KNOW (drug database)
  uses → TRUST (source reliability)
  uses → ASSESS_RISK (interaction severity)
  uses → EXPLAIN
  
DEVICE_REGISTRY
  feeds → KNOW (device knowledge)
  feeds → PERCEIVE (device signals)
  
ALARM_MANAGEMENT
  feeds → PERCEIVE (alarm signals)
  uses → TRUST (alarm credibility)
  uses → ASSESS_RISK (alarm severity)
  uses → DECIDE (escalation)
  
HOSPITAL_TWIN
  feeds → PERCEIVE (operational state)
  feeds → KNOW (hospital knowledge)
  uses → REASON
  uses → PLAN
  
CAPACITY_MANAGEMENT
  feeds → KNOW (capacity data)
  feeds → PERCEIVE (occupancy)
  uses → ASSESS_RISK (capacity risks)
  uses → PLAN
```

### Security → All

```
IDENTITY
  required by → all domain capabilities
  required by → all cognitive capabilities
  
AUTHORIZATION
  required by → all domain capabilities
  required by → all cognitive capabilities
  
AUDIT
  logs → all capability operations
  
ENCRYPTION
  protects → all data at rest
  protects → all data in transit
  
SECRETS
  protects → all credentials
  protects → all API keys
  
TRUST (security)
  validates → identity
  validates → authorization
  supports → all trust evaluations
  
POLICY
  enforces → all authorization
  enforces → access patterns
  supports → compliance
```

### Integration → Domain

```
FHIR
  feeds → CLINICAL_CONTEXT
  feeds → KNOW (FHIR resources as knowledge)
  exports → clinical decisions
  
HL7
  feeds → CLINICAL_CONTEXT
  feeds → ALARM_MANAGEMENT
  
DICOM
  feeds → KNOW (imaging metadata)
  feeds → DEVICE_REGISTRY
  
MQTT
  feeds → PERCEIVE (device telemetry)
  feeds → ALARM_MANAGEMENT (alarm streams)
  feeds → ASSET_TRACKING
  
REST
  enables → all external integrations
  enables → webhooks
  
Webhooks
  triggers → domain capabilities
  enables → external notifications
```

---

## Dependency Rules

### Rule 1: No Upward Dependencies

```
Cognitive should NOT depend on Domain.
  ❌ WRONG: REASONING depends on CLINICAL_CONTEXT
  ✅ RIGHT: CLINICAL_CONTEXT feeds REASONING
```

### Rule 2: Security is Foundation

```
No capability should function without security.
  ✅ Identity required by all
  ✅ Authorization required by all
  ✅ Audit logs everything
```

### Rule 3: Cognitive is Core

```
Domain capabilities use cognitive, not the reverse.
  ✅ DECISION_SUPPORT uses REASON
  ❌ REASON uses DECISION_SUPPORT
```

### Rule 4: Integration Adapts

```
Integration capabilities are adapters, not dependencies.
  ✅ FHIR adapts to clinical context
  ❌ Clinical context depends on FHIR
```

---

## Circular Dependency Prevention

### Potential Cycles (Must Break)

```
REMEMBER → REASON → DECIDE → LEARN → REMEMBER
  BREAK: LEARN → REMEMBER (must go through KNOW)

KNOW → TRUST → REASON → KNOW
  BREAK: Define trust as independent

DECIDE → EXPLAIN → LEARN → DECIDE
  BREAK: LEARN affects DECIDE indirectly via trust/knowledge
```

### Safe Cycles (Allowed)

```
Memory consolidation cycles are acceptable:
  LEARN → REMEMBER → KNOW → LEARN

Trust evolution is acceptable:
  REASON → TRUST → LEARN → REASON
```

---

## Coupling Matrix

| From \ To | Identity | Trust | Reason | Decide | Clinical | Biomedical | Hospital |
|----------|----------|-------|--------|--------|----------|------------|----------|
| **Identity** | - | S | S | S | S | S | S |
| **Trust** | S | - | H | H | H | H | S |
| **Reason** | S | H | - | H | H | H | S |
| **Decide** | S | S | H | - | H | H | H |
| **Clinical** | S | S | F | F | - | S | S |
| **Biomedical** | S | S | F | F | S | - | S |
| **Hospital** | S | S | F | F | S | S | - |

```
S = Security coupling (required)
H = High coupling (strong dependency)
F = Feed coupling (data flows, not dependencies)
- = No coupling
```

---

## Implementation Order

Based on dependencies, implementation should follow:

```
Step 1: Security Foundation
├── Identity
├── Authorization
├── Audit
└── Encryption

Step 2: Cognitive Foundation
├── Perceive
├── Remember
├── Know
└── Trust (independent evaluation)

Step 3: Core Cognitive
├── AssessRisk
├── Reason
├── Decide
└── Explain

Step 4: Clinical Foundation
├── ClinicalContext (needs: Identity, Know)
├── FHIR (needs: Identity, ClinicalContext)
└── MQTT (needs: Identity, Perceive)

Step 5: Clinical Capabilities
├── DecisionSupport (needs: Reason, Trust, AssessRisk)
├── DrugInteraction (needs: Know, Trust, AssessRisk)
└── EvidenceRetrieval (needs: Know, Reason)

Step 6: Biomedical
├── DeviceRegistry (needs: Identity, Audit)
├── AlarmManagement (needs: MQTT, Trust, AssessRisk)
└── CalibrationTracking (needs: DeviceRegistry)

Step 7: Hospital
├── HospitalTwin (needs: All domains)
├── CapacityManagement (needs: HospitalTwin)
└── MaintenanceScheduling (needs: DeviceRegistry)

Step 8: Advanced Cognitive
├── Learn (needs: Decide, Know, Remember)
├── Plan (needs: Decide, AssessRisk)
└── Reflect (needs: Learn)
```

---

## Key Architectural Decisions

### ADR-0001: Cognitive Core is Independent
```
Decision: Cognitive capabilities (Trust, Reason, Decide) 
          do NOT depend on domain capabilities.
          
Rationale: Ensures cognitive processing is reusable
           across all domains.
           
Impact: Domain capabilities feed cognitive, not the reverse.
```

### ADR-0002: Security is Horizontal
```
Decision: Security capabilities (Identity, Authorization, 
          Audit) are horizontal and required by all.
          
Rationale: HIPAA and IEC 62304 require security controls.
           
Impact: Every capability must integrate with security.
```

### ADR-0003: Integration is Adapters
```
Decision: Integration capabilities (FHIR, MQTT, DICOM) 
          are adapters, not dependencies.
          
Rationale: External systems should not constrain EREN design.
           
Impact: EREN defines its own models, adapters connect.
```

---

*EREN Capability Dependencies v1.0*
*Architecture Board - 2026-07-15*
