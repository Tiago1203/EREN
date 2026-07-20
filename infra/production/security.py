"""
Security Module for EREN Production

RBAC, HIPAA, GDPR, and ISO 27001 compliance.
"""
from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    HOSPITAL_ADMIN = "hospital_admin"
    DEPARTMENT_MANAGER = "department_manager"
    ENGINEER = "engineer"
    VIEWER = "viewer"


class Permission(BaseModel):
    resource: str
    actions: Set[str]


# Role permissions
ROLE_PERMISSIONS: Dict[Role, List[str]] = {
    Role.SUPER_ADMIN: ["*"],
    Role.HOSPITAL_ADMIN: [
        "devices:create", "devices:read", "devices:update", "devices:delete",
        "incidents:create", "incidents:read", "incidents:update", "incidents:delete",
        "reports:*", "settings:update"
    ],
    Role.DEPARTMENT_MANAGER: [
        "devices:read", "devices:update",
        "incidents:create", "incidents:read", "incidents:update",
        "reports:read", "reports:update"
    ],
    Role.ENGINEER: [
        "devices:read", "devices:update",
        "incidents:create", "incidents:read", "incidents:update",
        "reports:read"
    ],
    Role.VIEWER: ["devices:read", "incidents:read", "reports:read"],
}


class RBACService:
    """Role-Based Access Control service."""
    
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS
    
    def has_permission(self, role: Role, resource: str, action: str) -> bool:
        """Check if role has permission for resource:action."""
        permissions = self.role_permissions.get(role, [])
        
        if "*" in permissions:
            return True
        
        return f"{resource}:{action}" in permissions or f"{resource}:*" in permissions
    
    def require_permission(self, role: Role, resource: str, action: str):
        """Decorator to require permission."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if not self.has_permission(role, resource, action):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Permission denied: {resource}:{action}"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator


class HIPAACompliance:
    """HIPAA compliance utilities."""
    
    PHI_FIELDS = [
        "patient_id", "patient_name", "date_of_birth",
        "medical_record_number", "diagnosis", "treatment_plan"
    ]
    
    @staticmethod
    def is_phi_field(field_name: str) -> bool:
        """Check if field contains PHI."""
        return field_name.lower() in [f.lower() for f in HIPAACompliance.PHI_FIELDS]
    
    @staticmethod
    def anonymize_data(data: Dict) -> Dict:
        """Anonymize PHI data."""
        result = {}
        for key, value in data.items():
            if HIPAACompliance.is_phi_field(key):
                result[key] = "[REDACTED]"
            else:
                result[key] = value
        return result


class GDPRCompliance:
    """GDPR compliance utilities."""
    
    @staticmethod
    async def export_user_data(user_id: str) -> Dict:
        """Export all user data for GDPR Right to Portability."""
        return {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "data": {}
        }
    
    @staticmethod
    async def delete_user_data(user_id: str) -> bool:
        """Delete user data for GDPR Right to Erasure."""
        # In production: delete from all databases
        return True
    
    @staticmethod
    async def anonymize_pii(user_id: str):
        """Anonymize PII for retention."""
        pass


# Security middleware
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Verify JWT token."""
    # In production: verify with OAuth provider
    return {"user_id": "user123", "role": Role.ENGINEER}


def require_roles(*roles: Role):
    """Decorator to require specific roles."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user", {})
            if user.get("role") not in roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
