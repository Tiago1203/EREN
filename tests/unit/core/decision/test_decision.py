"""Tests for the Cognitive Decision Engine."""

from __future__ import annotations

from core.decision import (
    BalancedPolicy,
    BalancedStrategy,
    CognitiveDecisionEngine,
    ConservativePolicy,
    DecisionCandidate,
    DecisionCategory,
    DecisionContext,
    DecisionEvaluatorComponent,
    DecisionPriority,
    DecisionStatus,
    DecisionStrategyType,
    DecisionType,
    PriorityEvaluatorComponent,
    RiskEvaluatorComponent,
    RiskLevel,
)


class TestDecisionTypes:
    """Tests for decision types."""

    def test_decision_types(self) -> None:
        """All decision types should be defined."""
        assert DecisionType.CONTINUE_ANALYSIS
        assert DecisionType.EXECUTE_TOOL
        assert DecisionType.ESCALATE_TO_HUMAN
        assert DecisionType.STOP_ANALYSIS

    def test_decision_priority(self) -> None:
        """All priorities should be defined."""
        assert DecisionPriority.CRITICAL
        assert DecisionPriority.HIGH
        assert DecisionPriority.MEDIUM
        assert DecisionPriority.LOW

    def test_risk_levels(self) -> None:
        """All risk levels should be defined."""
        assert RiskLevel.MINIMAL
        assert RiskLevel.LOW
        assert RiskLevel.MEDIUM
        assert RiskLevel.HIGH
        assert RiskLevel.CRITICAL


class TestDecisionCandidate:
    """Tests for DecisionCandidate."""

    def test_candidate_creation(self) -> None:
        """Creating a candidate should work."""
        candidate = DecisionCandidate(
            candidate_id="cand_1",
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Continue with analysis",
            category=DecisionCategory.ANALYSIS,
            confidence=0.8,
        )

        assert candidate.candidate_id == "cand_1"
        assert candidate.decision_type == DecisionType.CONTINUE_ANALYSIS
        assert candidate.confidence == 0.8
        assert candidate.created_at != ""


class TestCognitiveDecisionEngine:
    """Tests for CognitiveDecisionEngine."""

    def test_engine_creation(self) -> None:
        """Creating engine should work."""
        engine = CognitiveDecisionEngine()

        assert engine is not None
        assert engine._evaluator is not None
        assert engine._policy is not None

    def test_create_candidate(self) -> None:
        """Creating a candidate should work."""
        engine = CognitiveDecisionEngine()

        candidate = engine.create_candidate(
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test decision",
            confidence=0.7,
            based_on_hypothesis="hyp_123",
        )

        assert candidate is not None
        assert candidate.decision_type == DecisionType.CONTINUE_ANALYSIS
        assert candidate.candidate_id.startswith("cand_")

    def test_select_decision(self) -> None:
        """Selecting a decision should work."""
        engine = CognitiveDecisionEngine()

        # Create candidates
        cand1 = engine.create_candidate(
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Continue",
            confidence=0.9,
        )
        cand2 = engine.create_candidate(
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Execute",
            confidence=0.6,
        )

        # Create context
        context = DecisionContext(
            session_id="test_session",
            best_hypothesis_id="hyp_123",
            best_hypothesis_confidence=0.8,
        )

        # Select decision
        decision = engine.select_decision(
            [cand1.candidate_id, cand2.candidate_id],
            context,
        )

        assert decision is not None
        assert decision.decision_id.startswith("dec_")

    def test_approve_decision(self) -> None:
        """Approving a decision should work."""
        engine = CognitiveDecisionEngine()

        cand = engine.create_candidate(
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test",
            confidence=0.9,
        )

        context = DecisionContext(session_id="test")
        decision = engine.select_decision([cand.candidate_id], context)

        if decision:
            approved = engine.approve_decision(decision.decision_id)
            assert approved is not None
            assert approved.status == DecisionStatus.APPROVED

    def test_reject_decision(self) -> None:
        """Rejecting a decision should work."""
        engine = CognitiveDecisionEngine()

        cand = engine.create_candidate(
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Test",
            confidence=0.5,
        )

        context = DecisionContext(session_id="test")
        decision = engine.select_decision([cand.candidate_id], context)

        if decision:
            rejected = engine.reject_decision(decision.decision_id, "Low confidence")
            assert rejected is not None
            assert rejected.status == DecisionStatus.REJECTED

    def test_capability_registration(self) -> None:
        """Capability registration should work."""
        engine = CognitiveDecisionEngine()

        engine.register_capabilities()
        assert not engine.capabilities_registered  # No registry provided


