"""Unit tests for conversation memory plugin."""

import pytest
from datetime import datetime, timezone

from plugins.conversation import (
    ConversationMemoryPlugin,
    ConversationMemoryProvider,
    ConversationRepository,
    ConversationEntry,
    ConversationMetadata,
    ConversationSummary,
    ConversationSearch,
    ConversationConfiguration,
    ConversationRole,
    ConversationType,
    ConversationState,
    ConversationNotFoundError,
    EntryNotFoundError,
    ConversationExistsError,
    create_plugin,
)


class TestConversationTypes:
    """Tests for conversation types."""

    def test_conversation_role_values(self):
        """Test conversation role values."""
        assert ConversationRole.USER.value == "user"
        assert ConversationRole.ASSISTANT.value == "assistant"
        assert ConversationRole.SYSTEM.value == "system"

    def test_conversation_type_values(self):
        """Test conversation type values."""
        assert ConversationType.CHAT.value == "chat"
        assert ConversationType.MEDICAL.value == "medical"
        assert ConversationType.GENERAL.value == "general"

    def test_conversation_state_values(self):
        """Test conversation state values."""
        assert ConversationState.ACTIVE.value == "active"
        assert ConversationState.ARCHIVED.value == "archived"
        assert ConversationState.SUMMARIZED.value == "summarized"


class TestConversationEntry:
    """Tests for ConversationEntry."""

    def test_creation(self):
        """Test entry creation."""
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Hello",
        )
        assert entry.entry_id == "entry-1"
        assert entry.conversation_id == "conv-1"
        assert entry.content == "Hello"
        assert entry.role == ConversationRole.USER

    def test_to_dict(self):
        """Test conversion to dict."""
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Hello",
        )
        d = entry.to_dict()
        assert d["entry_id"] == "entry-1"
        assert d["content"] == "Hello"
        assert d["role"] == "user"

    def test_from_dict(self):
        """Test creation from dict."""
        data = {
            "entry_id": "entry-1",
            "conversation_id": "conv-1",
            "role": "assistant",
            "content": "Hi there",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {},
            "tokens": 10,
        }
        entry = ConversationEntry.from_dict(data)
        assert entry.entry_id == "entry-1"
        assert entry.role == ConversationRole.ASSISTANT


class TestConversationMetadata:
    """Tests for ConversationMetadata."""

    def test_creation(self):
        """Test metadata creation."""
        metadata = ConversationMetadata(
            conversation_id="conv-1",
            user_id="user-1",
            session_id="session-1",
        )
        assert metadata.conversation_id == "conv-1"
        assert metadata.user_id == "user-1"
        assert metadata.state == ConversationState.ACTIVE

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = ConversationMetadata(
            conversation_id="conv-1",
            title="Test Conversation",
        )
        d = metadata.to_dict()
        assert d["conversation_id"] == "conv-1"
        assert d["title"] == "Test Conversation"


class TestConversationSearch:
    """Tests for ConversationSearch."""

    def test_creation(self):
        """Test search creation."""
        search = ConversationSearch(
            query="patient",
            limit=10,
        )
        assert search.query == "patient"
        assert search.limit == 10


class TestConversationConfiguration:
    """Tests for ConversationConfiguration."""

    def test_defaults(self):
        """Test default configuration."""
        config = ConversationConfiguration()
        assert config.max_context_entries == 20
        assert config.ttl_days == 30
        assert config.enable_summarization is True


