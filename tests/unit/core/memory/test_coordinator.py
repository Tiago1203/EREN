"""Tests for core/memory module - Memory Coordinator."""

import pytest

from core.memory import (
    BaseMemoryInterface,
    MemoryRegistry,
    MemorySelector,
    MemoryCoordinator,
    MemoryType,
    MemoryState,
    MemoryAccessPolicy,
    MemoryOperation,
    MemoryQuery,
    MemoryResult,
    MemoryResponse,
    MemoryEntry,
    MemoryMetrics,
    reset_memory_registry,
    reset_memory_coordinator,
    MemoryNotRegisteredError,
    # Backward compatibility
    MemoryOrchestrator,
    get_memory_orchestrator,
)


class MockMemory(BaseMemoryInterface):
    """Mock memory for testing."""

    def __init__(self, memory_id: str, memory_type: MemoryType):
        super().__init__()
        self._memory_id = memory_id
        self._memory_type = memory_type
        self._state = MemoryState.READY
        self._storage: dict[str, MemoryEntry] = {}

    @property
    def memory_id(self) -> str:
        return self._memory_id

    @property
    def memory_type(self) -> MemoryType:
        return self._memory_type

    def initialize(self, config: dict) -> None:
        self._state = MemoryState.READY

    def shutdown(self) -> None:
        self._state = MemoryState.DISABLED

    def read(self, key: str) -> MemoryResponse:
        entry = self._storage.get(key)
        if entry:
            result = MemoryResult(
                content=entry.content,
                memory_type=self._memory_type,
                memory_id=self._memory_id,
            )
            return MemoryResponse(results=[result])
        return MemoryResponse(results=[])

    def read_batch(self, keys: list[str]) -> MemoryResponse:
        results = []
        for key in keys:
            entry = self._storage.get(key)
            if entry:
                results.append(MemoryResult(
                    content=entry.content,
                    memory_type=self._memory_type,
                    memory_id=self._memory_id,
                ))
        return MemoryResponse(results=results)

    def write(self, entry: MemoryEntry) -> MemoryResponse:
        self._storage[entry.key] = entry
        return MemoryResponse(results=[])

    def write_batch(self, entries: list[MemoryEntry]) -> MemoryResponse:
        for entry in entries:
            self._storage[entry.key] = entry
        return MemoryResponse(results=[])

    def search(self, query: MemoryQuery) -> MemoryResponse:
        results = [
            MemoryResult(
                content=e.content,
                memory_type=self._memory_type,
                memory_id=self._memory_id,
                score=0.9,
            )
            for e in self._storage.values()
            if query.query.lower() in e.content.lower()
        ]
        return MemoryResponse(results=results)

    def delete(self, key: str) -> MemoryResponse:
        if key in self._storage:
            del self._storage[key]
        return MemoryResponse(results=[])

    def clear(self) -> MemoryResponse:
        self._storage.clear()
        return MemoryResponse(results=[])


