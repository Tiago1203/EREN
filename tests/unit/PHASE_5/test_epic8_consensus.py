"""
Tests for EPIC 8: Consensus Engine

Test suite for the Consensus Engine.
"""

import pytest
from datetime import UTC, datetime

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.foundation import (
    AgentType,
    AgentState,
    AgentTask,
)

from core.PHASE_5.epic8_consensus import (
    ConsensusEngine,
    ConsensusEngineConfig,
)

from core.PHASE_5.epic8_consensus.domain import (
    ConsensusDecision,
    ConsensusLevel,
    AgentVote,
    VoteOption,
    ConflictCase,
    ConflictType,
    ResolutionStrategy,
)

from core.PHASE_5.epic8_consensus.engines import (
    VotingEngine,
    ConflictResolver,
    RankingEngine,
    ConsensusBuilder,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def engine_config():
    """Create engine config."""
    return ConsensusEngineConfig(
        enable_voting=True,
        enable_conflict_resolution=True,
        enable_ranking=True,
        enable_consensus_building=True,
    )


@pytest.fixture
def consensus_engine(engine_config):
    """Create consensus engine."""
    return ConsensusEngine(
        agent_id="consensus_test_1",
        config=engine_config,
    )


# =============================================================================
# TEST CONSENSUS ENGINE
# =============================================================================

class TestConsensusEngine:
    """Tests for ConsensusEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, consensus_engine, engine_config):
        """Test engine initializes correctly."""
        assert consensus_engine.agent_id == "consensus_test_1"
        assert consensus_engine.agent_type == AgentType.CONSENSUS
        assert consensus_engine.config == engine_config
        
        # Engines should be initialized
        assert consensus_engine._voting_engine is not None
        assert consensus_engine._conflict_resolver is not None
        assert consensus_engine._ranking_engine is not None
        assert consensus_engine._consensus_builder is not None
    
    @pytest.mark.asyncio
    async def test_engine_initialize(self, consensus_engine):
        """Test engine initialization method."""
        await consensus_engine.initialize()
        assert consensus_engine.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_vote_action(self, consensus_engine):
        """Test voting action."""
        task = AgentTask(
            task_id="task_1",
            agent_id="consensus_test_1",
            task_type="consensus",
            input_data={
                "action": "vote",
                "decision_id": "decision_123",
                "votes": [
                    {"agent_id": "agent_1", "option": "approve", "confidence": 0.9},
                    {"agent_id": "agent_2", "option": "approve", "confidence": 0.8},
                    {"agent_id": "agent_3", "option": "reject", "confidence": 0.7},
                ],
            },
        )
        
        result = await consensus_engine.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["action"] == "vote"
    
    @pytest.mark.asyncio
    async def test_resolve_action(self, consensus_engine):
        """Test conflict resolution action."""
        task = AgentTask(
            task_id="task_2",
            agent_id="consensus_test_1",
            task_type="consensus",
            input_data={
                "action": "resolve",
                "case": {
                    "session_id": "session_123",
                    "type": "answer_conflict",
                    "responses": [
                        {"agent_id": "agent_1", "response": {"answer": "A"}},
                        {"agent_id": "agent_2", "response": {"answer": "B"}},
                    ],
                },
            },
        )
        
        result = await consensus_engine.execute(task)
        
        assert result is not None
        # Check output contains expected keys
        assert "action" in result.output or "resolved" in result.output
    
    @pytest.mark.asyncio
    async def test_metrics(self, consensus_engine):
        """Test engine metrics."""
        metrics = consensus_engine.get_metrics()
        
        assert "decisions_made" in metrics
        assert "conflicts_resolved" in metrics
        assert "engines_enabled" in metrics


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestAgentVote:
    """Tests for AgentVote."""
    
    def test_vote_creation(self):
        """Test vote creation."""
        vote = AgentVote(
            vote_id="vote_1",
            agent_id="agent_1",
            option=VoteOption.APPROVE,
        )
        
        assert vote.vote_id == "vote_1"
        assert vote.agent_id == "agent_1"
        assert vote.option == VoteOption.APPROVE
    
    def test_vote_weight(self):
        """Test vote weight calculation."""
        vote = AgentVote(
            agent_id="agent_1",
            option=VoteOption.APPROVE,
            confidence=0.8,
            expertise_level=0.9,
        )
        
        weight = vote.get_weight()
        assert 0.0 <= weight <= 1.0


class TestConsensusDecision:
    """Tests for ConsensusDecision."""
    
    def test_decision_creation(self):
        """Test decision creation."""
        decision = ConsensusDecision(
            decision_id="dec_1",
            session_id="session_1",
        )
        
        assert decision.decision_id == "dec_1"
        assert decision.consensus_level == ConsensusLevel.NONE
    
    def test_add_vote(self):
        """Test adding votes."""
        decision = ConsensusDecision(session_id="session_1")
        
        decision.add_vote(AgentVote(
            agent_id="agent_1",
            option=VoteOption.APPROVE,
        ))
        
        assert decision.total_votes == 1
    
    def test_unanimous_approval(self):
        """Test unanimous approval."""
        decision = ConsensusDecision(session_id="session_1")
        
        decision.add_vote(AgentVote(agent_id="agent_1", option=VoteOption.APPROVE))
        decision.add_vote(AgentVote(agent_id="agent_2", option=VoteOption.APPROVE))
        
        assert decision.consensus_level == ConsensusLevel.UNANIMOUS
    
    def test_no_consensus(self):
        """Test no consensus."""
        decision = ConsensusDecision(session_id="session_1")
        
        decision.add_vote(AgentVote(agent_id="agent_1", option=VoteOption.APPROVE))
        decision.add_vote(AgentVote(agent_id="agent_2", option=VoteOption.REJECT))
        
        assert decision.consensus_level != ConsensusLevel.UNANIMOUS
    
    def test_approval_rate(self):
        """Test approval rate."""
        decision = ConsensusDecision(session_id="session_1")
        
        decision.add_vote(AgentVote(agent_id="agent_1", option=VoteOption.APPROVE))
        decision.add_vote(AgentVote(agent_id="agent_2", option=VoteOption.APPROVE))
        decision.add_vote(AgentVote(agent_id="agent_3", option=VoteOption.REJECT))
        
        assert decision.get_approval_rate() == 2/3


class TestConflictCase:
    """Tests for ConflictCase."""
    
    def test_case_creation(self):
        """Test case creation."""
        case = ConflictCase(
            case_id="case_1",
            session_id="session_1",
            conflict_type=ConflictType.ANSWER_CONFLICT,
        )
        
        assert case.case_id == "case_1"
        assert case.status == "open"
    
    def test_add_response(self):
        """Test adding responses."""
        case = ConflictCase(session_id="session_1")
        
        case.add_response("agent_1", {"answer": "A"})
        
        assert len(case.conflicting_responses) == 1
        assert "agent_1" in case.agents_involved
    
    def test_resolve(self):
        """Test resolving conflict."""
        case = ConflictCase(session_id="session_1")
        
        case.add_response("agent_1", {"answer": "A"})
        case.add_response("agent_2", {"answer": "B"})
        
        case.resolve(ResolutionStrategy.MERGED, {"answer": "merged"})
        
        assert case.is_resolved() is True
        assert case.resolved_response == {"answer": "merged"}
    
    def test_escalate(self):
        """Test escalating conflict."""
        case = ConflictCase(session_id="session_1")
        
        case.escalate()
        
        assert case.status == "escalated"


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestVotingEngine:
    """Tests for VotingEngine."""
    
    @pytest.mark.asyncio
    async def test_vote(self):
        """Test voting."""
        engine = VotingEngine()
        
        votes = [
            AgentVote(agent_id="agent_1", option=VoteOption.APPROVE, confidence=0.9),
            AgentVote(agent_id="agent_2", option=VoteOption.APPROVE, confidence=0.8),
            AgentVote(agent_id="agent_3", option=VoteOption.REJECT, confidence=0.7),
        ]
        
        result = await engine.vote("decision_1", votes)
        
        assert result.decision_id == "decision_1"
        assert result.votes_count == 3
        assert result.consensus_level != ConsensusLevel.NONE
    
    @pytest.mark.asyncio
    async def test_tally_votes(self):
        """Test vote tallying."""
        engine = VotingEngine()
        
        votes = [
            AgentVote(agent_id="agent_1", option=VoteOption.APPROVE, confidence=0.9),
            AgentVote(agent_id="agent_2", option=VoteOption.APPROVE, confidence=0.8),
            AgentVote(agent_id="agent_3", option=VoteOption.ABSTAIN, confidence=0.5),
        ]
        
        tallied = await engine.tally_votes(votes)
        
        assert "approve" in tallied
        assert tallied["approve"] > 0


class TestConflictResolver:
    """Tests for ConflictResolver."""
    
    @pytest.mark.asyncio
    async def test_resolve(self):
        """Test conflict resolution."""
        resolver = ConflictResolver()
        
        case = ConflictCase(session_id="session_1")
        case.add_response("agent_1", {"answer": "A"})
        case.add_response("agent_2", {"answer": "B"})
        
        result = await resolver.resolve(case, ResolutionStrategy.MERGED)
        
        assert result.resolved is True
        assert result.strategy_used == ResolutionStrategy.MERGED


class TestRankingEngine:
    """Tests for RankingEngine."""
    
    @pytest.mark.asyncio
    async def test_rank(self):
        """Test ranking."""
        engine = RankingEngine()
        
        items = [
            {"id": "1", "confidence": 0.9},
            {"id": "2", "confidence": 0.7},
            {"id": "3", "confidence": 0.8},
        ]
        
        result = await engine.rank(items)
        
        assert len(result.ranked_items) == 3
        assert result.ranked_items[0]["score"] >= result.ranked_items[1]["score"]


class TestConsensusBuilder:
    """Tests for ConsensusBuilder."""
    
    @pytest.mark.asyncio
    async def test_build_single_response(self):
        """Test building consensus with single response."""
        builder = ConsensusBuilder()
        
        result = await builder.build("session_1", [{"answer": "A"}], ["agent_1"])
        
        assert result.success is True
        assert result.consensus_level == ConsensusLevel.UNANIMOUS
    
    @pytest.mark.asyncio
    async def test_build_multiple_responses(self):
        """Test building consensus with multiple responses."""
        builder = ConsensusBuilder()
        
        result = await builder.build(
            "session_1",
            [{"answer": "A"}, {"answer": "A"}, {"answer": "A"}],
            ["agent_1", "agent_2", "agent_3"],
        )
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_build_no_responses(self):
        """Test building consensus with no responses."""
        builder = ConsensusBuilder()
        
        result = await builder.build("session_1", [], [])
        
        assert result.success is False


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_consensus_level_values(self):
        """Test ConsensusLevel enum values."""
        assert ConsensusLevel.NONE.value == "none"
        assert ConsensusLevel.UNANIMOUS.value == "unanimous"
    
    def test_vote_option_values(self):
        """Test VoteOption enum values."""
        assert VoteOption.APPROVE.value == "approve"
        assert VoteOption.REJECT.value == "reject"
        assert VoteOption.ABSTAIN.value == "abstain"
    
    def test_conflict_type_values(self):
        """Test ConflictType enum values."""
        assert ConflictType.ANSWER_CONFLICT.value == "answer_conflict"
        assert ConflictType.PRIORITY_CONFLICT.value == "priority_conflict"
    
    def test_resolution_strategy_values(self):
        """Test ResolutionStrategy enum values."""
        assert ResolutionStrategy.MAJORITY.value == "majority"
        assert ResolutionStrategy.WEIGHTED.value == "weighted"
        assert ResolutionStrategy.MERGED.value == "merged"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