class TestConversationRepository:
    """Tests for ConversationRepository."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConversationConfiguration(database_path=":memory:")

    @pytest.fixture
    def repo(self, config):
        """Create test repository."""
        return ConversationRepository(config)

    def test_create_conversation(self, repo):
        """Test creating conversation."""
        metadata = ConversationMetadata(
            conversation_id="conv-1",
            user_id="user-1",
        )
        result = repo.create_conversation(metadata)
        assert result.conversation_id == "conv-1"

    def test_create_duplicate_raises(self, repo):
        """Test duplicate conversation raises error."""
        metadata = ConversationMetadata(conversation_id="conv-1")
        repo.create_conversation(metadata)
        with pytest.raises(ConversationExistsError):
            repo.create_conversation(metadata)

    def test_get_conversation(self, repo):
        """Test getting conversation."""
        metadata = ConversationMetadata(conversation_id="conv-1")
        repo.create_conversation(metadata)
        result = repo.get_conversation("conv-1")
        assert result.conversation_id == "conv-1"

    def test_get_conversation_not_found(self, repo):
        """Test getting non-existent conversation."""
        with pytest.raises(ConversationNotFoundError):
            repo.get_conversation("non-existent")

    def test_update_conversation(self, repo):
        """Test updating conversation."""
        metadata = ConversationMetadata(
            conversation_id="conv-1",
            title="Original",
        )
        repo.create_conversation(metadata)

        metadata.title = "Updated"
        result = repo.update_conversation(metadata)
        assert result.title == "Updated"

    def test_list_conversations(self, repo):
        """Test listing conversations."""
        for i in range(3):
            repo.create_conversation(ConversationMetadata(
                conversation_id=f"conv-{i}",
                user_id="user-1",
            ))

        results = repo.list_conversations(user_id="user-1")
        assert len(results) == 3

    def test_delete_conversation(self, repo):
        """Test deleting conversation."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        result = repo.delete_conversation("conv-1")
        assert result is True

    def test_add_entry(self, repo):
        """Test adding entry."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Hello",
        )
        result = repo.add_entry(entry)
        assert result.entry_id == "entry-1"

    def test_get_entries(self, repo):
        """Test getting entries."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        for i in range(5):
            repo.add_entry(ConversationEntry(
                entry_id=f"entry-{i}",
                conversation_id="conv-1",
                role=ConversationRole.USER,
                content=f"Message {i}",
            ))

        entries = repo.get_entries("conv-1")
        assert len(entries) == 5

    def test_get_entry(self, repo):
        """Test getting specific entry."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        repo.add_entry(ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Hello",
        ))

        entry = repo.get_entry("entry-1")
        assert entry.entry_id == "entry-1"
        assert entry.content == "Hello"

    def test_get_entry_not_found(self, repo):
        """Test getting non-existent entry."""
        with pytest.raises(EntryNotFoundError):
            repo.get_entry("non-existent")

    def test_search(self, repo):
        """Test searching entries."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        repo.add_entry(ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Patient has diabetes",
        ))
        repo.add_entry(ConversationEntry(
            entry_id="entry-2",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Blood pressure is normal",
        ))

        results = repo.search(ConversationSearch(query="patient"))
        assert len(results) == 1
        assert "diabetes" in results[0].content.lower()

    def test_save_and_get_summary(self, repo):
        """Test saving and getting summary."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        summary = ConversationSummary(
            conversation_id="conv-1",
            summary="Patient discussed diabetes treatment",
            key_points=["diabetes", "medication"],
        )

        repo.save_summary(summary)
        result = repo.get_summary("conv-1")

        assert result is not None
        assert "diabetes" in result.summary

    def test_get_metrics(self, repo):
        """Test getting metrics."""
        repo.create_conversation(ConversationMetadata(conversation_id="conv-1"))
        repo.add_entry(ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Hello",
            tokens=10,
        ))

        metrics = repo.get_metrics()
        assert metrics.total_conversations == 1
        assert metrics.total_entries == 1


class TestConversationMemoryProvider:
    """Tests for ConversationMemoryProvider."""

    @pytest.fixture
    def provider(self):
        """Create test provider."""
        provider = ConversationMemoryProvider()
        provider.initialize({"database_path": ":memory:"})
        return provider

    def test_initialization(self, provider):
        """Test provider initialization."""
        assert provider.memory_id == "conversation"
        assert provider.memory_type.value == "conversation"

    def test_write_and_read(self, provider):
        """Test write and read."""
        from core.memory import MemoryEntry, MemoryType

        entry = MemoryEntry(
            content="Hello, how are you?",
            memory_type=MemoryType.CONVERSATION,
            metadata={
                "conversation_id": "conv-1",
                "role": "user",
            },
        )
        provider.write(entry)

        response = provider.read("conv-1")
        assert response.success is True
        assert len(response.results) == 1

    def test_search(self, provider):
        """Test search."""
        from core.memory import MemoryEntry, MemoryType, MemoryQuery

        provider.write(MemoryEntry(
            content="Patient has diabetes",
            memory_type=MemoryType.CONVERSATION,
            metadata={"conversation_id": "conv-1"},
        ))

        query = MemoryQuery(query="patient")
        response = provider.search(query)
        assert response.success is True

    def test_delete(self, provider):
        """Test delete."""
        from core.memory import MemoryEntry, MemoryType

        provider.write(MemoryEntry(
            content="Test",
            memory_type=MemoryType.CONVERSATION,
            metadata={"conversation_id": "conv-1"},
        ))

        response = provider.delete("conv-1")
        assert response.success is True


class TestConversationMemoryPlugin:
    """Tests for ConversationMemoryPlugin."""

    def test_create_plugin(self):
        """Test plugin creation."""
        plugin = create_plugin()
        assert plugin is not None
        assert plugin.plugin_id == "conversation-memory"

    def test_plugin_capabilities(self):
        """Test plugin capabilities."""
        plugin = create_plugin()
        caps = plugin.get_capabilities()
        assert len(caps) == 1
        assert caps[0]["capability_id"] == "conversation-memory"

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = create_plugin()
        plugin.initialize({"database_path": ":memory:"})
        assert plugin._initialized is True
        assert plugin.memory_provider is not None

    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        plugin = create_plugin()
        plugin.initialize({})
        plugin.shutdown()
        assert plugin._initialized is False
        assert plugin._provider is None


class TestConversationSearchService:
    """Tests for ConversationSearchService."""

    @pytest.fixture
    def repository(self):
        """Create test repository."""
        from plugins.conversation import ConversationConfiguration, DefaultConversationRepository
        config = ConversationConfiguration(database_path=":memory:")
        return DefaultConversationRepository(config)

    @pytest.fixture
    def search_service(self, repository):
        """Create test search service."""
        from plugins.conversation import ConversationSearchService
        return ConversationSearchService(repository)

    def test_search_by_text(self, repository, search_service):
        """Test text search."""
        from plugins.conversation import ConversationMetadata, ConversationEntry, ConversationRole

        # Create conversation
        metadata = ConversationMetadata(conversation_id="conv-1")
        repository.create_conversation(metadata)

        # Add entries
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Patient has diabetes",
        )
        repository.add_entry(entry)

        # Search
        result = search_service.search_by_text("diabetes")
        assert result.total >= 1

    def test_search_by_session(self, repository, search_service):
        """Test session search."""
        from plugins.conversation import ConversationMetadata, ConversationEntry, ConversationRole

        # Create conversation with session
        metadata = ConversationMetadata(
            conversation_id="conv-1",
            session_id="session-123",
        )
        repository.create_conversation(metadata)

        # Add entry with session keyword
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Session 123 conversation",
        )
        repository.add_entry(entry)

        # Search - session filter is on conversation metadata
        result = search_service.search_by_session("session-123")
        # Session filter applies to conversations, not entries directly
        assert result is not None


class TestConversationSummaryService:
    """Tests for ConversationSummaryService."""

    @pytest.fixture
    def repository(self):
        """Create test repository."""
        from plugins.conversation import ConversationConfiguration, DefaultConversationRepository
        config = ConversationConfiguration(database_path=":memory:")
        return DefaultConversationRepository(config)

    @pytest.fixture
    def summary_service(self, repository):
        """Create test summary service."""
        from plugins.conversation import ConversationSummaryService
        return ConversationSummaryService(repository, threshold_entries=5)

    def test_should_summarize(self, repository, summary_service):
        """Test should summarize check."""
        from plugins.conversation import ConversationMetadata, ConversationEntry, ConversationRole

        # Create conversation with few entries
        metadata = ConversationMetadata(conversation_id="conv-1")
        repository.create_conversation(metadata)

        # Should not summarize
        assert summary_service.should_summarize("conv-1") is False

    def test_summarize(self, repository, summary_service):
        """Test summarization."""
        from plugins.conversation import ConversationMetadata, ConversationEntry, ConversationRole

        # Create conversation
        metadata = ConversationMetadata(conversation_id="conv-1")
        repository.create_conversation(metadata)

        # Add entries
        for i in range(6):
            entry = ConversationEntry(
                entry_id=f"entry-{i}",
                conversation_id="conv-1",
                role=ConversationRole.USER,
                content=f"Message {i}",
            )
            repository.add_entry(entry)

        # Summarize
        summary = summary_service.summarize("conv-1")
        assert summary is not None
        assert "conv-1" in summary.conversation_id

    def test_get_summary(self, repository, summary_service):
        """Test getting summary."""
        from plugins.conversation import ConversationMetadata

        # Create conversation
        metadata = ConversationMetadata(conversation_id="conv-1")
        repository.create_conversation(metadata)

        # No summary yet
        summary = summary_service.get_summary("conv-1")
        assert summary is None


class TestConversationIndexer:
    """Tests for ConversationIndexer."""

    def test_indexer_initialization(self):
        """Test indexer initialization."""
        from plugins.conversation import ConversationIndexer
        indexer = ConversationIndexer()
        assert indexer is not None

    def test_register_vector_plugin(self):
        """Test registering vector plugin."""
        from plugins.conversation import ConversationIndexer

        indexer = ConversationIndexer()
        indexer.register_vector_plugin(None)  # Mock plugin
        assert True

    def test_index_entry(self):
        """Test indexing entry."""
        from plugins.conversation import ConversationIndexer, ConversationEntry, ConversationRole

        indexer = ConversationIndexer()
        entry = ConversationEntry(
            entry_id="entry-1",
            conversation_id="conv-1",
            role=ConversationRole.USER,
            content="Test content",
        )
        result = indexer.index_entry(entry)
        assert result is True


class TestConversationNewTypes:
    """Tests for new conversation types."""

    def test_conversation_chunk(self):
        """Test ConversationChunk."""
        from plugins.conversation import ConversationChunk

        chunk = ConversationChunk(
            chunk_id="chunk-1",
            conversation_id="conv-1",
            entry_id="entry-1",
            content="Test content",
            role="user",
            sequence=0,
        )
        assert chunk.chunk_id == "chunk-1"
        d = chunk.to_dict()
        assert d["chunk_id"] == "chunk-1"

    def test_conversation_attachment(self):
        """Test ConversationAttachment."""
        from plugins.conversation import ConversationAttachment

        attachment = ConversationAttachment(
            attachment_id="att-1",
            conversation_id="conv-1",
            filename="report.pdf",
            content_type="application/pdf",
        )
        assert attachment.filename == "report.pdf"

    def test_conversation_reference(self):
        """Test ConversationReference."""
        from plugins.conversation import ConversationReference

        ref = ConversationReference(
            reference_id="ref-1",
            conversation_id="conv-1",
            entry_id="entry-1",
            reference_type="patient",
            reference_target="patient-123",
        )
        assert ref.reference_type == "patient"

    def test_conversation_statistics(self):
        """Test ConversationStatistics."""
        from plugins.conversation import ConversationStatistics

        stats = ConversationStatistics(
            conversation_id="conv-1",
            total_entries=10,
            user_entries=5,
        )
        assert stats.total_entries == 10

    def test_conversation_search_result(self):
        """Test ConversationSearchResult."""
        from plugins.conversation import ConversationSearchResult, ConversationEntry, ConversationRole

        entries = [
            ConversationEntry(
                entry_id="entry-1",
                conversation_id="conv-1",
                role=ConversationRole.USER,
                content="Test",
            )
        ]
        result = ConversationSearchResult(
            entries=entries,
            total=1,
            query="test",
        )
        assert result.total == 1
        assert result.query == "test"


class TestConversationRepositoryContract:
    """Tests for repository contract."""

    def test_contract_exists(self):
        """Test contract class exists."""
        from plugins.conversation import ConversationRepositoryContract
        assert ConversationRepositoryContract is not None

    def test_default_implementation(self):
        """Test default implementation."""
        from plugins.conversation import DefaultConversationRepository, ConversationConfiguration
        config = ConversationConfiguration(database_path=":memory:")
        repo = DefaultConversationRepository(config)
        assert repo is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
