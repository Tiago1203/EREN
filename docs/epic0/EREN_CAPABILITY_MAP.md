# EREN Capability Map
## Complete Capability Inventory for EREN OS

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |
| 1.1 | 2026-07-16 | Architecture Board | Realigned with EPIC roadmap phases |

---

## Overview

This document maps all capabilities required by EREN, organized by domain and cognitive function. Each capability is evaluated for:
- **Functional Maturity** (technical readiness)
- **Clinical Maturity** (evidence-based validation)
- **Domain Alignment** (Clinical, Biomedical, Hospital)

---

## Capability Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPABILITY LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  COGNITIVE CAPABILITIES (How EREN thinks)                  │
│  ├── Perceive  Remember  Know  Trust  AssessRisk           │
│  ├── Reason  Plan  Decide  Explain  Learn  Reflect          │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SECURITY CAPABILITIES (Trust & Safety)                     │
│  ├── Identity  Authorization  Audit  Encryption            │
│  ├── Secrets  Policy  Compliance  Trust  Risk                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CLINICAL CAPABILITIES (Patient Care)                       │
│  ├── ClinicalContext  DecisionSupport  Evidence             │
│  ├── Diagnostics  TreatmentGuidance  Alerting               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BIOMEDICAL CAPABILITIES (Device Management)                │
│  ├── DeviceManagement  Calibration  Maintenance             │
│  ├── AssetTracking  Monitoring  AlarmManagement             │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  HOSPITAL CAPABILITIES (Operations)                         │
│  ├── CapacityManagement  Staffing  Inventory               │
│  ├── Scheduling  Reporting  Analytics                       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INTEGRATION CAPABILITIES (External Systems)                 │
│  ├── FHIR  HL7  DICOM  MQTT  REST  Webhooks              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Cognitive Capabilities

> **⚠️ EXPERIMENTAL: This section is subject to significant change during initial implementation.**

Cognitive capabilities define how EREN processes information. They are likely to evolve substantially based on:
- Implementation experience
- Clinical validation
- Performance requirements
- Real-world testing

**Do not freeze cognitive models prematurely.**

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **Perceive** | Capture signals from environment | 4/2 | All | Critical |
| **Remember** | Store and retrieve memories | 3/1 | All | Critical |
| **Know** | Manage structured knowledge | 4/2 | All | Critical |
| **Trust** | Evaluate source credibility | 2/0 | All | Critical |
| **AssessRisk** | Evaluate potential harms | 2/1 | All | Critical |
| **Reason** | Generate inferences | 2/0 | All | Critical |
| **Plan** | Create action plans | 3/1 | All | High |
| **Decide** | Select among options | 2/0 | All | Critical |
| **Explain** | Generate human-readable explanations | 2/1 | All | Critical |
| **Learn** | Improve from outcomes | 1/0 | All | High |
| **Reflect** | Evaluate own reasoning | 1/0 | All | Medium |

### Cognitive Capability Details

#### Perceive
```
Purpose: Capture signals from devices, users, and systems
Inputs: Raw sensor data, user input, system events
Outputs: Structured perceptions with confidence
Dependencies: Device integration, event bus
Clinical Validation: Required for alarm handling
```

#### Remember
```
Purpose: Store experiences and retrieve relevant memories
Inputs: Experiences, outcomes, context
Outputs: Memory references
Dependencies: Memory stores, retrieval engine
Clinical Validation: Required for case-based reasoning
```

#### Trust
```
Purpose: Evaluate credibility of sources and evidence
Inputs: Sources, evidence, credentials
Outputs: Trust scores (0-100%)
Dependencies: Knowledge base, evidence engine
Clinical Validation: CRITICAL - affects all decisions
```

#### AssessRisk
```
Purpose: Evaluate potential harms and their likelihood
Inputs: Situations, scenarios, decisions
Outputs: Risk scores, hazard identification
Dependencies: Risk models, compliance engine
Clinical Validation: CRITICAL - patient safety
```

#### Reason
```
Purpose: Generate inferences from evidence
Inputs: Evidence, context, trust levels
Outputs: Inferences with confidence
Dependencies: Knowledge graph, evidence engine
Clinical Validation: Required for clinical decisions
```

#### Decide
```
Purpose: Select optimal action from options
Inputs: Options, preferences, constraints, risk tolerance
Outputs: Decisions with rationale
Dependencies: Reasoning, trust, risk assessment
Clinical Validation: CRITICAL - core function
```

---

## 2. Security Capabilities

