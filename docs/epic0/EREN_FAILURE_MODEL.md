# EREN Failure Model
## How EREN Responds to Failures

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This document defines:
1. How EREN responds when **infrastructure fails**
2. How EREN responds when **integrations fail**
3. How EREN responds when **AI models fail**
4. **Recovery procedures** for each failure mode

---

## Failure Classification

### By Severity

| Severity | Impact | Response Time | Examples |
|-----------|--------|---------------|----------|
| **P0 - Critical** | System unusable | Immediate | PostgreSQL down, Auth down |
| **P1 - High** | Major feature broken | < 5 min | Neo4j down, FHIR sync failing |
| **P2 - Medium** | Degraded experience | < 30 min | Redis down, search slow |
| **P3 - Low** | Minor issue | < 4 hours | Metrics delayed, logs missing |

### By Domain

```
INFRASTRUCTURE FAILURES
├── Database (PostgreSQL)
├── Cache (Redis)
├── Graph (Neo4j)
├── Vector Store (Qdrant)
└── Storage (S3)

INTEGRATION FAILURES
├── FHIR Server
├── HL7 Interface
├── MQTT Broker
├── DICOM PACS
└── External APIs

AI/ML FAILURES
├── LLM Timeout
├── LLM Error
├── Embedding Service Down
├── Model Unavailable
└── Hallucination Detected

SECURITY FAILURES
├── Auth Provider Down
├── Token Expired
├── Rate Limit Exceeded
└── Intrusion Detected
```

---

## Infrastructure Failures

### PostgreSQL Failure

```
Severity: P0 - CRITICAL
Impact: System is unusable

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  All write operations FAIL                                  │
│  All read operations FAIL                                  │
│  No transaction can commit                                 │
│  Sessions cannot be validated                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "CRITICAL - PostgreSQL unavailable"
2. All capabilities return: ServiceUnavailableError
3. No graceful degradation (PostgreSQL is source of truth)
4. Health check returns: unhealthy
5. On-call escalation triggered

RECOVERY:
1. DBA addresses PostgreSQL issue (failover, restore)
2. Health check recovers
3. Capabilities resume
4. No data loss (PostgreSQL was safe)

RTO: Depends on infrastructure (15 min - 4 hours)
RPO: Zero (no data loss)
```

### Redis Failure

```
Severity: P1 - HIGH
Impact: Cache unavailable, sessions at risk

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Cache misses → direct to PostgreSQL                       │
│  Session lookup → PostgreSQL                              │
│  Rate limiting → DISABLED (fail open)                     │
│  Active alarms cache → empty                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "Redis degraded"
2. Capabilities fall back to PostgreSQL (slower)
3. Rate limiting disabled for availability
4. Sessions continue via PostgreSQL
5. Dashboard slower (rebuilding cache)

GRACEFUL DEGRADATION:
✅ System continues operating
✅ Users experience slower response times
✅ No data loss
❌ Rate limiting temporarily disabled

RECOVERY:
1. Redis recovers (typically < 1 minute)
2. Cache rebuilds automatically
3. Rate limiting re-enabled

RTO: < 1 minute
RPO: Zero (no data in Redis is source of truth)
```

### Neo4j Failure

```
Severity: P1 - HIGH
Impact: Knowledge graph unavailable

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Graph queries FAIL                                         │
│  Relationship traversal unavailable                        │
│  Knowledge-based reasoning limited                          │
│  Semantic search continues (Qdrant)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "Neo4j degraded"
2. Graph queries return: "Knowledge graph unavailable"
3. Reasoning uses flat data only (no relationships)
4. Capabilities continue (PostgreSQL is source)

GRACEFUL DEGRADATION:
✅ Clinical decisions continue (PostgreSQL)
✅ Device management continues (PostgreSQL)
❌ Relationship-based queries unavailable
❌ Graph traversal reasoning limited

RECOVERY:
1. Neo4j recovers or failover
2. Resync runs from PostgreSQL
3. Graph queries resume

RTO: < 5 minutes
RPO: Zero (PostgreSQL has all data)
```

### Qdrant Failure

```
Severity: P2 - MEDIUM
Impact: Semantic search unavailable

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Semantic search FAILS                                      │
│  Embedding generation continues                             │
│  Full-text search continues (PostgreSQL)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "Vector search degraded"
2. Semantic search falls back to PostgreSQL full-text
3. Embeddings continue generating (buffered)
4. RAG uses keyword search only

GRACEFUL DEGRADATION:
✅ System continues
✅ Keyword search available
❌ Semantic similarity unavailable
❌ Lower search quality

RECOVERY:
1. Qdrant recovers
2. Embeddings bulk-loaded
3. Semantic search resumes

RTO: < 5 minutes
RPO: Zero (Qdrant is write-only from EREN)
```

