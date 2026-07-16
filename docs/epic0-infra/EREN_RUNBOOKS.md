# EREN Operational Runbooks
## Step-by-Step Procedures for Common Operations

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This document provides step-by-step operational runbooks for common scenarios in EREN's daily operations. Each runbook includes: symptoms, impact, procedure, and verification steps.

---

## Runbook Index

| ID | Title | Severity | Time to Resolve |
|----|-------|----------|----------------|
| RB-001 | PostgreSQL High CPU | P1 | 15 min |
| RB-002 | Kafka Consumer Lag | P1 | 30 min |
| RB-003 | Redis Unavailable | P1 | 15 min |
| RB-004 | Outbox Events Failing | P1 | 30 min |
| RB-005 | CDS Service Degradation | P1 | 30 min |
| RB-006 | Multi-Tenant Isolation Breach | P0 | Immediate |
| RB-007 | LLM Provider Down | P1 | 20 min |
| RB-008 | New Tenant Onboarding | P2 | 30 min |
| RB-009 | Database Backup Failure | P2 | 1 hour |
| RB-010 | SSL Certificate Renewal | P2 | 30 min |

---

## RB-001: PostgreSQL High CPU

### Symptoms
- Prometheus: `pg_stat_activity` count > 100 connections
- Prometheus: CPU > 90% on PostgreSQL pods
- Slow API response times (> 5s)
- Lock waits visible in `pg_locks`

### Impact
- API latency increase for all tenants
- Potential timeouts

### Procedure

```bash
# 1. Identify the cause
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT pid, usename, application_name, state, wait_event_type, wait_event, query
  FROM pg_stat_activity
  WHERE state != 'idle'
  ORDER BY query_start;
"

# 2. Check for long-running queries
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT pid, now() - query_start AS duration, state, query
  FROM pg_stat_activity
  WHERE state = 'active' AND now() - query_start > interval '5 minutes'
  ORDER BY duration DESC;
"

# 3. Check for lock contention
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT blocked.pid, blocked.query, blocking.pid AS blocker, blocking.query
  FROM pg_stat_activity blocked
  JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
  WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0;
"

# 4. If lock contention: terminate the blocking query
# (Replace PID with actual value from step 3)
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT pg_terminate_backend(PID_FROM_STEP_3);
"

# 5. If slow queries: check for missing indexes
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT schemaname, tablename, seq_scan, idx_scan,
         pg_size_pretty(pg_relation_size(schemaname||'.'||tablename))
  FROM pg_stat_user_tables
  WHERE seq_scan > idx_scan * 10
  ORDER BY seq_scan - idx_scan DESC;
"

# 6. Scale PostgreSQL (if persistent)
kubectl patch postgresql eren-postgres -n eren-infra \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/resources/requests/cpu", "value": "2"}]'
```

### Verification
- [ ] CPU < 70% on PostgreSQL
- [ ] API P95 latency < 2s
- [ ] No blocked queries

---

## RB-002: Kafka Consumer Lag

### Symptoms
- Prometheus: `kafka_consumer_lag_consumer_group_topic_partition` > 10,000
- CDS recommendations delayed
- Alarm delivery delayed

### Impact
- CDS recommendations delayed (P1 if > 1 minute)
- Alarm delivery delayed (P1 if > 5 minutes)

### Procedure

```bash
# 1. Identify which consumer group is lagging
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --list

# 2. Check lag per topic
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group eren-worker-clinical \
  --describe

# 3. Check for consumer crashes
kubectl get pods -n eren-production | grep worker

# 4. Restart stuck consumers
kubectl rollout restart deployment/eren-worker -n eren-production

# 5. If lag persists, check if Kafka broker is overloaded
kubectl top pod -n eren-infra | grep kafka

# 6. Scale workers (if needed)
kubectl scale deployment/eren-worker -n eren-production --replicas=6

# 7. If partition count is bottleneck, increase partitions
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic eren-clinical.cds.recommendations \
  --partitions 12
```

### Verification
- [ ] Consumer lag < 1,000 messages
- [ ] CDS latency < 5s
- [ ] No consumer group in ERROR state

---

## RB-003: Redis Unavailable

### Symptoms
- `RedisConnectionError` in API logs
- Rate limiting disabled
- Session errors in UI

### Impact
- Rate limiting disabled (all requests allowed)
- Session errors (users may be logged out)

### Procedure

