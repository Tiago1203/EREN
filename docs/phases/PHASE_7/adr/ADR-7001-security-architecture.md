# ADR-7001: Security Architecture for Production

## Status
**Implemented** (Julio 2025)

## Context
EREN PHASE 7 will be deployed in production hospital environments requiring compliance with HIPAA, FDA 21 CFR Part 11, ISO 13485, and IEC 62304. We need a security architecture that protects PHI data while enabling the platform's clinical intelligence capabilities.

## Decision
We adopt a defense-in-depth security architecture:

1. **Encryption at rest** - AES-256 for all PHI data
2. **Encryption in transit** - TLS 1.3 for all communications
3. **Access Control** - RBAC with ABAC for fine-grained permissions
4. **Audit Logging** - All data access logged with tamper-proof storage
5. **Data Classification** - PHI, PII, Public levels with corresponding controls
6. **Key Management** - HSM-based encryption key management

## Consequences
### Positive
- Full HIPAA compliance
- FDA 21 CFR Part 11 electronic records compliance
- Audit trail for regulatory inspections
- Fine-grained access control

### Negative
- Performance overhead from encryption
- Complexity in key management
- Additional infrastructure (HSM)