---

## Integration Failures

### FHIR Server Failure

```
Severity: P1 - HIGH
Impact: EHR integration broken

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  FHIR reads FAIL                                           │
│  FHIR writes FAIL                                          │
│  Patient data from EHR unavailable                         │
│  Local PostgreSQL data still available                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "FHIR server unavailable"
2. FHIR operations return: FHIRUnavailableError
3. Local cache serves stale data (with warning)
4. Write operations queued for retry

GRACEFUL DEGRADATION:
✅ EREN continues with local data
✅ Clinical operations continue
✅ Patient care unaffected
❌ Latest EHR data unavailable
❌ FHIR sync disabled

WHEN FHIR RETURNS:
1. Sync resumes automatically
2. Cached data updated
3. Queued writes transmitted

RECOVERY:
1. FHIR server recovers
2. Sync catches up
3. Stale flag cleared
```

### HL7 Interface Failure

```
Severity: P2 - MEDIUM
Impact: Real-time HL7 messages lost

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  HL7 messages accumulate in buffer                          │
│  Real-time vitals STOP updating                            │
│  Batch sync continues                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "HL7 interface degraded"
2. Buffer fills (capacity: 10,000 messages)
3. If buffer full: oldest messages dropped (with warning)
4. Batch sync uses last known good state

GRACEFUL DEGRADATION:
✅ Batch operations continue
✅ Last known values displayed
❌ Real-time updates delayed
❌ Latest vitals unavailable

RECOVERY:
1. HL7 interface recovers
2. Buffer drains
3. Real-time updates resume
```

### MQTT Broker Failure

```
Severity: P1 - HIGH
Impact: Device connectivity lost

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Device telemetry STOPS                                     │
│  Device alarms NOT received                                 │
│  Local buffering on devices                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "MQTT broker unavailable"
2. Devices attempt reconnect (exponential backoff)
3. Active alarms cleared after timeout (safety concern)
4. Fallback: Devices poll REST API if available

SAFETY PROTOCOL:
⚠️ CRITICAL ALARMS: 
   - If MQTT down > 5 minutes
   - All devices marked as "communication lost"
   - Central monitoring alert

RECOVERY:
1. MQTT broker recovers
2. Devices reconnect
3. Buffered data transmitted
4. Alarm status verified
```

### DICOM PACS Failure

```
Severity: P2 - MEDIUM
Impact: Medical imaging unavailable

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  New images NOT received                                   │
│  Image retrieval FAILS                                     │
│  Viewer integration broken                                 │
│  Local cache serves existing images                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "PACS unavailable"
2. Image access returns: PACSUnavailableError
3. Cached images still viewable
4. New studies queued

GRACEFUL DEGRADATION:
✅ Existing images viewable
❌ New imaging unavailable
❌ Study compare limited

RECOVERY:
1. PACS recovers
2. Queued studies transferred
3. Normal operation resumes
```

---

## AI/ML Failures

### LLM Timeout

```
Severity: P1 - HIGH
Impact: Reasoning delayed/failed

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  LLM request exceeds timeout (10 seconds default)           │
│  Response NOT received                                      │
│  Request is cancelled                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Timeout triggers
2. Fallback initiated
3. Response marked: confidence = LOW
4. Explanation: "LLM timed out"

FALLBACK CHAIN:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Request                                                   │
│     ↓                                                      │
│  Try: OpenAI GPT-4                                        │
│     ↓ Timeout (10s)                                        │
│  Try: Anthropic Claude                                     │
│     ↓ Timeout (10s)                                        │
│  Try: Local LLM (if configured)                            │
│     ↓ Timeout (30s)                                        │
│  Try: Rule-based response                                   │
│     ↓ Fallback                                            │
│  Return: "Unable to process request"                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

RECOVERY:
1. LLM responds
2. Normal operation resumes
3. Timeout logged for monitoring
```

### LLM Error (Non-Timeout)

```
Severity: P1 - HIGH
Impact: Reasoning failed

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  LLM returns error (500, 503, auth failure, etc.)          │
│  No response received                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Error detected
2. Retry with exponential backoff
3. If retry fails: Fallback to rule-based
4. Response marked: confidence = VERY_LOW
5. Alert fires: "LLM error"

RETRY CONFIG:
├── Max retries: 3
├── Backoff: 1s, 2s, 4s
├── Total max wait: 7 seconds
└── After retries: Fallback response
```

