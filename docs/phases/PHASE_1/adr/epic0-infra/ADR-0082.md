# ADR-0082: S3/MinIO Object Storage Strategy

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Infrastructure Team

---

## Context

EREN needs persistent storage for:
- **DICOM medical images** (large binary files, encrypted at rest)
- **Data exports** (CSV, JSON from queries)
- **Data imports** (batch uploads from hospitals)
- **Database backups** (PostgreSQL snapshots)
- **Application logs** (archival, long-term retention)
- **File attachments** (incident reports, maintenance documents)
- **Model artifacts** (ML models, embeddings indexes)

We evaluated **AWS S3 / Google Cloud Storage** and **MinIO**.

---

## Decision

**We will use S3-compatible object storage as the single storage layer.**

- **Production:** AWS S3 or Google Cloud Storage (managed, global)
- **On-premises / Development:** MinIO (S3-compatible, self-hosted)

This provides a single API (`boto3` / `s3transfer`) across all environments.

---

## Reasons

### Why Object Storage (not filesystem or block storage)

1. **Scalability:** Object storage scales to petabytes without capacity planning. DICOM files alone can grow to terabytes per hospital
2. **Durability:** S3 offers 99.999999999% (11 9s) durability. Critical for HIPAA-regulated medical data
3. **Lifecycle policies:** Automatic tiering (S3 → Glacier) reduces storage costs for old DICOM files
4. **Encryption:** Server-side encryption (SSE-S3 or SSE-KMS) for PHI at rest
5. **Access control:** IAM policies + bucket policies for fine-grained access per tenant
6. **No filesystem limits:** No inode limits, no filesystem size limits
7. **CDN integration:** CloudFront/Cloud CDN can serve DICOM thumbnails and exports

### Why MinIO (on-premises / development)

1. **S3 API compatibility:** Zero code changes between MinIO and S3
2. **Single binary deployment:** No complex setup
3. **Kubernetes native:** Can run as a StatefulSet with persistent volumes
4. **Erasure coding:** Data protection without RAID
5. **Performance:** Comparable to cloud object stores for moderate workloads

### Why not alternatives

**Local filesystem (rejected):**
- No built-in replication across nodes
- No lifecycle policies
- No access control per tenant
- Difficult to migrate to cloud

**Ceph/RADOSGW (rejected):**
- Over-engineered for our needs
- High operational complexity
- Not S3-compatible out of the box

---

## Consequences

### Positive

- Single storage API across all environments
- HIPAA-compliant storage for PHI (DICOM, exports)
- Automatic lifecycle management (DICOM → Glacier after 1 year)
- Tenant-scoped access via IAM policies
- No storage capacity planning for application team

### Negative

- **Latency:** Higher latency than local filesystem (network hop)
- **Cost:** Cloud storage costs (~$0.023/GB for S3 Standard)
- **Vendor lock-in:** Cloud-provider-specific features (S3 → Cloud Storage migration is non-trivial)
- **Offline scenario:** No access when internet/cloud is down

### Mitigations

- Use **presigned URLs** for temporary access (not permanent credentials)
- **MinIO on-premises** for locations with connectivity concerns
- Local cache for frequently accessed DICOM files
- Cloud storage costs factored into per-tenant pricing

---

## Bucket Architecture

```
Production (AWS S3):
  eren-prod-exports
  eren-prod-imports
  eren-prod-dicom       ← Encrypted (SSE-KMS)
  eren-prod-backups     ← Encrypted (SSE-KMS)
  eren-prod-logs
  eren-prod-attachments
  eren-prod-models      ← ML model artifacts

Development (MinIO):
  eren-dev-{bucket}
```

### Bucket Policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TenantScopedAccess",
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::eren-prod-*/tenant/${aws:PrincipalTag.tenant_id}/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:ExistingObjectTag/tenant_id": "${aws:PrincipalTag.tenant_id}"
        }
      }
    }
  ]
}
```

### Lifecycle Policies

```json
{
  "Rules": [
    {
      "ID": "dicom-glacier",
      "Prefix": "",
      "Status": "Enabled",
      "Transitions": [
        {"Days": 365, "StorageClass": "GLACIER"}
      ],
      "Filter": {"Prefix": "dicom/"}
    },
    {
      "ID": "exports-delete",
      "Prefix": "exports/",
      "Status": "Enabled",
      "Expiration": {"Days": 90}
    },
    {
      "ID": "backups-glacier",
      "Prefix": "backups/",
      "Status": "Enabled",
      "Transitions": [
        {"Days": 7, "StorageClass": "GLACIER"}
      ]
    }
  ]
}
```

---

## DICOM Storage (Special Case)

### Requirements

- **Encryption:** AES-256 at rest (SSE-KMS with customer-managed keys)
- **Access control:** Only authorized roles can read/write DICOM
- **Metadata indexing:** Store DICOM metadata separately in PostgreSQL (not in S3 metadata)
- **Format:** Standard DICOM Part 10 files (.dcm)

### Storage Structure

```
dicom/
├── {patient_id}/
│   ├── {study_id}/
│   │   ├── {series_id}/
│   │   │   ├── {sop_instance_uid}.dcm
│   │   │   └── {sop_instance_uid}.dcm
```

### Access Pattern

```python
# DICOM upload
async def upload_dicom(
    patient_id: UUID,
    study_id: UUID,
    series_id: UUID,
    sop_instance_uid: str,
    file_bytes: bytes,
    tenant_id: UUID,
):
    key = f"dicom/{patient_id}/{study_id}/{series_id}/{sop_instance_uid}.dcm"
    s3.put_object(
        Bucket=ERN_DICOM_BUCKET,
        Key=key,
        Body=file_bytes,
        ServerSideEncryption="aws:kms",
        SSEKMSKeyId=os.environ["DICOM_KMS_KEY_ID"],
        Metadata={"tenant_id": str(tenant_id)}
    )
```

---

## Backup Storage

Database backups go to S3:

```python
# Nightly backup script (run via Celery cron)
async def backup_database():
    date_str = datetime.utcnow().strftime("%Y%m%d")
    key = f"backups/postgresql/eren-{date_str}.dump.gz"

    # pg_dump to stdout → compress → upload to S3
    process = await asyncio.create_subprocess_exec(
        "pg_dump", "-Fc", "-f", "-", DATABASE_URL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    compressed, _ = await compress_gzip(process.stdout)
    s3.put_object(Bucket=ERN_BACKUP_BUCKET, Key=key, Body=compressed)
```

Retention: 30 days on S3 Standard, then Glacier.

---

## S3 Client Configuration

```python
import boto3
from botocore.config import Config

# Retry configuration
s3 = boto3.client(
    "s3",
    config=Config(
        retries={"max_attempts": 3, "mode": "standard"},
        connect_timeout=5,
        read_timeout=60,  # Higher for large files (DICOM)
    )
)

# Multipart upload for files > 100MB
config = boto3.s3.transfer.S3TransferConfig(
    multipart_threshold=100 * 1024 * 1024,  # 100MB
    max_concurrency=10,
)
```

---

*Infrastructure Team - 2026-07-16*
