"""Tests for registry models."""

from __future__ import annotations

import pytest

from core.registry.models import EngineDescriptor
from core.registry.types import (
    Capability,
    EngineMetadata,
    EnginePriority,
    EngineStatus,
    EventContract,
    EventContracts,
    VersionRequirement,
)


class TestEngineDescriptor:
    """Tests for EngineDescriptor."""

    def test_create_basic_descriptor(self) -> None:
        """Creating a basic descriptor should work."""
        descriptor = EngineDescriptor.create(
            engine_id="planner",
            display_name="Planner Engine",
            description="Plans cognitive tasks",
        )

        assert descriptor.engine_id == "planner"
        assert descriptor.display_name == "Planner Engine"
        assert descriptor.version == "1.0.0"
        assert descriptor.status == EngineStatus.INACTIVE
        assert descriptor.priority == EnginePriority.NORMAL

    def test_has_capability(self) -> None:
        """has_capability should return True for registered capabilities."""
        descriptor = EngineDescriptor.create(
            engine_id="diagnostic",
            display_name="Diagnostic Engine",
            description="Performs diagnostics",
            capabilities=[
                Capability(name="diagnostic", description="Can diagnose devices"),
                Capability(name="analysis", description="Can analyze data"),
            ],
        )

        assert descriptor.has_capability("diagnostic")
        assert descriptor.has_capability("analysis")
        assert not descriptor.has_capability("voice")

    def test_get_capability(self) -> None:
        """get_capability should return the capability if found."""
        descriptor = EngineDescriptor.create(
            engine_id="planner",
            display_name="Planner",
            description="Plans tasks",
            capabilities=[
                Capability(name="planning", description="Can create plans"),
            ],
        )

        cap = descriptor.get_capability("planning")
        assert cap is not None
        assert cap.name == "planning"

        not_found = descriptor.get_capability("nonexistent")
        assert not_found is None

    def test_is_active(self) -> None:
        """is_active should return True only for ACTIVE status."""
        descriptor = EngineDescriptor.create(
            engine_id="test",
            display_name="Test",
            description="Test",
        )

        assert not descriptor.is_active()

        # Create with ACTIVE status
        active_descriptor = EngineDescriptor.create(
            engine_id="test2",
            display_name="Test2",
            description="Test2",
        )
        # Manually set status for testing
        from dataclasses import replace
        active_descriptor = replace(active_descriptor, status=EngineStatus.ACTIVE)
        assert active_descriptor.is_active()

    def test_requires_engine(self) -> None:
        """requires_engine should check dependencies."""
        descriptor = EngineDescriptor.create(
            engine_id="test",
            display_name="Test",
            description="Test",
        )
        assert not descriptor.requires_engine("other")

        # With dependencies
        descriptor_with_deps = EngineDescriptor(
            engine_id="test",
            display_name="Test",
            description="Test",
            dependencies=(
                VersionRequirement(engine_name="planner", required=True),
            ),
        )
        assert descriptor_with_deps.requires_engine("planner")
        assert not descriptor_with_deps.requires_engine("other")

    def test_publishes_event(self) -> None:
        """publishes_event should check event contracts."""
        descriptor = EngineDescriptor.create(
            engine_id="test",
            display_name="Test",
            description="Test",
        )
        assert not descriptor.publishes_event("plan_created")

        # With event contracts
        descriptor_with_events = EngineDescriptor(
            engine_id="test",
            display_name="Test",
            description="Test",
            events=EventContracts(
                publishes=(
                    EventContract(event_type="test_event", direction="publishes"),
                ),
            ),
        )
        assert descriptor_with_events.publishes_event("test_event")
        assert not descriptor_with_events.publishes_event("other_event")


class TestCapability:
    """Tests for Capability dataclass."""

    def test_capability_matches(self) -> None:
        """Two capabilities should match by name."""
        cap1 = Capability(name="diagnostic", description="Test")
        cap2 = Capability(name="diagnostic", description="Different")

        assert cap1.matches(cap2)
        assert not cap1.matches(Capability(name="planning"))

    def test_capability_is_compatible_with(self) -> None:
        """is_compatible_with should check major version."""
        cap = Capability(name="test", version="2.3.4")

        assert cap.is_compatible_with("2.5.0")
        assert cap.is_compatible_with("2.0.0")
        assert not cap.is_compatible_with("3.0.0")
        assert not cap.is_compatible_with("1.9.9")


class TestVersionRequirement:
    """Tests for VersionRequirement."""

    def test_is_satisfied_by(self) -> None:
        """is_satisfied_by should check version ranges."""
        req = VersionRequirement(
            engine_name="planner",
            min_version="1.0.0",
            max_version="2.0.0",
        )

        assert req.is_satisfied_by("1.0.0")
        assert req.is_satisfied_by("1.5.0")
        assert not req.is_satisfied_by("0.9.0")
        assert not req.is_satisfied_by("2.0.0")
        assert not req.is_satisfied_by("3.0.0")


class TestEventContracts:
    """Tests for EventContracts."""

    def test_get_all_event_types(self) -> None:
        """get_all_event_types should return all event types."""
        contracts = EventContracts(
            publishes=(
                EventContract(event_type="event_a", direction="publishes"),
                EventContract(event_type="event_b", direction="publishes"),
            ),
            consumes=(
                EventContract(event_type="event_c", direction="consumes"),
            ),
        )

        all_types = contracts.get_all_event_types()
        assert all_types == {"event_a", "event_b", "event_c"}

    def test_requires_event(self) -> None:
        """requires_event should check for critical consuming events."""
        contracts = EventContracts(
            consumes=(
                EventContract(
                    event_type="critical_event",
                    direction="consumes",
                    is_critical=True,
                ),
                EventContract(
                    event_type="optional_event",
                    direction="consumes",
                    is_critical=False,
                ),
            ),
        )

        assert contracts.requires_event("critical_event")
        assert not contracts.requires_event("optional_event")
        assert not contracts.requires_event("nonexistent")
