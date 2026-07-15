"""Tests for EngineeringIncident aggregate."""

from __future__ import annotations

import pytest

from core.incident.domain import (
    Action,
    ActionResult,
    ActionType,
    ConversationMessage,
    EngineeringIncident,
    Evidence,
    Investigation,
    Priority,
    SafetyLevel,
)
from core.incident.domain.value_objects import (
    EvidenceType,
    Feedback,
    IncidentStatus,
    MessageSender,
    Resolution,
    Symptom,
)
from core.shared import DeviceId, EngineerId, IncidentId, TenantId


class TestEngineeringIncident:
    """Tests for EngineeringIncident aggregate."""

    @pytest.fixture
    def tenant_id(self) -> TenantId:
        return TenantId(value="tenant_001")

    @pytest.fixture
    def device_id(self) -> DeviceId:
        return DeviceId(value="device_001")

    @pytest.fixture
    def engineer_id(self) -> EngineerId:
        return EngineerId(value="engineer_001")

    @pytest.fixture
    def incident_id(self) -> IncidentId:
        return IncidentId.generate()

    @pytest.fixture
    def symptom(self) -> Symptom:
        return Symptom(
            description="High pressure alarm on ventilator",
            category="alarm",
        )

    def test_create_incident(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test creating a new incident."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Ventilator showing high pressure alarm in ICU-3",
            priority=Priority.medium(),
        )

        assert incident.tenant_id == tenant_id
        assert incident.device_id == device_id
        assert incident.reported_by == engineer_id
        assert incident.symptom == symptom
        assert incident.status == IncidentStatus.reported()
        assert incident.version == 1
        assert incident.has_pending_events()

    def test_incident_publishes_event_on_creation(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test that incident publishes IncidentReported event on creation."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )

        events = incident.pop_events()
        assert len(events) == 1
        assert events[0].event_type == "IncidentReported"

    def test_triage_incident(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test triaging an incident."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()  # Clear events

        incident.triage(
            priority=Priority.high(),
            safety_classification=SafetyLevel.warning(),
            triage_notes="Requires immediate attention",
            expected_version=1,
        )

        assert incident.status == IncidentStatus.triaged()
        assert incident.priority == Priority.high()
        assert incident.safety_classification == SafetyLevel.warning()
        assert incident.triage_notes == "Requires immediate attention"
        assert incident.version == 2

    def test_triage_fails_wrong_status(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test that triaging fails if not in reported status."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        # Triage once
        incident.triage(
            priority=Priority.high(),
            safety_classification=SafetyLevel.warning(),
            triage_notes="First triage",
            expected_version=1,
        )

        # Try to triage again - should fail
        with pytest.raises(Exception):
            incident.triage(
                priority=Priority.critical(),
                safety_classification=SafetyLevel.critical(),
                triage_notes="Second triage",
                expected_version=2,
            )

    def test_assign_incident(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test assigning an incident to an engineer."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        # Triage first
        incident.triage(
            priority=Priority.high(),
            safety_classification=SafetyLevel.warning(),
            triage_notes="Triaged",
            expected_version=1,
        )

        # Assign
        assignee_id = EngineerId(value="engineer_002")
        incident.assign(engineer_id=assignee_id, expected_version=2)

        assert incident.status == IncidentStatus.open()
        assert incident.assigned_to == assignee_id

    def test_resolve_incident(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test resolving an incident."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        # Go through lifecycle
        incident.triage(
            priority=Priority.high(),
            safety_classification=SafetyLevel.warning(),
            triage_notes="Triaged",
            expected_version=1,
        )

        incident.assign(engineer_id=engineer_id, expected_version=2)
        incident.start_investigation(expected_version=3)

        # Resolve
        resolution = Resolution(
            description="Replaced pressure sensor",
            root_cause="Faulty sensor",
            resolution_type="repair",
        )
        incident.resolve(
            resolution=resolution,
            resolved_by=engineer_id,
            actions_count=2,
            expected_version=4,
        )

        assert incident.status == IncidentStatus.resolved()
        assert incident.resolution == resolution

    def test_cannot_resolve_without_actions(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test that incident cannot be resolved without actions."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        incident.triage(
            priority=Priority.high(),
            safety_classification=SafetyLevel.warning(),
            triage_notes="Triaged",
            expected_version=1,
        )
        incident.assign(engineer_id=engineer_id, expected_version=2)
        incident.start_investigation(expected_version=3)

        with pytest.raises(ValueError, match="at least one action"):
            incident.resolve(
                resolution=Resolution(description="Test resolution"),
                resolved_by=engineer_id,
                actions_count=0,  # No actions
                expected_version=4,
            )

    def test_close_incident(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test closing a resolved incident."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        # Go through lifecycle
        incident.triage(Priority.high(), SafetyLevel.warning(), "Triaged", 1)
        incident.assign(engineer_id, 2)
        incident.start_investigation(3)
        incident.resolve(Resolution(description="Fixed"), engineer_id, 2, 4)
        incident.pop_events()  # Clear events

        # Close
        feedback = Feedback(feedback_type="positive", content="Good job")
        incident.close(
            feedback=feedback,
            recommendation_accepted=True,
            closed_by=engineer_id,
            expected_version=5,
        )

        assert incident.status == IncidentStatus.closed()
        assert incident.feedback == feedback
        assert incident.closed_at is not None
        assert incident.is_closed()

    def test_closed_incident_cannot_be_modified(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test that closed incidents cannot be modified."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.medium(),
        )
        incident.pop_events()

        # Close directly
        incident.triage(Priority.low(), SafetyLevel.informational(), "Triaged", 1)
        incident.assign(engineer_id, 2)
        incident.start_investigation(3)
        incident.resolve(Resolution(description="Fixed"), engineer_id, 1, 4)
        incident.close(None, False, engineer_id, 5)

        assert not incident.can_be_modified()

    def test_incident_to_dict(self, incident_id, tenant_id, device_id, engineer_id, symptom):
        """Test incident serialization."""
        incident = EngineeringIncident(
            id=incident_id,
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=engineer_id,
            symptom=symptom,
            description="Test incident",
            priority=Priority.high(),
        )

        data = incident.to_dict()

        assert data["tenant_id"] == str(tenant_id)
        assert data["device_id"] == str(device_id)
        assert data["priority"] == "high"
        assert data["status"] == "reported"


class TestInvestigation:
    """Tests for Investigation aggregate."""

    def test_create_investigation(self):
        """Test creating a new investigation."""
        incident_id = IncidentId.generate()
        investigation = Investigation(incident_id=incident_id)

        assert investigation.status == "active"
        assert investigation.incident_id == incident_id
        assert len(investigation.evidence_list) == 0
        assert len(investigation.actions_list) == 0
        assert len(investigation.messages_list) == 0

    def test_add_evidence(self):
        """Test adding evidence to investigation."""
        investigation = Investigation(incident_id=IncidentId.generate())
        evidence = Evidence(
            investigation_id=investigation.id,
            evidence_type=EvidenceType.measurement(),
            description="Pressure reading: 45 cmH2O",
            recorded_by=EngineerId(value="eng_001"),
        )

        investigation.add_evidence(evidence)

        assert len(investigation.evidence_list) == 1
        assert investigation.evidence_list[0] == evidence

    def test_add_action(self):
        """Test adding an action to investigation."""
        investigation = Investigation(incident_id=IncidentId.generate())
        action = Action(
            investigation_id=investigation.id,
            description="Replaced pressure sensor",
            action_type=ActionType.replace(),
            performed_by=EngineerId(value="eng_001"),
            result=ActionResult.success(),
        )

        investigation.add_action(action)

        assert len(investigation.actions_list) == 1
        assert investigation.get_actions_count() == 1

    def test_add_message(self):
        """Test adding a message to investigation."""
        investigation = Investigation(incident_id=IncidentId.generate())
        message = ConversationMessage(
            investigation_id=investigation.id,
            sender=MessageSender.engineer(),
            content="Found the issue in the sensor",
        )

        investigation.add_message(message)

        assert len(investigation.messages_list) == 1
        assert investigation.messages_list[0].content == "Found the issue in the sensor"

    def test_complete_investigation(self):
        """Test completing an investigation."""
        investigation = Investigation(incident_id=IncidentId.generate())
        investigation.complete()

        assert investigation.is_completed()
        assert investigation.completed_at is not None

    def test_cannot_add_to_completed_investigation(self):
        """Test that cannot add to completed investigation."""
        investigation = Investigation(incident_id=IncidentId.generate())
        investigation.complete()

        evidence = Evidence(
            investigation_id=investigation.id,
            evidence_type=EvidenceType.measurement(),
            description="Test",
            recorded_by=EngineerId(value="eng_001"),
        )

        with pytest.raises(ValueError, match="completed"):
            investigation.add_evidence(evidence)


class TestValueObjects:
    """Tests for Incident value objects."""

    def test_incident_status_transitions(self):
        """Test valid status transitions."""
        reported = IncidentStatus.reported()
        triaged = IncidentStatus.triaged()
        open = IncidentStatus.open()
        in_progress = IncidentStatus.in_progress()
        resolved = IncidentStatus.resolved()
        closed = IncidentStatus.closed()

        assert reported.can_transition_to(triaged)
        assert triaged.can_transition_to(open)
        assert open.can_transition_to(in_progress)
        assert in_progress.can_transition_to(resolved)
        assert resolved.can_transition_to(closed)

    def test_invalid_status_transition(self):
        """Test invalid status transitions."""
        reported = IncidentStatus.reported()
        closed = IncidentStatus.closed()

        assert not reported.can_transition_to(closed)

    def test_terminal_states(self):
        """Test terminal states."""
        assert IncidentStatus.closed().is_terminal()
        assert IncidentStatus.cancelled().is_terminal()
        assert not IncidentStatus.open().is_terminal()

    def test_symptom_normalizes_whitespace(self):
        """Test that symptom normalizes whitespace."""
        symptom = Symptom(description="  Multiple   spaces   here  ")
        assert symptom.description == "Multiple spaces here"

    def test_action_result_factory_methods(self):
        """Test action result factory methods."""
        assert ActionResult.success().value == "success"
        assert ActionResult.failure().value == "failure"

    def test_message_sender_factory_methods(self):
        """Test message sender factory methods."""
        assert MessageSender.engineer().value == "engineer"
        assert MessageSender.ai().value == "ai"
        assert MessageSender.system().value == "system"

    def test_feedback_validation(self):
        """Test feedback validation."""
        feedback = Feedback(feedback_type="positive", content="Good work")
        assert feedback.feedback_type == "positive"

        with pytest.raises(ValueError):
            Feedback(feedback_type="invalid", content="Test")
