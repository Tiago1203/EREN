# EREN Bounded Context Map
## Domain Contexts and Their Relationships

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |
| 1.1 | 2026-07-16 | Architecture Board | Hospital + CD contexts added for EPIC 3-5 |

---

## Purpose

This document defines:
1. **Bounded Contexts** within each domain
2. **Relationships** between contexts
3. **Integration patterns** between contexts
4. **Shared kernels** and **anti-corruption layers**

---

## Context Map Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                              CLINICAL DOMAIN                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │    PATIENT      │    │   DIAGNOSIS    │    │   TREATMENT    │         │
│  │    CONTEXT      │    │    CONTEXT     │    │    CONTEXT     │         │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘         │
│           │                      │                       │          │         │
│           └──────────────────────┼───────────────────────┘          │         │
│                                  │                                  │         │
│                    ┌─────────────┴─────────────┐                    │         │
│                    │   CLINICAL DECISION       │                    │         │
│                    │     SUPPORT               │                    │         │
│                    │     CONTEXT               │                    │         │
│                    └─────────────┬─────────────┘                    │         │
│                                  │                                  │         │
└──────────────────────────────────┼──────────────────────────────────┼──────────┘
                                   │                                  │
┌──────────────────────────────────┼──────────────────────────────────┼──────────┐
│                          BIOMEDICAL DOMAIN                         │          │
├──────────────────────────────────┼──────────────────────────────────┼──────────┤
│                                  │                                  │          │
│                    ┌─────────────┴─────────────┐                    │          │
│                    │       DEVICE             │                    │          │
│                    │       CONTEXT            │                    │          │
│                    └─────────────┬─────────────┘                    │          │
│                                  │                                  │          │
│           ┌──────────────────────┼──────────────────────┐        │          │
│           │                      │                      │        │          │
│  ┌────────▼────────┐    ┌────────▼────────┐   ┌────────▼────────┐│          │
│  │   ASSET         │    │   ALARM          │   │   MAINTENANCE   ││          │
│  │   CONTEXT       │    │   CONTEXT        │   │   CONTEXT      ││          │
│  └─────────────────┘    └─────────────────┘   └─────────────────┘│          │
└──────────────────────────────────────────────────────────────────┼──────────┘
                                   │                                  │
┌──────────────────────────────────┼──────────────────────────────────┼──────────┐
│                          HOSPITAL DOMAIN                         │          │
├──────────────────────────────────┼──────────────────────────────────┼──────────┤
│                                  │                                  │          │
│  ┌─────────────────┐    ┌────────┴────────┐   ┌─────────────────┐│          │
│  │   HOSPITAL      │    │  ORGANIZATION   │   │  DEPARTMENT     ││          │
│  │   CONTEXT       │    │   CONTEXT      │   │   CONTEXT      ││          │
│  └────────┬────────┘    └────────┬────────┘   └────────┬────────┘│          │
│           │                      │                       │          │          │
│  ┌────────┴────────┐    ┌────────┴────────┐   ┌────────┴────────┐│          │
│  │   CAMPUS        │    │   BUILDING      │   │   BIOMEDICAL   ││          │
│  │   CONTEXT       │    │   CONTEXT      │   │   ENGINEERING  ││          │
│  └────────┬────────┘    └────────┬────────┘   │   CONTEXT      ││          │
│           │                      │              └────────┬────────┘│          │
│  ┌────────┴────────┐    ┌────────┴────────┐   ┌────────┴────────┐│          │
│  │   FLOOR         │    │    ROOM         │   │  ASSET          ││          │
│  │   CONTEXT       │    │   CONTEXT      │   │  MANAGEMENT     ││          │
│  └────────┬────────┘    └────────┬────────┘   │   CONTEXT      ││          │
│           │                      │              └────────┬────────┘│          │
│  ┌────────┴────────┐    ┌────────┴────────┐   ┌────────┴────────┐│          │
│  │   BED           │    │   INVENTORY    │   │  PURCHASE      ││          │
│  │   CONTEXT       │    │   CONTEXT      │   │  ORDER         ││          │
│  └─────────────────┘    └─────────────────┘   │  CONTEXT       ││          │
│                                               └─────────────────┘│          │
└───────────────────────────────────────────────────────────────────┴──────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                    CLINICAL INTELLIGENCE DOMAIN                          │          │
├──────────────────────────────────┼──────────────────────────────────────────┤
│                                  │                                           │
│  ┌───────────────┐    ┌────────┴────────┐   ┌─────────────────┐           │
│  │  ROOT CAUSE   │    │  DIFFERENTIAL   │   │   FAILURE       │           │
│  │  ANALYSIS     │    │  DIAGNOSIS    │   │   PREDICTION    │           │
│  │  CONTEXT      │    │   CONTEXT     │   │   CONTEXT       │           │
│  └───────┬───────┘    └────────┬────────┘   └────────┬────────┘           │
│          │                     │                       │          │           │
│  ┌───────┴───────┐    ┌────────┴────────┐   ┌────────┴────────┐           │
│  │  TROUBLESHOOT │    │  RISK          │   │  CALIBRATION   │           │
│  │  CONTEXT      │    │  ASSESSMENT   │   │  ADVISOR      │           │
│  └───────┬───────┘    │   CONTEXT     │   │  CONTEXT       │           │
│          │            └────────┬────────┘   └─────────────────┘           │
│  ┌───────┴───────┐            │                                               │
│  │  MAINTENANCE  │    ┌──────┴──────┐                                     │
│  │  SUGGESTIONS  │    │  COMPLIANCE │                                     │
│  │  CONTEXT      │    │  ADVISOR    │                                     │
│  └───────────────┘    │  CONTEXT    │                                     │
│                       └─────────────┘                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

