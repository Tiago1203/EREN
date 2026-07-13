"""Hardening tests for the Cognitive Reasoning Engine.

Tests for:
- Division by zero protection
- Adapter functionality
- EventBus integration
- Capability registration
- Session immutability

Architecture only -- no business logic.
"""

from __future__ import annotations

import pytest

from core.reasoning import (
    BayesianConfidenceCalculator,
    CognitiveReasoningEngine,
    ConfidenceLevel,
    DempsterShaferCalculator,
    ReasoningContextAdapter,
    ReasoningMemoryAdapter,
    ReasoningSession,
    get_reasoning_capabilities,
    probability_to_level,
)
from core.reasoning.reasoning_types import (
    Evidence,
    EvidenceRelation,
    EvidenceSource,
    EvidenceType,
    Hypothesis,
    HypothesisPriority,
    ReasoningStage,
)


class TestDivisionByZeroProtection:
    """Tests for division by zero protection in calculators."""

    def test_bayesian_with_zero_denominator(self) -> None:
        """Bayesian calculator should return UNKNOWN on zero denominator."""
        calc = BayesianConfidenceCalculator()

        # Create evidence that leads to zero denominator
        # Prior = 0, supporting_prod = 1, contradicting_prod = 1
        # denominator = 0 * 1 + (1 - 0) * 1 = 1 (not zero)

        # Prior = 1, supporting_prod = 0, contradicting_prod = 0
        # denominator = 1 * 0 + (1 - 1) * 0 = 0 (ZERO!)
        hyp = Hypothesis(
            hypothesis_id="hyp_zero_denom",
            description="Test hypothesis",
            probability=1.0,  # Prior = 1
        )

        # Evidence that makes products zero
        evidence_supporting = [
            Evidence(
                evidence_id="ev1",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Test",
                confidence=1.0,
                weight=1.0,
            ),
            Evidence(
                evidence_id="ev2",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Test",
                confidence=1.0,
                weight=1.0,
            ),
        ]

        result = calc.calculate(hyp, evidence_supporting, [])

        # Should NOT raise ZeroDivisionError
        assert result is not None
        # Should return UNKNOWN confidence
        assert result.level == ConfidenceLevel.NONE
        assert result.value == 0.0

    def test_bayesian_with_negative_denominator(self) -> None:
        """Bayesian calculator should handle negative denominator."""
        calc = BayesianConfidenceCalculator()

        hyp = Hypothesis(
            hypothesis_id="hyp_neg",
            description="Test",
            probability=0.5,
        )

        # Create edge case evidence
        evidence = [
            Evidence(
                evidence_id="ev1",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Test",
                confidence=1.0,
                weight=1.0,
            ),
        ]

        result = calc.calculate(hyp, evidence, evidence)

        # Should not raise
        assert result is not None

    def test_dempster_shafer_with_high_conflict(self) -> None:
        """Dempster-Shafer should handle high conflict cases."""
        calc = DempsterShaferCalculator()

        hyp = Hypothesis(
            hypothesis_id="hyp_conflict",
            description="Test",
            probability=0.5,
        )

        # Evidence that causes high conflict
        supporting = [
            Evidence(
                evidence_id="ev1",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Supports",
                confidence=1.0,
                weight=1.0,
            ),
        ]

        contradicting = [
            Evidence(
                evidence_id="ev2",
                evidence_type=EvidenceType.OBSERVATION,
                source=EvidenceSource.USER,
                content="Contradicts",
                confidence=1.0,
                weight=1.0,
            ),
        ]

        result = calc.calculate(hyp, supporting, contradicting)

        # Should not raise
        assert result is not None

    def test_probability_to_level_helper(self) -> None:
        """Shared helper should work correctly."""
        assert probability_to_level(0.0) == ConfidenceLevel.NONE
        assert probability_to_level(0.1) == ConfidenceLevel.VERY_LOW
        assert probability_to_level(0.2) == ConfidenceLevel.LOW
        assert probability_to_level(0.4) == ConfidenceLevel.MODERATE
        assert probability_to_level(0.6) == ConfidenceLevel.HIGH
        assert probability_to_level(0.8) == ConfidenceLevel.VERY_HIGH
        assert probability_to_level(0.95) == ConfidenceLevel.CERTAIN


class TestReasoningContextAdapter:
    """Tests for ReasoningContextAdapter."""

    def test_adapter_with_no_reader(self) -> None:
        """Adapter should return empty when no reader."""
        adapter = ReasoningContextAdapter()

        evidence = adapter.read_evidence()
        assert evidence == []

        hypotheses = adapter.read_hypotheses()
        assert hypotheses == []

        device_info = adapter.read_device_info()
        assert device_info == {}

    def test_adapter_with_reader(self) -> None:
        """Adapter should call reader methods."""
        class MockReader:
            def get_evidence(self) -> list:
                return ["ev1", "ev2"]

            def get_hypotheses(self) -> list:
                return ["hyp1", "hyp2"]

            def get_device_info(self) -> dict:
                return {"model": "TestDevice"}

        adapter = ReasoningContextAdapter(reader=MockReader())

        assert adapter.read_evidence() == ["ev1", "ev2"]
        assert adapter.read_hypotheses() == ["hyp1", "hyp2"]
        assert adapter.read_device_info() == {"model": "TestDevice"}

    def test_adapter_write_conclusion(self) -> None:
        """Adapter should call writer methods."""
        class MockWriter:
            def __init__(self) -> None:
                self.conclusions: list = []

            def write_conclusion(self, conclusion: str) -> None:
                self.conclusions.append(conclusion)

            def update_confidence(self, confidence: float) -> None:
                pass

        writer = MockWriter()
        adapter = ReasoningContextAdapter(writer=writer)

        adapter.write_conclusion("Test conclusion")

        assert "Test conclusion" in writer.conclusions


