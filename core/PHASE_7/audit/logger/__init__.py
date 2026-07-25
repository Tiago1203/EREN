"""EPIC 1: Audit & Compliance System — Logger Module."""
from core.PHASE_7.audit.logger.audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditLog,
    AuditCategory,
    AuditAction,
    AuditSeverity,
    AuditRetentionPolicy,
)
from core.PHASE_7.audit.logger.event_capture import (
    set_audit_logger,
    get_audit_logger,
    audit_action,
    audit_phi_access,
    AuditContext,
)
from core.PHASE_7.audit.logger.async_logger import (
    AsyncAuditLogger,
    AsyncAuditConfig,
    FlushStrategy,
)
from core.PHASE_7.audit.logger.batch_writer import (
    BatchWriter,
    BatchWriteConfig,
    WriteStrategy,
)