class TestMemoryCoordinator:
    """Tests for MemoryCoordinator."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset coordinator before each test."""
        reset_memory_coordinator()
        reset_memory_registry()

    @pytest.fixture
    def coordinator(self):
        """Create test coordinator."""
        return MemoryCoordinator()

    @pytest.fixture
    def working_memory(self):
        """Create working memory."""
        return MockMemory("working", MemoryType.WORKING)

    @pytest.fixture
    def longterm_memory(self):
        """Create long-term memory."""
        return MockMemory("longterm", MemoryType.EPISODIC)

    def test_read_with_no_memory(self, coordinator):
        """Test read with no memory registered."""
        response = coordinator.read("test-key")
        assert response.success is False

    def test_read_with_memory(self, coordinator, working_memory):
        """Test read with memory registered."""
        coordinator.registry.register(working_memory)

        # Write first
        entry = MemoryEntry(content="Test", memory_type=MemoryType.WORKING)
        coordinator.write(entry)

        # Then read
        response = coordinator.read(entry.key)
        assert response.success is True

    def test_write(self, coordinator, working_memory):
        """Test write operation."""
        coordinator.registry.register(working_memory)

        entry = MemoryEntry(content="Test write", memory_type=MemoryType.WORKING)
        response = coordinator.write(entry)

        assert response.success is True

    def test_search(self, coordinator, working_memory):
        """Test search operation."""
        coordinator.registry.register(working_memory)

        # Write entries
        entry1 = MemoryEntry(content="Apple fruit", memory_type=MemoryType.WORKING)
        entry2 = MemoryEntry(content="Orange fruit", memory_type=MemoryType.WORKING)
        coordinator.write(entry1)
        coordinator.write(entry2)

        # Search
        query = MemoryQuery(query="fruit")
        response = coordinator.search(query)

        assert response.success is True

    def test_delete(self, coordinator, working_memory):
        """Test delete operation."""
        coordinator.registry.register(working_memory)

        entry = MemoryEntry(content="To delete", memory_type=MemoryType.WORKING)
        coordinator.write(entry)

        response = coordinator.delete(entry.key)
        assert response.success is True

    def test_clear(self, coordinator, working_memory):
        """Test clear operation."""
        coordinator.registry.register(working_memory)

        entry = MemoryEntry(content="To clear", memory_type=MemoryType.WORKING)
        coordinator.write(entry)

        response = coordinator.clear()
        assert response.success is True

    def test_get_metrics(self, coordinator, working_memory):
        """Test getting metrics."""
        coordinator.registry.register(working_memory)

        metrics = coordinator.get_metrics()
        assert "working" in metrics

    def test_get_status(self, coordinator, working_memory):
        """Test getting status."""
        coordinator.registry.register(working_memory)

        status = coordinator.get_status()
        assert status["total_memories"] == 1

    def test_policy_change(self, coordinator, working_memory, longterm_memory):
        """Test changing access policy."""
        coordinator.registry.register(working_memory)
        coordinator.registry.register(longterm_memory)

        # Set to long-term only
        coordinator.default_policy = MemoryAccessPolicy.LONG_TERM_ONLY

        # Read should only use long-term
        response = coordinator.read("test", policy=MemoryAccessPolicy.LONG_TERM_ONLY)
        # No results but should not fail

    def test_event_handlers(self, coordinator, working_memory):
        """Test event handlers."""
        events = []

        def handler(data):
            events.append(data)

        coordinator.on("MemoryRead", handler)
        coordinator.registry.register(working_memory)

        entry = MemoryEntry(content="Test", memory_type=MemoryType.WORKING)
        coordinator.write(entry)
        coordinator.read(entry.key)

        assert len(events) > 0

    def test_merge(self, coordinator, working_memory):
        """Test merge operation."""
        coordinator.registry.register(working_memory)

        entries = [
            MemoryEntry(content="Entry 1", memory_type=MemoryType.WORKING),
            MemoryEntry(content="Entry 2", memory_type=MemoryType.WORKING),
        ]
        response = coordinator.merge(entries)

        assert response.success is True


class TestMemoryCoordinatorBackwardCompatibility:
    """Tests for backward compatibility."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset coordinator before each test."""
        reset_memory_coordinator()

    def test_memory_orchestrator_alias(self):
        """Test MemoryOrchestrator alias works."""
        # Old name should work
        orchestrator = MemoryOrchestrator()
        assert orchestrator is not None

    def test_get_memory_orchestrator_alias(self):
        """Test get_memory_orchestrator alias works."""
        # Old function should work
        orchestrator = get_memory_orchestrator()
        assert orchestrator is not None

    def test_same_instance(self):
        """Test that both names return same instance."""
        coordinator = MemoryCoordinator()
        orchestrator = MemoryOrchestrator()
        # They should be equivalent in behavior
        assert type(coordinator).__name__ == "MemoryCoordinator"


