"""Tests for CognitiveContext."""

from __future__ import annotations

import pytest

from core.PHASE_2.context import (
    CognitiveContext,
    CognitiveBlackboard,
    ContextManager,
    ContextStatus,
    Confidence,
    ConfidenceLevel,
    Evidence,
    EvidenceType,
    EvidenceSource,
    Hypothesis,
    Observation,
    UserContext,
    HospitalContext,
    DeviceContext,
    IntentResult,
)


class TestCognitiveContext:
    """Tests for CognitiveContext."""

    def test_create_context(self) -> None:
        """Creating a context should work."""
        context = CognitiveContext.create(
            correlation_id="corr-123",
            session_id="session-456",
        )

        assert context.context_id.startswith("ctx_")
        assert context.status == ContextStatus.INITIALIZING
        assert context.current_stage.name == "INTENTION"

    def test_update_status(self) -> None:
        """Updating status should return new context."""
        context = CognitiveContext.create()

        updated = context.update_status(ContextStatus.PROCESSING)

        assert updated.status == ContextStatus.PROCESSING
        assert updated != context  # Should be a new instance

    def test_add_evidence(self) -> None:
        """Adding evidence should return new context."""
        context = CognitiveContext.create()

        evidence = Evidence(
            evidence_id="ev-1",
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Patient reported error E101",
        )

        updated = context.add_evidence(evidence)

        assert len(updated.evidence) == 1
        assert updated.evidence[0] == evidence

    def test_add_hypothesis(self) -> None:
        """Adding hypothesis should return new context."""
        context = CognitiveContext.create()

        hypothesis = Hypothesis(
            hypothesis_id="hyp-1",
            description="Sensor malfunction",
            probability=0.7,
        )

        updated = context.add_hypothesis(hypothesis)

        assert len(updated.hypotheses) == 1
        assert updated.hypotheses[0].description == "Sensor malfunction"

    def test_rank_hypotheses(self) -> None:
        """Ranking hypotheses should sort by probability."""
        context = CognitiveContext.create()

        context = context.add_hypothesis(
            Hypothesis(hypothesis_id="hyp-1", description="Low prob", probability=0.3)
        )
        context = context.add_hypothesis(
            Hypothesis(hypothesis_id="hyp-2", description="High prob", probability=0.8)
        )
        context = context.add_hypothesis(
            Hypothesis(hypothesis_id="hyp-3", description="Medium prob", probability=0.5)
        )

        ranked = context.rank_hypotheses()

        assert ranked.hypotheses[0].hypothesis_id == "hyp-2"
        assert ranked.hypotheses[1].hypothesis_id == "hyp-3"
        assert ranked.hypotheses[2].hypothesis_id == "hyp-1"

    def test_complete(self) -> None:
        """Completing context should set final status."""
        context = CognitiveContext.create()

        from core.PHASE_2.context import ResponseResult
        completed = context.complete(
            response=ResponseResult(content="Diagnosis complete"),
        )

        assert completed.status == ContextStatus.COMPLETED
        assert completed.response.content == "Diagnosis complete"

    def test_recalculate_confidence(self) -> None:
        """Recalculating confidence should compute average."""
        context = CognitiveContext.create()

        context = context.add_evidence(
            Evidence(
                evidence_id="ev-1",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Test",
                confidence=Confidence(level=ConfidenceLevel.HIGH, score=0.8),
            )
        )
        context = context.add_evidence(
            Evidence(
                evidence_id="ev-2",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Test 2",
                confidence=Confidence(level=ConfidenceLevel.MODERATE, score=0.6),
            )
        )

        recalculated = context.recalculate_confidence()

        assert recalculated.overall_confidence.score > 0
        assert recalculated.overall_confidence.score < 1