### Embedding Service Failure

```
Severity: P2 - MEDIUM
Impact: New embeddings unavailable

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  New documents CANNOT be embedded                           │
│  Semantic search UNCHANGED (existing embeddings)             │
│  Batch processing paused                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "Embedding service degraded"
2. Document storage continues (PostgreSQL)
3. Embedding queued for later
4. Search uses existing embeddings only

GRACEFUL DEGRADATION:
✅ System continues
✅ Existing knowledge available
❌ New knowledge not searchable
❌ Knowledge graph not updated

RECOVERY:
1. Embedding service recovers
2. Queued embeddings processed
3. Full search resumes
```

### Hallucination Detected

```
Severity: P1 - HIGH
Impact: Potentially incorrect information

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  EREN generates response without evidence                   │
│  Hallucination detector flags response                      │
│  Response contains unverified claims                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE (GUARDRAIL G5.1):
1. Hallucination detected by validation layer
2. Response is BLOCKED
3. User sees: "I cannot provide that information"
4. Request logged: potential hallucination
5. Alert fires: "Hallucination blocked"

RESPONSE TO USER:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  "I don't have sufficient evidence to answer that question.  │
│   I cannot provide information without verified sources.    │
│   Please consult [appropriate resource]."                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

PHILOSOPHY ENFORCED:
✅ "EREN never fabricates clinical information"
✅ "EREN always shows evidence"
```

---

## Security Failures

### Auth Provider Failure

```
Severity: P0 - CRITICAL
Impact: Login impossible

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Login attempts FAIL                                        │
│  Token verification FAILS                                   │
│  Existing sessions may become invalid                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. Alert fires: "Authentication service unavailable"
2. Login blocked
3. Existing sessions: Continue with cached validation
4. Emergency access: Requires approval

EMERGENCY PROTOCOL:
⚠️ If auth down > 15 minutes:
   - Emergency access procedure initiated
   - Requires: Department head approval
   - Audit: Every emergency access logged
   - Review: Post-incident review required
```

### Rate Limit Exceeded

```
Severity: P3 - LOW
Impact: Request rejected

WHAT HAPPENS:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  User exceeds rate limit                                    │
│  Request rejected                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EREN RESPONSE:
1. HTTP 429 returned
2. Retry-After header included
3. Logged for monitoring
4. User sees: "Please wait before retrying"
```

---

## Failure Response Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                         FAILURE RESPONSE MATRIX                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COMPONENT          │ SEVERITY │ BEHAVIOR          │ RECOVERY         │
│ ───────────────────┼──────────┼───────────────────┼─────────────────── │
│  PostgreSQL         │ P0      │ Full outage       │ Failover/restore │
│  Redis              │ P1      │ Degraded          │ Auto-reconnect    │
│  Neo4j              │ P1      │ Degraded          │ Resync            │
│  Qdrant             │ P2      │ Degraded          │ Auto-reconnect    │
│  FHIR Server        │ P1      │ Local fallback     │ Auto-retry       │
│  HL7 Interface      │ P2      │ Buffered          │ Auto-retry       │
│  MQTT Broker        │ P1      │ Safety alerts     │ Reconnect        │
│  DICOM PACS         │ P2      │ Cached fallback   │ Auto-retry       │
│  LLM Provider       │ P1      │ Fallback chain    │ Retry + fallback  │
│  Embedding Service  │ P2      │ Queued           │ Auto-retry       │
│  Auth Provider      │ P0      │ Cached sessions   │ Emergency access │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Circuit Breaker Pattern

### When to Use

```
Circuit Breaker is used for:
✅ External API calls (FHIR, LLM)
✅ Integration calls (MQTT, HL7)
✅ Third-party services

Circuit Breaker is NOT used for:
❌ Internal calls (PostgreSQL, Redis)
❌ Data stores (these fail-over differently)
❌ Critical paths (should fail, not circuit break)
```

### Configuration

```python
class CircuitBreakerConfig:
    """Circuit breaker for external integrations."""
    
    # FHIR
    FHIR: CircuitBreaker = CircuitBreaker(
        failure_threshold=5,      # Open after 5 failures
        recovery_timeout=30,      # Try again after 30s
        half_open_max_calls=3,   # Allow 3 test calls
    )
    
    # LLM
    LLM: CircuitBreaker = CircuitBreaker(
        failure_threshold=3,     # Open after 3 failures
        recovery_timeout=60,      # Try again after 60s
        half_open_max_calls=1,   # Allow 1 test call
    )
    
    # MQTT
    MQTT: CircuitBreaker = CircuitBreaker(
        failure_threshold=10,    # More tolerant
        recovery_timeout=15,     # Quick recovery
        half_open_max_calls=5,
    )
```

