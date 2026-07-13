"""Tests for capability core module."""

from __future__ import annotations

import pytest

from core.capabilities.capability import Capability, CapabilityTemplates
from core.capabilities.types import (
    CapabilityCategory,
    CapabilityId,
    CapabilityMetadata,
    CapabilityPriority,
    CapabilityStatus,
    CriticalityLevel,
    EventContract,
    Permission,
    SecurityLevel,
)


class TestCapability:
    """Tests for Capability class."""

    def test_create_capability(self) -> None:
        """Creating a capability should work."""
        cap = Capability.create(
            category=CapabilityCategory.DIAGNOSTIC,
            action="analyze",
            name="Diagnose Device",
            description="Performs device diagnostics",
            provider_id="diagnostic_engine_v1",
        )

        assert cap.name == "Diagnose Device"
        assert cap.category == CapabilityCategory.DIAGNOSTIC
        assert cap.provider_id == "diagnostic_engine_v1"
        assert cap.status == CapabilityStatus.AVAILABLE

    def test_capability_id_string(self) -> None:
        """Capability ID string should be formatted correctly."""
        cap = Capability.create(
            category="planning",
            action="create",
            name="Create Plan",
            description="Creates plans",
            provider_id="planner",
            target="maintenance",
        )

        assert cap.id_string == "planning.create.maintenance"

    def test_is_active(self) -> None:
        """is_active should check status."""
        cap = Capability.create(
            category="diagnostic",
            action="analyze",
            name="Test",
            description="Test",
            provider_id="test",
        )

        assert not cap.is_active()

        from dataclasses import replace
        active_cap = replace(cap, status=CapabilityStatus.ACTIVE)
        assert active_cap.is_active()

    def test_publishes_event(self) -> None:
        """publishes_event should check event contracts."""
        cap = Capability.create(
            category="diagnostic",
            action="analyze",
            name="Test",
            description="Test",
            provider_id="test",
            publishes=(
                EventContract(event_type="diagnostic_completed", direction="publishes"),
            ),
        )

        assert cap.publishes_event("diagnostic_completed")
        assert not cap.publishes_event("diagnostic_started")

    def test_consumes_event(self) -> None:
        """consumes_event should check event contracts."""
        cap = Capability.create(
            category="diagnostic",
            action="analyze",
            name="Test",
            description="Test",
            provider_id="test",
            consumes=(
                EventContract(
                    event_type="diagnostic_requested",
                    direction="consumes",
                    is_critical=True,
                ),
            ),
        )

        assert cap.consumes_event("diagnostic_requested")
        assert cap.requires_event("diagnostic_requested")
        assert not cap.consumes_event("other_event")

    def test_requires_capability(self) -> None:
        """requires_capability should check dependencies."""
        cap = Capability.create(
            category="diagnostic",
            action="analyze",
            name="Test",
            description="Test",
            provider_id="test",
            required_capabilities=("planning.create",),
        )

        assert cap.requires_capability("planning.create")
        assert not cap.requires_capability("other.capability")

    def test_has_permissions(self) -> None:
        """has_permissions should check required permissions."""
        cap = Capability.create(
            category="diagnostic",
            action="analyze",
            name="Test",
            description="Test",
            provider_id="test",
            required_permissions=(
                Permission(resource="devices", action="read"),
                Permission(resource="reports", action="write"),
            ),
        )

        assert cap.has_permissions({"devices:read", "reports:write"})
        assert not cap.has_permissions({"devices:read"})


class TestCapabilityId:
    """Tests for CapabilityId."""

    def test_parse_full_id(self) -> None:
        """Parsing a full ID should work."""
        cap_id = CapabilityId.parse("planning.create.maintenance")

        assert cap_id.category == "planning"
        assert cap_id.action == "create"
        assert cap_id.target == "maintenance"

    def test_parse_partial_id(self) -> None:
        """Parsing a partial ID should work."""
        cap_id = CapabilityId.parse("diagnostic.analyze")

        assert cap_id.category == "diagnostic"
        assert cap_id.action == "analyze"
        assert cap_id.target == ""

    def test_parse_invalid_id(self) -> None:
        """Parsing an invalid ID should raise."""
        with pytest.raises(ValueError):
            CapabilityId.parse("invalid")

    def test_string_representation(self) -> None:
        """String representation should format correctly."""
        cap_id = CapabilityId(category="diagnostic", action="analyze", target="monitor")

        assert str(cap_id) == "diagnostic.analyze.monitor"


class TestCapabilityTemplates:
    """Tests for capability templates."""

    def test_diagnostic_template(self) -> None:
        """Diagnostic template should create correct capability."""
        cap = CapabilityTemplates.diagnostic("monitor", "diagnostic_engine")

        assert cap.category == CapabilityCategory.DIAGNOSTIC
        assert cap.action == "analyze"
        assert cap.target == "monitor"
        assert cap.provider_id == "diagnostic_engine"

    def test_knowledge_search_template(self) -> None:
        """Knowledge search template should create correct capability."""
        cap = CapabilityTemplates.knowledge_search("knowledge_engine")

        assert cap.category == CapabilityCategory.KNOWLEDGE
        assert cap.action == "search"
