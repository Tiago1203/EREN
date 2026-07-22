"""Unit tests for EREN Knowledge Asset Registry (KAR)."""

import pytest

from core.PHASE_1.domain.knowledge_assets.types import (
    AssetType,
    LifecycleState,
    PermissionLevel,
    AuditAction,
    AssetMetadata,
    AssetVersion,
    AssetCollection,
    AuditLog,
    AssetStatistics,
    AssetSearchQuery,
)
from core.PHASE_1.domain.knowledge_assets.exceptions import (
    AssetNotFoundError,
    DuplicateAssetError,
)
from core.PHASE_1.domain.knowledge_assets.catalog import (
    AssetCatalog,
    get_asset_catalog,
    reset_asset_catalog,
)
from core.PHASE_1.domain.knowledge_assets.collections import (
    AssetCollections,
    get_asset_collections,
    reset_asset_collections,
)
from core.PHASE_1.domain.knowledge_assets.versions import (
    VersionManager,
    get_version_manager,
    reset_version_manager,
)
from core.PHASE_1.domain.knowledge_assets.permissions import (
    AuditLogger,
    PermissionChecker,
    get_audit_logger,
    reset_permissions,
)
from core.PHASE_1.domain.knowledge_assets.registry import KnowledgeAssetRegistry


class TestAssetTypes:
    """Tests for asset types."""

    def test_asset_type_values(self):
        """Test asset type enum values."""
        assert AssetType.DOCUMENT.value == "document"
        assert AssetType.MEDICAL_GUIDELINE.value == "medical_guideline"
        assert AssetType.FHIR_RESOURCE.value == "fhir_resource"
        assert AssetType.HL7_MESSAGE.value == "hl7_message"
        assert AssetType.DICOM_IMAGE.value == "dicom_image"
        assert AssetType.VIDEO.value == "video"
        assert AssetType.FIRMWARE.value == "firmware"
        assert AssetType.DATASET.value == "dataset"

    def test_lifecycle_state_values(self):
        """Test lifecycle state enum values."""
        assert LifecycleState.DRAFT.value == "draft"
        assert LifecycleState.REGISTERED.value == "registered"
        assert LifecycleState.ACTIVE.value == "active"
        assert LifecycleState.ARCHIVED.value == "archived"

    def test_permission_level_values(self):
        """Test permission level enum values."""
        assert PermissionLevel.PUBLIC.value == "public"
        assert PermissionLevel.INTERNAL.value == "internal"
        assert PermissionLevel.CONFIDENTIAL.value == "confidential"


class TestAssetMetadata:
    """Tests for asset metadata."""

    def test_asset_metadata_creation(self):
        """Test asset metadata creation."""
        asset = AssetMetadata(
            asset_id="asset-123",
            asset_type=AssetType.DOCUMENT,
            title="Test Asset",
        )
        assert asset.asset_id == "asset-123"
        assert asset.title == "Test Asset"
        assert asset.lifecycle_state == LifecycleState.REGISTERED

    def test_asset_metadata_to_dict(self):
        """Test metadata to dict."""
        asset = AssetMetadata(
            asset_id="asset-123",
            asset_type=AssetType.MEDICAL_GUIDELINE,
            title="Medical Guide",
            author="Dr. Smith",
        )
        data = asset.to_dict()
        assert data["asset_id"] == "asset-123"
        assert data["asset_type"] == "medical_guideline"
        assert data["author"] == "Dr. Smith"


