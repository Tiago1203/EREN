# EREN Domain Events Catalog
## Complete Registry of Domain Events

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |
| 1.1 | 2026-07-16 | Architecture Board | Hospital + Clinical Intelligence events added |

---

## Purpose

This catalog defines all domain events in EREN. Every event is a contract between producers and consumers.

**Rule:** Before creating a new event, check if one already exists.

---

## Event Format

```yaml
EventName:
  aggregate: Domain entity that owns the event
  version: Current schema version
  idempotent: Yes/No
  ordering: Stream key for ordering
  payload:
    - field: description (required/optional)
  pii: Yes/No
  hipaa: Yes/No
  retention_days: 2555 (7 years) or specific
  published_by: Context that publishes
  consumed_by: [List of contexts]
  retry_policy: EXACTLY_ONCE / AT_LEAST_ONCE / AT_MOST_ONCE
  dlq: Dead letter queue name
```

---

## Clinical Domain Events

### Patient Events

| Event | Purpose |
|-------|---------|
| PatientCreated | New patient registered |
| PatientUpdated | Patient demographics changed |
| PatientDeceased | Patient death recorded |
| PatientTransferred | Patient moved to another unit |

#### PatientCreated

```yaml
PatientCreated (v1.0):
  aggregate: Patient
  idempotent: Yes
  ordering: patient_id
  payload:
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - mrn: string (required)
    - admitted_at: timestamp (required)
    - version: "1.0"
  pii: Yes (name, DOB)
  hipaa: Yes
  retention_days: 2555
  published_by: Patient Context
  consumed_by: [Diagnosis, Treatment, Capacity, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: clinical-patient-dlq
```

#### PatientUpdated

```yaml
PatientUpdated (v1.0):
  aggregate: Patient
  idempotent: Yes
  ordering: patient_id
  payload:
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - changes: object (required)
    - updated_at: timestamp (required)
  pii: Yes (if demographics change)
  hipaa: Yes
  retention_days: 2555
  published_by: Patient Context
  consumed_by: [Diagnosis, Treatment, Capacity, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: clinical-patient-dlq
```

---

### Diagnosis Events

| Event | Purpose |
|-------|---------|
| DiagnosisMade | New diagnosis recorded |
| DiagnosisUpdated | Diagnosis modified |
| DiagnosisConfirmed | Diagnosis confirmed by physician |

#### DiagnosisMade

```yaml
DiagnosisMade (v1.0):
  aggregate: Diagnosis
  idempotent: Yes
  ordering: diagnosis_id
  payload:
    - diagnosis_id: UUID (required)
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - icd10_code: string (required)
    - diagnosed_by: Staff ID (required)
    - diagnosed_at: timestamp (required)
  pii: No
  hipaa: Yes (linked to patient)
  retention_days: 2555
  published_by: Diagnosis Context
  consumed_by: [Treatment, CDS, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: clinical-diagnosis-dlq
```

---

### Treatment Events

| Event | Purpose |
|-------|---------|
| TreatmentStarted | Treatment plan initiated |
| TreatmentModified | Treatment changed |
| TreatmentCompleted | Treatment finished |
| TreatmentCancelled | Treatment stopped |

#### TreatmentStarted

```yaml
TreatmentStarted (v1.0):
  aggregate: Treatment
  idempotent: Yes
  ordering: treatment_id
  payload:
    - treatment_id: UUID (required)
    - patient_id: UUID (required)
    - diagnosis_id: UUID (required)
    - tenant_id: UUID (required)
    - treatment_type: string (required)
    - ordered_by: Staff ID (required)
    - started_at: timestamp (required)
  pii: No
  hipaa: Yes
  retention_days: 2555
  published_by: Treatment Context
  consumed_by: [CDS, Medication, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: clinical-treatment-dlq
```

---

### Clinical Decision Support Events

| Event | Purpose |
|-------|---------|
| RecommendationGenerated | CDS produced a recommendation |
| RecommendationAccepted | Clinician accepted recommendation |
| RecommendationRejected | Clinician rejected recommendation |
| RecommendationSuperseded | Better recommendation available |

#### RecommendationGenerated

```yaml
RecommendationGenerated (v1.0):
  aggregate: Recommendation
  idempotent: Yes
  ordering: recommendation_id
  payload:
    - recommendation_id: UUID (required)
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - action: string (required)
    - confidence: float (0.0-1.0) (required)
    - evidence: array (required)
    - reasoning_chain: array (optional)
    - generated_at: timestamp (required)
  pii: No
  hipaa: Yes
  retention_days: 2555
  published_by: CDS Context
  consumed_by: [Audit]
  retry_policy: EXACTLY_ONCE
  dlq: cds-recommendation-dlq
```