**Total: 20 Bounded Contexts**

---

## Clinical Domain Contexts

### Context: Patient Context

```
┌─────────────────────────────────────────────────────────────┐
│                    PATIENT CONTEXT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                           │
│  - Patient identity and demographics                        │
│  - Patient history and records                             │
│  - Patient consent and privacy                             │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Patient (aggregate root)                                 │
│  - Demographics                                            │
│  - Consent                                                 │
│  - Patient Identifier (MRN, SSN, etc.)                    │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Patient data                                      │
│  - Knows: Staff identities (for assignments)              │
│  - Does NOT know: Clinical decisions                        │
│                                                              │
│  REPOSITORY: PatientRepository                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Diagnosis Context

```
┌─────────────────────────────────────────────────────────────┐
│                    DIAGNOSIS CONTEXT                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Clinical diagnoses (ICD-10, SNOMED)                     │
│  - Differential diagnosis tracking                          │
│  - Diagnosis relationships                                   │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Diagnosis (aggregate)                                    │
│  - ICDCode                                                 │
│  - SNOMEDConcept                                           │
│  - DifferentialDiagnosis                                   │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Diagnosis data                                     │
│  - Knows: Patient context (patient_id)                      │
│  - Knows: Ordering clinician (staff_id)                     │
│  - Does NOT know: Treatment details                         │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (patient_id)                             │
│  → Treatment Context (diagnosis_id)                          │
│  → Decision Support (diagnoses for CDS)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Treatment Context

```
┌─────────────────────────────────────────────────────────────┐
│                    TREATMENT CONTEXT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Treatment plans and orders                               │
│  - Medication administration                                │
│  - Procedure tracking                                       │
│                                                              │
│  CORE ENTITIES:                                            │
│  - TreatmentPlan (aggregate root)                          │
│  - Order                                                   │
│  - Medication (with dosing)                                │
│  - Procedure                                              │
│  - AdministrationRecord                                     │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Treatment data                                     │
│  - Knows: Patient context (patient_id)                       │
│  - Knows: Diagnosis context (diagnosis_id)                   │
│  - Knows: Medication context (medication_id)                 │
│  - Does NOT know: Device details                            │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (patient_id)                             │
│  ← Diagnosis Context (diagnosis_id)                         │
│  → Order Context (for fulfillment)                         │
│  → Medication Context (for dispensing)                      │
│  → Decision Support (treatments for CDS)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Clinical Decision Support Context

```
┌─────────────────────────────────────────────────────────────┐
│               CLINICAL DECISION SUPPORT CONTEXT              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Generate clinical recommendations                        │
│  - Evaluate evidence                                        │
│  - Assess trust and risk                                    │
│  - Explain reasoning                                        │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Recommendation (aggregate)                              │
│  - Evidence                                                │
│  - ReasoningChain                                          │
│  - Explanation                                             │
│  - TrustScore                                              │
│  - RiskAssessment                                           │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Recommendations                                    │
│  - Consumes: Everything else                              │
│  - Produces: Insights for other contexts                    │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (patient context)                        │
│  ← Diagnosis Context (diagnoses)                          │
│  ← Treatment Context (current treatments)                  │
│  ← Device Context (device data)                            │
│  ← Knowledge Graph (evidence)                              │
│  ← Trust Service (trust scores)                            │
│  → All Contexts (recommendations)                           │
│                                                              │
│  NOTE: This is a SYNTHESIZING context                      │
│        It combines data from many contexts                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Biomedical Domain Contexts