class TestAssetCatalog:
    """Tests for asset catalog."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset catalog before each test."""
        reset_asset_catalog()

    @pytest.fixture
    def catalog(self):
        """Create test catalog."""
        return AssetCatalog()

    def test_catalog_register(self, catalog):
        """Test registering asset."""
        asset = AssetMetadata(
            asset_id="asset-123",
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )
        result = catalog.register(asset)
        assert result == "asset-123"
        assert catalog.count() == 1

    def test_catalog_get(self, catalog):
        """Test getting asset."""
        asset = AssetMetadata(
            asset_id="asset-123",
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )
        catalog.register(asset)

        retrieved = catalog.get("asset-123")
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_catalog_search(self, catalog):
        """Test searching assets."""
        asset1 = AssetMetadata(
            asset_id="asset-1",
            asset_type=AssetType.MEDICAL_GUIDELINE,
            title="Cardiology Guide",
            tags=["cardiology"],
        )
        asset2 = AssetMetadata(
            asset_id="asset-2",
            asset_type=AssetType.TECHNICAL_MANUAL,
            title="Neurology Guide",
            tags=["neurology"],
        )
        catalog.register(asset1)
        catalog.register(asset2)

        query = AssetSearchQuery(asset_types=[AssetType.MEDICAL_GUIDELINE])
        results = catalog.search(query)
        assert len(results) == 1
        assert results[0].asset_type == AssetType.MEDICAL_GUIDELINE


class TestAssetCollections:
    """Tests for asset collections."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset collections before each test."""
        reset_asset_collections()

    @pytest.fixture
    def collections(self):
        """Create test collections manager."""
        return AssetCollections()

    def test_collections_create(self, collections):
        """Test creating collection."""
        collection = collections.create(
            name="Medical",
            description="Medical guidelines",
            owner="admin",
        )
        assert collection.name == "Medical"
        assert collections.count() == 1

    def test_collections_add_asset(self, collections):
        """Test adding asset to collection."""
        collection = collections.create(name="Medical")
        result = collections.add_asset(collection.collection_id, "asset-123")
        assert result is True

        retrieved = collections.get(collection.collection_id)
        assert "asset-123" in retrieved.asset_ids


class TestVersionManager:
    """Tests for version manager."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset version manager before each test."""
        reset_version_manager()

    @pytest.fixture
    def versions(self):
        """Create test version manager."""
        return VersionManager()

    def test_versions_create(self, versions):
        """Test creating version."""
        version = versions.create_version(
            asset_id="asset-123",
            version="1.0.0",
            created_by="admin",
        )
        assert version.version == "1.0.0"
        assert version.asset_id == "asset-123"

    def test_versions_get_latest(self, versions):
        """Test getting latest version."""
        versions.create_version(asset_id="asset-123", version="1.0.0")
        versions.create_version(asset_id="asset-123", version="1.1.0")

        latest = versions.get_latest("asset-123")
        assert latest.version == "1.1.0"


class TestPermissions:
    """Tests for permissions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset permissions before each test."""
        reset_permissions()

    @pytest.fixture
    def audit(self):
        """Create test audit logger."""
        return AuditLogger()

    @pytest.fixture
    def checker(self):
        """Create test permission checker."""
        return PermissionChecker()

    def test_audit_log(self, audit):
        """Test audit logging."""
        log = audit.log(
            action=AuditAction.REGISTER,
            asset_id="asset-123",
            user_id="admin",
        )
        assert log.audit_id is not None
        assert audit.count() == 1

    def test_permission_checker(self, checker):
        """Test permission checking."""
        checker.set_user_permission("admin", PermissionLevel.CONFIDENTIAL)

        assert checker.can_access("admin", PermissionLevel.PUBLIC) is True
        assert checker.can_access("admin", PermissionLevel.CONFIDENTIAL) is True

    def test_permission_hierarchy(self, checker):
        """Test permission hierarchy."""
        checker.set_user_permission("user", PermissionLevel.PUBLIC)

        assert checker.can_access("user", PermissionLevel.PUBLIC) is True
        assert checker.can_access("user", PermissionLevel.INTERNAL) is False