### States

```
CLOSED (Normal)
├── Failures counted
├── Threshold reached → OPEN
└── All calls pass through

OPEN (Failing)
├── All calls fail immediately
├── Timeout reached → HALF_OPEN
└── Alert: "Circuit breaker OPEN"

HALF_OPEN (Testing)
├── Limited calls pass through
├── Success → CLOSED
└── Failure → OPEN
```

---

## Health Checks

### Component Health Model

```python
@dataclass
class ComponentHealth:
    """Health status for a component."""
    
    component: str
    status: HealthStatus  # HEALTHY, DEGRADED, UNHEALTHY
    
    # Health indicators
    can_accept_requests: bool
    can_complete_requests: bool
    dependencies_healthy: dict[str, bool]
    
    # Metrics
    latency_p50_ms: float
    latency_p95_ms: float
    error_rate_percent: float
    
    # Timestamps
    last_check: datetime
    last_failure: datetime | None
```

### Health Check Implementation

```python
async def check_component_health(
    component: str,
    check_function: Callable,
) -> ComponentHealth:
    """Check health of a component."""
    
    try:
        start = datetime.now()
        result = await asyncio.wait_for(check_function(), timeout=5)
        latency = (datetime.now() - start).total_seconds() * 1000
        
        return ComponentHealth(
            component=component,
            status=HealthStatus.HEALTHY,
            can_accept_requests=True,
            can_complete_requests=True,
            latency_p50_ms=latency,
            error_rate_percent=0,
            last_check=datetime.now(),
        )
        
    except TimeoutError:
        return ComponentHealth(
            component=component,
            status=HealthStatus.DEGRADED,
            can_accept_requests=True,
            can_complete_requests=False,
            latency_p50_ms=5000,
            error_rate_percent=100,
            last_failure=datetime.now(),
        )
        
    except Exception as e:
        return ComponentHealth(
            component=component,
            status=HealthStatus.UNHEALTHY,
            can_accept_requests=False,
            can_complete_requests=False,
            error_rate_percent=100,
            last_failure=datetime.now(),
        )
```

---

## Alerting

### Alert Definitions

```yaml
alerts:
  # Critical - Immediate response
  - name: postgresql_down
    severity: critical
    condition: postgresql.status == unhealthy
    notification: [pagerduty, slack-critical]
    auto_ resolve: false
  
  - name: auth_provider_down
    severity: critical
    condition: auth.status == unhealthy
    notification: [pagerduty, slack-critical]
    auto_resolve: false
  
  # High - Response within 5 minutes
  - name: redis_down
    severity: high
    condition: redis.status == unhealthy
    notification: [slack-high]
    auto_resolve: true
  
  - name: llm_error_rate_high
    severity: high
    condition: llm.error_rate > 10%
    notification: [slack-high]
    auto_resolve: true
  
  # Medium - Response within 30 minutes
  - name: vector_search_degraded
    severity: medium
    condition: qdrant.status == degraded
    notification: [slack-ops]
    auto_resolve: true
  
  # Low - Response within 4 hours
  - name: metrics_delayed
    severity: low
    condition: metrics.age > 5min
    notification: [slack-ops]
    auto_resolve: true
```

---

## Runbooks

### Runbook: PostgreSQL Failure

```markdown
# PostgreSQL Failure Runbook

## Immediate (< 5 minutes)
1. Check PostgreSQL status
2. Check connection pool status
3. Check disk space
4. Check replication status

## If Primary Down
1. Trigger failover to replica
2. Promote replica to primary
3. Update connection string
4. Verify writes succeeding

## If Replica Lagging
1. Check network between primary and replica
2. Check disk I/O on replica
3. If persistent: Provision new replica

## Post-Incident
1. Root cause analysis
2. Update monitoring
3. Document lessons learned
```

### Runbook: LLM Failure

```markdown
# LLM Failure Runbook

## Immediate (< 5 minutes)
1. Check LLM provider status page
2. Check EREN error logs
3. Verify API keys valid

## If Provider Down
1. Switch to fallback provider
2. Update provider priority in config
3. Monitor fallback performance

## If Rate Limited
1. Check request volume
2. Implement request queuing
3. Consider rate limit increase

## Post-Incident
1. Contact provider support
2. Document incident
3. Update fallback chain if needed
```

---

*EREN Failure Model v1.0*
*Architecture Board - 2026-07-15*