class TestReasoningMemoryAdapter:
    """Tests for ReasoningMemoryAdapter."""

    def test_adapter_with_no_retriever(self) -> None:
        """Adapter should return empty when no retriever."""
        adapter = ReasoningMemoryAdapter()

        assert adapter.retrieve("query") == []
        assert adapter.search("query") == []

    def test_adapter_with_no_storer(self) -> None:
        """Adapter should return empty string when no storer."""
        adapter = ReasoningMemoryAdapter()

        result = adapter.store("content", "reasoning")
        assert result == ""

    def test_adapter_full_functionality(self) -> None:
        """Adapter should call underlying implementations."""
        class MockRetriever:
            def retrieve(self, query: str) -> list:
                return [f"result for {query}"]

            def search(self, query: str, limit: int = 10) -> list:
                return [f"search {query}"]

        class MockStorer:
            def store(self, content: str, memory_type: str) -> str:
                return f"stored_{content}"

        adapter = ReasoningMemoryAdapter(
            retriever=MockRetriever(),
            storer=MockStorer(),
        )

        assert adapter.retrieve("test") == ["result for test"]
        assert adapter.search("test") == ["search test"]
        assert adapter.store("content", "test") == "stored_content"


class TestCapabilityRegistration:
    """Tests for capability registration."""

    def test_get_reasoning_capabilities(self) -> None:
        """Should return all reasoning capabilities."""
        caps = get_reasoning_capabilities()

        assert len(caps) >= 14  # At least 14 capabilities

        # Check capability structure
        for cap in caps:
            assert "id" in cap
            assert "name" in cap
            assert "description" in cap
            assert "category" in cap
            assert "version" in cap

        # Check specific capabilities exist
        cap_ids = [c["id"] for c in caps]
        assert "reasoning.analyze" in cap_ids
        assert "reasoning.hypothesis.generate" in cap_ids
        assert "reasoning.decision.generate" in cap_ids
        assert "reasoning.trace" in cap_ids

    def test_capability_registrar(self) -> None:
        """Capability registrar should work without registry."""
        from core.reasoning.reasoning_engine import ReasoningCapabilityRegistrar

        registrar = ReasoningCapabilityRegistrar()

        # Should not raise even with None
        registrar.register(None)

        # Should not be registered (no registry provided)
        assert not registrar.is_registered


class TestSessionImmutability:
    """Tests for session immutability."""

    def test_session_is_frozen(self) -> None:
        """Session should be a frozen dataclass."""
        session = ReasoningSession(session_id="test")

        # Should be able to create
        assert session.session_id == "test"

        # Should not be able to modify
        with pytest.raises(Exception):  # FrozenInstanceError
            session.session_id = "modified"

    def test_session_creation(self) -> None:
        """Session should set timestamps on creation."""
        session = ReasoningSession(session_id="test")

        assert session.created_at != ""
        assert session.started_at == ""
        assert session.completed_at == ""

    def test_engine_creates_immutable_sessions(self) -> None:
        """Engine should create immutable sessions."""
        engine = CognitiveReasoningEngine()

        session = engine.start_session()

        assert isinstance(session, ReasoningSession)


class TestEventBusIntegration:
    """Tests for EventBus integration."""

    def test_event_publisher_disabled_without_bus(self) -> None:
        """Event publisher should handle missing EventBus gracefully."""
        from core.reasoning.reasoning_engine import ReasoningEventPublisher

        publisher = ReasoningEventPublisher()

        # Should not raise
        publisher.publish("test_event", test_data="value")

        # Should be disabled
        assert not publisher._enabled

    def test_engine_with_adapters(self) -> None:
        """Engine should accept adapters."""
        engine = CognitiveReasoningEngine(
            context_adapter=ReasoningContextAdapter(),
            memory_adapter=ReasoningMemoryAdapter(),
        )

        # Should work
        session = engine.start_session()
        assert session is not None

        # Adapters should be set
        assert engine._context_adapter is not None
        assert engine._memory_adapter is not None

    def test_capability_registration_method(self) -> None:
        """Engine should have register_capabilities method."""
        engine = CognitiveReasoningEngine()

        # Should exist and not raise
        engine.register_capabilities()

        # Should not be registered (no registry)
        assert not engine.capabilities_registered


class TestAdaptersInEngine:
    """Tests for adapters integrated in engine."""

    def test_engine_initializes_adapters(self) -> None:
        """Engine should initialize adapters by default."""
        engine = CognitiveReasoningEngine()

        assert isinstance(engine._context_adapter, ReasoningContextAdapter)
        assert isinstance(engine._memory_adapter, ReasoningMemoryAdapter)

    def test_engine_accepts_custom_adapters(self) -> None:
        """Engine should accept custom adapters."""
        custom_ctx = ReasoningContextAdapter()
        custom_mem = ReasoningMemoryAdapter()

        engine = CognitiveReasoningEngine(
            context_adapter=custom_ctx,
            memory_adapter=custom_mem,
        )

        assert engine._context_adapter is custom_ctx
        assert engine._memory_adapter is custom_mem
