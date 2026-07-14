"""Consensus manager for EREN Multi-Agent Collaboration Engine.

Handles consensus building between agents.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.collaboration.types import (
    ConsensusState,
    Proposal,
    VoteValue,
)

if TYPE_CHECKING:
    pass


class ConsensusManager:
    """Manages consensus building.

    The Consensus Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Creates proposals
    - Collects votes
    - Determines consensus
    """

    def __init__(self):
        """Initialize consensus manager."""
        self._proposals: dict[str, Proposal] = {}

    def create_proposal(
        self,
        session_id: str,
        proposer_id: str,
        title: str,
        description: str,
        content: Any,
        required_votes: int = 0,
        deadline_seconds: float = 60.0,
    ) -> Proposal:
        """Create a new proposal.

        Args:
            session_id: Session ID.
            proposer_id: Proposer agent ID.
            title: Proposal title.
            description: Proposal description.
            content: Proposal content.
            required_votes: Required votes for consensus.
            deadline_seconds: Deadline in seconds.

        Returns:
            Created proposal.
        """
        proposal = Proposal.create(
            session_id=session_id,
            proposer_id=proposer_id,
            title=title,
            description=description,
            content=content,
            required_votes=required_votes,
            deadline_seconds=deadline_seconds,
        )

        self._proposals[proposal.proposal_id] = proposal
        return proposal

    def get_proposal(
        self,
        proposal_id: str,
    ) -> Proposal | None:
        """Get a proposal by ID.

        Args:
            proposal_id: Proposal ID.

        Returns:
            Proposal or None.
        """
        return self._proposals.get(proposal_id)

    def get_session_proposals(
        self,
        session_id: str,
    ) -> list[Proposal]:
        """Get all proposals for a session.

        Args:
            session_id: Session ID.

        Returns:
            List of proposals.
        """
        return [
            p for p in self._proposals.values()
            if p.session_id == session_id
        ]

    def vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: VoteValue,
    ) -> bool:
        """Vote on a proposal.

        Args:
            proposal_id: Proposal ID.
            agent_id: Voting agent ID.
            vote: Vote value.

        Returns:
            True if vote recorded.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        if proposal.state not in [ConsensusState.PENDING, ConsensusState.VOTING]:
            return False

        proposal.vote(agent_id, vote)
        return True

    def is_consensus_reached(
        self,
        proposal_id: str,
    ) -> bool:
        """Check if consensus is reached.

        Args:
            proposal_id: Proposal ID.

        Returns:
            True if consensus reached.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        return proposal.state == ConsensusState.AGREED

    def is_consensus_rejected(
        self,
        proposal_id: str,
    ) -> bool:
        """Check if consensus is rejected.

        Args:
            proposal_id: Proposal ID.

        Returns:
            True if consensus rejected.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        return proposal.state == ConsensusState.DISAGREED

    def check_deadline(
        self,
        proposal_id: str,
    ) -> bool:
        """Check if proposal deadline passed.

        Args:
            proposal_id: Proposal ID.

        Returns:
            True if deadline passed.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        if proposal.deadline:
            return datetime.now(UTC).timestamp() > proposal.deadline.timestamp()

        return False

    def timeout_proposal(
        self,
        proposal_id: str,
    ) -> bool:
        """Mark proposal as timed out.

        Args:
            proposal_id: Proposal ID.

        Returns:
            True if timed out.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        proposal.state = ConsensusState.TIMEOUT
        return True

    def get_vote_counts(
        self,
        proposal_id: str,
    ) -> dict[str, int]:
        """Get vote counts.

        Args:
            proposal_id: Proposal ID.

        Returns:
            Dictionary of vote counts.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return {"accept": 0, "reject": 0, "abstain": 0}

        counts = {
            "accept": 0,
            "reject": 0,
            "abstain": 0,
        }

        for vote in proposal.votes.values():
            if vote == VoteValue.ACCEPT:
                counts["accept"] += 1
            elif vote == VoteValue.REJECT:
                counts["reject"] += 1
            else:
                counts["abstain"] += 1

        return counts

    def get_active_proposals(
        self,
        session_id: str,
    ) -> list[Proposal]:
        """Get active proposals for a session.

        Args:
            session_id: Session ID.

        Returns:
            List of active proposals.
        """
        return [
            p for p in self._proposals.values()
            if p.session_id == session_id
            and p.state in [ConsensusState.PENDING, ConsensusState.VOTING]
        ]

    def close_proposal(
        self,
        proposal_id: str,
    ) -> bool:
        """Close a proposal.

        Args:
            proposal_id: Proposal ID.

        Returns:
            True if closed.
        """
        if proposal_id in self._proposals:
            del self._proposals[proposal_id]
            return True
        return False

    def clear_session(
        self,
        session_id: str,
    ) -> int:
        """Clear all proposals for a session.

        Args:
            session_id: Session ID.

        Returns:
            Number of proposals cleared.
        """
        to_remove = [
            p_id for p_id, p in self._proposals.items()
            if p.session_id == session_id
        ]

        for p_id in to_remove:
            del self._proposals[p_id]

        return len(to_remove)


# Global consensus manager
_global_consensus_manager: ConsensusManager | None = None
_consensus_lock = __import__("threading").Lock()


def get_consensus_manager() -> ConsensusManager:
    """Get the global consensus manager.

    Returns:
        Global ConsensusManager instance.
    """
    global _global_consensus_manager
    with _consensus_lock:
        if _global_consensus_manager is None:
            _global_consensus_manager = ConsensusManager()
        return _global_consensus_manager


def reset_consensus_manager() -> None:
    """Reset the global consensus manager."""
    global _global_consensus_manager
    with _consensus_lock:
        _global_consensus_manager = None