### Context: Device Context

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVICE CONTEXT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Medical device registry                                  │
│  - Device specifications                                     │
│  - Device status and location                               │
│  - Device relationships                                      │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Device (aggregate root)                                  │
│  - DeviceSpecification                                       │
│  - DeviceStatus                                             │
│  - DeviceLocation                                          │
│  - DeviceClassification (IEC 60601)                         │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Device data                                       │
│  - Knows: Patient context (device assignments)             │
│  - Does NOT know: Clinical decisions                        │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (patient_id, for assignments)           │
│  ← Capacity Context (bed_id, room_id)                      │
│  → Alarm Context (device alarms)                           │
│  → Maintenance Context (device maintenance)                │
│  → Decision Support (device trust, calibration status)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Alarm Context

```
┌─────────────────────────────────────────────────────────────┐
│                    ALARM CONTEXT                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Receive device alarms                                     │
│  - Prioritize and route alarms                             │
│  - Track alarm acknowledgment                                │
│  - Alarm analytics                                          │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Alarm (aggregate)                                        │
│  - AlarmPriority                                            │
│  - AlarmAcknowledgment                                      │
│  - AlarmRouting                                            │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Alarm lifecycle                                   │
│  - Knows: Device (source device)                           │
│  - Knows: Patient (affected patient)                        │
│  - Knows: Staff (who should receive)                       │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (alarm source)                           │
│  ← Patient Context (affected patient)                     │
│  ← Staffing Context (on-call staff)                        │
│  → Clinical Decision Support (alarms as evidence)           │
│  → Notification Context (alarm notifications)              │
│                                                              │
│  SAFETY-CRITICAL:                                          │
│  ⚠️ CRITICAL alarms cannot be lost                         │
│  ⚠️ Requires AT LEAST ONCE delivery                        │
│  ⚠️ Requires acknowledgment tracking                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Maintenance Context

```
┌─────────────────────────────────────────────────────────────┐
│                    MAINTENANCE CONTEXT                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Preventive maintenance scheduling                        │
│  - Corrective maintenance tracking                          │
│  - Calibration management                                    │
│  - Work order management                                    │
│                                                              │
│  CORE ENTITIES:                                            │
│  - MaintenanceRecord (aggregate)                            │
│  - WorkOrder                                               │
│  - CalibrationRecord                                        │
│  - MaintenanceSchedule                                      │
│  - MaintenanceTechnician                                    │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Maintenance lifecycle                              │
│  - Knows: Device (maintenance target)                       │
│  - Knows: Staff (technicians)                               │
│  - Does NOT know: Patient clinical data                     │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (device to maintain)                     │
│  ← Staffing Context (technicians)                          │
│  ← Capacity Context (room availability for maintenance)     │
│  → Device Context (updated device status)                  │
│  → Decision Support (maintenance recommendations)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Hospital Domain Contexts

### Context: Capacity Context

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPACITY CONTEXT                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Bed management and tracking                              │
│  - Room and unit occupancy                                  │
│  - Capacity planning and prediction                          │
│  - Resource allocation                                      │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Bed (aggregate root)                                    │
│  - Room                                                    │
│  - Unit                                                    │
│  - Building                                                │
│  - OccupancyRecord                                         │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Physical resource tracking                        │
│  - Knows: Patient (bed assignments)                        │
│  - Knows: Device (location)                                │
│  - Does NOT know: Clinical details                         │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (admission/discharge)                  │
│  ← Device Context (device locations)                        │
│  ← Staffing Context (staff assignments)                    │
│  ← Scheduling Context (OR schedules)                      │
│  → Patient Context (bed assignment)                       │
│  → Clinical Decision Support (capacity as context)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Staffing Context

