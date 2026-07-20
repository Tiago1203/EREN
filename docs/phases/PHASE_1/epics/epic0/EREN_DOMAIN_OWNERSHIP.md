# EREN Domain Ownership
## Definitive Guide: Which Domain Owns Each Entity

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial - Epic 0.1 |

---

## Purpose

Every entity in EREN must have a single owner domain. This prevents:
- Domain conflicts
- Unclear responsibilities
- Circular dependencies
- Implementation ambiguity

---

## Domain Ownership Matrix

### Primary Owners

| Entity | Owner Domain | Used By | Notes |
|--------|--------------|---------|-------|
| **Patient** | Clinical | Hospital, Biomedical | Clinical owns patient identity |
| **Diagnosis** | Clinical | Hospital | Diagnostic data owned by Clinical |
| **Treatment** | Clinical | Hospital | Treatment plans owned by Clinical |
| **Medication** | Clinical | Hospital, Biomedical | Clinical owns therapeutic decisions |
| **Vital Signs** | Clinical | Biomedical | Raw data from devices, owned by Clinical |
| **Clinical Alert** | Clinical | Hospital, Biomedical | Clinical alert management |
| **Clinical Decision** | Clinical | All | CDS decisions owned by Clinical |
| **Evidence** | Clinical | All | Clinical evidence hierarchy |
| **Guideline** | Clinical | All | Clinical guidelines |

### Biomedical Domain

| Entity | Owner Domain | Used By | Notes |
|--------|--------------|---------|-------|
| **Device** | Biomedical | Hospital, Clinical | Device registry owned by Biomedical |
| **Calibration Record** | Biomedical | Hospital | Calibration tracking |
| **Maintenance Record** | Biomedical | Hospital | Maintenance history |
| **Device Alarm** | Biomedical | Clinical, Hospital | Raw alarm from device |
| **Device Status** | Biomedical | Hospital | Operational status |
| **Asset** | Biomedical | Hospital | Physical asset tracking |
| **Work Order** | Biomedical | Hospital | Maintenance work orders |
| **Risk Assessment (Device)** | Biomedical | Clinical, Hospital | ISO 14971 risk |
| **MTBF Data** | Biomedical | Hospital | Reliability metrics |

### Hospital Domain

| Entity | Owner Domain | Used By | Notes |
|--------|--------------|---------|-------|
| **Bed** | Hospital | Clinical | Bed management |
| **Room** | Hospital | Clinical | Physical location |
| **Unit/Floor** | Hospital | Clinical | Organizational unit |
| **Building** | Hospital | - | Physical structure |
| **Staff** | Hospital | Clinical, Biomedical | Personnel management |
| **Shift** | Hospital | Clinical | Staff scheduling |
| **Occupancy** | Hospital | Clinical | Capacity tracking |
| **Inventory (Consumables)** | Hospital | Biomedical | Supply chain |
| **Appointment** | Hospital | Clinical | Scheduling |
| **OR Schedule** | Hospital | Clinical | Operating room booking |
| **Report (Operational)** | Hospital | All | Operational reports |

### Operations Domain (Implied)

| Entity | Owner Domain | Used By | Notes |
|--------|--------------|---------|-------|
| **Bill** | Operations | Hospital | Billing records |
| **Supply Order** | Operations | Hospital | Procurement |
| **Compliance Record** | Operations | All | Regulatory compliance |
| **Audit (Financial)** | Operations | Hospital | Financial audit |

---

## Cross-Domain Relationships

### Clinical ↔ Biomedical

```
Clinical reads:
├── Vital Signs (from Device readings)
├── Device Status (is equipment reliable?)
└── Alarm History (for patient context)

Biomedical reads:
├── Patient Criticality (affects maintenance priority)
└── Treatment Plan (affects device selection)
```

### Clinical ↔ Hospital

```
Clinical reads:
├── Bed Availability
├── Staff Assignment
└── OR Schedule

Hospital reads:
├── Patient Census
├── Diagnosis Mix
└── Length of Stay
```

### Biomedical ↔ Hospital

