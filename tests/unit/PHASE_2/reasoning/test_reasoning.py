"""Tests for the Cognitive Reasoning Engine."""

from __future__ import annotations

import pytest

from core.PHASE_2.reasoning import (
    CognitiveReasoningEngine,
    ConfidenceScore,
    DecisionType,
    EvidenceManager,
    EvidenceRelation,
    EvidenceSource,
    EvidenceType,
    HypothesisManager,
    HypothesisPriority,
    HypothesisStatus,
    ReasoningStrategy,
)


class TestHypothesisManager:
    """Tests for HypothesisManager."""

    def test_create_hypothesis(self) -> None:
        """Creating a hypothesis should work."""
        manager = HypothesisManager()

        hyp = manager.create(
            description="Sensor malfunction",
            initial_probability=0.8,
        )

        assert hyp.hypothesis_id.startswith("hyp_")
        assert hyp.description == "Sensor malfunction"
        assert hyp.probability == 0.8
        assert hyp.status == HypothesisStatus.ACTIVE

    def test_get_hypothesis(self) -> None:
        """Getting a hypothesis should work."""
        manager = HypothesisManager()

        created = manager.create(description="Test hypothesis")
        retrieved = manager.get(created.hypothesis_id)

        assert retrieved is not None
        assert retrieved.hypothesis_id == created.hypothesis_id

    def test_add_evidence(self) -> None:
        """Adding evidence should update hypothesis."""
        manager = HypothesisManager()

        hyp = manager.create(description="Test")

        updated = manager.add_evidence(
            hyp.hypothesis_id,
            "ev_123",
            EvidenceRelation.SUPPORTS,
        )

        assert updated is not None
        assert "ev_123" in updated.supporting_evidence

    def test_rank_hypotheses(self) -> None:
        """Ranking should sort by probability."""
        manager = HypothesisManager()

        h1 = manager.create("Low", initial_probability=0.3)
        h2 = manager.create("High", initial_probability=0.8)
        h3 = manager.create("Medium", initial_probability=0.5)

        ranked = manager.rank_hypotheses()

        assert ranked[0].hypothesis_id == h2.hypothesis_id
        assert ranked[1].hypothesis_id == h3.hypothesis_id
        assert ranked[2].hypothesis_id == h1.hypothesis_id


class TestEvidenceManager:
    """Tests for EvidenceManager."""

    def test_add_evidence(self) -> None:
        """Adding evidence should work."""
        manager = EvidenceManager()

        ev = manager.add(
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Error E101 detected",
            confidence=0.9,
        )

        assert ev.evidence_id.startswith("ev_")
        assert ev.content == "Error E101 detected"
        assert ev.confidence == 0.9

    def test_add_measurement(self) -> None:
        """Adding measurement should work."""
        manager = EvidenceManager()

        ev = manager.add_measurement(
            value=98.5,
            unit="%",
            normal_range=(95, 100),
        )

        assert ev.evidence_type == EvidenceType.MEASUREMENT
        assert ev.content["value"] == 98.5

    def test_derive_evidence(self) -> None:
        """Deriving evidence should work."""
        manager = EvidenceManager()

        parent = manager.add(
            EvidenceType.OBSERVATION,
            EvidenceSource.USER,
            "Observation",
        )

        derived = manager.derive(
            parent.evidence_id,
            {"derived": True},
            confidence=0.7,
        )

        assert derived is not None
        assert derived.parent_evidence_id == parent.evidence_id
        assert derived.confidence < parent.confidence


class TestCognitiveReasoningEngine:
    """Tests for CognitiveReasoningEngine."""

    def test_start_session(self) -> None:
        """Starting a session should work."""
        engine = CognitiveReasoningEngine()

        session = engine.start_session()

        assert session.session_id.startswith("sess_")
        assert session.stage.value == "initial"

    def test_generate_hypotheses(self) -> None:
        """Generating hypotheses should work."""
        engine = CognitiveReasoningEngine()
        engine.start_session()

        hypotheses = engine.generate_hypotheses([
            "Sensor malfunction",
            "Calibration needed",
            "Cable damage",
        ])

        assert len(hypotheses) == 3
        assert all(h.status == HypothesisStatus.ACTIVE for h in hypotheses)

    def test_add_evidence(self) -> None:
        """Adding evidence should work."""
        engine = CognitiveReasoningEngine()
        engine.start_session()

        evidence = engine.add_evidence(
            EvidenceType.OBSERVATION,
            "Device shows error E101",
            EvidenceSource.USER,
            confidence=0.9,
        )

        assert evidence.evidence_id.startswith("ev_")
        assert evidence.content == "Device shows error E101"

    def test_make_decision(self) -> None:
        """Making a decision should work."""
        engine = CognitiveReasoningEngine()
        engine.start_session()

        # Create hypothesis
        hyps = engine.generate_hypotheses(["Sensor malfunction"])
        hyp = hyps[0]

        # Add evidence to increase confidence
        engine.add_evidence(
            EvidenceType.OBSERVATION,
            "Error confirmed",
            EvidenceSource.USER,
            0.9,
        )
        engine.incorporate_evidence(
            evidence_id=engine.get_session().state.active_evidence > 0 and list(engine._evidence_manager.get_all())[0].evidence_id,
            hypothesis_id=hyp.hypothesis_id,
            relation=EvidenceRelation.SUPPORTS,
        )

        # Make decision
        decision = engine.make_decision(
            decision_type=DecisionType.DIAGNOSTIC,
            based_on_hypothesis_id=hyp.hypothesis_id,
            justification=["Based on sensor malfunction hypothesis"],
        )

        assert decision.decision_id.startswith("dec_")
        assert decision.based_on_hypothesis == hyp.hypothesis_id

    def test_get_trace(self) -> None:
        """Getting trace should work."""
        engine = CognitiveReasoningEngine()
        engine.start_session()
        engine.generate_hypotheses(["Test"])
        engine.add_evidence(
            EvidenceType.OBSERVATION,
            "Test observation",
            EvidenceSource.USER,
        )

        trace = engine.get_trace()

        assert trace is not None
        assert trace.trace_id.startswith("trace_")
        assert len(trace.events) > 0

    def test_end_session(self) -> None:
        """Ending session should work."""
        engine = CognitiveReasoningEngine()
        engine.start_session()

        session = engine.end_session()

        assert session is not None
        assert session.stage.value == "completed"


class TestConfidenceCalculators:
    """Tests for confidence calculators."""

    def test_default_calculator(self) -> None:
        """Default calculator should work."""
        from core.PHASE_2.reasoning.confidence_model import DefaultConfidenceCalculator
        from core.PHASE_2.reasoning.reasoning_types import Hypothesis

        calc = DefaultConfidenceCalculator()

        hyp = Hypothesis(
            hypothesis_id="hyp_test",
            description="Test",
            probability=0.5,
        )

        score = calc.calculate(hyp, [], [])

        assert 0.0 <= score.value <= 1.0

    def test_factory(self) -> None:
        """Factory should create calculators."""
        from core.PHASE_2.reasoning.confidence_model import ConfidenceCalculatorFactory

        calc = ConfidenceCalculatorFactory.create("default")
        assert calc is not None

        calc_bayesian = ConfidenceCalculatorFactory.create("bayesian")
        assert calc_bayesian is not None