---

## Biomedical Domain Events

### Device Events

| Event | Purpose |
|-------|---------|
| DeviceRegistered | New device added to inventory |
| DeviceStatusChanged | Device status updated |
| DeviceLocationChanged | Device moved |
| DeviceRetired | Device decommissioned |

#### DeviceRegistered

```yaml
DeviceRegistered (v1.0):
  aggregate: Device
  idempotent: Yes
  ordering: device_id
  payload:
    - device_id: UUID (required)
    - tenant_id: UUID (required)
    - serial_number: string (required)
    - device_type: string (required)
    - manufacturer: string (required)
    - model: string (required)
    - registered_at: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 2555
  published_by: Device Context
  consumed_by: [Alarm, Maintenance, Capacity, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: biomedical-device-dlq
```

---

### Alarm Events

| Event | Purpose |
|-------|---------|
| DeviceAlarmTriggered | Device alarm activated |
| DeviceAlarmAcknowledged | Alarm acknowledged by staff |
| DeviceAlarmEscalated | Alarm escalated due to no response |

#### DeviceAlarmTriggered

```yaml
DeviceAlarmTriggered (v1.0):
  aggregate: DeviceAlarm
  idempotent: Yes
  ordering: alarm_id
  payload:
    - alarm_id: UUID (required)
    - device_id: UUID (required)
    - patient_id: UUID (optional)
    - tenant_id: UUID (required)
    - alarm_type: string (required)
    - severity: int (1-5) (required)
    - priority: string (critical/high/medium/low) (required)
    - alarm_value: float (optional)
    - threshold: float (optional)
    - triggered_at: timestamp (required)
  pii: Yes (linked to patient if present)
  hipaa: Yes
  retention_days: 2555
  published_by: Alarm Context
  consumed_by: [Clinical Decision Support, Notification, Audit]
  retry_policy: AT_LEAST_ONCE
  dlq: biomedical-alarm-dlq
```

---

### Maintenance Events

| Event | Purpose |
|-------|---------|
| CalibrationDue | Device needs calibration |
| CalibrationCompleted | Calibration performed |
| MaintenanceScheduled | Work order created |
| MaintenanceCompleted | Work order finished |

#### CalibrationCompleted

```yaml
CalibrationCompleted (v1.0):
  aggregate: Calibration
  idempotent: Yes
  ordering: calibration_id
  payload:
    - calibration_id: UUID (required)
    - device_id: UUID (required)
    - tenant_id: UUID (required)
    - standard: string (required)
    - result: string (pass/fail) (required)
    - performed_by: Staff ID (required)
    - calibrated_at: timestamp (required)
    - next_due: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 2555
  published_by: Maintenance Context
  consumed_by: [Device, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: biomedical-maintenance-dlq
```

---

## Hospital Domain Events

### Capacity Events

| Event | Purpose |
|-------|---------|
| BedOccupied | Bed assigned to patient |
| BedVacated | Patient discharged, bed available |
| UnitCapacityChanged | Unit occupancy threshold crossed |

#### BedOccupied

```yaml
BedOccupied (v1.0):
  aggregate: Bed
  idempotent: Yes
  ordering: bed_id
  payload:
    - bed_id: UUID (required)
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - unit_id: string (required)
    - occupied_at: timestamp (required)
  pii: Yes (linked to patient)
  hipaa: Yes
  retention_days: 2555
  published_by: Capacity Context
  consumed_by: [Patient, Alarm, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: hospital-capacity-dlq
```

---

### Staffing Events

| Event | Purpose |
|-------|---------|
| StaffAssigned | Staff assigned to unit/patient |
| StaffShiftStarted | Shift began |
| StaffShiftEnded | Shift ended |

---

## Hospital Domain Events (Extended)

### Organization Events

| Event | Purpose |
|-------|---------|
| OrganizationRegistered | New hospital organization created |
| OrganizationUpdated | Organization details changed |
| OrganizationSuspended | Organization temporarily suspended |

#### OrganizationRegistered

```yaml
OrganizationRegistered (v1.0):
  aggregate: Organization
  idempotent: Yes
  ordering: organization_id
  payload:
    - organization_id: UUID (required)
    - tenant_id: UUID (required)
    - name: string (required)
    - registered_at: timestamp (required)
  pii: No
  hipaa: Yes (linked to hospital)
  retention_days: 2555
  published_by: Organization Context
  consumed_by: [All contexts]
  retry_policy: EXACTLY_ONCE
  dlq: hospital-organization-dlq
```