These capabilities ensure EREN operates safely and compliantly.

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **Identity** | Manage user/device identities | 5/5 | All | Critical |
| **Authorization** | Control access permissions | 5/5 | All | Critical |
| **Audit** | Log all significant actions | 4/4 | All | Critical |
| **Encryption** | Protect data at rest/transit | 4/4 | All | Critical |
| **Secrets** | Manage credentials and keys | 3/3 | All | High |
| **Policy** | Enforce access policies | 3/2 | All | High |
| **Compliance** | Ensure regulatory compliance | 1/0 | All | Critical |

### Security Capability Details

#### Identity
```
Purpose: Authenticate users and devices
Inputs: Credentials, tokens, certificates
Outputs: Verified identity principals
Dependencies: Auth providers (Supabase, Keycloak, LDAP)
Clinical Validation: HIPAA required
Maturity: PRODUCTION
```

#### Authorization
```
Purpose: Enforce access control policies
Inputs: Identity, resource, action
Outputs: Permit/deny decision
Dependencies: Policy engine, RBAC/ABAC
Clinical Validation: HIPAA required
Maturity: PRODUCTION
```

#### Audit
```
Purpose: Create immutable audit trail
Inputs: Events, actions, data access
Outputs: Audit records with timestamps
Dependencies: Event bus, storage
Clinical Validation: HIPAA, IEC 62304 required
Maturity: BETA (incomplete)
```

---

## 3. Clinical Capabilities

These capabilities support direct patient care decisions.

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **ClinicalContext** | Maintain patient/episode context | 4/2 | Clinical | Critical |
| **DecisionSupport** | Provide clinical recommendations | 2/0 | Clinical | Critical |
| **EvidenceRetrieval** | Find relevant clinical evidence | 3/1 | Clinical | High |
| **Diagnostics** | Support differential diagnosis | 1/0 | Clinical | High |
| **TreatmentGuidance** | Recommend evidence-based treatments | 2/0 | Clinical | High |
| **DrugInteraction** | Check medication safety | 3/2 | Clinical | Critical |
| **AlertManagement** | Prioritize and route alerts | 3/1 | Clinical | High |
| **ClinicalDocs** | Manage clinical documentation | 4/3 | Clinical | High |

### Clinical Capability Details

#### ClinicalContext
```
Purpose: Maintain comprehensive patient episode context
Inputs: Patient data, vitals, history, devices
Outputs: Structured clinical context
Dependencies: FHIR integration, device data
Clinical Validation: Required for accurate CDS
Priority: CRITICAL
```

#### DecisionSupport
```
Purpose: Generate actionable recommendations
Inputs: Clinical context, evidence, trust, risk
Outputs: Recommendations with confidence
Dependencies: Reasoning, knowledge, trust, risk
Clinical Validation: FDA guidance required
Priority: CRITICAL
Maturity: EXPERIMENTAL (both dimensions)
```

#### EvidenceRetrieval
```
Purpose: Find clinically relevant evidence
Inputs: Query, clinical context
Outputs: Ranked evidence with relevance
Dependencies: Knowledge graph, RAG, embeddings
Clinical Validation: Required for EBM
Priority: HIGH
```

#### DrugInteraction
```
Purpose: Identify medication safety issues
Inputs: Medication list, patient data
Outputs: Interactions with severity levels
Dependencies: Drug database, patient allergies
Clinical Validation: Required for medication safety
Priority: CRITICAL
```

---

## 4. Biomedical Capabilities

These capabilities manage medical devices and equipment.

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **DeviceRegistry** | Track all medical devices | 5/4 | Biomedical | Critical |
| **CalibrationTracking** | Monitor calibration status | 4/4 | Biomedical | High |
| **MaintenanceScheduling** | Plan preventive maintenance | 4/3 | Biomedical | High |
| **AlarmManagement** | Process device alarms | 3/2 | Biomedical | Critical |
| **AssetTracking** | Locate equipment in hospital | 3/2 | Biomedical | Medium |
| **IncidentManagement** | Document device incidents | 4/3 | Biomedical | High |
| **RiskAssessment** | Evaluate device risks (ISO 14971) | 2/1 | Biomedical | High |
| **ComplianceTracking** | Monitor regulatory compliance | 2/1 | Biomedical | High |

### Biomedical Capability Details

#### DeviceRegistry
```
Purpose: Comprehensive device inventory
Inputs: Device data, specifications, location
Outputs: Device registry with status
Dependencies: DICOM, HL7 integration
Regulations: IEC 60601, FDA, CE marking
Clinical Validation: ISO 13485 required
Maturity: PRODUCTION (Functional), CLINICAL (Clinical)
```

#### AlarmManagement
```
Purpose: Process, prioritize, route device alarms
Inputs: Device alarms, patient context
Outputs: Prioritized alerts with actions
Dependencies: MQTT, device integration
Clinical Validation: Critical for patient safety
ISO 60601-1-8 compliance required
Maturity: BETA
```

