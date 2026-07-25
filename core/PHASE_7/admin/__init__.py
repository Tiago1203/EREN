"""EPIC 5: Admin Panel & Migration.

Backend services para:
- User management (CRUD, roles, permissions)
- Role management
- System settings
- Data migration (PHASE_1 -> PHASE_7)
- Admin API

Integración:
- EPIC 1: audit events
- EPIC 2: multi-tenant context
- EPIC 3: HA health checks
- EPIC 4: observability metrics
"""
from core.PHASE_7.admin.domain import User, Role, Permission, UserStatus, RoleType
from core.PHASE_7.admin.services import AdminService, MigrationService, MigrationEntity, MigrationStatus
from core.PHASE_7.admin.api import AdminAPI
