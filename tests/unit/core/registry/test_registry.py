"""Tests for the EngineRegistry."""

from __future__ import annotations

import pytest

from core.contracts import CognitiveEngine
from core.registry import (
    EngineAlreadyRegisteredError,
    EngineDescriptor,
    EngineNotFoundError,
    EngineRegistry,
    EngineStatus,
    Capability,
)


class MockEngine(CognitiveEngine):
    """Mock engine for testing."""

    def __init__(self, name: str, description: str = "Mock engine") -> None:
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    def describe(self) -> str:
        return self._description


class TestEngineRegistry:
    """Tests for EngineRegistry."""

    def test_register_and_get(self) -> None:
        """Registering and getting an engine should work."""
        registry = EngineRegistry()
        engine = MockEngine("planner", "Plans tasks")

        registry.register(engine)

        retrieved = registry.get("planner")
        assert retrieved is engine
        assert "planner" in registry

    def test_register_duplicate_raises(self) -> None:
        """Registering a duplicate should raise."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner"))

        with pytest.raises(EngineAlreadyRegisteredError):
            registry.register(MockEngine("planner"))

    def test_register_with_replace(self) -> None:
        """Registering with replace=True should work."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner", "First"))

        new_engine = MockEngine("planner", "Second")
        registry.register(new_engine, replace=True)

        assert registry.get("planner") is new_engine

    def test_unregister(self) -> None:
        """Unregistering should remove the engine."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner"))

        registry.unregister("planner")

        assert "planner" not in registry
        with pytest.raises(EngineNotFoundError):
            registry.get("planner")

    def test_unregister_not_found_raises(self) -> None:
        """Unregistering nonexistent should raise."""
        registry = EngineRegistry()

        with pytest.raises(EngineNotFoundError):
            registry.unregister("nonexistent")

    def test_list(self) -> None:
        """Listing should return all engines."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner"))
        registry.register(MockEngine("diagnostic"))

        engines = registry.list()
        assert len(engines) == 2

    def test_get_descriptor(self) -> None:
        """Getting descriptor should return metadata."""
        registry = EngineRegistry()
        descriptor = EngineDescriptor.create(
            engine_id="planner",
            display_name="Planner",
            description="Plans tasks",
            capabilities=[Capability(name="planning")],
        )
        registry.register(MockEngine("planner"), descriptor=descriptor)

        retrieved = registry.get_descriptor("planner")
        assert retrieved.engine_id == "planner"
        assert retrieved.has_capability("planning")

    def test_find_by_capability(self) -> None:
        """Finding by capability should work."""
        registry = EngineRegistry()

        registry.register(
            MockEngine("planner"),
            descriptor=EngineDescriptor.create(
                engine_id="planner",
                display_name="Planner",
                description="Plans tasks",
                capabilities=[Capability(name="planning")],
            ),
        )
        registry.register(
            MockEngine("diagnostic"),
            descriptor=EngineDescriptor.create(
                engine_id="diagnostic",
                display_name="Diagnostic",
                description="Diagnoses issues",
                capabilities=[Capability(name="diagnostic")],
            ),
        )

        planners = registry.find_by_capability("planning")
        assert len(planners) == 1
        assert planners[0].engine_id == "planner"

    def test_set_status(self) -> None:
        """Setting status should update the descriptor."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner"))

        registry.set_status("planner", EngineStatus.ACTIVE)

        descriptor = registry.get_descriptor("planner")
        assert descriptor.status == EngineStatus.ACTIVE

    def test_get_active_engines(self) -> None:
        """Getting active engines should filter correctly."""
        registry = EngineRegistry()

        registry.register(MockEngine("planner"))
        registry.set_status("planner", EngineStatus.ACTIVE)

        registry.register(MockEngine("diagnostic"))
        registry.set_status("diagnostic", EngineStatus.INACTIVE)

        active = registry.get_active_engines()
        assert len(active) == 1
        assert active[0].engine_id == "planner"

    def test_len_and_contains(self) -> None:
        """Len and contains should work."""
        registry = EngineRegistry()

        assert len(registry) == 0
        assert "planner" not in registry

        registry.register(MockEngine("planner"))

        assert len(registry) == 1
        assert "planner" in registry

    def test_snapshot(self) -> None:
        """Snapshot should capture current state."""
        registry = EngineRegistry()
        registry.register(MockEngine("planner"))
        registry.set_status("planner", EngineStatus.ACTIVE)

        snapshot = registry.snapshot()

        assert snapshot.engine_count == 1
        assert snapshot.active_count == 1
        assert len(snapshot.descriptors) == 1


class TestEngineRegistryThreadSafety:
    """Tests for thread safety."""

    def test_concurrent_registration(self) -> None:
        """Concurrent registration should be safe."""
        import threading

        registry = EngineRegistry()
        errors: list[Exception] = []

        def register_engine(name: str) -> None:
            try:
                registry.register(MockEngine(name))
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=register_engine, args=(f"engine_{i}",))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(registry) == 10
