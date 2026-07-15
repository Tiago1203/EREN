"""Tests for Domain Events."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from core.shared import IncidentReported
from core.shared.events import (
    DeviceLocationChanged,
    DeviceRegistered,
    DeviceStatusChanged,
    DomainEvent,
    IncidentClosed,
    IncidentEscalated,
    IncidentOpened,
    IncidentProgressed,
    IncidentReported,
    IncidentResolved,
    IncidentTriaged,
    MaintenanceCompleted,
    MaintenanceScheduled,
    RecommendationAccepted,
    RecommendationGenerated,
    RecommendationRejected,
)


class TestDomainEvent:
    """Tests for DomainEvent base class."""

    def test_event_has_unique_id(self) -> None:
        """Event should have a unique identifier."""
        event1 = IncidentReported(
            incident_id="inc_1",
            tenant_id="tenant_1",
            device_id="dev_1",
            reported_by="eng_1",
            symptom="Test",
            description="Test",
            priority="medium",
        )
        event2 = IncidentReported(
            incident_id="inc_2",
            tenant_id="tenant_1",
            device_id="dev_1",
            reported_by="eng_1",
            symptom="Test",
            description="Test",
            priority="medium",
        )

        assert event1.event_id != event2.event_id

    def test_event_has_timestamp(self) -> None:
        """Event should have an occurred_at timestamp."""
        event = IncidentReported(
            incident_id="inc_1",
            tenant_id="tenant_1",
            device_id="dev_1",
            reported_by="eng_1",
            symptom="Test",
            description="Test",
            priority="medium",
        )

        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)

    def test_event_to_dict(self) -> None:
        """Event should serialize to dict."""
        event = IncidentReported(
            incident_id="inc_1",
            tenant_id="tenant_1",
            device_id="dev_1",
            reported_by="eng_1",
            symptom="Test",
            description="Test",
            priority="medium",
        )

        data = event.to_dict()

        assert "event_id" in data
        assert "event_type" in data
        assert "occurred_at" in data
        assert "version" in data
        assert data["incident_id"] == "inc_1"
        assert data["tenant_id"] == "tenant_1"
        assert data["event_type"] == "IncidentReported"


class TestIncidentEvents:
    """Tests for Incident-related events."""

    def test_incident_reported_event(self) -> None:
        """IncidentReported should contain all required fields."""
        event = IncidentReported(
            incident_id="inc_123",
            tenant_id="tenant_1",
            device_id="dev_456",
            reported_by="engineer_789",
            symptom="High pressure alarm",
            description="Ventilator showing alarm",
            priority="high",
            correlation_id="corr_123",
        )

        assert event.incident_id == "inc_123"
        assert event.device_id == "dev_456"
        assert event.priority == "high"
        assert event.event_type == "IncidentReported"

    def test_incident_triaged_event(self) -> None:
        """IncidentTriaged should contain triage information."""
        event = IncidentTriaged(
            incident_id="inc_123",
            priority="critical",
            triage_notes="Requires immediate attention",
            triaged_by="senior_engineer",
            safety_classification="critical",
        )

        assert event.priority == "critical"
        assert event.safety_classification == "critical"

    def test_incident_closed_event(self) -> None:
        """IncidentClosed should contain feedback."""
        event = IncidentClosed(
            incident_id="inc_123",
            closed_by="engineer_1",
            feedback="Problem resolved successfully",
            recommendation_accepted=True,
        )

        assert event.feedback == "Problem resolved successfully"
        assert event.recommendation_accepted is True


class TestRecommendationEvents:
    """Tests for AI Recommendation events."""

    def test_recommendation_generated_event(self) -> None:
        """RecommendationGenerated should contain AI data."""
        event = RecommendationGenerated(
            incident_id="inc_123",
            recommendation_id="rec_456",
            content="Replace the pressure sensor",
            confidence_score=0.85,
            evidence_count=13,
            safety_level="recommendation",
            sources=("manual_servo_i", "similar_incidents"),
        )

        assert event.confidence_score == 0.85
        assert event.evidence_count == 13
        assert len(event.sources) == 2

    def test_recommendation_accepted_event(self) -> None:
        """RecommendationAccepted should track acceptance."""
        event = RecommendationAccepted(
            incident_id="inc_123",
            recommendation_id="rec_456",
            accepted_by="engineer_1",
        )

        assert event.recommendation_id == "rec_456"

    def test_recommendation_rejected_event(self) -> None:
        """RecommendationRejected should track rejection with reason."""
        event = RecommendationRejected(
            incident_id="inc_123",
            recommendation_id="rec_456",
            rejected_by="engineer_1",
            reason="Not applicable for this device model",
        )

        assert event.reason == "Not applicable for this device model"


class TestDeviceEvents:
    """Tests for Device-related events."""

    def test_device_registered_event(self) -> None:
        """DeviceRegistered should contain device info."""
        event = DeviceRegistered(
            device_id="dev_123",
            tenant_id="tenant_1",
            serial_number="SN-2024-001",
            model="Servo-i",
            manufacturer="Getinge",
            registered_by="admin_1",
        )

        assert event.serial_number == "SN-2024-001"
        assert event.model == "Servo-i"

    def test_device_status_changed_event(self) -> None:
        """DeviceStatusChanged should track status transitions."""
        event = DeviceStatusChanged(
            device_id="dev_123",
            previous_status="operational",
            new_status="faulty",
            reason="Incident reported",
            changed_by="engineer_1",
        )

        assert event.previous_status == "operational"
        assert event.new_status == "faulty"


class TestMaintenanceEvents:
    """Tests for Maintenance-related events."""

    def test_maintenance_scheduled_event(self) -> None:
        """MaintenanceScheduled should contain scheduling info."""
        scheduled_date = datetime.now(UTC)

        event = MaintenanceScheduled(
            maintenance_id="maint_123",
            device_id="dev_456",
            maintenance_type="preventive",
            scheduled_date=scheduled_date,
            scheduled_by="admin_1",
        )

        assert event.maintenance_type == "preventive"

    def test_maintenance_completed_event(self) -> None:
        """MaintenanceCompleted should track completion details."""
        event = MaintenanceCompleted(
            maintenance_id="maint_123",
            device_id="dev_456",
            incident_id="inc_789",
            completed_by="engineer_1",
            parts_used=("sensor_123", "filter_456"),
            duration_minutes=45,
        )

        assert len(event.parts_used) == 2
        assert event.duration_minutes == 45
