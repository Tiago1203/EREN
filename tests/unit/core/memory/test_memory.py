"""Tests for CognitiveMemoryEngine."""

from __future__ import annotations

import pytest

from core.memory import (
    CognitiveMemoryEngine,
    MemoryEntry,
    MemoryQuery,
    MemoryType,
    ContentType,
    MemoryContent,
    MemoryTemplates,
)


class TestCognitiveMemoryEngine:
    """Tests for CognitiveMemoryEngine."""

    def test_store_memory(self) -> None:
        """Storing a memory should return an ID."""
        engine = CognitiveMemoryEngine()

        memory_id = engine.store(
            content="Test memory content",
            memory_type=MemoryType.SHORT_TERM,
            summary="Test summary",
        )

        assert memory_id is not None
        assert memory_id.startswith("mem_")

    def test_retrieve_memory(self) -> None:
        """Retrieving a stored memory should return the entry."""
        engine = CognitiveMemoryEngine()

        memory_id = engine.store(
            content="Test memory content",
            memory_type=MemoryType.SHORT_TERM,
        )

        retrieved = engine.retrieve(memory_id, MemoryType.SHORT_TERM)

        assert retrieved is not None
        assert "Test memory content" in str(retrieved.content.data)

    def test_retrieve_not_found(self) -> None:
        """Retrieving non-existent memory should return None."""
        engine = CognitiveMemoryEngine()

        retrieved = engine.retrieve("nonexistent_id", MemoryType.SHORT_TERM)

        assert retrieved is None

    def test_search_memory(self) -> None:
        """Searching should find matching memories."""
        engine = CognitiveMemoryEngine()

        engine.store(
            content="Patient with arrhythmia",
            memory_type=MemoryType.EPISODIC,
            summary="Arrhythmia case",
        )
        engine.store(
            content="Device calibration procedure",
            memory_type=MemoryType.PROCEDURAL,
            summary="Calibration procedure",
        )

        results = engine.search(
            MemoryQuery(query_text="arrhythmia")
        )

        assert len(results) >= 1
        assert any("arrhythmia" in str(r.memory.content.data) for r in results)

    def test_stress_memory(self) -> None:
        """Strengthening a memory should increase its strength."""
        engine = CognitiveMemoryEngine()

        memory_id = engine.store(
            content="Important information",
            memory_type=MemoryType.LONG_TERM,
        )

        memory = engine.retrieve(memory_id)
        original_strength = memory.strength

        engine.strengthen(memory_id, amount=0.2)

        updated = engine.retrieve(memory_id)
        assert updated.strength > original_strength

    def test_consolidate_memory(self) -> None:
        """Consolidating should transfer to long-term."""
        engine = CognitiveMemoryEngine()

        memory_id = engine.store(
            content="Important event",
            memory_type=MemoryType.SHORT_TERM,
            importance=8,
        )

        engine.strengthen(memory_id, amount=0.5)
        affected = engine.consolidate(memory_id, target_type=MemoryType.LONG_TERM)

        assert len(affected) >= 1

    def test_statistics(self) -> None:
        """Getting statistics should return counts."""
        engine = CognitiveMemoryEngine()

        engine.store(content="Memory 1", memory_type=MemoryType.WORKING)
        engine.store(content="Memory 2", memory_type=MemoryType.SHORT_TERM)
        engine.store(content="Memory 3", memory_type=MemoryType.LONG_TERM)

        stats = engine.get_statistics()

        assert stats["total_memories"] == 3

    def test_snapshot(self) -> None:
        """Creating a snapshot should capture state."""
        engine = CognitiveMemoryEngine()

        engine.store(content="Test", memory_type=MemoryType.SHORT_TERM)

        snapshot = engine.snapshot()

        assert "timestamp" in snapshot
        assert "statistics" in snapshot


class TestMemoryTemplates:
    """Tests for memory templates."""

    def test_clinical_encounter(self) -> None:
        """Clinical encounter template should create episodic memory."""
        memory = MemoryTemplates.clinical_encounter(
            memory_id="test-1",
            patient_id="patient-123",
            encounter_type="checkup",
            summary="Routine checkup",
        )

        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.metadata.tags == ("patient-123", "clinical", "encounter")

    def test_device_diagnostic(self) -> None:
        """Device diagnostic template should create episodic memory."""
        memory = MemoryTemplates.device_diagnostic(
            memory_id="test-2",
            device_id="monitor-001",
            diagnostic_result="Sensor malfunction",
        )

        assert memory.memory_type == MemoryType.EPISODIC
        assert "monitor-001" in memory.metadata.tags

    def test_technical_knowledge(self) -> None:
        """Technical knowledge template should create semantic memory."""
        memory = MemoryTemplates.technical_knowledge(
            memory_id="test-3",
            topic="Philips IntelliVue",
            content="Maintenance procedures for IntelliVue monitors",
        )

        assert memory.memory_type == MemoryType.SEMANTIC
        assert "knowledge" in memory.metadata.tags


class TestMemoryEntry:
    """Tests for MemoryEntry."""

    def test_create_memory(self) -> None:
        """Creating a memory entry should work."""
        memory = MemoryEntry.create(
            memory_id="test-id",
            memory_type=MemoryType.SHORT_TERM,
            content=MemoryContent(
                type=ContentType.TEXT,
                data="Test content",
            ),
            summary="Test summary",
        )

        assert memory.memory_id == "test-id"
        assert memory.memory_type == MemoryType.SHORT_TERM
        assert memory.strength == 1.0

    def test_strengthen(self) -> None:
        """Strengthening should increase strength."""
        memory = MemoryEntry.create(
            memory_id="test",
            memory_type=MemoryType.SHORT_TERM,
            content=MemoryContent(type=ContentType.TEXT, data="Test"),
        )

        stronger = memory.strengthen(0.3)

        assert stronger.strength == memory.strength + 0.3

    def test_weaken(self) -> None:
        """Weakening should decrease strength."""
        memory = MemoryEntry.create(
            memory_id="test",
            memory_type=MemoryType.SHORT_TERM,
            content=MemoryContent(type=ContentType.TEXT, data="Test"),
        )

        weaker = memory.weaken(0.3)

        assert weaker.strength == memory.strength - 0.3
