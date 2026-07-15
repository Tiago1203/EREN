# EREN Consistency Model
## Source of Truth for Every Data Type

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This document defines:
1. Which database is the **source of truth** for each data type
2. How data **synchronizes** between stores
3. What happens when **sync fails**
4. How to handle **conflicts**

---

## Data Stores Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA STORES                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │ POSTGRESQL  │    │   NEO4J    │    │   QDRANT   │   │
│  │             │    │             │    │             │   │
│  │ Source of   │    │ Knowledge   │    │ Embeddings  │   │
│  │ Truth      │    │ Graph       │    │ Semantic    │   │
│  │             │    │             │    │ Search      │   │
│  │ ACID       │    │ Traversal   │    │ Similarity  │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   REDIS    │    │   S3/MINIO │    │ ELASTICSEARCH│   │
│  │             │    │             │    │             │   │
│  │ Sessions    │    │ Documents   │    │ Search      │   │
│  │ Cache      │    │ Reports     │    │ Logs       │   │
│  │ Rate Limit │    │ Backups    │    │ Audit      │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Source of Truth Matrix

### Clinical Domain

| Data Type | Source of Truth | Sync Strategy | Sync Frequency |
|-----------|-----------------|---------------|----------------|
| Patient | PostgreSQL | → Neo4j (patient node) | Immediate (transactional) |
| Diagnosis | PostgreSQL | → Neo4j (diagnosis edges) | Immediate |
| Treatment | PostgreSQL | → Neo4j (treatment nodes) | Immediate |
| Medication | PostgreSQL | → Neo4j (medication nodes) | Immediate |
| Vital Signs | PostgreSQL | → Redis (latest) | Immediate |
| Lab Results | PostgreSQL | → Neo4j (lab edges) | Immediate |
| Clinical Document | PostgreSQL + S3 | S3 for blob | Async |

### Biomedical Domain

| Data Type | Source of Truth | Sync Strategy | Sync Frequency |
|-----------|-----------------|---------------|----------------|
| Device | PostgreSQL | → Neo4j (device relationships) | Immediate |
| Calibration | PostgreSQL | → Neo4j (calibration history) | Immediate |
| Maintenance | PostgreSQL | → Neo4j (maintenance graph) | Immediate |
| Alarm | PostgreSQL (immutable) | → Redis (active) | Immediate |
| Work Order | PostgreSQL | → Neo4j (workflow graph) | Immediate |

### Hospital Domain

| Data Type | Source of Truth | Sync Strategy | Sync Frequency |
|-----------|-----------------|---------------|----------------|
| Bed | PostgreSQL | → Redis (status cache) | Immediate |
| Room | PostgreSQL | → Redis (occupancy) | Immediate |
| Staff | PostgreSQL | → Redis (availability) | Immediate |
| Schedule | PostgreSQL | → Redis (today only) | On-change |
| Inventory | PostgreSQL | → Redis (alerts) | On-change |

### Security Domain

| Data Type | Source of Truth | Sync Strategy | Sync Frequency |
|-----------|-----------------|---------------|----------------|
| Principal | PostgreSQL | → Redis (lookup cache) | On-change |
| Session | PostgreSQL | → Redis (active sessions) | Immediate |
| Role | PostgreSQL | → Redis (permissions) | On-change |
| Audit Log | PostgreSQL (append-only) | → Elasticsearch (search) | Batched (1 min) |

### Cognitive Domain

| Data Type | Source of Truth | Sync Strategy | Sync Frequency |
|-----------|-----------------|---------------|----------------|
| Knowledge Graph | Neo4j | ← PostgreSQL (primary) | Immediate |
| Embeddings | Qdrant | ← Knowledge Graph | On-demand |
| Trust Scores | PostgreSQL | Cache → Redis | Immediate |
| Reasoning History | PostgreSQL | → Elasticsearch | Batched |

---

## Synchronization Patterns

### Pattern 1: Transactional Sync (Primary → Secondary)

```
Used for: Patient, Diagnosis, Treatment, Device

PostgreSQL (Primary)
      │
      │ BEGIN TRANSACTION
      │ INSERT patient
      │ COMMIT
      │
      ▼ (async, guaranteed delivery)
Neo4j
      │
      │ MERGE (patient {id})
      │ SET properties
      │ CREATE relationships
```

**Guarantees:**
- ✅ PostgreSQL always has correct data
- ✅ Neo4j eventually consistent
- ✅ If Neo4j fails, PostgreSQL is unaffected
- ✅ Retry mechanism for Neo4j sync

---

### Pattern 2: Cache-Aside (Read-Heavy)

```
Used for: Sessions, Latest Vitals, Rate Limits

READ:
  ┌──────────┐
  │ Request   │
  └────┬─────┘
       ↓
  ┌────▼─────┐    Cache Hit?
  │  Redis   │──────────→ Return cached data
  └────┬─────┘
       │ Cache Miss
       ↓
  ┌────▼─────┐
  │PostgreSQL│──→ Return data, cache it
  └──────────┘

WRITE:
  ┌──────────┐
  │ Request   │
  └────┬─────┘
       ↓
  ┌────▼─────┐
  │PostgreSQL│ (source of truth)
  └────┬─────┘
       ↓
  ┌────▼─────┐
  │  Redis   │ (invalidate cache)
  └──────────┘
```

