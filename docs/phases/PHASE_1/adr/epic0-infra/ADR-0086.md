# ADR-0086: Backup and Disaster Recovery Strategy

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Infrastructure Team

---

## Context

EREN handles Protected Health Information (PHI) and must comply with HIPAA's requirements for backup and disaster recovery. Loss of patient data, device records, or audit logs would have severe consequences.

Epic 0 NFRs define targets but do not specify implementation:
- RTO (Recovery Time Objective): 4 hours for critical services
- RPO (Recovery Point Objective): 1 hour for clinical data

We evaluated backup strategies for each data store: PostgreSQL, Redis, Neo4j, Qdrant, Kafka, and S3.

---

## Decision

**We will implement a tiered backup and DR strategy:**

| Data Store | Backup Method | Frequency | Retention | RPO | RTO |
|-----------|--------------|-----------|-----------|-----|-----|
| PostgreSQL | pg_dump + S3 | Every 4h + continuous WAL | 30 days | 1h | 2h |
| Redis | RDB snapshot + S3 | Every 4h | 7 days | 1h | 30min |
| Neo4j | Neo4j backup + S3 | Every 12h | 30 days | 4h | 2h |
| Qdrant | Snapshot + S3 | Every 24h | 7 days | 24h | 1h |
| Kafka | Topic retention (7 days) | Continuous | 7 days | 7 days | 4h |
| S3 (existing) | Native versioning + lifecycle | Continuous | Per bucket policy | 0h | 0h |
| Kafka | MirrorMaker2 cross-region | Continuous | 7 days | 1h | 4h |

---

## Reasons

### Tiered approach by data criticality

1. **PostgreSQL (highest criticality):** All business entities. Requires continuous WAL archiving + point-in-time recovery (PITR)
2. **Redis (medium criticality):** Cache + sessions. Can be rebuilt from PostgreSQL. RPO 1h is acceptable
3. **Neo4j (medium criticality):** Relationship graphs. Less frequent backups due to larger data size
4. **Qdrant (medium criticality):** Vector embeddings. Can be rebuilt from source data. Daily backups sufficient
5. **Kafka (lowest criticality for DR):** Events are published continuously. Retention of 7 days covers most DR scenarios. For RPO 1h, MirrorMaker2 provides cross-region replication

### S3-native features

- **Versioning:** Every object version is preserved
- **Lifecycle policies:** Automatic tiering to Glacier
- **Cross-region replication:** For multi-region DR

---

## Consequences

### Positive

- **HIPAA compliance:** Audit logs and patient data backed up with PITR capability
- **Tiered strategy:** Most critical data (PostgreSQL) has the most frequent backups
- **Cloud-native:** Leverages S3 durability (11 9s) for off-site storage
- **Cross-region:** MirrorMaker2 provides geographic redundancy for Kafka

### Negative

- **Cost:** S3 storage costs for backups + Glacier for long-term
- **RTO complexity:** PostgreSQL PITR requires practiced recovery procedures
- **Kafka RPO:** 7-day retention is acceptable but events between backups could be lost

### Mitigations

- Regular DR drills (quarterly)
- Documented runbooks for each data store recovery
- S3 Intelligent-Tiering for automatic cost optimization
- Outbox pattern ensures PostgreSQL is the source of truth (Kafka can be rebuilt)

---

## Implementation

### 1. PostgreSQL: Continuous WAL + pg_dump

```python
# scripts/backup/postgres_backup.py
import asyncio
from datetime import datetime

class PostgresBackup:
    def __init__(self, s3_client, pg_conn):
        self.s3 = s3_client
        self.conn = pg_conn

    async def full_backup(self):
        """Full pg_dump every 4 hours."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
        filename = f"backups/postgres/eren-full-{timestamp}.dump.gz"

        # pg_dump to stdout → gzip → S3
        process = await asyncio.create_subprocess_exec(
            "pg_dump", "-Fc", "-f", "-",
            env={**os.environ, "PGPASSWORD": os.environ["POSTGRES_PASSWORD"]},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        compressed = await self._compress(process.stdout)
        self.s3.put_object(
            Bucket=ERN_BACKUP_BUCKET,
            Key=filename,
            Body=compressed,
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=os.environ["BACKUP_KMS_KEY_ID"],
        )

        return filename

    async def point_in_time_recovery(self, target_time: datetime):
        """Restore PostgreSQL to a specific point in time."""
        # 1. Find the base backup just before target_time
        # 2. Restore base backup to new instance
        # 3. Replay WAL segments up to target_time
        # 4. Validate data integrity
        pass
```

```python
# Celery beat schedule
beat_schedule = {
    "postgres-backup-4h": {
        "task": "backup.postgres_full",
        "schedule": crontab(minute=0, hour="*/4"),  # Every 4h
    },
}
```

### 2. PostgreSQL WAL Archiving

