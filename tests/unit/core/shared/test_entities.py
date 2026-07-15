"""Tests for BaseEntity and AggregateRoot."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.shared import (
    AggregateRoot,
    BaseEntity,
    ConcurrencyError,
    EntityId,
)


class TestBaseEntity:
    """Tests for BaseEntity."""

    def test_entity_has_unique_id(self) -> None:
        """Entity should have a unique identifier."""
        id1 = EntityId.generate()
        id2 = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity1 = TestEntity(id=id1, name="Test 1")
        entity2 = TestEntity(id=id2, name="Test 2")

        assert entity1.id == id1
        assert entity2.id == id2
        assert entity1.id != entity2.id

    def test_entity_equality_by_id(self) -> None:
        """Entities should be equal if they have the same ID."""
        id1 = EntityId(value="id_123")
        id2 = EntityId(value="id_456")

        @dataclass(eq=False)
        class TestEntity(BaseEntity):
            name: str

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        entity1 = TestEntity(id=id1, name="Test 1", created_at=now, updated_at=now)
        entity2 = TestEntity(id=id1, name="Different", created_at=now, updated_at=now)
        entity3 = TestEntity(id=id2, name="Test 1", created_at=now, updated_at=now)

        # Same ID = equal
        assert entity1 == entity2
        # Different ID = not equal
        assert entity1 != entity3
        # Hash based on ID
        assert hash(entity1) == hash(entity2)
        assert hash(entity1) != hash(entity3)

    def test_entity_version_starts_at_1(self) -> None:
        """Entity version should start at 1."""
        entity_id = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        assert entity.version == 1

    def test_entity_immutable_after_init(self) -> None:
        """Entity attributes should be immutable after init."""
        entity_id = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        with pytest.raises(AttributeError, match="Cannot modify attribute"):
            entity.name = "New Name"

    def test_entity_tracks_events(self) -> None:
        """Entity should track domain events."""
        from core.shared.events import IncidentReported

        entity_id = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        event = IncidentReported(
            incident_id="inc_123",
            tenant_id="tenant_1",
            device_id="dev_456",
            reported_by="engineer_789",
            symptom="Test",
            description="Test",
            priority="medium",
        )

        entity.add_event(event)
        assert entity.has_pending_events()

        events = entity.pop_events()
        assert len(events) == 1
        assert not entity.has_pending_events()

    def test_entity_assert_version_correct(self) -> None:
        """Should not raise when version matches."""
        entity_id = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        # Should not raise
        entity._assert_version(1)

    def test_entity_assert_version_incorrect(self) -> None:
        """Should raise ConcurrencyError when version mismatches."""
        entity_id = EntityId.generate()

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        with pytest.raises(ConcurrencyError):
            entity._assert_version(2)

    def test_entity_to_dict(self) -> None:
        """Entity should serialize to dict."""
        entity_id = EntityId(value="id_123")

        @dataclass
        class TestEntity(BaseEntity):
            name: str

        entity = TestEntity(id=entity_id, name="Test")

        data = entity.to_dict()

        assert data["id"] == "id_123"
        assert data["version"] == 1
        assert "created_at" in data
        assert "updated_at" in data


class TestAggregateRoot:
    """Tests for AggregateRoot."""

    def test_aggregate_root_inherits_from_entity(self) -> None:
        """AggregateRoot should inherit from BaseEntity."""
        entity_id = EntityId.generate()

        @dataclass
        class TestAggregate(AggregateRoot):
            name: str

        aggregate = TestAggregate(id=entity_id, name="Test")

        assert isinstance(aggregate, BaseEntity)
        assert aggregate.id == entity_id