class TestCognitiveBlackboard:
    """Tests for CognitiveBlackboard."""

    def test_write_evidence(self) -> None:
        """Writing evidence should add to blackboard."""
        blackboard = CognitiveBlackboard()

        evidence = Evidence(
            evidence_id="ev-1",
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Error detected",
        )

        entry_id = blackboard.write_evidence(
            engine_id="diagnostic_engine",
            evidence=evidence,
        )

        assert entry_id.startswith("entry_")
        stored = blackboard.read_entry(entry_id)
        assert stored is not None
        assert stored.author_engine == "diagnostic_engine"

    def test_read_evidence(self) -> None:
        """Reading evidence should return all evidence."""
        blackboard = CognitiveBlackboard()

        evidence1 = Evidence(
            evidence_id="ev-1",
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Error 1",
        )
        evidence2 = Evidence(
            evidence_id="ev-2",
            evidence_type=EvidenceType.MEASUREMENT,
            source=EvidenceSource.SENSOR,
            content="Error 2",
        )

        blackboard.write_evidence("engine1", evidence1)
        blackboard.write_evidence("engine2", evidence2)

        all_evidence = blackboard.read_evidence()

        assert len(all_evidence) == 2

    def test_read_by_engine(self) -> None:
        """Reading by engine should filter correctly."""
        blackboard = CognitiveBlackboard()

        evidence = Evidence(
            evidence_id="ev-1",
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Test",
        )

        blackboard.write_evidence("diagnostic_engine", evidence)

        entries = blackboard.read_by_engine("diagnostic_engine")
        assert len(entries) == 1

        entries = blackboard.read_by_engine("other_engine")
        assert len(entries) == 0

    def test_supersede_entry(self) -> None:
        """Superseding an entry should mark it inactive."""
        blackboard = CognitiveBlackboard()

        evidence = Evidence(
            evidence_id="ev-1",
            evidence_type=EvidenceType.OBSERVATION,
            source=EvidenceSource.USER,
            content="Test",
        )

        old_id = blackboard.write_evidence("engine", evidence)
        new_id = "entry_new"

        blackboard.supersede_entry(old_id, new_id)

        entry = blackboard.read_entry(old_id)
        assert entry is not None
        assert entry.superseded_by == new_id

        # Should not appear in active reads
        active = blackboard.read_all_entries(include_superseded=False)
        assert old_id not in [e.entry_id for e in active]


class TestContextManager:
    """Tests for ContextManager."""

    def test_create_context(self) -> None:
        """Creating context through manager should work."""
        manager = ContextManager()

        context = manager.create_context(
            correlation_id="corr-123",
            session_id="session-456",
        )

        assert context.context_id.startswith("ctx_")
        assert manager.get_context(context.context_id) is context

    def test_update_context(self) -> None:
        """Updating context should persist changes."""
        manager = ContextManager()

        context = manager.create_context()
        updated = context.update_status(ContextStatus.PROCESSING)

        manager.update_context(updated)

        retrieved = manager.get_context(context.context_id)
        assert retrieved.status == ContextStatus.PROCESSING

    def test_find_by_session(self) -> None:
        """Finding by session should return matching contexts."""
        manager = ContextManager()

        ctx1 = manager.create_context(session_id="session-123")
        ctx2 = manager.create_context(session_id="session-456")

        found = manager.find_by_session("session-123")

        assert len(found) == 1
        assert found[0].context_id == ctx1.context_id

    def test_statistics(self) -> None:
        """Getting statistics should return counts."""
        manager = ContextManager()

        manager.create_context()
        manager.create_context()

        stats = manager.get_statistics()

        assert stats.total == 2
        assert stats.by_status.get("INITIALIZING", 0) == 2

    def test_delete_context(self) -> None:
        """Deleting context should remove it."""
        manager = ContextManager()

        context = manager.create_context()
        result = manager.delete_context(context.context_id)

        assert result is True
        assert manager.get_context(context.context_id) is None


class TestConfidence:
    """Tests for Confidence."""

    def test_is_confident(self) -> None:
        """Confidence threshold should work."""
        conf = Confidence(level=ConfidenceLevel.MODERATE, score=0.6)

        assert conf.is_confident(threshold=0.5)
        assert not conf.is_confident(threshold=0.8)

    def test_is_certain(self) -> None:
        """Certainty check should work."""
        conf_low = Confidence(level=ConfidenceLevel.LOW, score=0.3)
        conf_high = Confidence(level=ConfidenceLevel.HIGH, score=0.8)

        assert not conf_low.is_certain()
        assert conf_high.is_certain()
