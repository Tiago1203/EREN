"""Unit tests for EREN Knowledge Registry."""

import pytest

from core.PHASE_1.domain.knowledge.registry_types import (
    KnowledgeEntry,
    KnowledgeStatus,
    PermissionLevel,
    KnowledgeVersion,
    KnowledgeCollection,
    AuditLog,
    AuditAction,
    RegistrySearchQuery,
    RegistryStatistics,
)
from core.PHASE_1.domain.knowledge.registry_exceptions import (
    KnowledgeNotFoundError,
    DuplicateKnowledgeError,
)
from core.PHASE_1.domain.knowledge.catalog import (
    KnowledgeCatalog,
    get_knowledge_catalog,
    reset_knowledge_catalog,
)
from core.PHASE_1.domain.knowledge.collections import (
    KnowledgeCollections,
    get_knowledge_collections,
    reset_knowledge_collections,
)
from core.PHASE_1.domain.knowledge.versions import (
    VersionManager,
    get_version_manager,
    reset_version_manager,
)
from core.PHASE_1.domain.knowledge.permissions import (
    AuditLogger,
    PermissionChecker,
    get_audit_logger,
    reset_permissions,
)
from core.PHASE_1.domain.knowledge.registry import KnowledgeRegistry


class TestRegistryTypes:
    """Tests for registry types."""

    def test_knowledge_entry_creation(self):
        """Test knowledge entry creation."""
        entry = KnowledgeEntry(
            knowledge_id="test-123",
            document_id="doc-456",
            title="Test Knowledge",
        )
        assert entry.knowledge_id == "test-123"
        assert entry.title == "Test Knowledge"
        assert entry.status == KnowledgeStatus.REGISTERED

    def test_knowledge_entry_to_dict(self):
        """Test entry to dict."""
        entry = KnowledgeEntry(
            knowledge_id="test-123",
            document_id="doc-456",
            title="Test Knowledge",
        )
        data = entry.to_dict()
        assert data["knowledge_id"] == "test-123"
        assert "created_at" in data

    def test_knowledge_version_creation(self):
        """Test version creation."""
        version = KnowledgeVersion(
            version_id="v-123",
            knowledge_id="k-456",
            version="1.0.0",
        )
        assert version.version == "1.0.0"

    def test_knowledge_collection_creation(self):
        """Test collection creation."""
        collection = KnowledgeCollection(
            collection_id="c-123",
            name="Medical Guidelines",
            owner="admin",
        )
        assert collection.name == "Medical Guidelines"
        assert collection.size == 0

    def test_audit_log_creation(self):
        """Test audit log creation."""
        log = AuditLog(
            audit_id="a-123",
            action=AuditAction.REGISTER,
            knowledge_id="k-456",
        )
        assert log.action == AuditAction.REGISTER

    def test_registry_search_query_defaults(self):
        """Test search query defaults."""
        query = RegistrySearchQuery()
        assert query.limit == 100
        assert query.offset == 0

    def test_registry_statistics_defaults(self):
        """Test statistics defaults."""
        stats = RegistryStatistics()
        assert stats.total_entries == 0
        assert stats.total_collections == 0


class TestKnowledgeCatalog:
    """Tests for knowledge catalog."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset catalog before each test."""
        reset_knowledge_catalog()

    @pytest.fixture
    def catalog(self):
        """Create test catalog."""
        return KnowledgeCatalog()

    def test_catalog_register(self, catalog):
        """Test registering entry."""
        entry = KnowledgeEntry(
            knowledge_id="k-123",
            document_id="doc-456",
            title="Test",
        )
        result = catalog.register(entry)
        assert result == "k-123"
        assert catalog.count() == 1

    def test_catalog_get(self, catalog):
        """Test getting entry."""
        entry = KnowledgeEntry(
            knowledge_id="k-123",
            document_id="doc-456",
            title="Test",
        )
        catalog.register(entry)

        retrieved = catalog.get("k-123")
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_catalog_get_by_document(self, catalog):
        """Test getting by document ID."""
        entry = KnowledgeEntry(
            knowledge_id="k-123",
            document_id="doc-456",
            title="Test",
        )
        catalog.register(entry)

        retrieved = catalog.get_by_document("doc-456")
        assert retrieved is not None
        assert retrieved.knowledge_id == "k-123"

    def test_catalog_update(self, catalog):
        """Test updating entry."""
        entry = KnowledgeEntry(
            knowledge_id="k-123",
            document_id="doc-456",
            title="Test",
        )
        catalog.register(entry)

        entry.title = "Updated"
        result = catalog.update(entry)
        assert result is True

        retrieved = catalog.get("k-123")
        assert retrieved.title == "Updated"

    def test_catalog_delete(self, catalog):
        """Test deleting entry."""
        entry = KnowledgeEntry(
            knowledge_id="k-123",
            document_id="doc-456",
            title="Test",
        )
        catalog.register(entry)

        result = catalog.delete("k-123")
        assert result is True
        assert catalog.count() == 0


