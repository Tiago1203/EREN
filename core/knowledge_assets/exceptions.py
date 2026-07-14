"""Knowledge Asset Registry exceptions for EREN OS."""

from __future__ import annotations


class AssetRegistryError(Exception):
    """Base exception for asset registry errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class AssetNotFoundError(AssetRegistryError):
    """Raised when asset is not found."""

    def __init__(self, asset_id: str):
        super().__init__(f"Asset not found: {asset_id}")
        self.asset_id = asset_id


class CollectionNotFoundError(AssetRegistryError):
    """Raised when collection is not found."""

    def __init__(self, collection_id: str):
        super().__init__(f"Collection not found: {collection_id}")
        self.collection_id = collection_id


class VersionNotFoundError(AssetRegistryError):
    """Raised when version is not found."""

    def __init__(self, version_id: str, asset_id: str = ""):
        msg = f"Version not found: {version_id}"
        if asset_id:
            msg += f" for asset {asset_id}"
        super().__init__(msg)
        self.version_id = version_id
        self.asset_id = asset_id


class DuplicateAssetError(AssetRegistryError):
    """Raised when asset already exists."""

    def __init__(self, asset_id: str):
        super().__init__(f"Asset already exists: {asset_id}")
        self.asset_id = asset_id


class DuplicateCollectionError(AssetRegistryError):
    """Raised when collection already exists."""

    def __init__(self, collection_id: str):
        super().__init__(f"Collection already exists: {collection_id}")
        self.collection_id = collection_id


class PermissionDeniedError(AssetRegistryError):
    """Raised when permission is denied."""

    def __init__(self, action: str, resource: str = ""):
        msg = f"Permission denied: {action}"
        if resource:
            msg += f" on {resource}"
        super().__init__(msg)
        self.action = action
        self.resource = resource


class ValidationError(AssetRegistryError):
    """Raised when validation fails."""

    def __init__(self, field: str, reason: str = ""):
        msg = f"Validation error on {field}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.field = field
        self.reason = reason


class AuditLogError(AssetRegistryError):
    """Raised when audit logging fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Audit log error: {reason}")
        self.reason = reason


class ConfigurationError(AssetRegistryError):
    """Raised when configuration is invalid."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Configuration error: {reason}")
        self.reason = reason