---

### Department Events

| Event | Purpose |
|-------|---------|
| DepartmentCreated | New department added to organization |
| DepartmentUpdated | Department details changed |
| DepartmentClosed | Department permanently closed |
| DepartmentStaffChanged | Staff composition changed |

---

### Campus Events

| Event | Purpose |
|-------|---------|
| CampusRegistered | New campus added to organization |
| CampusConfigured | Campus settings updated |
| CampusDeactivated | Campus temporarily deactivated |

---

### Building Events

| Event | Purpose |
|-------|---------|
| BuildingRegistered | New building added to campus |
| BuildingConfigured | Building settings updated |
| BuildingDeactivated | Building temporarily closed |

---

### Floor Events

| Event | Purpose |
|-------|---------|
| FloorConfigured | Floor configured in building |
| FloorCapacityUpdated | Floor bed capacity changed |

---

### Room Events

| Event | Purpose |
|-------|---------|
| RoomConfigured | Room configured in floor |
| RoomStatusChanged | Room status updated (operational, maintenance, etc.) |

#### RoomConfigured

```yaml
RoomConfigured (v1.0):
  aggregate: Room
  idempotent: Yes
  ordering: room_id
  payload:
    - room_id: UUID (required)
    - tenant_id: UUID (required)
    - floor_id: UUID (required)
    - room_number: string (required)
    - room_type: string (required)
    - bed_count: integer (required)
    - configured_at: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 2555
  published_by: Room Context
  consumed_by: [Capacity, Scheduling, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: hospital-room-dlq
```

---

### Biomedical Engineering Events

| Event | Purpose |
|-------|---------|
| BiomedicalTeamAssigned | BMET team assigned to campus |
| EngineeringProjectCreated | New engineering project started |
| EngineeringProjectCompleted | Engineering project finished |

---

### Asset Management Events

| Event | Purpose |
|-------|---------|
| AssetAssigned | Asset assigned to location/person |
| AssetTransferred | Asset moved to new location |
| AssetRetired | Asset permanently removed from inventory |

---

### Inventory Events

| Event | Purpose |
|-------|---------|
| SparePartAdded | Spare part added to inventory |
| SparePartConsumed | Spare part used in maintenance |
| SparePartLowStock | Spare part below minimum threshold |
| InventoryAdjusted | Manual inventory adjustment made |

#### SparePartLowStock

```yaml
SparePartLowStock (v1.0):
  aggregate: SparePart
  idempotent: Yes
  ordering: spare_part_id
  payload:
    - spare_part_id: UUID (required)
    - tenant_id: UUID (required)
    - part_number: string (required)
    - current_quantity: integer (required)
    - minimum_quantity: integer (required)
    - warehouse_id: UUID (required)
    - alert_at: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 365
  published_by: Inventory Context
  consumed_by: [PurchaseOrder, BiomedicalEngineering, Audit]
  retry_policy: AT_LEAST_ONCE
  dlq: hospital-inventory-dlq
```

---

### Purchase Order Events

| Event | Purpose |
|-------|---------|
| PurchaseOrderCreated | New PO created for spare parts |
| PurchaseOrderApproved | PO approved for procurement |
| PurchaseOrderReceived | PO items received at warehouse |
| PurchaseOrderCancelled | PO cancelled before fulfillment |

---

## Clinical Intelligence Domain Events

### Root Cause Analysis Events

| Event | Purpose |
|-------|---------|
| RootCauseAnalysisRequested | New RCA initiated |
| RootCauseIdentified | Root cause found |
| CausalChainGenerated | Causal chain generated |
| FailurePatternDetected | Recurring failure pattern detected |

#### RootCauseIdentified

```yaml
RootCauseIdentified (v1.0):
  aggregate: RootCauseAnalysis
  idempotent: Yes
  ordering: analysis_id
  payload:
    - analysis_id: UUID (required)
    - tenant_id: UUID (required)
    - incident_id: UUID (required)
    - device_id: UUID (required)
    - root_cause: string (required)
    - confidence: float (0.0-1.0) (required)
    - evidence: array (required)
    - identified_at: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 2555
  published_by: RootCauseAnalysis Context
  consumed_by: [Troubleshooting, Maintenance, Audit]
  retry_policy: EXACTLY_ONCE
  dlq: ai-rootcause-dlq
```

---

### Differential Diagnosis Events

| Event | Purpose |
|-------|---------|
| DifferentialDiagnosisRequested | New differential diagnosis requested |
| DiagnosisRanked | Diagnosis candidates ranked by likelihood |
| DiagnosisConfidenceUpdated | Diagnosis confidence recalculated |