class TestRiskEvaluator:
    """Tests for RiskEvaluatorComponent."""

    def test_evaluate_low_risk(self) -> None:
        """Evaluating low risk should return low score."""
        evaluator = RiskEvaluatorComponent()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test",
            category=DecisionCategory.ANALYSIS,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
        )

        context = DecisionContext(session_id="test")

        score = evaluator.evaluate(candidate, context)

        assert score < 0.5  # Low risk

    def test_evaluate_critical_risk(self) -> None:
        """Evaluating critical risk should return high score."""
        evaluator = RiskEvaluatorComponent()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.ESCALATE_TO_HUMAN,
            description="Test",
            category=DecisionCategory.CONTROL,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.5,
        )

        context = DecisionContext(session_id="test")

        score = evaluator.evaluate(candidate, context)

        assert score > 0.7  # High risk


class TestPriorityEvaluator:
    """Tests for PriorityEvaluatorComponent."""

    def test_evaluate_critical_priority(self) -> None:
        """Critical priority should score highest."""
        evaluator = PriorityEvaluatorComponent()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.ESCALATE_TO_HUMAN,
            description="Test",
            category=DecisionCategory.CONTROL,
            priority=DecisionPriority.CRITICAL,
            confidence=0.9,
        )

        context = DecisionContext(session_id="test")

        score = evaluator.evaluate(candidate, context)

        assert score >= 100  # Critical = 100

    def test_evaluate_low_priority(self) -> None:
        """Low priority should score lowest."""
        evaluator = PriorityEvaluatorComponent()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test",
            category=DecisionCategory.ANALYSIS,
            priority=DecisionPriority.LOW,
            confidence=0.9,
        )

        context = DecisionContext(session_id="test")

        score = evaluator.evaluate(candidate, context)

        assert score < 50  # Low = 25 + bonus


class TestPolicies:
    """Tests for decision policies."""

    def test_conservative_approve(self) -> None:
        """Conservative policy should require high confidence."""
        policy = ConservativePolicy()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Test",
            category=DecisionCategory.ACTION,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            based_on_evidence=("ev1",),
        )

        context = DecisionContext(session_id="test")

        should_approve = policy.should_approve(candidate, context)

        assert should_approve is True

    def test_conservative_reject_low_confidence(self) -> None:
        """Conservative policy should reject low confidence."""
        policy = ConservativePolicy()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Test",
            category=DecisionCategory.ACTION,
            risk_level=RiskLevel.LOW,
            confidence=0.5,  # Low
            based_on_evidence=("ev1",),
        )

        context = DecisionContext(session_id="test")

        should_approve = policy.should_approve(candidate, context)

        assert should_approve is False

    def test_conservative_escalate_critical(self) -> None:
        """Conservative policy should escalate critical risk."""
        policy = ConservativePolicy()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Test",
            category=DecisionCategory.ACTION,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.9,
        )

        context = DecisionContext(session_id="test")

        should_escalate = policy.should_escalate(candidate, context)

        assert should_escalate is True


class TestStrategies:
    """Tests for decision strategies."""

    def test_balanced_strategy(self) -> None:
        """Balanced strategy should calculate score."""
        strategy = BalancedStrategy()

        candidate = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test",
            category=DecisionCategory.ANALYSIS,
            confidence=0.8,
        )

        context = DecisionContext(session_id="test")

        score = strategy.calculate_score(
            candidate=candidate,
            risk_score=0.3,
            priority_score=75,
            context=context,
        )

        assert 0.0 <= score <= 1.0

    def test_strategy_rank(self) -> None:
        """Strategy should rank candidates."""
        strategy = BalancedStrategy()

        cand1 = DecisionCandidate(
            candidate_id="c1",
            decision_type=DecisionType.CONTINUE_ANALYSIS,
            description="Test 1",
            category=DecisionCategory.ANALYSIS,
            confidence=0.9,
        )
        cand2 = DecisionCandidate(
            candidate_id="c2",
            decision_type=DecisionType.EXECUTE_TOOL,
            description="Test 2",
            category=DecisionCategory.ACTION,
            confidence=0.6,
        )

        scored = [
            (0.8, cand1),
            (0.5, cand2),
        ]

        ranked = strategy.rank(scored)

        assert ranked[0][0] == 0.8  # Highest score first
        assert ranked[1][0] == 0.5


class TestDecisionContext:
    """Tests for DecisionContext."""

    def test_context_creation(self) -> None:
        """Creating context should work."""
        context = DecisionContext(
            session_id="test_session",
            best_hypothesis_id="hyp_123",
            best_hypothesis_confidence=0.85,
            available_evidence=("ev1", "ev2", "ev3"),
        )

        assert context.session_id == "test_session"
        assert context.best_hypothesis_confidence == 0.85
        assert len(context.available_evidence) == 3