#### MaintenanceScheduling
```
Purpose: Optimize preventive maintenance
Inputs: Device schedules, history, MTBF
Outputs: Maintenance calendar with priorities
Dependencies: Device registry, inventory
Clinical Validation: ISO 14971 required
Maturity: BETA
```

---

## 5. Hospital Capabilities

These capabilities optimize hospital operations.

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **CapacityManagement** | Monitor bed/resource availability | 4/3 | Hospital | High |
| **StaffingOptimization** | Optimize personnel allocation | 2/1 | Hospital | Medium |
| **InventoryManagement** | Track supplies and equipment | 3/2 | Hospital | Medium |
| **Scheduling** | Coordinate appointments/procedures | 2/1 | Hospital | Medium |
| **Analytics** | Generate operational insights | 3/1 | Hospital | Medium |
| **Reporting** | Produce regulatory reports | 3/2 | Hospital | High |
| **HospitalTwin** | Digital representation of hospital | 3/1 | Hospital | Medium |

> **NOTE:** HospitalTwin is a **HIGH-LEVEL PRODUCT** built from multiple capabilities, not a standalone capability.
> It synthesizes: CapacityManagement, DeviceRegistry, PatientContext, etc.

### Hospital Capability Details

#### HospitalTwin (Product, not Capability)
```
Status: PRODUCT (not standalone capability)
Purpose: Unified digital representation of hospital

Components:
├── CapacityManagement (beds, rooms)
├── DeviceRegistry (equipment tracking)
├── PatientContext (clinical state)
├── OccupancyAnalytics (predictions)
└── RiskDashboard (hospital-wide risk)

This is what EREN SHOWS to operators.
Not a capability itself.
Maturity: ALPHA (depends on component capabilities)
```

#### CapacityManagement
```
Purpose: Real-time resource visibility
Inputs: Bed status, OR schedules, staff
Outputs: Capacity dashboard, predictions
Dependencies: ADT feeds, scheduling
Clinical Validation: CMS required
Maturity: BETA
```

---

## 6. Integration Capabilities

These capabilities connect EREN to external systems.

| Capability | Description | Maturity F/C | Domain | Priority |
|------------|-------------|-------------|--------|----------|
| **FHIR** | FHIR R4 integration | 3/2 | Clinical | Critical |
| **HL7** | HL7 V2/V3 integration | 3/2 | Clinical | High |
| **DICOM** | Medical imaging integration | 2/1 | Clinical | High |
| **MQTT** | IoT/device messaging | 3/2 | Biomedical | Critical |
| **REST** | REST API for external systems | 4/3 | All | High |
| **Webhooks** | Event-driven integrations | 3/2 | All | Medium |

### Integration Capability Details

#### FHIR
```
Purpose: Interoperate with EHR systems
Inputs: FHIR resources (Patient, Observation, etc.)
Outputs: FHIR-compliant data exchange
Standards: FHIR R4, USCDI
Clinical Validation: Required for clinical integration
Priority: CRITICAL
```

#### MQTT
```
Purpose: Real-time device data streaming
Inputs: Device telemetry, alarms
Outputs: Processed device events
Dependencies: Device drivers
Clinical Validation: IEC 60601 required
Priority: CRITICAL
```

---

## Capability Dependency Graph

```
                    ┌─────────────┐
                    │   DECIDE    │
                    │  (Cognitive)│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │   REASON   │   │   TRUST   │   │ASSESS_RISK│
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                      │
┌───▼───┐         ┌─────▼─────┐         ┌─────▼─────┐
│ KNOW  │         │  REMEMBER │         │ PERCEIVE  │
└───┬───┘         └─────┬─────┘         └─────┬─────┘
    │                   │                      │
    │                   │                      │
    └───────────────────┼──────────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
      ┌───────▼───────┐   ┌──────▼──────┐
      │ CLINICAL_CONTX │   │DEVICE_DATA  │
      └───────┬───────┘   └──────┬──────┘
              │                   │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │  KNOWLEDGE_GRAPH  │
              └─────────┬─────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
      ┌───────▼───────┐   ┌──────▼──────┐
      │   RAG/SEARCH  │   │  EVIDENCE   │
      └───────────────┘   └─────────────┘
```

---

## Capability Maturity Matrix (2D)

| Capability | Functional | Clinical | Status |
|------------|------------|----------|--------|
| Identity | 5 | 5 | ✅ Production |
| Authorization | 5 | 5 | ✅ Production |
| Audit | 4 | 4 | ⚠️ Beta |
| Encryption | 4 | 4 | ⚠️ Beta |
| ClinicalContext | 4 | 2 | ⚠️ Beta |
| DeviceRegistry | 5 | 4 | ⚠️ Beta |
| CapacityManagement | 4 | 3 | ⚠️ Beta |
| FHIR | 3 | 2 | ⚠️ Alpha |
| MQTT | 3 | 2 | ⚠️ Alpha |
| Trust | 2 | 0 | 🔬 Research |
| AssessRisk | 2 | 1 | 🔬 Research |
| DecisionSupport | 2 | 0 | 🔬 Research |
| Reason | 2 | 0 | 🔬 Research |
| HospitalTwin | 3 | 1 | 🔬 Alpha |
| DrugInteraction | 3 | 2 | ⚠️ Alpha |