**Guarantees:**
- ✅ Reads are fast (cache)
- ✅ Writes are consistent (PostgreSQL)
- ✅ Cache misses trigger rebuild

---

### Pattern 3: Write-Behind (High-Volume)

```
Used for: Audit Logs, Metrics, Search Index

Write Path:
  ┌──────────┐
  │ Request   │
  └────┬─────┘
       ↓
  ┌────▼─────┐
  │PostgreSQL│ (primary, immutable)
  └──────────┘
       │
       │ Async batch
       ▼
  ┌─────────────┐
  │Elasticsearch│ (searchable)
  └─────────────┘
```

**Guarantees:**
- ✅ Write is fast (primary only)
- ✅ Elasticsearch eventually consistent
- ✅ If ES fails, PostgreSQL is safe

---

### Pattern 4: Materialized View (Read Optimization)

```
Used for: Patient Dashboard, Device Status, Capacity View

PostgreSQL (Source)
      │
      │ Scheduled refresh (1 min)
      ▼
  ┌─────────────┐
  │ Redis       │ (aggregated view)
  │             │ - patient_count
  │             │ - bed_occupancy
  │             │ - active_alarms
  └─────────────┘
       │
       │ Fast reads
       ▼
  ┌─────────────┐
  │   Dashboard  │
  └─────────────┘
```

---

## Conflict Resolution

### When Conflicts Happen

```
Scenario: Neo4j sync fails for 5 minutes
         PostgreSQL gets 3 patient updates
         Neo4j is now inconsistent

Timeline:
T0: Patient name = "John"
T1: Update → "John A" (PostgreSQL ✓, Neo4j ✗)
T2: Update → "John B" (PostgreSQL ✓, Neo4j ✗)
T3: Neo4j comes back online
T4: Resync runs from PostgreSQL
T5: Neo4j = "John B" ✓ (matches PostgreSQL)
```

### Resolution Strategy: Last-Write-Wins

```
PostgreSQL is ALWAYS the source of truth.
Neo4j resyncs from PostgreSQL on failure.

No conflict resolution needed.
Neo4j is derived, not authoritative.
```

### Exception: Graph-Specific Conflicts

```
When: Neo4j has relationships that don't exist in PostgreSQL
Then: PostgreSQL wins
      Neo4j orphan relationships are deleted during resync
```

---

## Failure Handling

### When Neo4j Fails

```
Impact: Knowledge Graph unavailable

Response:
1. Capabilities continue working (PostgreSQL is source)
2. Graph queries return "unavailable" or cached results
3. Alerts fire: "Neo4j degraded"
4. No data is lost (PostgreSQL has everything)
5. Auto-recovery: When Neo4j comes back, resync runs

Recovery Time: < 5 minutes typically
Data Loss: None (PostgreSQL is safe)
```

### When Redis Fails

```
Impact: Cache unavailable, sessions at risk

Response:
1. Fallback to PostgreSQL for reads (slower but works)
2. Sessions continue (PostgreSQL has session data)
3. Rate limiting disabled (fail open for availability)
4. Alerts fire: "Redis degraded"

Recovery Time: < 1 minute (Redis restarts fast)
User Impact: Slower reads, no data loss
```

### When Qdrant Fails

```
Impact: Semantic search unavailable

Response:
1. Fallback to PostgreSQL full-text search
2. Embedding generation continues (Qdrant is write-only for this)
3. Search uses simpler algorithm
4. Alerts fire: "Vector search degraded"

Recovery Time: < 5 minutes
User Impact: Less accurate search, no data loss
```

### When PostgreSQL Fails

```
Impact: CRITICAL - System is down

Response:
1. All write operations fail
2. Read operations fail (no cache fallback for primary)
3. Alert fires: "CRITICAL - Database unavailable"
4. Escalation: On-call DBA
5. Recovery: PostgreSQL failover or restore

Recovery Time: Depends on backup strategy (15 min - 4 hours)
User Impact: Full system outage
```

---

## Data Flow Examples

### Example 1: Patient Update

```
Request: Update patient name to "John Smith"

┌─────────────────────────────────────────────────────────────┐
│ STEP 1: PostgreSQL (Source of Truth)                      │
│                                                              │
│ UPDATE patients SET name = 'John Smith', updated_at = NOW() │
│ WHERE patient_id = '123' AND tenant_id = 'hospital-abc'    │
│                                                              │
│ ✓ Transaction committed                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Neo4j Sync (Async)                                 │
│                                                              │
│ MERGE (p:Patient {patient_id: '123'})                     │
│ SET p.name = 'John Smith', p.updated_at = TIMESTAMP()     │
│                                                              │
│ ✓ Graph updated                                             │
│ ✗ If fails → Resync on recovery                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Redis Cache (Invalidate)                          │
│                                                              │
│ DEL patient:123                                            │
│                                                              │
│ ✓ Next read rebuilds cache                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Audit Log                                          │
│                                                              │
│ INSERT INTO audit_logs (event_type, patient_id, ...)       │
│ VALUES ('patient.updated', '123', ...)                      │
│                                                              │
│ ✓ Immutable audit trail created                            │
└─────────────────────────────────────────────────────────────┘
```

