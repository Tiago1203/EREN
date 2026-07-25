"""
PHASE 7 - EPIC 0: FDA 21 CFR Part 11 - Audit Trail

Sistema de audit trail para registros electrónicos:
- Tamper-evident logging
- Time-stamped entries
- Operator identification
- Action/change tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib


class AuditEntryType(str, Enum):
    """Tipos de entradas de auditoría FDA."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    PRINT = "print"
    EXPORT = "export"
    SIGN = "sign"
    APPROVE = "approve"
    REJECT = "reject"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"


@dataclass
class FDAAuditEntry:
    """Entrada de audit trail FDA 21 CFR Part 11 compliant."""
    entry_id: str
    timestamp: datetime

    # Who
    operator_id: str
    operator_name: str
    operator_role: str
    workstation: str

    # What
    action: AuditEntryType
    record_type: str
    record_id: str
    record_name: str

    # Changes
    field_changed: str = ""
    previous_value: str = ""
    new_value: str = ""

    # Context
    reason: str = ""
    linked_signature_id: str = ""
    session_id: str = ""

    # Integrity
    entry_hash: str = ""
    previous_entry_hash: str = ""
    is_valid: bool = True


class FDAAuditTrail:
    """Audit trail FDA 21 CFR Part 11 compliant."""

    def __init__(self):
        self._entries: list[FDAAuditEntry] = []
        self._last_hash: str = ""

    def log(
        self,
        operator_id: str,
        operator_name: str,
        operator_role: str,
        workstation: str,
        action: AuditEntryType,
        record_type: str,
        record_id: str,
        record_name: str,
        reason: str = "",
        field_changed: str = "",
        previous_value: str = "",
        new_value: str = "",
        linked_signature_id: str = "",
        session_id: str = "",
    ) -> FDAAuditEntry:
        """Registra entrada en audit trail."""
        entry_id = f"fda-audit-{len(self._entries) + 1:08d}"

        entry = FDAAuditEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            operator_id=operator_id,
            operator_name=operator_name,
            operator_role=operator_role,
            workstation=workstation,
            action=action,
            record_type=record_type,
            record_id=record_id,
            record_name=record_name,
            reason=reason,
            field_changed=field_changed,
            previous_value=previous_value,
            new_value=new_value,
            linked_signature_id=linked_signature_id,
            session_id=session_id,
            previous_entry_hash=self._last_hash,
        )

        # Create tamper-evident hash
        entry.entry_hash = self._compute_entry_hash(entry)
        self._last_hash = entry.entry_hash

        self._entries.append(entry)
        return entry

    def _compute_entry_hash(self, entry: FDAAuditEntry) -> str:
        """Calcula hash de entrada para tamper-evidence."""
        data = (
            f"{entry.entry_id}:{entry.timestamp.isoformat()}:{entry.operator_id}:"
            f"{entry.action.value}:{entry.record_id}:{entry.previous_entry_hash}:"
            f"{entry.field_changed}:{entry.previous_value}"
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_chain_integrity(self) -> tuple[bool, list[str]]:
        """Verifica integridad de toda la cadena."""
        errors = []
        if not self._entries:
            return True, []

        for i, entry in enumerate(self._entries):
            computed = self._compute_entry_hash(entry)
            if computed != entry.entry_hash:
                errors.append(f"Entry {entry.entry_id}: hash mismatch")
            if i > 0:
                prev_entry = self._entries[i - 1]
                if entry.previous_entry_hash != prev_entry.entry_hash:
                    errors.append(f"Entry {entry.entry_id}: broken chain")

        return len(errors) == 0, errors

    def get_entries(
        self,
        record_id: Optional[str] = None,
        operator_id: Optional[str] = None,
        action: Optional[AuditEntryType] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
    ) -> list[FDAAuditEntry]:
        """Consulta entradas de auditoría."""
        entries = self._entries

        if record_id:
            entries = [e for e in entries if e.record_id == record_id]
        if operator_id:
            entries = [e for e in entries if e.operator_id == operator_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        if until:
            entries = [e for e in entries if e.timestamp <= until]

        return entries[-limit:]

    def generate_compliance_report(
        self,
        since: datetime,
        until: datetime,
    ) -> dict:
        """Genera reporte de compliance FDA."""
        entries = self.get_entries(since=since, until=until)

        by_action = {}
        for entry in entries:
            key = entry.action.value
            by_action[key] = by_action.get(key, 0) + 1

        by_operator = {}
        for entry in entries:
            by_operator[entry.operator_name] = by_operator.get(entry.operator_name, 0) + 1

        return {
            "report_period": f"{since.isoformat()} to {until.isoformat()}",
            "total_entries": len(entries),
            "entries_by_action": by_action,
            "entries_by_operator": by_operator,
            "integrity_verified": self.verify_chain_integrity()[0],
            "first_entry": entries[0].timestamp.isoformat() if entries else None,
            "last_entry": entries[-1].timestamp.isoformat() if entries else None,
        }