class TestKnowledgeAssetRegistry:
    """Tests for knowledge asset registry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset all components before each test."""
        reset_asset_catalog()
        reset_asset_collections()
        reset_version_manager()
        reset_permissions()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return KnowledgeAssetRegistry()

    def test_registry_register_document(self, registry):
        """Test registering document asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Clinical Guidelines",
            author="Hospital",
        )
        assert asset.asset_id is not None
        assert asset.title == "Clinical Guidelines"

    def test_registry_register_fhir(self, registry):
        """Test registering FHIR resource."""
        asset = registry.register(
            asset_type=AssetType.FHIR_RESOURCE,
            title="Patient Record",
            author="Hospital",
        )
        assert asset.asset_type == AssetType.FHIR_RESOURCE

    def test_registry_register_hl7(self, registry):
        """Test registering HL7 message."""
        asset = registry.register(
            asset_type=AssetType.HL7_MESSAGE,
            title="ADT Message",
        )
        assert asset.asset_type == AssetType.HL7_MESSAGE

    def test_registry_register_dicom(self, registry):
        """Test registering DICOM image."""
        asset = registry.register(
            asset_type=AssetType.DICOM_IMAGE,
            title="Chest X-Ray",
            hospital="Radiology Dept",
        )
        assert asset.asset_type == AssetType.DICOM_IMAGE

    def test_registry_register_video(self, registry):
        """Test registering video asset."""
        asset = registry.register(
            asset_type=AssetType.VIDEO,
            title="Training Video",
        )
        assert asset.asset_type == AssetType.VIDEO

    def test_registry_register_firmware(self, registry):
        """Test registering firmware."""
        asset = registry.register(
            asset_type=AssetType.FIRMWARE,
            title="Device Firmware v2.0",
        )
        assert asset.asset_type == AssetType.FIRMWARE
        assert asset.version == "1.0.0"  # Default version

    def test_registry_register_dataset(self, registry):
        """Test registering dataset."""
        asset = registry.register(
            asset_type=AssetType.DATASET,
            title="Training Data",
            chunk_count=1000,
            embedding_count=5000,
        )
        assert asset.asset_type == AssetType.DATASET
        assert asset.chunk_count == 1000

    def test_registry_register_custom(self, registry):
        """Test registering custom asset type."""
        asset = registry.register(
            asset_type=AssetType.CUSTOM,
            title="Custom Asset",
        )
        assert asset.asset_type == AssetType.CUSTOM

    def test_registry_get(self, registry):
        """Test getting asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )

        retrieved = registry.get(asset.asset_id)
        assert retrieved.asset_id == asset.asset_id

    def test_registry_get_not_found(self, registry):
        """Test getting non-existent asset."""
        with pytest.raises(AssetNotFoundError):
            registry.get("non-existent")

    def test_registry_update(self, registry):
        """Test updating asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Original",
        )

        updated = registry.update(
            asset_id=asset.asset_id,
            title="Updated",
        )
        assert updated.title == "Updated"

    def test_registry_delete(self, registry):
        """Test deleting asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )

        result = registry.delete(asset.asset_id)
        assert result is True

        # After deletion, state should be DELETED
        retrieved = registry.get(asset.asset_id)
        assert retrieved.lifecycle_state == LifecycleState.DELETED

    def test_registry_archive(self, registry):
        """Test archiving asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )

        archived = registry.archive(asset.asset_id)
        assert archived.lifecycle_state == LifecycleState.ARCHIVED

    def test_registry_restore(self, registry):
        """Test restoring asset."""
        asset = registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Test",
        )
        registry.archive(asset.asset_id)

        restored = registry.restore(asset.asset_id)
        assert restored.lifecycle_state == LifecycleState.ACTIVE

    def test_registry_search(self, registry):
        """Test searching assets."""
        registry.register(
            asset_type=AssetType.MEDICAL_GUIDELINE,
            title="Cardiology Guidelines",
            tags=["cardiology"],
        )
        registry.register(
            asset_type=AssetType.TECHNICAL_MANUAL,
            title="Device Manual",
            tags=["technical"],
        )

        query = AssetSearchQuery(asset_types=[AssetType.MEDICAL_GUIDELINE])
        results = registry.search(query)
        assert len(results) == 1

    def test_registry_statistics(self, registry):
        """Test getting statistics."""
        registry.register(
            asset_type=AssetType.DOCUMENT,
            title="Doc 1",
            chunk_count=10,
        )
        registry.register(
            asset_type=AssetType.FHIR_RESOURCE,
            title="FHIR 1",
            chunk_count=20,
        )

        stats = registry.get_statistics()
        assert stats.total_assets == 2
        assert stats.total_chunks == 30
        assert stats.assets_by_type["document"] == 1
        assert stats.assets_by_type["fhir_resource"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
