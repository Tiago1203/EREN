# EREN Non-Functional Requirements
## Performance, Scalability, and Quality Objectives

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |
| 1.1 | 2026-07-16 | Architecture Board | AI/LLM + UX + Integration targets added for EPIC 4-7 |

---

## Purpose

This document defines measurable performance, scalability, and quality objectives for EREN.

**Note:** These are target objectives based on current understanding. They will be revised with real data from MVP and production deployments.

---

## Quality Attributes (Priority Order)

```
1. PATIENT SAFETY        ⭐⭐⭐⭐⭐
2. HUMAN AUTHORITY       ⭐⭐⭐⭐⭐
3. SECURITY & PRIVACY    ⭐⭐⭐⭐
4. TRACEABILITY          ⭐⭐⭐⭐
5. AVAILABILITY          ⭐⭐⭐⭐
6. RELIABILITY           ⭐⭐⭐
7. MAINTAINABILITY       ⭐⭐⭐
8. PERFORMANCE           ⭐⭐⭐
9. SCALABILITY           ⭐⭐
```

### Quality Attributes Definitions

| Attribute | Definition | Why It Matters |
|-----------|------------|---------------|
| Patient Safety | System never harms patients | Core purpose |
| Human Authority | Clinicians always decide | EREN philosophy |
| Security & Privacy | PHI protected always | HIPAA compliance |
| Traceability | Every action is auditable | Accountability |
| Availability | System accessible when needed | Clinical workflow |
| Reliability | Consistent, correct behavior | Trust |
| Maintainability | Easy to evolve | Long-term viability |
| Performance | Responsive system | Clinical efficiency |
| Scalability | Grows with demand | Business growth |

---

## Availability

### Targets by Service

| Service | MVP Target | Production Target |
|---------|------------|-------------------|
| REST APIs | 99.5% | 99.95% |
| Critical Alarms | 99.9% | 99.99% |
| CDS Recommendations | 99.5% | 99.9% |
| Dashboard | 99.0% | 99.9% |
| Background Jobs | 99.0% | 99.5% |

### What This Means

```
MVP 99.5%:   ~3.5 hours downtime/month
Prod 99.95%: ~22 minutes downtime/month
```

### Critical Alarm SLA

Critical alarms (severity 1-2) have higher SLA than normal APIs because patient safety depends on timely delivery.

---

## Latency (p95)

### API Latency

| Endpoint Type | MVP Target | Production Target |
|---------------|------------|-----------------|
| Simple read (GET) | < 200ms | < 150ms |
| Complex query | < 500ms | < 300ms |
| Write operations | < 300ms | < 200ms |
| Auth endpoints | < 300ms | < 200ms |

### CDS Latency

| Request Type | MVP Target | Production Target |
|-------------|------------|-----------------|
| Simple recommendation | < 5s | < 3s |
| Complex reasoning | < 10s | < 5s |
| Evidence retrieval | < 2s | < 1s |

### Alarm Latency

| Stage | Target |
|-------|--------|
| Device alarm → EREN | < 500ms |
| EREN processing | < 200ms |
| Notification delivery | < 500ms |
| **Total alarm pipeline** | **< 1.5s** |

---

## Scalability

### Current Targets

| Metric | MVP Target | Production Target |
|--------|------------|-----------------|
| Concurrent users | 1,000 | 50,000 |
| Hospitals | 5 | 1,000 |
| Devices connected | 5,000 | 100,000 |
| Events/day | 100,000 | 10,000,000 |
| CDS requests/day | 10,000 | 1,000,000 |

### Note

These are initial estimates. Actual scalability requirements will be measured during MVP and adjusted for production deployment.

---

## Recovery

### Recovery Objectives

| Metric | Target | Definition |
|--------|--------|-----------|
| RTO (Recovery Time Objective) | 15 min | Time to restore service |
| RPO (Recovery Point Objective) | 0 | Maximum acceptable data loss |
| Backup frequency | Every 4 hours | + continuous replication |

### What This Means

- **RTO 15 min**: System must be restorable within 15 minutes of failure
- **RPO 0**: No data loss acceptable (HIPAA requirement)

---

## Security

### Encryption

| Data State | Standard | Notes |
|------------|----------|-------|
| At rest | AES-256 | All PHI, audit logs |
| In transit | TLS 1.3 | All connections |
| Backup | AES-256 | Encrypted backups |

### Authentication

| Requirement | Target |
|------------|--------|
| MFA required | Clinical staff |
| Session timeout | 30 minutes idle |
| Token lifetime | 1 hour |
| Failed login lockout | 5 attempts |

---

## AI Governance

### When AI Can Be Used

| Use Case | AI Allowed? | Requirements |
|----------|------------|-------------|
| CDS Recommendations | ✅ Yes | Evidence required, human review |
| Evidence retrieval | ✅ Yes | Traceability |
| Risk assessment | ✅ Yes | Explainability required |
| Administrative tasks | ✅ Yes | Audit trail |
| Clinical decisions | ❌ No | Only recommendations |

### AI Limitations

```
AI is FOR recommendations.
AI is NOT FOR decisions.
Human clinician always has final authority.
```

### CDS Requirements

| Requirement | Target |
|-------------|--------|
| Evidence required | 100% of recommendations |
| Confidence threshold | Explicit when < 50% |
| Hallucination detection | Required before response |
| Explanation required | Always |
| Alternative options | When available |

### AI Performance Targets

| Metric | Target |
|--------|--------|
| CDS confidence accuracy | > 85% |
| Hallucination rate | < 1% |
| Evidence citation rate | 100% |
| Recommendation acceptance rate | Monitor (no target) |

---

## AI/LLM Targets (EPIC 4-5)

### LLM Latency