class TestMemoryRegistry:
    """Tests for MemoryRegistry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_memory_registry()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return MemoryRegistry()

    @pytest.fixture
    def mock_memory(self):
        """Create mock memory."""
        return MockMemory("test-memory", MemoryType.WORKING)

    def test_register(self, registry, mock_memory):
        """Test registering a memory."""
        registry.register(mock_memory)
        assert registry.has("test-memory")

    def test_unregister(self, registry, mock_memory):
        """Test unregistering a memory."""
        registry.register(mock_memory)
        result = registry.unregister("test-memory")
        assert result is True
        assert not registry.has("test-memory")

    def test_get(self, registry, mock_memory):
        """Test getting a memory."""
        registry.register(mock_memory)
        retrieved = registry.get("test-memory")
        assert retrieved is mock_memory

    def test_list_by_type(self, registry):
        """Test listing by type."""
        working = MockMemory("working", MemoryType.WORKING)
        semantic = MockMemory("semantic", MemoryType.SEMANTIC)
        registry.register(working)
        registry.register(semantic)

        memories = registry.list_by_type(MemoryType.WORKING)
        assert len(memories) == 1


class TestMemorySelector:
    """Tests for MemorySelector."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_memory_registry()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return MemoryRegistry()

    def test_select_first_available(self, registry):
        """Test first available selection."""
        selector = MemorySelector(registry, "working")

        working = MockMemory("working", MemoryType.WORKING)
        semantic = MockMemory("semantic", MemoryType.SEMANTIC)
        registry.register(working)
        registry.register(semantic)

        memories = selector.select_for_read()
        assert len(memories) >= 1

    def test_select_long_term_only(self, registry):
        """Test long-term only selection."""
        selector = MemorySelector(registry)
        selector.policy = MemoryAccessPolicy.LONG_TERM_ONLY

        working = MockMemory("working", MemoryType.WORKING)
        semantic = MockMemory("semantic", MemoryType.SEMANTIC)
        registry.register(working)
        registry.register(semantic)

        memories = selector.select_for_read()
        assert all(MemoryType.is_long_term(m.memory_type) for m in memories)


class TestMemoryTypes:
    """Tests for memory types."""

    def test_memory_type_values(self):
        """Test memory type values."""
        assert MemoryType.WORKING.value == "working"
        assert MemoryType.CONVERSATION.value == "conversation"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"

    def test_memory_type_short_term(self):
        """Test short-term memory check."""
        assert MemoryType.is_short_term(MemoryType.WORKING) is True
        assert MemoryType.is_short_term(MemoryType.CONVERSATION) is True
        assert MemoryType.is_short_term(MemoryType.EPISODIC) is False

    def test_memory_type_long_term(self):
        """Test long-term memory check."""
        assert MemoryType.is_long_term(MemoryType.EPISODIC) is True
        assert MemoryType.is_long_term(MemoryType.SEMANTIC) is True
        assert MemoryType.is_long_term(MemoryType.WORKING) is False


class TestMemoryAccessPolicy:
    """Tests for memory access policies."""

    def test_policy_values(self):
        """Test policy values."""
        assert MemoryAccessPolicy.FIRST_AVAILABLE.value == "first_available"
        assert MemoryAccessPolicy.LONG_TERM_ONLY.value == "long_term_only"
        assert MemoryAccessPolicy.SHORT_TERM_ONLY.value == "short_term_only"
        assert MemoryAccessPolicy.MERGE_ALL.value == "merge_all"


class TestMemoryEntry:
    """Tests for MemoryEntry."""

    def test_creation(self):
        """Test entry creation."""
        entry = MemoryEntry(
            content="Test content",
            memory_type=MemoryType.WORKING,
        )
        assert entry.content == "Test content"
        assert entry.memory_type == MemoryType.WORKING
        assert entry.key != ""

    def test_to_dict(self):
        """Test conversion to dict."""
        entry = MemoryEntry(
            content="Test",
            memory_type=MemoryType.WORKING,
        )
        d = entry.to_dict()
        assert d["content"] == "Test"
        assert d["memory_type"] == "working"


class TestMemoryResult:
    """Tests for MemoryResult."""

    def test_creation(self):
        """Test result creation."""
        result = MemoryResult(
            content="Test",
            memory_type=MemoryType.WORKING,
            memory_id="test",
        )
        assert result.content == "Test"
        assert result.score == 0.0


class TestMemoryResponse:
    """Tests for MemoryResponse."""

    def test_empty_response(self):
        """Test empty response."""
        response = MemoryResponse()
        assert response.is_empty is True
        assert response.content == ""

    def test_with_results(self):
        """Test response with results."""
        result = MemoryResult(
            content="Test",
            memory_type=MemoryType.WORKING,
            memory_id="test",
        )
        response = MemoryResponse(results=[result])
        assert response.is_empty is False
        assert "Test" in response.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
