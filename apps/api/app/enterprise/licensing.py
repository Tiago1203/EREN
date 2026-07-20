"""
Licensing Module

Enterprise licensing system.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class LicenseTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class LicenseStatus(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class License(BaseModel):
    """License model."""
    id: str
    tier: LicenseTier
    customer_id: str
    customer_name: str
    issued_at: datetime
    expires_at: datetime
    max_users: int
    max_devices: int
    features: List[str] = []
    status: LicenseStatus = LicenseStatus.VALID
    metadata: Dict[str, Any] = {}


class FeatureFlags:
    """Feature flags based on license tier."""
    
    FEATURES = {
        LicenseTier.COMMUNITY: [
            "basic_ai",
            "device_management",
            "incident_tracking",
        ],
        LicenseTier.PROFESSIONAL: [
            "basic_ai",
            "device_management",
            "incident_tracking",
            "clinical_intelligence",
            "analytics",
            "api_access",
        ],
        LicenseTier.ENTERPRISE: [
            "basic_ai",
            "device_management",
            "incident_tracking",
            "clinical_intelligence",
            "analytics",
            "api_access",
            "predictive_maintenance",
            "anomaly_detection",
            "custom_integrations",
            "sso",
            "audit_logs",
            "dedicated_support",
            "custom_branding",
        ],
    }
    
    @classmethod
    def get_features(cls, tier: LicenseTier) -> List[str]:
        """Get features for license tier."""
        return cls.FEATURES.get(tier, [])
    
    @classmethod
    def is_enabled(cls, tier: LicenseTier, feature: str) -> bool:
        """Check if feature is enabled."""
        return feature in cls.get_features(tier)


class LicenseValidator:
    """Validates licenses."""
    
    def __init__(self):
        self._cache: Dict[str, License] = {}
    
    def validate(self, license_key: str) -> bool:
        """Validate license key."""
        # In production: call license server
        # For now: basic validation
        return len(license_key) > 0
    
    def check_expiration(self, license: License) -> LicenseStatus:
        """Check license expiration."""
        if license.expires_at < datetime.utcnow():
            return LicenseStatus.EXPIRED
        return license.status


class LicenseManager:
    """Manages licenses."""
    
    def __init__(self):
        self.validator = LicenseValidator()
        self._licenses: Dict[str, License] = {}
    
    async def register_license(self, license: License) -> bool:
        """Register a new license."""
        if self.validator.validate(license.id):
            self._licenses[license.id] = license
            return True
        return False
    
    async def validate_license(self, license_key: str) -> Optional[License]:
        """Validate and return license."""
        license = self._licenses.get(license_key)
        if not license:
            return None
        
        status = self.validator.check_expiration(license)
        if status != LicenseStatus.VALID:
            return None
        
        return license
    
    async def get_feature_flags(self, license_key: str) -> List[str]:
        """Get enabled features for license."""
        license = await self.validate_license(license_key)
        if not license:
            return []
        
        return FeatureFlags.get_features(license.tier)
    
    async def check_feature(self, license_key: str, feature: str) -> bool:
        """Check if feature is enabled."""
        license = await self.validate_license(license_key)
        if not license:
            return False
        
        return FeatureFlags.is_enabled(license.tier, feature)
    
    async def get_usage_stats(self, license_key: str) -> Dict[str, Any]:
        """Get usage statistics."""
        license = await self.validate_license(license_key)
        if not license:
            return {}
        
        return {
            "tier": license.tier,
            "max_users": license.max_users,
            "max_devices": license.max_devices,
            "expires_at": license.expires_at.isoformat(),
            "features_count": len(license.features),
        }