```bash
# 1. Check Redis pod status
kubectl get pods -n eren-infra | grep redis

# 2. Check Redis logs
kubectl logs -n eren-infra redis-0 --tail=100

# 3. If OOM: check memory usage
kubectl exec -it redis-0 -n eren-infra -- redis-cli info memory

# 4. If replica lag: check replication
kubectl exec -it redis-0 -n eren-infra -- redis-cli info replication

# 5. Restart Redis (if unresponsive)
kubectl delete pod redis-0 -n eren-infra

# 6. Scale Redis (if persistent load)
kubectl scale statefulset redis -n eren-infra --replicas=3
```

### Verification
- [ ] `redis-cli ping` returns PONG
- [ ] Rate limiting active
- [ ] No session errors in logs

---

## RB-004: Outbox Events Failing

### Symptoms
- Events not appearing in Kafka topics
- DLQ filling up
- `OutboxPublishError` alerts

### Impact
- Downstream services not receiving events
- CDS recommendations not triggering

### Procedure

```bash
# 1. Check outbox DLQ size
kubectl exec -it eren-worker-0 -n eren-production -- \
  python -c "
  from eren.infrastructure.database import get_pool
  import asyncio
  async def check():
    pool = await get_pool()
    async with pool.acquire() as conn:
      dlq_count = await conn.fetchval(
        \"SELECT COUNT(*) FROM outbox_events_dlq WHERE created_at > NOW() - INTERVAL '24 hours'\"
      )
      print(f'DLQ events in last 24h: {dlq_count}')
  asyncio.run(check())
  "

# 2. Check Kafka connectivity from workers
kubectl exec -it eren-worker-0 -n eren-production -- \
  python -c "
  from kafka import KafkaProducer
  import os
  producer = KafkaProducer(
    bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'].split(',')
  )
  producer.close()
  print('Kafka connection OK')
  "

# 3. Check outbox publisher task is running
kubectl get pods -n eren-production | grep beat

# 4. Manually retry DLQ events
kubectl exec -it eren-worker-0 -n eren-production -- \
  python -c "
  from eren.worker.tasks.outbox import retry_dlq
  retry_dlq.delay(batch_size=100)
  "

# 5. If persistent, check schema compatibility
kubectl exec -it kafka-0 -n eren-infra -- \
  kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic eren-clinical.events
```

### Verification
- [ ] DLQ size decreasing
- [ ] Events appearing in Kafka topics
- [ ] No new OutboxPublishError alerts

---

## RB-005: CDS Service Degradation

### Symptoms
- CDS latency > 10s
- CDS fallback mode active
- `CDSRecommendationFallback` events in logs

### Impact
- Slower clinical decision support
- Lower quality recommendations (rule-based fallback)

### Procedure

```bash
# 1. Check LLM provider health
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --max-time 5

# 2. Check LLM error rate
kubectl exec -it prometheus-0 -n eren-monitoring -- \
  promtool query instant \
  'rate(eren_llm_errors_total[5m])' | grep -v "{}"

# 3. Check for rate limiting
kubectl exec -it prometheus-0 -n eren-monitoring -- \
  promtool query instant \
  'rate(eren_llm_rate_limit_total[5m])'

# 4. If LLM down: switch to fallback
# (Code automatically falls back, but verify)
kubectl logs -f -n eren-production -l app=eren-worker | grep "fallback"

# 5. Check embedding service
kubectl exec -it eren-api-0 -n eren-production -- \
  curl -s http://localhost:8000/health/embedding | jq .

# 6. Restart LLM-dependent pods
kubectl rollout restart deployment/eren-worker -n eren-production
```

### Verification
- [ ] CDS P95 latency < 5s
- [ ] No fallback mode (unless LLM is down)
- [ ] LLM error rate < 1%

---

## RB-006: Multi-Tenant Isolation Breach

### Symptoms
- `CrossTenantAccessAttempted` event in audit logs
- `MultiTenantIsolationBreach` alert (CRITICAL)
- User report: seeing another tenant's data

### Impact
- **CRITICAL:** PHI data exposure between tenants
- HIPAA violation risk

### Procedure

```bash
# 1. IMMEDIATELY isolate the affected accounts
# (This is automated via Guardrail G2.2, but verify)

# 2. Check audit log for the breach
kubectl exec -it eren-api-0 -n eren-production -- \
  python -c "
  import asyncio
  from eren.infrastructure.database import get_pool
  async def audit():
    pool = await get_pool()
    async with pool.acquire() as conn:
      breaches = await conn.fetch('''
        SELECT * FROM audit_log
        WHERE event_type = 'CROSS_TENANT_ACCESS'
          AND created_at > NOW() - INTERVAL '1 hour'
        ORDER BY created_at DESC
        LIMIT 100;
      ''')
      for b in breaches:
        print(dict(b))
  asyncio.run(audit())
  "

# 3. Identify the tenant affected
# 4. Notify affected tenant(s) per HIPAA requirements
# 5. Preserve all audit logs for investigation
# 6. Escalate to Security team

# 7. Verify RLS is still enforcing
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT tablename, rowsecurity
  FROM pg_tables
  WHERE schemaname = 'public'
  AND rowsecurity = true;
"

# 8. If RLS was disabled, re-enable immediately
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SELECT 'ALTER TABLE ' || tablename || ' ENABLE ROW LEVEL SECURITY;'
  FROM pg_tables
  WHERE schemaname = 'public'
  AND rowsecurity = false;
"
```

