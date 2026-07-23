"""Unit tests for EPIC 9: Medical Knowledge Repository."""

import pytest
import asyncio


class TestEPIC9Imports:
    """Tests for EPIC 9 module imports."""

    def test_import_epic9(self):
        """Test EPIC 9 module imports."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Repository,
            KnowledgeVersion,
            Collection,
        )
        assert Repository is not None
        assert KnowledgeVersion is not None

    def test_import_repository(self):
        """Test repository module imports."""
        from core.PHASE_4.epic9_knowledge_repository.repository import (
            RepositoryType,
            Repository,
            InMemoryRepositoryManager,
        )
        assert RepositoryType is not None
        assert Repository is not None

    def test_import_versioning(self):
        """Test versioning module imports."""
        from core.PHASE_4.epic9_knowledge_repository.versioning import (
            VersionType,
            KnowledgeVersion,
            InMemoryVersionManager,
        )
        assert VersionType is not None
        assert KnowledgeVersion is not None

    def test_import_collections(self):
        """Test collections module imports."""
        from core.PHASE_4.epic9_knowledge_repository.collections import (
            CollectionType,
            Collection,
            InMemoryCollectionManager,
        )
        assert CollectionType is not None
        assert Collection is not None


class TestRepository:
    """Tests for Repository."""

    def test_repository_creation(self):
        """Test repository creation."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Repository,
            RepositoryType,
        )
        
        repo = Repository(
            repository_id="repo_1",
            name="Clinical Guidelines",
            repository_type=RepositoryType.PRIMARY,
        )
        
        assert repo.repository_id == "repo_1"
        assert repo.name == "Clinical Guidelines"
        assert repo.repository_type == RepositoryType.PRIMARY

    def test_repository_stats(self):
        """Test repository stats."""
        from core.PHASE_4.epic9_knowledge_repository import RepositoryStats
        
        stats = RepositoryStats(
            total_documents=100,
            total_chunks=500,
        )
        
        assert stats.total_documents == 100
        assert stats.total_chunks == 500


class TestRepositoryManager:
    """Tests for InMemoryRepositoryManager."""

    @pytest.mark.asyncio
    async def test_create_repository(self):
        """Test creating repository."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Repository,
            RepositoryType,
            InMemoryRepositoryManager,
        )
        
        manager = InMemoryRepositoryManager()
        repo = Repository(
            repository_id="repo_1",
            name="Test",
            repository_type=RepositoryType.PRIMARY,
        )
        
        created = await manager.create_repository(repo)
        
        assert created.repository_id == "repo_1"

    @pytest.mark.asyncio
    async def test_get_repository(self):
        """Test getting repository."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Repository,
            RepositoryType,
            InMemoryRepositoryManager,
        )
        
        manager = InMemoryRepositoryManager()
        repo = Repository(
            repository_id="repo_1",
            name="Test",
            repository_type=RepositoryType.PRIMARY,
        )
        
        await manager.create_repository(repo)
        retrieved = await manager.get_repository("repo_1")
        
        assert retrieved is not None
        assert retrieved.name == "Test"


class TestKnowledgeVersion:
    """Tests for KnowledgeVersion."""

    def test_version_creation(self):
        """Test version creation."""
        from core.PHASE_4.epic9_knowledge_repository import (
            KnowledgeVersion,
            VersionType,
        )
        
        version = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.0.0",
            version_type=VersionType.MAJOR,
        )
        
        assert version.version_id == "v1"
        assert version.version_number == "1.0.0"

    def test_version_string(self):
        """Test version string."""
        from core.PHASE_4.epic9_knowledge_repository import KnowledgeVersion
        
        version = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.2.3",
        )
        
        assert version.get_version_string() == "1.2.3"


class TestVersionManager:
    """Tests for InMemoryVersionManager."""

    @pytest.mark.asyncio
    async def test_create_version(self):
        """Test creating version."""
        from core.PHASE_4.epic9_knowledge_repository import (
            KnowledgeVersion,
            VersionType,
            InMemoryVersionManager,
        )
        
        manager = InMemoryVersionManager()
        version = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.0.0",
            version_type=VersionType.MAJOR,
        )
        
        created = await manager.create_version(version)
        
        assert created.version_id == "v1"

    @pytest.mark.asyncio
    async def test_publish_version(self):
        """Test publishing version."""
        from core.PHASE_4.epic9_knowledge_repository import (
            KnowledgeVersion,
            VersionType,
            VersionStatus,
            InMemoryVersionManager,
        )
        
        manager = InMemoryVersionManager()
        version = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.0.0",
            version_type=VersionType.MAJOR,
        )
        
        await manager.create_version(version)
        published = await manager.publish_version("v1")
        
        assert published.status == VersionStatus.PUBLISHED
        assert published.published_at != ""