```
Biomedical reads:
├── Asset Location (where is equipment?)
├── Staff Schedules (who performs maintenance?)
└── Occupancy (affects maintenance windows)

Hospital reads:
├── Device Availability
├── Maintenance Schedule
└── Risk Status
```

---

## Ownership Rules

### Rule 1: Single Owner

Every entity has ONE owner domain. No entity is owned by multiple domains.

```
❌ WRONG:
Patient — owned by Clinical AND Hospital

✅ CORRECT:
Patient — owned by Clinical
Patient Location — owned by Hospital
```

### Rule 2: Owner Has Final Say

The owner domain defines:
- Entity schema
- Validation rules
- Business logic
- Lifecycle management

### Rule 3: Consumer Domains Read Only

Consumer domains:
- Read entity data
- Subscribe to entity events
- Query entity state
- Cannot modify entity data

### Rule 4: Cross-Domain Events Flow Upward

```
Device Alarm (Biomedical)
    ↓
Clinical Alert (Clinical)
    ↓
Bed Notification (Hospital)
```

---

## Entity Lifecycle Example

### Device Entity

```
Biomedical Domain (Owner)
├── Creates Device record
├── Updates Device status
├── Records Calibration
├── Schedules Maintenance
├── Tracks MTBF
└── Manages Device lifecycle

Clinical Domain (Consumer)
├── Reads Device status (is monitor reliable?)
├── Receives Device alarms
├── Trusts Device readings based on calibration
└── Cannot modify Device records

Hospital Domain (Consumer)
├── Tracks Device location
├── Assigns Device to room
├── Reports Device inventory
└── Cannot modify Device technical data
```

---

## Service Ownership Example

### Alert Service

**Question:** Which domain owns the alert service?

**Answer:** It depends on the alert TYPE.

```
Clinical Alert Service — OWNED by Clinical Domain
├── Triggers: Patient deterioration
├── Processing: Clinical algorithms
├── Routing: To clinical staff
└── Recording: Clinical audit trail

Biomedical Alert Service — OWNED by Biomedical Domain
├── Triggers: Device malfunction
├── Processing: Device diagnostics
├── Routing: To biomedical staff
└── Recording: Maintenance records
```

**Key Insight:** Alert services are domain-specific, not shared.

---

## Implementation Notes

### Database Schema

Each domain has its own schema:

```sql
-- Clinical Schema
clinical.patient
clinical.diagnosis
clinical.treatment

-- Biomedical Schema  
biomedical.device
biomedical.calibration
biomedical.maintenance

-- Hospital Schema
hospital.bed
hospital.room
hospital.staff
hospital.occupancy
```

### Event Ownership

```
Domain publishes events for its OWN entities:
- Clinical publishes: PatientUpdated, DecisionMade
- Biomedical publishes: DeviceAlarm, CalibrationComplete
- Hospital publishes: BedOccupied, StaffAssigned

Cross-domain events are derived:
- Clinical derives: ClinicalAlert from DeviceAlarm
- Hospital derives: BedAlert from ClinicalAlert
```

---

## Boundary Violations to Avoid

### ❌ Clinical Should NOT Own

- Device maintenance schedules
- Bed inventory
- Staff payroll
- Building infrastructure

### ❌ Biomedical Should NOT Own

- Patient treatment plans
- Clinical diagnoses
- Bed assignments
- Appointment scheduling

### ❌ Hospital Should NOT Own

- Device calibration algorithms
- Clinical decision logic
- Treatment protocols
- Medical records

---

## Review Checklist

When designing new entities, ask:

```
1. Is there a clear single owner domain?
2. Does the owner domain have final say?
3. Are consumer domains read-only?
4. Are cross-domain events defined?
5. Does this violate ownership rules?
```

If any answer is unclear, escalate to Architecture Board.

---

## Open Questions

| Question | Status | Owner |
|----------|--------|-------|
| Who owns Consent records? | Open | Clinical |
| Who owns Insurance data? | Open | Operations |
| Who owns Research data? | Open | TBD |

These will be resolved as EREN evolves.

---

*EREN Domain Ownership v1.0*
*Architecture Board - 2026-07-15*