### Verification
- [ ] No new cross-tenant access attempts
- [ ] RLS enabled on all tables
- [ ] Security team notified
- [ ] Affected tenants notified

---

## RB-007: LLM Provider Down

### Symptoms
- LLM request timeout
- CDS fully using rule-based fallback
- `LLMProviderUnavailable` alert

### Impact
- CDS continues with rule-based responses (degraded quality)
- No new PHI content generated

### Procedure

```bash
# 1. Check primary provider (OpenAI)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "ping"}]}' \
  --max-time 10

# 2. Check fallback provider (Anthropic)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{"model": "claude-3-sonnet", "messages": [{"role": "user", "content": "ping"}]}' \
  --max-time 10

# 3. If primary is down, verify fallback is active
kubectl logs -n eren-production -l app=eren-worker | grep "fallback.*anthropic"

# 4. If both down, escalate immediately (P0)
# 5. Monitor for hallucination increase (Guardrail G5.1)

# 6. After recovery, verify LLM is working
kubectl exec -it eren-api-0 -n eren-production -- \
  curl -s http://localhost:8000/health/llm | jq .
```

### Verification
- [ ] LLM provider responding
- [ ] CDS back to AI-powered mode
- [ ] No hallucination increase

---

## RB-008: New Tenant Onboarding

### Procedure

```bash
# 1. Create tenant record
kubectl exec -it eren-api-0 -n eren-production -- \
  python -c "
  import asyncio
  from eren.application.services import TenantService
  async def create():
    service = TenantService()
    tenant = await service.create(
      name='New Hospital',
      slug='new-hospital',
      admin_email='admin@newhospital.com'
    )
    print(f'Created tenant: {tenant.id}')
  asyncio.run(create())
  "

# 2. Create tenant-specific Vault secrets
vault kv put eren/production/tenant/TENANT_ID_HERE \
  api_key="tenant_specific_key" \
  webhook_secret="$(openssl rand -hex 32)"

# 3. Run tenant-specific migrations (if needed)
kubectl exec -it eren-api-0 -n eren-production -- \
  alembic upgrade head --tenant=TENANT_ID_HERE

# 4. Verify RLS for new tenant
kubectl exec -it postgres-0 -n eren-infra -- psql -U eren -c "
  SET app.tenant_id = 'TENANT_ID_HERE';
  SELECT COUNT(*) FROM patients;  -- Should return 0
"

# 5. Create initial demo data (optional)
kubectl exec -it eren-api-0 -n eren-production -- \
  python -m eren.seed --tenant=TENANT_ID_HERE --demo

# 6. Notify tenant admin
# (Automated via email template)
```

---

## RB-009: Database Backup Failure

### Procedure

```bash
# 1. Check backup logs
kubectl logs -n eren-production -l app=eren-cron | \
  grep -A5 "backup" | tail -50

# 2. Check S3 connectivity
kubectl exec -it eren-worker-0 -n eren-production -- \
  aws s3 ls s3://eren-backup/ --recursive | tail -5

# 3. Retry failed backup manually
kubectl exec -it eren-worker-0 -n eren-production -- \
  python -m eren.backup.postgres --full

# 4. Verify backup size (should be > 1MB for a populated DB)
aws s3 ls s3://eren-backup/postgres/ --recursive | \
  sort | tail -5

# 5. If persistent failure, check disk space
kubectl exec -it postgres-0 -n eren-infra -- df -h
```

---

## RB-010: SSL Certificate Renewal

### Symptoms
- `cert-manager` alert: certificate expiring in < 30 days
- External services report SSL errors

### Procedure

```bash
# 1. Check certificate status
kubectl get certificate -n eren-production

# 2. Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager --tail=50

# 3. Force renewal (if needed)
kubectl delete certificate eren-tls -n eren-production
kubectl apply -f infra/k8s/certificate.yaml -n eren-production

# 4. Verify new certificate
kubectl get certificate -n eren-production
# Wait for READY=True

# 5. Verify TLS is working
curl -v https://api.eren.io/health 2>&1 | grep "SSL certificate verify ok"
```

---

*Infrastructure Team - 2026-07-16*