class TestCollection:
    """Tests for Collection."""

    def test_collection_creation(self):
        """Test collection creation."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Collection,
            CollectionType,
        )
        
        collection = Collection(
            collection_id="col_1",
            name="Cardiology Guidelines",
            collection_type=CollectionType.GUIDELINE,
        )
        
        assert collection.collection_id == "col_1"
        assert collection.collection_type == CollectionType.GUIDELINE

    def test_add_document(self):
        """Test adding document to collection."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Collection,
            CollectionType,
        )
        
        collection = Collection(
            collection_id="col_1",
            name="Test",
            collection_type=CollectionType.GUIDELINE,
        )
        
        collection.add_document("doc_1")
        
        assert collection.document_count == 1
        assert "doc_1" in collection.document_ids

    def test_remove_document(self):
        """Test removing document from collection."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Collection,
            CollectionType,
        )
        
        collection = Collection(
            collection_id="col_1",
            name="Test",
            collection_type=CollectionType.GUIDELINE,
        )
        
        collection.add_document("doc_1")
        collection.remove_document("doc_1")
        
        assert collection.document_count == 0
        assert "doc_1" not in collection.document_ids


class TestCollectionManager:
    """Tests for InMemoryCollectionManager."""

    @pytest.mark.asyncio
    async def test_create_collection(self):
        """Test creating collection."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Collection,
            CollectionType,
            InMemoryCollectionManager,
        )
        
        manager = InMemoryCollectionManager()
        collection = Collection(
            collection_id="col_1",
            name="Test",
            collection_type=CollectionType.GUIDELINE,
        )
        
        created = await manager.create_collection(collection)
        
        assert created.collection_id == "col_1"

    @pytest.mark.asyncio
    async def test_add_to_collection(self):
        """Test adding document to collection."""
        from core.PHASE_4.epic9_knowledge_repository import (
            Collection,
            CollectionType,
            InMemoryCollectionManager,
        )
        
        manager = InMemoryCollectionManager()
        collection = Collection(
            collection_id="col_1",
            name="Test",
            collection_type=CollectionType.GUIDELINE,
        )
        
        await manager.create_collection(collection)
        updated = await manager.add_to_collection("col_1", "doc_1")
        
        assert updated.document_count == 1


class TestVersionHistory:
    """Tests for VersionHistory."""

    def test_add_version(self):
        """Test adding version to history."""
        from core.PHASE_4.epic9_knowledge_repository import (
            KnowledgeVersion,
            VersionHistory,
        )
        
        history = VersionHistory(document_id="doc_1")
        version = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.0.0",
        )
        
        history.add_version(version)
        
        assert len(history.versions) == 1
        assert history.current_version == ""

    def test_get_published_versions(self):
        """Test getting published versions."""
        from core.PHASE_4.epic9_knowledge_repository import (
            KnowledgeVersion,
            VersionStatus,
            VersionHistory,
        )
        
        history = VersionHistory(document_id="doc_1")
        
        v1 = KnowledgeVersion(
            version_id="v1",
            document_id="doc_1",
            version_number="1.0.0",
            status=VersionStatus.PUBLISHED,
        )
        v2 = KnowledgeVersion(
            version_id="v2",
            document_id="doc_1",
            version_number="1.0.1",
            status=VersionStatus.DRAFT,
        )
        
        history.add_version(v1)
        history.add_version(v2)
        
        published = history.get_published_versions()
        
        assert len(published) == 1
        assert published[0].version_id == "v1"


class TestCollectionTypes:
    """Tests for CollectionType."""

    def test_collection_types(self):
        """Test collection type enum."""
        from core.PHASE_4.epic9_knowledge_repository import CollectionType
        
        assert CollectionType.GUIDELINE.value == "guideline"
        assert CollectionType.PROTOCOL.value == "protocol"
        assert CollectionType.TRAINING.value == "training"


class TestVersionTypes:
    """Tests for VersionType."""

    def test_version_types(self):
        """Test version type enum."""
        from core.PHASE_4.epic9_knowledge_repository import VersionType
        
        assert VersionType.MAJOR.value == "major"
        assert VersionType.MINOR.value == "minor"
        assert VersionType.PATCH.value == "patch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