---

### Failure Prediction Events

| Event | Purpose |
|-------|---------|
| FailurePredictionRequested | Failure prediction triggered |
| DeviceFailureRiskUpdated | Device failure risk score updated |
| PreventiveMaintenanceRecommended | Preventive maintenance suggested |

#### DeviceFailureRiskUpdated

```yaml
DeviceFailureRiskUpdated (v1.0):
  aggregate: FailurePrediction
  idempotent: Yes
  ordering: device_id
  payload:
    - prediction_id: UUID (required)
    - tenant_id: UUID (required)
    - device_id: UUID (required)
    - risk_level: string (required)  # critical/high/medium/low
    - failure_probability: float (required)
    - prediction_window_hours: integer (required)
    - contributing_factors: array (required)
    - updated_at: timestamp (required)
  pii: No
  hipaa: No
  retention_days: 2555
  published_by: FailurePrediction Context
  consumed_by: [Maintenance, Capacity, Alarm, Audit]
  retry_policy: AT_LEAST_ONCE
  dlq: ai-failure-prediction-dlq
```

---

### Risk Assessment Events

| Event | Purpose |
|-------|---------|
| RiskAssessmentRequested | New risk assessment requested |
| RiskLevelChanged | Risk level updated |
| RiskMitigationRecommended | Mitigation actions suggested |

---

### Calibration Advisor Events

| Event | Purpose |
|-------|---------|
| CalibrationRecommended | Calibration schedule recommended |
| CalibrationUrgencyChanged | Calibration urgency level changed |
| CalibrationWindowIdentified | Optimal calibration window found |

---

### Compliance Advisor Events

| Event | Purpose |
|-------|---------|
| ComplianceViolationDetected | Regulatory violation identified |
| ComplianceCheckCompleted | Compliance check finished |
| ComplianceRemediationRecommended | Remediation actions suggested |

---

### Troubleshooting Events

| Event | Purpose |
|-------|---------|
| TroubleshootingSessionStarted | New troubleshooting session initiated |
| DiagnosticStepExecuted | Diagnostic step completed |
| TroubleshootingCompleted | Troubleshooting session concluded |
| ResolutionRecommended | Resolution action recommended |

---

### Maintenance Suggestions Events

| Event | Purpose |
|-------|---------|
| MaintenanceSuggestionGenerated | AI-generated maintenance recommendation |
| MaintenancePriorityUpdated | Maintenance priority recalculated |
| MaintenanceSuggestionAccepted | Staff accepted maintenance suggestion |
| MaintenanceSuggestionRejected | Staff rejected maintenance suggestion |

---

## System Events

### Audit Events

| Event | Purpose |
|-------|---------|
| PHIAccessed | Protected health information accessed |
| DataExported | Patient data exported |
| PolicyViolated | Security policy violated |
| CrossTenantAccessAttempted | Cross-tenant data access attempted (blocked) |

### AI System Events

| Event | Purpose |
|-------|---------|
| CDSRecommendationGenerated | Clinical decision support recommendation produced |
| CDSHallucinationDetected | AI hallucination detected in response |
| CDSConfidenceLow | CDS recommendation below confidence threshold |
| ReasoningChainGenerated | AI reasoning chain generated |
| ExplanationGenerated | AI explanation generated for recommendation |
| FeedbackReceived | User feedback on AI recommendation received |

#### PHIAccessed

```yaml
PHIAccessed (v1.0):
  aggregate: Audit
  idempotent: Yes
  ordering: event_id
  payload:
    - event_id: UUID (required)
    - principal_id: UUID (required)
    - patient_id: UUID (required)
    - tenant_id: UUID (required)
    - action: string (required)
    - fields_accessed: array (required)
    - accessed_at: timestamp (required)
  pii: Yes (all PHI)
  hipaa: Yes (accounting of disclosures)
  retention_days: 2555
  published_by: Audit Context
  consumed_by: []
  retry_policy: EXACTLY_ONCE
  dlq: system-audit-dlq
```

---

## Event Statistics

| Category | Count |
|----------|-------|
| Clinical Events | 10 |
| Biomedical Events | 8 |
| Hospital Events | 27 |
| Clinical Intelligence Events | 14 |
| System Events | 8 |
| **Total** | **67** |

---

## Adding New Events

1. Check if similar event exists
2. Define event in this catalog
3. Create ADR if event represents architectural decision
4. Update producer/consumer contexts
5. Document in Domain Events Catalog

---

*EREN Domain Events Catalog v1.1*
*Architecture Board - 2026-07-16*
