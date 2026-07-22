"""Tests for capability registry."""

from __future__ import annotations

import pytest

from core.PHASE_2.capabilities import (
    Capability,
    CapabilityAlreadyRegisteredError,
    CapabilityCategory,
    CapabilityNotFoundError,
    CapabilityRegistry,
    CapabilityStatus,
    SearchOptions,
)


class TestCapabilityRegistry:
    """Tests for CapabilityRegistry."""

    def test_register_and_get(self) -> None:
        """Registering and getting a capability should work."""
        registry = CapabilityRegistry()
        cap = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose",
            description="Diagnoses devices",
            provider_id="diagnostic_engine",
        )

        registry.register(cap)

        retrieved = registry.get("diagnostic.analyze")
        assert retrieved is cap
        assert "diagnostic.analyze" in registry

    def test_register_duplicate_raises(self) -> None:
        """Registering a duplicate should raise."""
        registry = CapabilityRegistry()
        cap = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose",
            description="Diagnoses devices",
            provider_id="diagnostic_engine",
        )

        registry.register(cap)

        with pytest.raises(CapabilityAlreadyRegisteredError):
            registry.register(cap)

    def test_register_with_replace(self) -> None:
        """Registering with replace should work."""
        registry = CapabilityRegistry()
        cap1 = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose V1",
            description="Diagnoses devices",
            provider_id="diagnostic_engine",
        )
        cap2 = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose V2",
            description="Diagnoses devices v2",
            provider_id="diagnostic_engine",
        )

        registry.register(cap1)
        registry.register(cap2, replace=True)

        retrieved = registry.get("diagnostic.analyze")
        assert retrieved.name == "Diagnose V2"

    def test_unregister(self) -> None:
        """Unregistering should remove the capability."""
        registry = CapabilityRegistry()
        cap = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose",
            description="Diagnoses devices",
            provider_id="diagnostic_engine",
        )

        registry.register(cap)
        registry.unregister("diagnostic.analyze")

        assert "diagnostic.analyze" not in registry
        with pytest.raises(CapabilityNotFoundError):
            registry.get("diagnostic.analyze")

    def test_find_by_category(self) -> None:
        """Finding by category should work."""
        registry = CapabilityRegistry()

        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="analyze",
                name="Diagnose",
                description="Diagnoses devices",
                provider_id="engine1",
            )
        )
        registry.register(
            Capability.create(
                category=CapabilityCategory.PLANNING,
                action="create",
                name="Plan",
                description="Creates plans",
                provider_id="engine2",
            )
        )

        diagnostics = registry.find_by_category(CapabilityCategory.DIAGNOSTIC)
        assert len(diagnostics) == 1
        assert diagnostics[0].category == CapabilityCategory.DIAGNOSTIC

    def test_find_by_provider(self) -> None:
        """Finding by provider should work."""
        registry = CapabilityRegistry()

        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="analyze",
                name="Diagnose",
                description="Diagnoses devices",
                provider_id="diagnostic_v1",
            )
        )
        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="diagnose_v2",
                name="Diagnose V2",
                description="Diagnoses devices v2",
                provider_id="diagnostic_v2",
            )
        )

        v1_caps = registry.find_by_provider("diagnostic_v1")
        assert len(v1_caps) == 1

    def test_find_active(self) -> None:
        """Finding active capabilities should work."""
        registry = CapabilityRegistry()

        cap1 = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose",
            description="Diagnoses devices",
            provider_id="engine1",
        )
        cap2 = Capability.create(
            category=CapabilityCategory.PLANNING,
            action="create",
            name="Plan",
            description="Creates plans",
            provider_id="engine2",
        )

        from dataclasses import replace
        cap1_active = replace(cap1, status=CapabilityStatus.ACTIVE)

        registry.register(cap1_active)
        registry.register(cap2)

        active = registry.find_active()
        assert len(active) == 1
        assert active[0].status == CapabilityStatus.ACTIVE

    def test_search_with_filter(self) -> None:
        """Searching with filter should work."""
        registry = CapabilityRegistry()

        from core.PHASE_2.capabilities.types import CapabilityFilter

        cap1 = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose",
            description="Diagnoses devices",
            provider_id="engine1",
        )
        cap2 = Capability.create(
            category=CapabilityCategory.PLANNING,
            action="create",
            name="Plan",
            description="Creates plans",
            provider_id="engine2",
        )

        registry.register(cap1)
        registry.register(cap2)

        results = registry.search(
            SearchOptions(
                filter=CapabilityFilter(
                    category=CapabilityCategory.DIAGNOSTIC,
                )
            )
        )

        assert len(results) == 1
        assert results[0].category == CapabilityCategory.DIAGNOSTIC

    def test_list(self) -> None:
        """Listing should return all capabilities."""
        registry = CapabilityRegistry()

        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="analyze",
                name="Diagnose",
                description="Diagnoses devices",
                provider_id="engine1",
            )
        )
        registry.register(
            Capability.create(
                category=CapabilityCategory.PLANNING,
                action="create",
                name="Plan",
                description="Creates plans",
                provider_id="engine2",
            )
        )

        all_caps = registry.list()
        assert len(all_caps) == 2

    def test_snapshot(self) -> None:
        """Snapshot should capture current state."""
        registry = CapabilityRegistry()

        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="analyze",
                name="Diagnose",
                description="Diagnoses devices",
                provider_id="engine1",
            )
        )

        snapshot = registry.snapshot()

        assert snapshot.capability_count == 1
        assert snapshot.version == "1.0.0"

    def test_len(self) -> None:
        """Len should return count."""
        registry = CapabilityRegistry()

        assert len(registry) == 0

        registry.register(
            Capability.create(
                category=CapabilityCategory.DIAGNOSTIC,
                action="analyze",
                name="Diagnose",
                description="Diagnoses devices",
                provider_id="engine1",
            )
        )

        assert len(registry) == 1