| Request Type | MVP Target | Production Target |
|-------------|------------|-------------------|
| Simple CDS recommendation | < 5s | < 3s |
| Complex reasoning (multi-step) | < 10s | < 5s |
| Evidence retrieval (semantic) | < 2s | < 1s |
| Root cause analysis | < 15s | < 10s |
| Failure prediction | < 5s | < 3s |
| Context embedding generation | < 1s | < 500ms |

### LLM Throughput

| Metric | MVP Target | Production Target |
|--------|-----------|-------------------|
| Concurrent CDS requests | 100 | 1,000 |
| CDS requests/minute | 1,000 | 10,000 |
| LLM token budget/day | 10M tokens | 100M tokens |

### LLM Quality

| Metric | Target | Notes |
|--------|--------|-------|
| Hallucination rate | < 1% | Guardrail G5.1 |
| Self-validation pass rate | > 95% | Before response delivery |
| Evidence citation accuracy | > 90% | Sources actually support claims |
| CDS confidence calibration | > 85% | Actual outcomes vs predicted |
| Context truncation rate | < 5% | Due to context window |
| Rate limit impact | < 2% requests | Affected by throttling |

### LLM Context Limits

| Metric | Target |
|--------|--------|
| Max context tokens | 128,000 (configurable per model) |
| Max output tokens | 4,096 per response |
| Memory retrieval items | Top 20 relevant memories |
| Evidence retrieval items | Top 10 relevant sources |

---

## Integration Targets (EPIC 6)

### FHIR Integration

| Metric | MVP Target | Production Target |
|--------|-----------|-------------------|
| FHIR sync latency | < 5s | < 2s |
| FHIR resource validation | 100% | 100% |
| FHIR throughput | 100 resources/min | 1,000 resources/min |
| FHIR sync reliability | > 99% | > 99.9% |

### MQTT Integration

| Metric | MVP Target | Production Target |
|--------|-----------|-------------------|
| MQTT message latency | < 500ms | < 200ms |
| MQTT throughput | 1,000 msgs/s | 10,000 msgs/s |
| Alarm delivery (device → UI) | < 1.5s total | < 1s total |
| MQTT reconnect time | < 5s | < 2s |
| Message loss rate | < 0.1% | < 0.01% |

### HL7 Integration

| Metric | MVP Target | Production Target |
|--------|-----------|-------------------|
| HL7 message processing | < 1s | < 500ms |
| HL7 throughput | 500 messages/min | 5,000 messages/min |
| Buffer capacity | 10,000 messages | 100,000 messages |
| HL7 ack timeout | 30s | 10s |

### Vendor API Integration

| Metric | Target |
|--------|--------|
| Philips API response | < 3s |
| GE API response | < 3s |
| Dräger API response | < 3s |
| Mindray API response | < 3s |
| SAP/ServiceNow/Maximo API | < 5s |
| Vendor API circuit breaker | 5 failures → open |
| Vendor API retry | 3x with exponential backoff |

---

## User Experience Targets (EPIC 7)

### Web Performance

| Metric | Target |
|--------|--------|
| Dashboard load time | < 3s |
| First contentful paint | < 1.5s |
| Time to interactive | < 3s |
| API response (dashboard) | < 500ms (p95) |
| Chat response (streaming) | First token < 1s |

### Mobile Performance

| Metric | Target |
|--------|--------|
| App launch time | < 3s |
| Offline data access | 48 hours minimum |
| Sync on reconnect | < 30s |
| Battery impact | < 5% per hour active use |
| Data usage | < 50MB/month average |

### Accessibility

| Standard | Target |
|----------|--------|
| WCAG 2.1 AA | Required |
| Screen reader support | VoiceOver, NVDA, JAWS |
| Keyboard navigation | Full functionality |
| Color contrast | 4.5:1 minimum |
| Touch targets | 44x44px minimum |
| Response time (accessibility) | < 3s for all operations |

---

## Monitoring & Observability

### Metrics Required

Every capability must expose:

```yaml
- request_count_total
- request_duration_seconds (histogram)
- error_count_total
- active_requests (gauge)

Optional by service:
- cache_hit_rate
- database_query_duration
- external_api_duration
```

### Alerts Required

| Alert | Severity | Condition |
|-------|----------|-----------|
| API latency high | Warning | p95 > target |
| Error rate high | Critical | > 1% errors |
| CDS confidence low | Warning | Average < 70% |
| Alarm delay | Critical | > 5s pipeline |
| Service down | Critical | Health check failed |

---

## Compliance

### Standards

| Standard | Applicability |
|----------|---------------|
| HIPAA | All PHI data |
| IEC 60601 | Medical devices |
| ISO 14971 | Risk management |
| ISO 13485 | Quality management |

### Audit Requirements

| Requirement | Target |
|-------------|--------|
| PHI access logged | 100% |
| Log retention | 7 years (HIPAA) |
| Audit log immutability | Required |
| Access review | Quarterly |

---

## Trade-off Guidelines

When quality attributes conflict, use this hierarchy:

```
Patient Safety > Human Authority > Security > Traceability > Availability > Reliability > Performance
```

**Examples:**

| Conflict | Resolution |
|----------|-----------|
| Fast alarm vs. validated alarm | Validate first (safety) |
| Cached PHI vs. up-to-date | Fetch fresh (accuracy) |
| Performance vs. security | Security (HIPAA) |
| Feature velocity vs. reliability | Reliability (trust) |

---

## Review Schedule

NFRs are reviewed quarterly:
- Q1: January-March
- Q2: April-June
- Q3: July-September
- Q4: October-December

Revisions based on:
- MVP measurements
- Production telemetry
- User feedback
- Regulatory changes

---

*EREN Non-Functional Requirements v1.1*
*Architecture Board - 2026-07-16*