```
Maturity Scale:
5 - Production: Fully validated, production-ready
4 - Beta: Tested, minor issues
3 - Alpha: Prototype, testing in progress
2 - Design: RFC approved, not implemented
1 - Research: Concept only
0 - Not Started: No work began
```

---

## Priority Ranking

### Critical (Must Have for v1.0)

1. **Identity** - Authentication is foundational
2. **Authorization** - Access control is mandatory
3. **Audit** - HIPAA requires audit trail
4. **ClinicalContext** - Core clinical capability
5. **DecisionSupport** - Primary value proposition
6. **FHIR** - EHR interoperability
7. **MQTT** - Device connectivity
8. **Trust** - Affects all CDS
9. **AssessRisk** - Patient safety

### High (Should Have for v1.0)

10. **DrugInteraction** - Medication safety
11. **AlarmManagement** - Device safety
12. **CalibrationTracking** - Device reliability
13. **DeviceRegistry** - Asset management
14. **CapacityManagement** - Operations
15. **Explain** - Transparency requirement

### Medium (Can Wait for v1.1)

16. **MaintenanceScheduling** - Preventive maintenance
17. **HospitalTwin** - Digital representation
18. **EvidenceRetrieval** - Knowledge access
19. **DICOM** - Imaging integration
20. **Analytics** - Operational insights

### Low (Future Releases)

21. **StaffingOptimization** - Personnel
22. **Scheduling** - Appointments
23. **InventoryManagement** - Supplies
24. **Learn** - Improvement
25. **Reflect** - Metacognition

---

## Domain-Capability Matrix

| Capability | Clinical | Biomedical | Hospital |
|------------|----------|------------|----------|
| Perceive | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Remember | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Know | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Trust | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| AssessRisk | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Reason | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Plan | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Decide | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Explain | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Learn | ⭐⭐ | ⭐ | ⭐ |
| Identity | ⭐ | ⭐ | ⭐ |
| Authorization | ⭐ | ⭐ | ⭐ |
| Audit | ⭐ | ⭐ | ⭐ |
| ClinicalContext | ⭐⭐⭐ | ⭐ | ⭐ |
| DecisionSupport | ⭐⭐⭐ | ⭐ | - |
| DeviceRegistry | - | ⭐⭐⭐ | ⭐⭐ |
| AlarmManagement | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| HospitalTwin | - | ⭐ | ⭐⭐⭐ |
| FHIR | ⭐⭐⭐ | ⭐ | ⭐ |
| MQTT | ⭐ | ⭐⭐⭐ | ⭐ |

```
⭐ = Not applicable  ⭐⭐ = Supporting    ⭐⭐⭐ = Primary
```

---

## Implementation Phases (Aligned with EPIC Roadmap)

### EPIC 0: Foundation (Pre-implementation)
- Philosophy, Domain Model, Architecture, Bounded Contexts

### EPIC 1: Infrastructure Platform
- Identity, Authorization, Audit, Encryption, Secrets, Policy, Compliance

### EPIC 2: Core Business Domain
- DeviceRegistry, ClinicalContext, IncidentManagement, RecommendationEngine, KnowledgeRetrieval

### EPIC 3: Hospital Management Platform
- CapacityManagement, StaffingOptimization, InventoryManagement, Scheduling, HospitalTwin, AssetTracking, BiomedicalEngineering

### EPIC 4: AI Core
- Perceive, Remember, Know, Trust, Reason, Decide, Explain, Reflect

### EPIC 5: Clinical Intelligence
- AssessRisk, Plan, Diagnostics, TreatmentGuidance, RootCauseAnalysis, FailurePrediction, CalibrationAdvisor, ComplianceAdvisor, Troubleshooting, MaintenanceSuggestions

### EPIC 6: Integrations
- FHIR, HL7, DICOM, MQTT, REST, Webhooks

### EPIC 7: User Experience
- Web Dashboard, Chat Interface, Mobile (Android/iOS), Accessibility

### EPIC 8: Production Readiness
- Learn (improved), Analytics, Performance Optimization

### EPIC 9: Machine Learning
- Learn (ML feedback), Model Evaluation, Fine Tuning, Prompt Optimization

---

*EREN Capability Map v1.1*
*Architecture Board - 2026-07-16*
