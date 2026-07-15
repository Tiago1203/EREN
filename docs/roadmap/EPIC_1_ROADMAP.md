# Epic 1 — First Vertical Slice

## Goal

**Deliver the first complete use case.**

A user can authenticate, create a patient, and the system provides complete evidence of the operation.

---

## Definition of Done

A use case is **DONE** when:

| Check | Requirement |
|-------|-------------|
| ✓ Authenticated | JWT valid, not expired |
| ✓ Tenant resolved | tenant_id present in context |
| ✓ Validated | Pydantic validation passes |
| ✓ Persisted | PostgreSQL confirms INSERT |
| ✓ Audited | audit_event in audit table |
| ✓ Event stored | message in outbox |
| ✓ Logs | Structured JSON with trace_id, tenant_id |
| ✓ Tests | Unit + integration pass |

**Nothing else.**

---

## What We're NOT Building Yet

- Neo4j
- Qdrant
- Kafka
- Multi-agent
- RAG
- CQRS
- Event Sourcing
- Complex workflows

---

## First Flow

```
POST /patients
    ↓
JWT validated
    ↓
Tenant resolved
    ↓
Validate request
    ↓
Create patient
    ↓
Save to PostgreSQL
    ↓
Record audit
    ↓
Store PatientCreated in Outbox
    ↓
HTTP 201
```

---

## Milestones

### M1: Authentication Provider
- SupabaseAuthenticationProvider implemented
- JWT validation works
- Tenant extraction from token

### M2: Patient Context
- Patient model
- Create Patient endpoint
- Outbox pattern

### M3: Audit
- Audit middleware on every request
- PHI access logged

### M4: First Integration Test
- Full flow test passes
- All components wired

---

## Success Criteria

**In 4 weeks:** A 5-minute demo where:
1. User logs in
2. Creates a patient
3. Sees audit record
4. Sees event in outbox

---

## Rules

1. Every PR enables a **complete use case**, not half a component
2. Audit is **transversal**, not a sprint
3. No technical decision depends on Cognitive Model (still experimental)
4. Architecture is validated with **working software**, not documents

---

*Last updated: 2026-07-15*
*Status: STARTING*