```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 3
archive_mode = on
archive_command = "aws s3 cp %p s3://eren-backup/wal/%f"
archive_timeout = 300  # Force archive every 5 minutes
```

### 3. Redis: RDB Snapshots

```python
# scripts/backup/redis_backup.py
async def backup_redis():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")

    # BGSAVE triggers snapshot without blocking
    await redis.bgrewriteaof()
    await redis.bgsave()

    # Wait for snapshot to complete
    await wait_for_snapshot_completion(timeout=60)

    # Copy RDB file to S3
    s3.upload_file(
        Filename="/data/dump.rdb",
        Bucket=ERN_BACKUP_BUCKET,
        Key=f"backups/redis/eren-redis-{timestamp}.rdb",
    )
```

### 4. Neo4j Backup

```bash
# scripts/backup/neo4j_backup.sh
#!/bin/bash
NEO4J_BACKUP_DIR="/data/neo4j-backups"
S3_BUCKET="s3://eren-backup"

# Full backup (requires Neo4j to be offline or in HA mode)
neo4j-admin database backup --database=neo4j \
    --backup-dir=$NEO4J_BACKUP_DIR \
    --check-level=REQUIRED

# Copy to S3
aws s3 cp $NEO4J_BACKUP_DIR s3://eren-backup/neo4j/ \
    --recursive --sse aws:kms
```

### 5. Qdrant Snapshot

```python
# scripts/backup/qdrant_backup.py
async def backup_qdrant():
    """Qdrant collections as snapshots to S3."""
    collections = ["knowledge_base_evidence", "device_documentation"]

    for collection in collections:
        # Create snapshot
        snapshot_name = await qdrant.create_snapshot(collection)

        # Download to local
        local_path = await qdrant.download_snapshot(collection, snapshot_name)

        # Upload to S3
        s3.upload_file(
            local_path,
            Bucket=ERN_BACKUP_BUCKET,
            Key=f"backups/qdrant/{collection}-{snapshot_name}",
        )
```

### 6. Kafka: MirrorMaker2 Cross-Region

```yaml
# infra/kafka/mirrormaker2.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaMirrorMaker2
metadata:
  name: eren-dr-mirrormaker
spec:
  version: 3.6.0
  replicas: 3
  connectCluster: "primary"
  clusters:
    - alias: "primary"
      bootstrapServers: primary-kafka:9092
      tls:
        trustedCertificates:
          - secretName: primary-cluster-ca-cert
            certificate: ca.crt
    - alias: "dr"
      bootstrapServers: dr-kafka:9092
      tls:
        trustedCertificates:
          - secretName: dr-cluster-ca-cert
            certificate: ca.crt
  mirrors:
    - sourceCluster: "primary"
      targetCluster: "dr"
      sourceConnector:
        tasksMax: 10
        config:
          replication.factor: 3
          offset-syncs.topic.replication.factor: 3
          sync.topic.acls.enabled: "false"
      heartbeatConnector:
        config:
          heartbeats.interval.seconds: 10
      checkpointsConnector:
        config:
          checkpoints.interval.seconds: 60
      topicsPattern: "eren-.*"
      groupsPattern: ".*"
```

### 7. S3 Native Features

```python
# Enable versioning on all buckets
for bucket in EREN_BUCKETS:
    s3.put_bucket_versioning(
        Bucket=bucket,
        VersioningConfiguration={"Status": "Enabled"}
    )

# Lifecycle policies (see ADR-0082_OBJECT_STORAGE.md)
```

---

## Disaster Recovery Runbooks

### RTO/RTO Targets

| Scenario | RTO | RPO | Recovery Procedure |
|---------|-----|-----|---------------------|
| PostgreSQL failure | 2h | 1h | PITR from latest base backup + WAL |
| Redis failure | 30min | 1h | Rebuild from PostgreSQL + recent cache |
| Neo4j failure | 2h | 4h | Restore from latest backup |
| Qdrant failure | 1h | 24h | Rebuild vectors from source data |
| Kafka failure | 4h | 1h | MirrorMaker2 DR cluster |
| Complete region failure | 8h | 1h | Multi-region failover |

### DR Test Schedule

```
Quarterly: Full DR drill (all data stores)
Monthly: PostgreSQL PITR test
Monthly: Redis backup/restore test
Weekly: S3 backup integrity verification
```

---

## Backup Verification

```python
# scripts/backup/verify_backups.py
async def verify_postgres_backup(backup_file: str):
    """Verify backup is not corrupted."""
    # 1. Download from S3
    # 2. pg_restore --list to verify catalog
    # 3. Run CHECKPOINT on restored DB
    # 4. Verify row counts for critical tables
    # 5. Report to monitoring
    pass

# Automated verification after every backup
async def backup_completed(backup_file: str, backup_type: str):
    await verify_postgres_backup(backup_file)
    await send_alert(
        severity="info",
        message=f"Backup {backup_file} completed and verified"
    )
```

---

*Infrastructure Team - 2026-07-16*
