# EREN Architecture Principles
## Rules for Resolving Design Conflicts

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

These principles resolve design conflicts. When two valid approaches conflict, these principles determine which wins.

**Rule:** All principles are hierarchically ordered. Higher principles always win.

---

## Principle Hierarchy

```
CRITICAL (Never broken without Architecture Board approval)
───────────────────────────────────────────────────────────
1. Patient Safety Above All
2. Human Clinician Has Final Authority
3. PHI is Protected and Audited

HIGH (Require approval to break)
───────────────────────────────────────────────────────────
4. Every PHI Access is Auditable
5. Events Are Immutable
6. Services Own Their Data
7. Fail Safely

MEDIUM (Guidelines, not rules)
───────────────────────────────────────────────────────────
8. APIs Are Backward Compatible
9. All Public APIs Have Contracts
10. External Integrations Behind Adapters
11. Every Capability Has Health Checks
12. Trust But Verify External Systems
```

---

## Critical Principles

### 1. Patient Safety Above All

```
Statement: Patient safety is never compromised for any other consideration.

Resolution: When patient safety conflicts with any other principle,
            patient safety wins without exception.

Examples:
- Slow alarm > dropped alarm
- Cached data > stale data
- Secure > fast
```

### 2. Human Clinician Has Final Authority

```
Statement: EREN provides recommendations. Clinicians make decisions.

Resolution: EREN never acts on clinical decisions without human authorization.
            CDS recommendations require clinician review for P0/P1 severity.

Examples:
- Alarm escalation requires acknowledgment
- CDS recommendation requires clinician decision
- Emergency override requires audit trail
```

### 3. PHI is Protected and Audited

```
Statement: Protected Health Information is always encrypted and access is logged.

Resolution: No PHI access without encryption and audit.
            Violation is a critical security incident.

Examples:
- PHI in transit = TLS 1.3
- PHI at rest = AES-256
- Every PHI access = audit log
```

---

## High Principles

### 4. Every PHI Access is Auditable

```
Statement: Every read, write, and export of PHI is logged.

Resolution: Access to PHI generates immutable audit event.
            Audit cannot be disabled or bypassed.

Examples:
- Patient lookup = audit event
- Diagnosis update = audit event
- Data export = audit event + approval
```

### 5. Events Are Immutable

```
Statement: Once published, domain events cannot be modified or deleted.

Resolution: Corrections published as new events. Original event preserved.

Examples:
- Wrong diagnosis? Publish DiagnosisCorrected event
- Patient name change? Publish PatientNameChanged event
- Never modify existing events
```

### 6. Services Own Their Data

```
Statement: Each bounded context owns its data. No direct cross-context data modification.

Resolution: Data changes flow through events and published interfaces.

Examples:
- Patient Context owns Patient data
- Diagnosis Context reads Patient ID, doesn't modify
- Capacity Context receives PatientAdmitted event
```

### 7. Fail Safely

```
Statement: System failures preserve safety and data integrity.

Resolution: Graceful degradation maintains safety. Failures don't cause harm.

Examples:
- LLM timeout = fallback to rules, mark confidence low
- Database down = return error, don't cache stale PHI
- Device offline = alert and continue
```

---

## Medium Principles

### 8. APIs Are Backward Compatible

```
Statement: API changes don't break existing clients.

Resolution: Additive changes OK. Breaking changes require new version.

Examples:
- Add optional fields = OK
- Add required fields = New version
- Remove fields = Deprecated, then removed
```

### 9. All Public APIs Have Contracts

```
Statement: Every public API is defined by a contract (interface/schema).

Resolution: No implementation without contract. Contract is versioned.

Examples:
- REST endpoints have OpenAPI spec
- Events have schema
- gRPC has proto definition
```

### 10. External Integrations Behind Adapters

```
Statement: Core logic never imports external SDKs directly.

Resolution: External systems accessed through adapters only.

Examples:
- FHIR SDK → FHIR Adapter → FHIR Contract
- MQTT client → MQTT Adapter → MQTT Contract
```

### 11. Every Capability Has Health Checks

```
Statement: Every capability exposes health and dependency status.

Resolution: Health endpoint returns ready/alive/dependency status.

Examples:
- Ready = Can accept requests
- Alive = Is responding
- Dependencies = All dependencies healthy
```

### 12. Trust But Verify External Systems

```
Statement: External systems are untrusted until verified.

Resolution: Validate all external inputs. Never trust blindly.

Examples:
- Validate FHIR resources
- Verify MQTT message schema
- Check LLM response format
- Reject malformed external data
```

---

## Violation Process

When a principle must be violated:

```
1. Document: Create ADR explaining violation
2. Approve: Architecture Board review
3. Limit: Minimize scope of violation
4. Review: Post-incident review required
5. Track: Add to violation log
```

---

## Conflict Resolution Examples

| Conflict | Resolution |
|----------|-----------|
| Speed vs. Safety | Safety |
| Availability vs. Security | Security (for PHI) |
| Performance vs. Traceability | Traceability |
| Convenience vs. Compliance | Compliance |
| Feature vs. Reliability | Reliability |

---

## Review Schedule

Principles reviewed quarterly with Architecture Board.

Changes require:
1. Proposal with rationale
2. Impact analysis
3. Architecture Board approval
4. ADR documentation

---

*EREN Architecture Principles v1.0*
*Architecture Board - 2026-07-15*
