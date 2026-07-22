"""Knowledge Permissions for EREN Knowledge Registry.

Manages access control and audit logging.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.domain.knowledge.registry_types import (
    AuditAction,
    AuditLog,
    PermissionLevel,
)

if TYPE_CHECKING:
    pass


class AuditLogger:
    """Audit logger for knowledge registry.

    Tracks all actions on the registry.
    """

    def __init__(self, max_entries: int = 10000):
        """Initialize audit logger.

        Args:
            max_entries: Maximum number of entries to keep.
        """
        self._lock = threading.RLock()
        self._logs: list[AuditLog] = []
        self._max_entries = max_entries

    def log(
        self,
        action: AuditAction,
        knowledge_id: str = "",
        user_id: str = "",
        details: dict | None = None,
        ip_address: str = "",
    ) -> AuditLog:
        """Log an action.

        Args:
            action: Action performed.
            knowledge_id: Knowledge ID affected.
            user_id: User who performed action.
            details: Additional details.
            ip_address: IP address of request.

        Returns:
            Created audit log entry.
        """
        with self._lock:
            audit_id = str(uuid.uuid4())

            log_entry = AuditLog(
                audit_id=audit_id,
                action=action,
                knowledge_id=knowledge_id,
                user_id=user_id,
                details=details or {},
                timestamp=datetime.now(UTC),
                ip_address=ip_address,
            )

            self._logs.append(log_entry)

            # Trim if over max
            if len(self._logs) > self._max_entries:
                self._logs = self._logs[-self._max_entries:]

            return log_entry

    def get_logs(
        self,
        knowledge_id: str | None = None,
        user_id: str | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs.

        Args:
            knowledge_id: Filter by knowledge ID.
            user_id: Filter by user ID.
            action: Filter by action.
            limit: Maximum number of logs.

        Returns:
            List of audit logs.
        """
        with self._lock:
            logs = self._logs

            if knowledge_id:
                logs = [l for l in logs if l.knowledge_id == knowledge_id]

            if user_id:
                logs = [l for l in logs if l.user_id == user_id]

            if action:
                logs = [l for l in logs if l.action == action]

            # Sort by timestamp descending
            logs = sorted(logs, key=lambda l: l.timestamp, reverse=True)

            return logs[:limit]

    def count(self) -> int:
        """Count total logs.

        Returns:
            Number of logs.
        """
        with self._lock:
            return len(self._logs)

    def clear(self) -> None:
        """Clear all logs."""
        with self._lock:
            self._logs.clear()


class PermissionChecker:
    """Permission checker for knowledge registry.

    Validates access permissions.
    """

    def __init__(self):
        """Initialize permission checker."""
        self._lock = threading.RLock()
        self._user_permissions: dict[str, PermissionLevel] = {}

    def set_user_permission(
        self,
        user_id: str,
        level: PermissionLevel,
    ) -> None:
        """Set user permission level.

        Args:
            user_id: User ID.
            level: Permission level.
        """
        with self._lock:
            self._user_permissions[user_id] = level

    def get_user_permission(self, user_id: str) -> PermissionLevel:
        """Get user permission level.

        Args:
            user_id: User ID.

        Returns:
            Permission level.
        """
        with self._lock:
            return self._user_permissions.get(user_id, PermissionLevel.PUBLIC)

    def can_access(
        self,
        user_id: str,
        required_level: PermissionLevel,
    ) -> bool:
        """Check if user can access resource.

        Args:
            user_id: User ID.
            required_level: Required permission level.

        Returns:
            True if access allowed.
        """
        with self._lock:
            user_level = self._user_permissions.get(user_id, PermissionLevel.PUBLIC)

            # Define permission hierarchy
            hierarchy = {
                PermissionLevel.CONFIDENTIAL: 4,
                PermissionLevel.RESTRICTED: 3,
                PermissionLevel.INTERNAL: 2,
                PermissionLevel.PUBLIC: 1,
            }

            user_value = hierarchy.get(user_level, 0)
            required_value = hierarchy.get(required_level, 0)

            return user_value >= required_value

    def can_modify(
        self,
        user_id: str,
        resource_owner: str,
    ) -> bool:
        """Check if user can modify resource.

        Args:
            user_id: User ID.
            resource_owner: Resource owner ID.

        Returns:
            True if modification allowed.
        """
        with self._lock:
            # Owner can always modify
            if user_id == resource_owner:
                return True

            # Check for elevated permissions
            level = self.get_user_permission(user_id)
            return level in (PermissionLevel.RESTRICTED, PermissionLevel.CONFIDENTIAL)


# Global instances
_global_audit_logger: AuditLogger | None = None
_global_permission_checker: PermissionChecker | None = None
_audit_lock = threading.Lock()
_perm_lock = threading.Lock()


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger.

    Returns:
        Global AuditLogger instance.
    """
    global _global_audit_logger
    with _audit_lock:
        if _global_audit_logger is None:
            _global_audit_logger = AuditLogger()
        return _global_audit_logger


def get_permission_checker() -> PermissionChecker:
    """Get the global permission checker.

    Returns:
        Global PermissionChecker instance.
    """
    global _global_permission_checker
    with _perm_lock:
        if _global_permission_checker is None:
            _global_permission_checker = PermissionChecker()
        return _global_permission_checker


def reset_permissions() -> None:
    """Reset global permission instances."""
    global _global_audit_logger, _global_permission_checker
    with _audit_lock:
        if _global_audit_logger is not None:
            _global_audit_logger.clear()
        _global_audit_logger = None
    with _perm_lock:
        _global_permission_checker = None
