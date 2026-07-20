# EREN Three Domains Model
## Clinical, Biomedical, and Hospital Domains

---

## Overview

EREN operates at the intersection of three distinct domains, each with its own:
- Ubiquitous language
- Key entities
- Core processes
- Regulatory framework
- Success metrics

---

## Domain Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        EREN                                  │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  CLINICAL   │◄──►│   HOSPITAL  │◄──►│ BIOMEDICAL  │     │
│  │   DOMAIN    │    │    DOMAIN    │    │   DOMAIN    │     │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤     │
│  │ Patient     │    │ Beds        │    │ Device      │     │
│  │ Diagnosis   │    │ Occupancy   │    │ Monitor     │     │
│  │ Treatment   │    │ Inventory   │    │ Ventilator  │     │
│  │ Symptoms    │    │ Staff       │    │ Calibration │     │
│  │ Laboratory  │    │ Costs       │    │ MTBF        │     │
│  │ Prognosis   │    │ Shifts      │    │ Preventive  │     │
│  │ Outcome     │    │ ORs         │    │ Corrective  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│                    DECISION ENGINE                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Clinical Domain

### Purpose
Improve patient outcomes through evidence-based decision support.

### Ubiquitous Language

| Term | Definition |
|------|------------|
| Patient | Individual receiving healthcare services |
| Diagnosis | Clinical judgment about health condition |
| Treatment | Intervention to address diagnosis |
| Prognosis | Expected course and outcome |
| Symptom | Patient-reported observation |
| Sign | Clinically observable finding |
| Comorbidity | Concurrent conditions |
| Adverse Event | Unintended harmful occurrence |

### Key Entities

```
Clinical Domain
├── Patient
│   ├── Demographics
│   ├── Medical History
│   ├── Current Conditions
│   ├── Medications
│   ├── Allergies
│   └── Consent Status
├── Encounter
│   ├── Type (Inpatient, Outpatient, ED)
│   ├── Chief Complaint
│   ├── Assessment
│   └── Plan
├── Diagnosis
│   ├── ICD-10 Code
│   ├── Status (Active, Resolved)
│   └── Evidence
├── Order
│   ├── Type (Medication, Lab, Imaging)
│   ├── Status
│   └── Result
└── Outcome
    ├── Type
    ├── Timing
    └── Assessment
```

### Core Questions

| Question | EREN Capability |
|----------|-----------------|
| What is the likely diagnosis? | Diagnostic Support |
| What treatment is evidence-based? | Treatment Guidance |
| What are the drug interactions? | Safety Check |
| What is the prognosis? | Outcome Prediction |
| What monitoring is needed? | Alert Configuration |

### Regulatory Framework
- HIPAA (patient privacy)
- FDA (clinical decision support software)
- State medical licensing

### Success Metrics
- Diagnosis accuracy
- Treatment outcome
- Adverse event reduction
- Readmission rates

---

## 2. Biomedical Domain

### Purpose
Ensure medical technology is safe, functional, and properly maintained.

### Ubiquitous Language

| Term | Definition |
|------|------------|
| Device | Medical equipment with specific function |
| Medical Device | FDA-regulated device |
| Biomedical Device | Device under biomedical engineering management |
| Calibration | Verification of measurement accuracy |
| MTBF | Mean Time Between Failures |
| Preventive Maintenance | Scheduled maintenance to prevent failure |
| Corrective Maintenance | Maintenance to fix actual failure |
| Predictive Maintenance | Maintenance based on condition monitoring |

### Key Entities

```
Biomedical Domain
├── Device
│   ├── Classification (Class I, II, III)
│   ├── Manufacturer
│   ├── Model
│   ├── Serial Number
│   ├── Location
│   └── Status (Operational, Maintenance, Retired)
├── Maintenance Record
│   ├── Type (Preventive, Corrective, Predictive)
│   ├── Date
│   ├── Technician
│   ├── Actions Taken
│   └── Parts Replaced
├── Calibration
│   ├── Standard (NIST-traceable)
│   ├── Date
│   ├── Result (Pass/Fail)
│   ├── Certificate
│   └── Next Due
├── Alert/Alarm
│   ├── Priority (Critical, Warning, Info)
│   ├── Source Device
│   ├── Timestamp
│   └── Acknowledged
└── Risk Assessment
    ├── Hazard Identification
    ├── Probability
    ├── Severity
    └── Risk Level
```

### Core Questions

| Question | EREN Capability |
|----------|-----------------|
| Is this device due for maintenance? | Maintenance Scheduling |
| Is this device calibrated? | Calibration Tracking |
| What is the device failure risk? | Risk Assessment |
| What happened to this device? | Incident Analysis |
| What devices need attention? | Priority Dashboard |

### Regulatory Framework
- IEC 60601 (medical device safety)
- IEC 62304 (software lifecycle)
- ISO 14971 (risk management)
- FDA 510(k) (device clearance)
- ISO 13485 (quality management)

### Success Metrics
- Device uptime
- Calibration compliance
- Mean Time To Repair (MTTR)
- Mean Time Between Failures (MTBF)
- Preventive vs. corrective maintenance ratio

---

## 3. Hospital Domain

### Purpose
Optimize hospital operations for efficient, safe patient care delivery.

### Ubiquitous Language

