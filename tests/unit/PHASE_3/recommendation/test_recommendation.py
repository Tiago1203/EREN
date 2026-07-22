"""Tests for AIRecommendation aggregate."""

from __future__ import annotations

import pytest

from core.PHASE_3.recommendation.domain import (
    AIRecommendation,
    RecommendationCategory,
    RecommendationConfidence,
    RecommendationStatus,
    RecommendationUrgency,
    RejectionReason,
)
from core.PHASE_1.infrastructure.shared import DeviceId, EngineerId, IncidentId, RecommendationId, TenantId


class TestAIRecommendation:
    """Tests for AIRecommendation aggregate."""

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
        return IncidentId(value="incident_001")

    @pytest.fixture
    def recommendation_id(self) -> RecommendationId:
        return RecommendationId.generate()

    def test_create_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        incident_id,
    ):
        """Test creating a new recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=incident_id,
            device_id=device_id,
            title="Replace pressure sensor",
            description="The pressure sensor is showing drift",
            rationale="Based on 15 similar cases",
            category=RecommendationCategory.repair(),
            confidence=RecommendationConfidence.high(),
            model_version="v2.1",
        )

        assert recommendation.tenant_id == tenant_id
        assert recommendation.device_id == device_id
        assert recommendation.title == "Replace pressure sensor"
        assert recommendation.status == RecommendationStatus.generated()
        assert recommendation.version == 1
        assert recommendation.has_pending_events()

    def test_recommendation_publishes_event_on_creation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        incident_id,
    ):
        """Test that recommendation publishes event on creation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=incident_id,
            device_id=device_id,
            title="Test recommendation",
            description="Test description",
            rationale="Test rationale",
            category=RecommendationCategory.calibration(),
            confidence=RecommendationConfidence.medium(),
            model_version="v1",
        )

        events = recommendation.pop_events()
        assert len(events) == 1
        assert events[0].event_type == "RecommendationCreated"

    def test_accept_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        engineer_id,
    ):
        """Test accepting a recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test recommendation",
            description="Test description",
            rationale="Test rationale",
            category=RecommendationCategory.preventive_maintenance(),
            confidence=RecommendationConfidence.high(),
            model_version="v1",
        )
        recommendation.pop_events()

        recommendation.accept(
            engineer_id=engineer_id,
            note=None,
            expected_version=1,
        )

        assert recommendation.status == RecommendationStatus.accepted()
        assert recommendation.reviewed_by == engineer_id
        assert recommendation.reviewed_at is not None
        assert recommendation.version == 2

    def test_reject_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        engineer_id,
    ):
        """Test rejecting a recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test recommendation",
            description="Test description",
            rationale="Test rationale",
            category=RecommendationCategory.repair(),
            confidence=RecommendationConfidence.low(),
            model_version="v1",
        )
        recommendation.pop_events()

        reason = RejectionReason.not_applicable(description="Already done")
        recommendation.reject(
            engineer_id=engineer_id,
            reason=reason,
            feedback="Already fixed the sensor",
            expected_version=1,
        )

        assert recommendation.status == RecommendationStatus.rejected()
        assert recommendation.rejection_reason == reason
        assert recommendation.engineer_feedback == "Already fixed the sensor"
        assert recommendation.reviewed_by == engineer_id

    def test_cannot_accept_terminal_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        engineer_id,
    ):
        """Test that terminal recommendations cannot be accepted."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test recommendation",
            description="Test description",
            rationale="Test rationale",
            category=RecommendationCategory.repair(),
            confidence=RecommendationConfidence.high(),
            model_version="v1",
        )
        recommendation.pop_events()

        # First accept
        recommendation.accept(engineer_id=engineer_id, expected_version=1)

        # Try to accept again - should fail
        with pytest.raises(Exception):
            recommendation.accept(engineer_id=engineer_id, expected_version=2)

    def test_provide_feedback(
        self,
        recommendation_id,
        tenant_id,
        device_id,
        engineer_id,
    ):
        """Test providing feedback on a recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test recommendation",
            description="Test description",
            rationale="Test rationale",
            category=RecommendationCategory.calibration(),
            confidence=RecommendationConfidence.medium(),
            model_version="v1",
        )
        recommendation.pop_events()

        recommendation.provide_feedback(
            engineer_id=engineer_id,
            feedback="Need more evidence before accepting",
            expected_version=1,
        )

        assert recommendation.engineer_feedback == "Need more evidence before accepting"
        assert recommendation.version == 2

    def test_high_confidence_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
    ):
        """Test high confidence recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test",
            description="Test",
            rationale="Test",
            category=RecommendationCategory.safety(),
            confidence=RecommendationConfidence.high(),
            model_version="v1",
        )

        assert recommendation.is_high_confidence()
        assert not recommendation.is_low_confidence()

    def test_low_confidence_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
    ):
        """Test low confidence recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test",
            description="Test",
            rationale="Test",
            category=RecommendationCategory.repair(),
            confidence=RecommendationConfidence.low(),
            model_version="v1",
        )

        assert recommendation.is_low_confidence()
        assert not recommendation.is_high_confidence()

    def test_urgent_recommendation(
        self,
        recommendation_id,
        tenant_id,
        device_id,
    ):
        """Test urgent recommendation."""
        recommendation = AIRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            incident_id=None,
            device_id=device_id,
            title="Test",
            description="Test",
            rationale="Test",
            category=RecommendationCategory.safety(),
            confidence=RecommendationConfidence.high(),
            model_version="v1",
            urgency=RecommendationUrgency.immediate(),
        )

        assert recommendation.is_urgent()


class TestRecommendationValueObjects:
    """Tests for Recommendation value objects."""

    def test_recommendation_status_factory_methods(self):
        """Test status factory methods."""
        assert RecommendationStatus.generated().value == "generated"
        assert RecommendationStatus.accepted().value == "accepted"
        assert RecommendationStatus.rejected().value == "rejected"

    def test_recommendation_status_is_terminal(self):
        """Test terminal states."""
        assert RecommendationStatus.accepted().is_terminal()
        assert RecommendationStatus.rejected().is_terminal()
        assert not RecommendationStatus.pending_review().is_terminal()

    def test_recommendation_category_factory_methods(self):
        """Test category factory methods."""
        assert RecommendationCategory.preventive_maintenance().value == "preventive_maintenance"
        assert RecommendationCategory.calibration().value == "calibration"
        assert RecommendationCategory.safety().value == "safety"

    def test_recommendation_confidence_factory_methods(self):
        """Test confidence factory methods."""
        assert RecommendationConfidence.high().score == 0.85
        assert RecommendationConfidence.medium().score == 0.65
        assert RecommendationConfidence.low().score == 0.35

    def test_recommendation_confidence_bounds(self):
        """Test confidence validation."""
        with pytest.raises(ValueError):
            RecommendationConfidence(score=1.5, evidence_count=1, model_version="v1")

    def test_rejection_reason_codes(self):
        """Test rejection reason codes."""
        reason = RejectionReason.already_done(description="Sensor already replaced")
        assert reason.reason_code == "already_done"

        reason = RejectionReason.insufficient_evidence(
            description="Need more data",
            alternative="Check logs first",
        )
        assert reason.reason_code == "insufficient_evidence"
        assert reason.alternative_suggestion == "Check logs first"

    def test_recommendation_urgency_levels(self):
        """Test urgency levels."""
        assert RecommendationUrgency.immediate().value == "immediate"
        assert RecommendationUrgency.soon().value == "soon"
        assert RecommendationUrgency.scheduled().value == "scheduled"
        assert RecommendationUrgency.optional().value == "optional"
