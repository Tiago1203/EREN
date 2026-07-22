"""Tests for Cognitive Capabilities (PR-052)."""

import pytest
from core.PHASE_2.capabilities.cognitive_capabilities_integration import (
    Capability,
    CapabilityRegistry,
    CapabilityResolver,
    CapabilityEvent,
    CapabilityEventType,
)


class TestCapabilityRegistry:
    def test_register(self):
        registry = CapabilityRegistry()
        cap = Capability(id="test", name="Test Capability")
        registry.register(cap)
        assert "test" in [c.id for c in registry.list_all()]

    def test_unregister(self):
        registry = CapabilityRegistry()
        cap = Capability(id="test", name="Test")
        registry.register(cap)
        assert registry.unregister("test") is True
        assert registry.resolve("test") is None

    def test_resolve(self):
        registry = CapabilityRegistry()
        cap = Capability(id="test", name="Test")
        registry.register(cap)
        resolved = registry.resolve("test")
        assert resolved is not None
        assert resolved.id == "test"

    def test_find_by_tag(self):
        registry = CapabilityRegistry()
        registry.register(Capability(id="c1", name="C1", tags=("medical",)))
        registry.register(Capability(id="c2", name="C2", tags=("engineering",)))
        results = registry.find_by_tag("medical")
        assert len(results) == 1
        assert results[0].id == "c1"

    def test_events(self):
        registry = CapabilityRegistry()
        events = []
        registry.subscribe(lambda e: events.append(e))
        registry.register(Capability(id="test", name="Test"))
        assert len(events) == 1
        assert events[0].event_type == CapabilityEventType.REGISTERED


class TestCapabilityResolver:
    def test_resolve_and_execute(self):
        registry = CapabilityRegistry()
        registry.register(Capability(
            id="sum",
            name="Sum",
            handler=lambda ctx: ctx.get("a", 0) + ctx.get("b", 0),
        ))
        resolver = CapabilityResolver(registry)
        result = resolver.resolve_and_execute("sum", {"a": 2, "b": 3})
        assert result["success"] is True
        assert result["result"] == 5

    def test_not_found(self):
        resolver = CapabilityResolver()
        result = resolver.resolve_and_execute("nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"]