| Term | Definition |
|------|------------|
| Bed | Licensed inpatient location |
| Occupancy | Current bed utilization |
| LOS | Length of Stay |
| Throughput | Patient flow rate |
| Staffing | Personnel allocation |
| Turnaround | Time for process completion |
| Capacity | Maximum workload capability |

### Key Entities

```
Hospital Domain
├── Physical Plant
│   ├── Building
│   ├── Floor
│   ├── Unit (ICU, Med-Surg, OR, ED)
│   ├── Room
│   └── Bed
├── Resources
│   ├── Staff (Physicians, Nurses, Techs)
│   ├── Equipment (shared devices)
│   ├── Rooms (ORs, procedure rooms)
│   └── Supplies
├── Operations
│   ├── Admission
│   ├── Transfer
│   ├── Discharge
│   └── Scheduling
└── Financial
    ├── Cost
    ├── Revenue
    └── Payer
```

### Core Questions

| Question | EREN Capability |
|----------|-----------------|
| What is current occupancy? | Capacity Dashboard |
| Where are bottlenecks? | Flow Analysis |
| Who is available for shift? | Staffing Optimization |
| What is average LOS by diagnosis? | Analytics |
| When will beds be available? | Prediction |

### Regulatory Framework
- CMS Conditions of Participation
- State hospital licensing
- Joint Commission standards
- OSHA (workplace safety)

### Success Metrics
- Bed occupancy rate
- Average length of stay
- Patient throughput
- Staff satisfaction
- Cost per discharge

---

## Cross-Domain Integration

### The Integration Challenge

```
Clinical asks: "Is the IV pump functioning correctly?"
    ↓
Biomedical knows: "Pump calibration due in 2 days"
    ↓
Hospital knows: "Current patient is high-acuity, relocating is risky"
    ↓
EREN synthesizes: "Recommendation: Expedite calibration. Risk if delayed: HIGH"
```

### Cross-Domain Entities

| Entity | Clinical | Biomedical | Hospital |
|--------|----------|------------|----------|
| Patient | Patient | - | Admitted |
| Device | Monitoring | Device | Equipment |
| Room | ICU | - | Room |
| Staff | Physician | BMET | Nurse |
| Alert | Critical | Alarm | Notification |
| Risk | Clinical | Device | Operational |

### Decision Integration Example

```
Scenario: "Patient in Room 305 requires transport to MRI"

Clinical input:
- Patient stability: MODERATE
- Transport risk: LOW-MODERATE
- Monitoring needed: YES

Biomedical input:
- Transport monitor: Available, calibrated
- MRI machine: Operational, scheduled maintenance in 3 days
- Backup equipment: AVAILABLE

Hospital input:
- MRI wait time: 45 minutes
- Current census: 87% occupancy
- Staff availability: 2 escorts available

EREN Decision:
- Recommendation: PROCEED with monitoring
- Confidence: 85%
- Risk if delayed: MODERATE
- Alternative: Reschedule (risk: LOW clinical, HIGH operational)
```

---

## Domain Capability Matrix

| Capability | Clinical | Biomedical | Hospital |
|------------|----------|------------|----------|
| Identity | High | High | High |
| Authorization | High | High | High |
| Audit | High | High | High |
| Trust | Critical | High | Medium |
| Risk | Critical | Critical | Medium |
| Compliance | Critical | Critical | High |
| Knowledge | Critical | High | Medium |
| Memory | High | High | High |
| Reasoning | Critical | High | Medium |
| Planning | Medium | High | High |
| Decision | Critical | Medium | Medium |
| Explain | Critical | High | Medium |

---

## Architecture Implications

### Contracts Must Span Domains

```python
# Example: Trust spans all three domains
class TrustProvider(Protocol):
    # Clinical trust
    async def evaluate_clinical_trust(guideline: ClinicalGuideline) -> TrustScore
    async def evaluate_evidence_trust(study: ResearchStudy) -> TrustScore
    
    # Biomedical trust
    async def evaluate_device_trust(device: Device) -> TrustScore
    async def evaluate_calibration_trust(record: CalibrationRecord) -> TrustScore
    
    # Hospital trust
    async def evaluate_staff_trust(staff: Staff) -> TrustScore
    async def evaluate_protocol_trust(protocol: HospitalProtocol) -> TrustScore
```

### Events Cross Domains

```python
# Example: A single event affects all domains
class DeviceAlarmEvent(DomainEvent):
    domain: Domain = Domain.BIOMEDICAL  # Primary domain
    affected_domains: set[Domain] = {Domain.CLINICAL, Domain.HOSPITAL}
    
    # Biomedical perspective
    device_id: str
    alarm_type: AlarmType
    
    # Clinical perspective
    patient_id: str | None
    care_area: str
    
    # Hospital perspective
    bed_id: str | None
    staff_needed: list[StaffRole]
```

---

## Implementation Guidance

### 1. Domain Boundaries
- Each domain has a clear bounded context
- Cross-domain communication via contracts
- No direct domain-to-domain coupling

### 2. Shared Kernel
- Patient ID (anonymized where required)
- Device ID
- Location hierarchy
- Time (UTC)

### 3. Ubiquitous Language
- Each domain maintains its own glossary
- Translation layer for cross-domain terms
- Regular synchronization

### 4. Integration Testing
- Test each domain independently
- Test cross-domain scenarios
- Verify no domain coupling

---

*EREN Three Domains Model v1.0*
*Architecture Board - 2026-07-15*