### Example 2: Device Alarm

```
Event: Monitor shows critical alarm for patient in bed 204

┌─────────────────────────────────────────────────────────────┐
│ STEP 1: MQTT Event Received                                 │
│                                                              │
│ Device publishes: {"alarm": "critical", "device_id": "M-01" │
│                     "patient_id": "P-123", "bed_id": "204"} │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Validation & Transformation                        │
│                                                              │
│ Validate schema                                             │
│ Enrich with device metadata                                  │
│ Enrich with patient context                                 │
│ Convert to DeviceAlarm event                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Audit Log (First Priority)                         │
│                                                              │
│ INSERT INTO audit_logs (event_type, device_alarm, ...)     │
│ VALUES ('device.alarm.critical', ...)                       │
│                                                              │
│ ✓ EXACTLY ONCE delivery                                    │
│ ✓ HIPAA required                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌────────┴────────┐
                    ▼                 ▼
        ┌───────────────────┐ ┌───────────────────┐
        │ PostgreSQL        │ │ Redis             │
        │ (Alarm record)     │ │ (Active alarms)   │
        │ EXACTLY ONCE       │ │ AT LEAST ONCE     │
        └───────────────────┘ └───────────────────┘
                    │                 │
                    ▼                 ▼
        ┌───────────────────┐ ┌───────────────────┐
        │ Clinical Alert    │ │ Nurse Dashboard   │
        │ Processing         │ │ (real-time)       │
        └───────────────────┘ └───────────────────┘
```

### Example 3: Embedding Generation

```
Request: Add document to knowledge base

┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Document Stored                                    │
│                                                              │
│ PostgreSQL: INSERT INTO documents (id, content, ...)       │
│ S3: PUT document.pdf                                       │
│                                                              │
│ ✓ Source of truth created                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Embedding Generated                                │
│                                                              │
│ LLM generates embedding vector                              │
│ Qdrant upsert (id, vector, payload)                        │
│                                                              │
│ ✓ Semantic search ready                                     │
│ ✗ If fails → Background retry queue                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Neo4j Relationships                                │
│                                                              │
│ MERGE (d:Document {id: 'doc-123'})                       │
│ MERGE (p:Patient {id: 'P-456'})                           │
│ CREATE (d)-[:ABOUT]->(p)                                  │
│                                                              │
│ ✓ Knowledge graph enriched                                  │
│ ✗ If fails → Resync on recovery                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Recovery Procedures

### Neo4j Recovery

```python
async def resync_neo4j_from_postgresql():
    """Resync Neo4j from PostgreSQL source of truth."""
    
    # 1. Pause incoming Neo4j writes
    await pause_neo4j_sync()
    
    # 2. Identify last sync point
    last_sync = await get_last_sync_timestamp("neo4j")
    
    # 3. Fetch changes since last sync
    changes = await postgres.fetch_changes_since(last_sync)
    
    # 4. Apply to Neo4j in batches
    for batch in chunk(changes, 1000):
        await neo4j.apply_batch(batch)
    
    # 5. Verify integrity
    await verify_graph_integrity()
    
    # 6. Resume sync
    await resume_neo4j_sync()
```

### Redis Recovery

```python
async def recover_redis():
    """Recover Redis from PostgreSQL."""
    
    # 1. Check what's missing
    missing_keys = await identify_missing_cache_keys()
    
    # 2. Rebuild critical caches
    #    - Sessions
    #    - Active alarms
    #    - Rate limits
    for key in critical_keys:
        await rebuild_cache(key)
    
    # 3. Other caches rebuild on-demand (cache-aside)
```

---

## Consistency Guarantees Summary

| Scenario | PostgreSQL | Neo4j | Redis | Qdrant |
|----------|-----------|-------|-------|---------|
| Primary failure | N/A | Resync | Rebuild | Rebuild |
| Secondary failure | Safe | Safe | Safe | Safe |
| Sync delay | Instant | < 1 sec | < 100ms | < 10 sec |
| Data loss on failure | 0 | 0 | Possible | Possible |
| Consistency model | Strong | Eventual | Eventual | Eventual |

---

## Key Principles

```
1. PostgreSQL is ALWAYS source of truth
2. All other stores are derived
3. Sync failures never lose data (PostgreSQL is safe)
4. Read operations gracefully degrade
5. Write operations require PostgreSQL
6. Neo4j, Redis, Qdrant are optimizations, not requirements
```

---

*EREN Consistency Model v1.0*
*Architecture Board - 2026-07-15*