class TestKnowledgeCollections:
    """Tests for knowledge collections."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset collections before each test."""
        reset_knowledge_collections()

    @pytest.fixture
    def collections(self):
        """Create test collections manager."""
        return KnowledgeCollections()

    def test_collections_create(self, collections):
        """Test creating collection."""
        collection = collections.create(
            name="Medical",
            description="Medical guidelines",
            owner="admin",
        )
        assert collection.name == "Medical"
        assert collections.count() == 1

    def test_collections_get(self, collections):
        """Test getting collection."""
        collection = collections.create(name="Medical")
        retrieved = collections.get(collection.collection_id)
        assert retrieved is not None
        assert retrieved.name == "Medical"

    def test_collections_add_knowledge(self, collections):
        """Test adding knowledge to collection."""
        collection = collections.create(name="Medical")
        result = collections.add_knowledge(collection.collection_id, "k-123")
        assert result is True

        retrieved = collections.get(collection.collection_id)
        assert "k-123" in retrieved.knowledge_ids


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
            knowledge_id="k-123",
            version="1.0.0",
            created_by="admin",
        )
        assert version.version == "1.0.0"
        assert version.knowledge_id == "k-123"

    def test_versions_get_versions(self, versions):
        """Test getting versions."""
        versions.create_version(knowledge_id="k-123", version="1.0.0")
        versions.create_version(knowledge_id="k-123", version="1.1.0")

        vlist = versions.get_versions("k-123")
        assert len(vlist) == 2

    def test_versions_get_latest(self, versions):
        """Test getting latest version."""
        versions.create_version(knowledge_id="k-123", version="1.0.0")
        versions.create_version(knowledge_id="k-123", version="1.1.0")

        latest = versions.get_latest("k-123")
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
            knowledge_id="k-123",
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


class TestKnowledgeRegistry:
    """Tests for knowledge registry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset all components before each test."""
        reset_knowledge_catalog()
        reset_knowledge_collections()
        reset_version_manager()
        reset_permissions()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return KnowledgeRegistry()

    def test_registry_register(self, registry):
        """Test registering knowledge."""
        entry = registry.register(
            document_id="doc-123",
            title="Medical Guidelines",
            doc_type="guideline",
            medical_specialty="cardiology",
            author="Dr. Smith",
        )
        assert entry.knowledge_id is not None
        assert entry.title == "Medical Guidelines"

    def test_registry_register_duplicate(self, registry):
        """Test registering duplicate document."""
        registry.register(
            document_id="doc-123",
            title="First",
        )

        with pytest.raises(DuplicateKnowledgeError):
            registry.register(
                document_id="doc-123",
                title="Second",
            )

    def test_registry_get(self, registry):
        """Test getting knowledge."""
        entry = registry.register(
            document_id="doc-123",
            title="Test",
        )

        retrieved = registry.get(entry.knowledge_id)
        assert retrieved.knowledge_id == entry.knowledge_id

    def test_registry_get_not_found(self, registry):
        """Test getting non-existent knowledge."""
        with pytest.raises(KnowledgeNotFoundError):
            registry.get("non-existent")

    def test_registry_update(self, registry):
        """Test updating knowledge."""
        entry = registry.register(
            document_id="doc-123",
            title="Original",
        )

        updated = registry.update(
            knowledge_id=entry.knowledge_id,
            title="Updated",
        )
        assert updated.title == "Updated"

    def test_registry_delete(self, registry):
        """Test deleting knowledge."""
        entry = registry.register(
            document_id="doc-123",
            title="Test",
        )

        result = registry.delete(entry.knowledge_id)
        assert result is True

        # After deletion, status should be DELETED
        retrieved = registry.get(entry.knowledge_id)
        assert retrieved.status == KnowledgeStatus.DELETED

    def test_registry_search(self, registry):
        """Test searching knowledge."""
        registry.register(
            document_id="doc-1",
            title="Cardiology Guidelines",
            medical_specialty="cardiology",
        )
        registry.register(
            document_id="doc-2",
            title="Neurology Guidelines",
            medical_specialty="neurology",
        )

        query = RegistrySearchQuery(
            specialties=["cardiology"],
        )
        results = registry.search(query)
        assert len(results) == 1
        assert results[0].medical_specialty == "cardiology"

    def test_registry_statistics(self, registry):
        """Test getting statistics."""
        registry.register(
            document_id="doc-1",
            title="Doc 1",
            medical_specialty="cardiology",
            chunk_count=10,
        )
        registry.register(
            document_id="doc-2",
            title="Doc 2",
            medical_specialty="neurology",
            chunk_count=20,
        )

        stats = registry.get_statistics()
        assert stats.total_entries == 2
        assert stats.total_chunks == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