```
┌─────────────────────────────────────────────────────────────┐
│                    STAFFING CONTEXT                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Staff management                                          │
│  - Shift scheduling                                          │
│  - Role and qualification tracking                          │
│  - Staff availability                                        │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Staff (aggregate root)                                   │
│  - Role                                                    │
│  - Qualification                                           │
│  - Shift                                                   │
│  - Schedule                                                │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Staff employment data                              │
│  - Knows: Staff identity (for assignments)                  │
│  - Does NOT know: Clinical decisions                        │
│                                                              │
│  INTEGRATION:                                              │
│  ← Capacity Context (staff on unit)                       │
│  ← Scheduling Context (scheduled shifts)                   │
│  → Alarm Context (who receives alarms)                    │
│  → Treatment Context (who ordered treatment)               │
│  → Maintenance Context (who performs maintenance)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Scheduling Context

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEDULING CONTEXT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Appointment scheduling                                    │
│  - OR scheduling                                            │
│  - Procedure scheduling                                      │
│  - Resource booking                                          │
│                                                              │
│  CORE ENTITIES:                                            │
│  - Appointment (aggregate)                                   │
│  - ProcedureBooking                                         │
│  - OperatingRoomSchedule                                     │
│  - ProcedureRoom                                            │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Scheduling data                                    │
│  - Knows: Patient (appointment subject)                    │
│  - Knows: Staff (performing clinician)                     │
│  - Knows: Capacity (rooms, equipment)                       │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (appointment patient)                   │
│  ← Staffing Context (staff availability)                   │
│  ← Capacity Context (room/equipment availability)           │
│  → Treatment Context (scheduled procedures)                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Context Relationships

### Relationship Types

```
┌─────────────────────────────────────────────────────────────┐
│                  RELATIONSHIP TYPES                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CUSTOMER-SUPPLIER (One context serves another)          │
│     ┌───────────┐    Customer    ┌───────────┐             │
│     │  Source   │ ─────────────▶│   Target  │             │
│     │  Context  │               │  Context  │             │
│     └───────────┘               └───────────┘             │
│                                                              │
│  2. CONFORMIST (Target uses Source's model)                 │
│     ┌───────────┐               ┌───────────┐             │
│     │  Source   │ ─────────────▶│   Target  │             │
│     │  Context  │ (uses model)   │  Context  │             │
│     └───────────┘               └───────────┘             │
│                                                              │
│  3. ANTICORRUPTION LAYER (Target protects its model)       │
│     ┌───────────┐   ACL    ┌───────────┐                   │
│     │  Source   │ ───────▶│   Target  │                   │
│     │  Context  │         │  Context  │                   │
│     └───────────┘         └───────────┘                   │
│                               │                             │
│                          Adapter                           │
│                        (translation)                        │
│                                                              │
│  4. PUBLISHED LANGUAGE (Shared vocabulary)                   │
│     ┌───────────┐    Shared    ┌───────────┐               │
│     │ Context A │◀────────────▶│ Context B │               │
│     │           │   Language    │           │               │
│     └───────────┘               └───────────┘               │
│                                                              │
│  5. SHARED KERNEL (Shared subset of model)                  │
│     ┌───────────────────────────────┐                       │
│     │         SHARED KERNEL         │                       │
│     │  (Patient ID, Staff ID, etc) │                       │
│     └───────────────────────────────┘                       │
│               │                 │                          │
│     ┌─────────▼─────┐   ┌───────▼────────┐               │
│     │  Context A    │   │    Context B    │               │
│     └───────────────┘   └────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Clinical Domain Relationships

```
┌─────────────────────────────────────────────────────────────┐
│               CLINICAL CONTEXT MAP                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Patient ─────────────┬─────────────────────────────────────│
│  Context              │                                     │
│         │            │                                     │
│         │ Customer-Supplier (Patient provides ID)          │
│         │            │                                     │
│         ▼            ▼                                     │
│  Diagnosis ◀──────────┘                                     │
│  Context        │                                           │
│         │      │                                           │
│         │ Customer-Supplier (Patient is subject)           │
│         │      │                                           │
│         ▼      ▼                                           │
│  Treatment ◀────┘                                           │
│  Context        │                                           │
│         │      │                                           │
│         │ Customer-Supplier (Diagnosis leads to treatment)│
│         │      │                                           │
│         ▼      ▼                                           │
│  Clinical ──────┘                                           │
│  Decision                                                   │
│  Support                                                    │
│                                                              │
│  [SHARED KERNEL]                                           │
│  - Patient ID                                               │
│  - Staff ID                                                │
│  - Timestamp                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Cross-Domain Relationships

```
┌─────────────────────────────────────────────────────────────┐
│              CROSS-DOMAIN RELATIONSHIPS                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CLINICAL ◀───────────────────────────────▶ BIOMEDICAL     │
│       │                                              │       │
│       │ Patient uses Device                          │       │
│       │ (monitor attached to patient)               │       │
│       │                                              │       │
│       │ Device affects Patient                      │       │
│       │ (alarm for patient)                        │       │
│       │                                              │       │
│       │ Anticipates: Alarm Context                  │       │
│       │ Conformist: Patient ID is shared            │       │
│                                                              │
│  CLINICAL ◀───────────────────────────────▶ HOSPITAL        │
│       │                                              │       │
│       │ Patient assigned to Bed                     │       │
│       │ (capacity allocation)                      │       │
│       │                                              │       │
│       │ Bed affects Patient                        │       │
│       │ (room location, unit)                     │       │
│       │                                              │       │
│       │ Conformist: Patient ID, Bed ID shared      │       │
│                                                              │
│  BIOMEDICAL ◀─────────────────────────────▶ HOSPITAL       │
│       │                                              │       │
│       │ Device located in Room                     │       │
│       │ (physical location)                        │       │
│       │                                              │       │
│       │ Maintenance scheduled around                │       │
│       │ patient occupancy                         │       │
│       │                                              │       │
│       │ Anticorruption Layer:                      │       │
│       │ Device doesn't need patient data           │       │
│       │ to track location                          │       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Patterns by Context

### Patient Context → Diagnosis Context

```
Pattern: Customer-Supplier
Direction: Patient Context is upstream supplier

┌─────────────────┐                    ┌─────────────────┐
│  PATIENT        │                    │  DIAGNOSIS       │
│  CONTEXT        │                    │  CONTEXT         │
│                 │                    │                 │
│ Patient Entity  │──patient_id──────▶│ Diagnosis       │
│                 │   (reference)     │ Entity          │
│                 │                    │                 │
│                 │◀───query──────────│                 │
│                 │   (get patient)   │                 │
└─────────────────┘                    └─────────────────┘

Integration via: Domain Events
├── PatientCreated → Diagnosis subscribes
├── PatientUpdated → Diagnosis updates references
└── PatientDeceased → Diagnosis marks records
```

### Treatment Context → Decision Support Context

```
Pattern: Customer-Supplier + Anticorruption Layer
Direction: Treatment Context is upstream, CDS consumes

┌─────────────────┐                    ┌─────────────────┐
│  TREATMENT      │                    │  DECISION        │
│  CONTEXT        │                    │  SUPPORT         │
│                 │                    │  CONTEXT         │
│ TreatmentPlan  │───treatments─────▶│ Recommendation  │
│ Entity         │   (view/read)      │ Entity          │
│                 │                    │                 │
│                 │◀──recommendation─│                 │
│                 │   (request CDS) │                 │
└─────────────────┘                    └─────────────────┘

CDS translates treatment model:
├── Extracts: medication, dosage, frequency
├── Ignores: internal IDs, implementation details
├── Produces: evidence-based recommendations
```

### Device Context ↔ Alarm Context

```
Pattern: Partnership (bidirectional)
Both contexts need each other equally

┌─────────────────┐                    ┌─────────────────┐
│    DEVICE       │                    │     ALARM        │
│   CONTEXT       │                    │    CONTEXT       │
│                 │                    │                 │
│ Device Entity  │◀───────────────│ Device Entity   │
│                 │   bidirectional  │                 │
│                 │◀───────────────│ Alarm Entity    │
│                 │   (source)      │                 │
└─────────────────┘                    └─────────────────┘

Shared understanding:
├── Device generates Alarm
├── Alarm references Device
├── No translation layer needed
└── Same team/domain ownership
```

---

## Anti-Corruption Layers

### When ACL Is Needed

```
ACL is needed when:
✅ External system has incompatible model
✅ Context should not be coupled to external changes
✅ Legacy system needs integration

ACL is NOT needed when:
❌ Both contexts share same model (Conformist)
❌ Partnership relationship (bidirectional)
❌ Same team/domain ownership
```

### Example: HL7 → Patient Context ACL

```
┌─────────────────────────────────────────────────────────────┐
│  WITHOUT ACL (BAD)                                          │
│                                                              │
│  Patient Context imports HL7 models                         │
│  HL7 v2 changes → Patient Context breaks                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  WITH ACL (GOOD)                                           │
│                                                              │
│  HL7 v2 ────▶│ ACL │───▶ Patient Context                 │
│               │     │                                     │
│               │     │ Transforms:                          │
│               │     │ - HL7 PID → Patient                 │
│               │     │ - HL7 PV1 → Location               │
│               │     │ - Filters: only what we need        │
│               │     │                                     │
│               │     │ Patient Context never sees HL7       │
└─────────────────────────────────────────────────────────────┘
```

---

## Shared Kernel

### What Is Shared

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED KERNEL                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ENTITIES (Immutable identifiers):                           │
│  ├── PatientId { value: str }                              │
│  ├── StaffId { value: str }                               │
│  ├── DeviceId { value: str }                               │
│  ├── BedId { value: str }                                  │
│  └── TenantId { value: str }                               │
│                                                              │
│  VALUE OBJECTS:                                            │
│  ├── Timestamp { value: datetime }                         │
│  ├── Location { floor, room, bed }                        │
│  └── Priority { level: int, name: str }                   │
│                                                              │
│  EVENTS (Universal):                                       │
│  ├── EntityCreated { id, type, timestamp }               │
│  ├── EntityUpdated { id, type, changes, timestamp }       │
│  └── EntityDeleted { id, type, timestamp }                 │
│                                                              │
│  RULES:                                                    │
│  ├── IDs are immutable                                     │
│  ├── Timestamps in UTC                                     │
│  └── Multi-tenant by default                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What Is NOT Shared

```
NOT IN SHARED KERNEL (Each context owns its model):
├── Patient demographics
├── Staff employment details
├── Device specifications
├── Bed status
├── Treatment plans
├── Diagnosis codes
└── Alarm details
```

---

## Context Ownership Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CONTEXT OWNERSHIP                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CONTEXT                          │ OWNER TEAM         │ LOCATION        │
│ ────────────────────────────────┼────────────────────┼────────────────-│
│  CLINICAL DOMAIN                                                          │
│  ──────────────────────────────────────────────────────────────────────│
│  Patient                        │ Clinical            │ /clinical/patient│
│  Diagnosis                      │ Clinical            │ /clinical/diag   │
│  Treatment                      │ Clinical            │ /clinical/tx     │
│  Clinical Decision Support      │ Clinical + AI       │ /clinical/cds   │
│                                                                         │
│  BIOMEDICAL DOMAIN                                                        │
│  ──────────────────────────────────────────────────────────────────────│
│  Device                        │ Biomedical          │ /biomedical/device│
│  Alarm                         │ Biomedical          │ /biomedical/alarm │
│  Maintenance                   │ Biomedical          │ /biomedical/maint│
│                                                                         │
│  HOSPITAL DOMAIN                                                           │
│  ──────────────────────────────────────────────────────────────────────│
│  Hospital                      │ Hospital Ops        │ /hospital         │
│  Organization                  │ Hospital Ops        │ /hospital/org    │
│  Department                    │ Hospital Ops        │ /hospital/dept   │
│  Campus                        │ Hospital Ops        │ /hospital/campus │
│  Building                      │ Hospital Ops        │ /hospital/building│
│  Floor                         │ Hospital Ops        │ /hospital/floor  │
│  Room                          │ Hospital Ops        │ /hospital/room   │
│  Bed                           │ Hospital Ops        │ /hospital/bed    │
│  BiomedicalEngineering         │ Biomedical          │ /biomedical/eng  │
│  AssetManagement               │ Biomedical          │ /biomedical/asset│
│  Inventory                     │ Hospital Ops        │ /hospital/inventory│
│  PurchaseOrder                 │ Hospital Ops        │ /hospital/purchase│
│                                                                         │
│  CLINICAL INTELLIGENCE DOMAIN                                             │
│  ──────────────────────────────────────────────────────────────────────│
│  RootCauseAnalysis            │ Clinical Intelligence│ /ai/rootcause   │
│  DifferentialDiagnosis         │ Clinical Intelligence│ /ai/differential │
│  Troubleshooting               │ Biomedical          │ /ai/troubleshoot │
│  FailurePrediction             │ Biomedical          │ /ai/failure      │
│  RiskAssessment                │ Clinical            │ /ai/risk         │
│  CalibrationAdvisor            │ Biomedical          │ /ai/calibration  │
│  ComplianceAdvisor             │ Clinical            │ /ai/compliance   │
│  MaintenanceSuggestions        │ Biomedical          │ /ai/maintenance  │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Clinical Intelligence Domain Contexts

### Context: Root Cause Analysis

```
┌─────────────────────────────────────────────────────────────┐
│               ROOT CAUSE ANALYSIS CONTEXT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Identify root causes of device failures                 │
│  - Analyze incident patterns                                │
│  - Generate causal chains                                   │
│                                                              │
│  CORE ENTITIES:                                            │
│  - RootCauseAnalysis (aggregate root)                     │
│  - CausalChain                                            │
│  - FailurePattern                                         │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Root cause findings                              │
│  - Knows: Incident, Device, Maintenance context            │
│  - Does NOT know: Clinical patient data                    │
│                                                              │
│  INTEGRATION:                                              │
│  ← Incident Context (incident data)                        │
│  ← Device Context (device history)                         │
│  ← Maintenance Context (maintenance records)               │
│  → Troubleshooting Context (root causes)                   │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Differential Diagnosis

```
┌─────────────────────────────────────────────────────────────┐
│               DIFFERENTIAL DIAGNOSIS CONTEXT                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Generate differential diagnoses from symptoms            │
│  - Rank diagnoses by likelihood                             │
│  - Identify missing information                             │
│                                                              │
│  CORE ENTITIES:                                            │
│  - DifferentialDiagnosis (aggregate root)                  │
│  - DiagnosisCandidate                                      │
│  - EvidenceWeight                                          │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Diagnostic hypotheses                             │
│  - Knows: Patient symptoms, vital signs                    │
│  - Does NOT know: Clinical treatment details                │
│                                                              │
│  INTEGRATION:                                              │
│  ← Patient Context (symptoms, history)                     │
│  ← Diagnosis Context (ICD codes)                           │
│  ← Knowledge Context (medical guidelines)                   │
│  → Treatment Context (suggested treatments)                 │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Failure Prediction

```
┌─────────────────────────────────────────────────────────────┐
│               FAILURE PREDICTION CONTEXT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Predict device failures before they occur               │
│  - Assess failure risk                                      │
│  - Recommend preventive actions                             │
│                                                              │
│  CORE ENTITIES:                                            │
│  - FailurePrediction (aggregate root)                       │
│  - RiskScore                                              │
│  - PredictionModel                                         │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Failure predictions and risk scores               │
│  - Knows: Device telemetry, maintenance history            │
│  - Does NOT know: Patient clinical data                    │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (device data, telemetry)                 │
│  ← Maintenance Context (maintenance history, MTBF)         │
│  → Device Context (maintenance recommendations)             │
│  → MaintenanceSuggestions Context (preventive work orders) │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Risk Assessment

```
┌─────────────────────────────────────────────────────────────┐
│               RISK ASSESSMENT CONTEXT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Evaluate clinical and operational risks                  │
│  - Quantify risk levels                                    │
│  - Recommend mitigation strategies                          │
│                                                              │
│  CORE ENTITIES:                                            │
│  - RiskAssessment (aggregate root)                         │
│  - RiskScore                                              │
│  - MitigationStrategy                                      │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Risk evaluations and scores                       │
│  - Knows: Clinical, device, and operational context       │
│  - Does NOT make clinical decisions (only advises)         │
│                                                              │
│  INTEGRATION:                                              │
│  ← All domains (risk data)                                │
│  → All domains (risk scores)                               │
│  → Clinical Decision Support (risk as context)            │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Calibration Advisor

```
┌─────────────────────────────────────────────────────────────┐
│               CALIBRATION ADVISOR CONTEXT                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Recommend calibration schedules                          │
│  - Assess calibration urgency                               │
│  - Verify NIST traceability                                 │
│                                                              │
│  CORE ENTITIES:                                            │
│  - CalibrationRecommendation (aggregate root)               │
│  - CalibrationSchedule                                     │
│  - TraceabilityRecord                                     │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Calibration recommendations                       │
│  - Knows: Device calibration history, standards             │
│  - Does NOT know: Patient clinical data                    │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (device calibration requirements)         │
│  ← Maintenance Context (calibration records)               │
│  → Maintenance Suggestions (calibration work orders)        │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Compliance Advisor

```
┌─────────────────────────────────────────────────────────────┐
│               COMPLIANCE ADVISOR CONTEXT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Monitor regulatory compliance                            │
│  - Detect compliance violations                             │
│  - Recommend corrective actions                             │
│                                                              │
│  CORE ENTITIES:                                            │
│  - ComplianceCheck (aggregate root)                         │
│  - ViolationRecord                                         │
│  - RegulatoryStandard                                       │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Compliance evaluations                            │
│  - Knows: All domain compliance-relevant data              │
│  - Does NOT enforce (only advises)                         │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (IEC 60601 compliance)                   │
│  ← Maintenance Context (maintenance records)                │
│  ← All domains (regulatory requirements)                   │
│  → All domains (compliance recommendations)                │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Troubleshooting

```
┌─────────────────────────────────────────────────────────────┐
│               TROUBLESHOOTING CONTEXT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Guide troubleshooting steps for device issues            │
│  - Generate diagnostic workflows                           │
│  - Recommend resolution actions                             │
│                                                              │
│  CORE ENTITIES:                                            │
│  - TroubleshootingSession (aggregate root)                   │
│  - DiagnosticStep                                          │
│  - ResolutionAction                                        │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Troubleshooting workflows                         │
│  - Knows: Device state, alarm history, knowledge base      │
│  - Does NOT know: Patient clinical data                     │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (device state)                           │
│  ← Alarm Context (alarm history)                           │
│  ← Knowledge Context (troubleshooting guides)              │
│  ← RootCauseAnalysis (causal chains)                       │
│  → Maintenance Context (work orders)                       │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Context: Maintenance Suggestions

```
┌─────────────────────────────────────────────────────────────┐
│               MAINTENANCE SUGGESTIONS CONTEXT                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESPONSIBILITY:                                             │
│  - Generate intelligent maintenance recommendations          │
│  - Prioritize by risk, cost, and impact                   │
│  - Optimize maintenance scheduling                          │
│                                                              │
│  CORE ENTITIES:                                            │
│  - MaintenanceSuggestion (aggregate root)                   │
│  - PriorityScore                                           │
│  - MaintenancePlan                                         │
│                                                              │
│  BOUNDARY:                                                 │
│  - Owns: Maintenance recommendations                       │
│  - Knows: Device, FailurePrediction, CalibrationAdvisor   │
│  - Does NOT know: Patient clinical details                  │
│                                                              │
│  INTEGRATION:                                              │
│  ← Device Context (device state)                           │
│  ← FailurePrediction (failure risks)                       │
│  ← CalibrationAdvisor (calibration needs)                   │
│  ← Capacity Context (maintenance windows)                   │
│  → Maintenance Context (work order suggestions)            │
│                                                              │
│  EPIC: EPIC 5 - Clinical Intelligence                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*EREN Bounded Context Map v1.1*
*Architecture Board - 2026-07-16*
