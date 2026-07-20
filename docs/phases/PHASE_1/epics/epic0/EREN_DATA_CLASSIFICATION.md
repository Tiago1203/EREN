# EREN Data Classification
## How We Protect Every Type of Data

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This document defines how EREN classifies, protects, and manages different types of data.

**Rule:** Every data type has a classification. Classification determines handling requirements.

---

## Classification Levels

| Level | Name | Description | Examples |
|-------|------|-------------|----------|
| 1 | **PHI** | Protected Health Information | Patient data, diagnoses, treatments |
| 2 | **Regulatory** | Compliance-required data | Audit logs, consent records |
| 3 | **Operational** | System-generated data | Metrics, device telemetry |
| 4 | **Internal** | Internal use only | Sessions, configurations |

---

## Data Classification Matrix

| Data Type | Class | Encrypt | Audit | Retention | Tenant Isolation | Sharing |
|-----------|-------|---------|-------|-----------|-----------------|--------|
| **Patient demographics** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Diagnosis** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Treatment plans** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Vital signs** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Medications** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Lab results** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Consent records** | PHI | ✅ AES-256 | ✅ ALL | 10 years | ✅ Required | ❌ None |
| **Audit logs** | Regulatory | ✅ AES-256 | ❌ N/A | 10 years | ✅ Required | ❌ None |
| **Device telemetry** | Operational | Optional | Med | 90 days | ✅ Required | ❌ None |
| **Alarm history** | Operational | Optional | Med | 1 year | ✅ Required | ❌ None |
| **CDS recommendations** | PHI | ✅ AES-256 | ✅ ALL | 7 years | ✅ Required | ❌ Limited |
| **Metrics** | Internal | ❌ No | ❌ No | 30 days | ❌ Optional | ❌ None |
| **Sessions** | Auth | ✅ AES-256 | Auth only | 90 days | ✅ Required | ❌ None |
| **Configurations** | Internal | Optional | No | Lifetime | ✅ Required | ❌ None |

---

## Classification Definitions

### PHI (Protected Health Information)

**Definition:** Any individually identifiable health information.

**Handling Requirements:**
- ✅ Always encrypt at rest (AES-256)
- ✅ Always encrypt in transit (TLS 1.3)
- ✅ Audit every access
- ✅ Never share across tenants
- ✅ Retain minimum 7 years
- ✅ Delete on patient request (with legal hold exceptions)

**Examples:**
- Patient name, DOB, MRN
- Diagnoses, treatments, medications
- Lab results, vital signs
- Clinical notes, imaging
- CDS recommendations

---

### Regulatory

**Definition:** Data required for compliance and auditing.

**Handling Requirements:**
- ✅ Encrypt at rest
- ✅ Immutable (no modifications)
- ✅ Retain per regulation
- ✅ Tenant isolation required
- ⚠️ May be shared with auditors (with proper authorization)

**Examples:**
- Audit logs
- Consent records
- Access history
- Compliance reports

---

### Operational

**Definition:** System-generated data for operations and monitoring.

**Handling Requirements:**
- ⚠️ Encryption optional
- ⚠️ Audit on sensitive operations
- ⏱️ Shorter retention (30-365 days)
- ✅ Tenant isolation required

**Examples:**
- Device telemetry
- Alarm history
- System logs
- Performance metrics

---

### Internal

**Definition:** Data for internal system operation.

**Handling Requirements:**
- ❌ No encryption required
- ❌ No audit required
- ⏱️ Short retention (days to weeks)
- ✅ Tenant isolation recommended

**Examples:**
- Cache data
- Session tokens
- System configurations
- Prometheus metrics

---

## Data Flow Classification

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA CLASSIFICATION FLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Patient Data                                                        │
│       ↓                                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CLASSIFIED AS: PHI                                             │   │
│  │                                                              │   │
│  │  Storage: PostgreSQL (encrypted)                            │   │
│  │  Cache: Redis (encrypted)                                    │   │
│  │  Audit: Every read/write                                    │   │
│  │  Retention: 7 years                                          │   │
│  │  Tenant: Isolated                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Device Telemetry                                                   │
│       ↓                                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CLASSIFIED AS: Operational                                     │   │
│  │                                                              │   │
│  │  Storage: Time-series DB                                      │   │
│  │  Cache: None (streaming)                                      │   │
│  │  Audit: High-priority alarms only                            │   │
│  │  Retention: 90 days                                          │   │
│  │  Tenant: Isolated                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Audit Logs                                                         │
│       ↓                                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CLASSIFIED AS: Regulatory                                     │   │
│  │                                                              │   │
│  │  Storage: Immutable (append-only)                           │   │
│  │  Audit: N/A (it's the audit)                               │   │
│  │  Retention: 10 years                                         │   │
│  │  Tenant: Isolated                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Retention by Data Type

| Data Type | Minimum | Maximum | Trigger |
|-----------|---------|---------|---------|
| Patient records | 7 years | Life + 10 years | Patient death |
| Consent records | 10 years | Life + 10 years | Consent revocation |
| Audit logs | 10 years | Indefinite | Regulatory requirement |
| Device telemetry | 90 days | 1 year | Storage cost |
| CDS recommendations | 7 years | 7 years | HIPAA |
| Sessions | 90 days | 90 days | Session timeout |
| Metrics | 30 days | 90 days | Storage cost |

---

## Tenant Isolation Requirements

| Classification | Cross-Tenant Access | Notes |
|---------------|---------------------|-------|
| PHI | ❌ Never | Strict isolation |
| Regulatory | ⚠️ Auditors only | With proper authorization |
| Operational | ⚠️ Admin only | System administration |
| Internal | ⚠️ System only | Infrastructure needs |

---

## Compliance Mapping

| Regulation | Data Types | Requirements |
|------------|-----------|--------------|
| HIPAA | PHI | Encryption, audit, retention, access control |
| IEC 60601 | Device data | Calibration records, maintenance history |
| ISO 14971 | Risk data | Risk assessments, incident reports |
| ISO 13485 | Quality data | Document control, records |

---

## Adding New Data Types

1. Classify the data type
2. Apply handling requirements
3. Update this matrix
4. Document in ADR if significant

---

*EREN Data Classification v1.0*
*Architecture Board - 2026-07-15*
