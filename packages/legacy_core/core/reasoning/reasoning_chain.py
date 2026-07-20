"""Reasoning chain management.

Builds and manages chains of reasoning steps.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from .reasoning_types import (
    ConfidenceLevel,
    ConfidenceScore,
    InferenceType,
    ReasoningChain,
    ReasoningStep,
)

if TYPE_CHECKING:
    pass


class ReasoningChainBuilder:
    """Builds reasoning chains from evidence and hypotheses."""

    def build(
        self,
        hypothesis_id: str,
        evidence_ids: list[str],
        inference_type: InferenceType = InferenceType.ABDUCTIVE,
    ) -> ReasoningChain:
        """Build a reasoning chain.

        Args:
            hypothesis_id: The hypothesis being evaluated.
            evidence_ids: Evidence IDs to chain.
            inference_type: Type of inference.

        Returns:
            A reasoning chain.
        """
        steps = []
        chain_id = f"chain_{uuid.uuid4().hex[:16]}"

        # Create initial step from evidence
        if evidence_ids:
            evidence_step = ReasoningStep(
                step_id=f"{chain_id}_evidence",
                inference_type=inference_type,
                description=f"Evidence collected: {', '.join(evidence_ids[:3])}...",
                conclusions=(f"{chain_id}_analysis",),
                evidence_id=evidence_ids[0] if evidence_ids else "",
            )
            steps.append(evidence_step)

        # Create analysis step
        analysis_step = ReasoningStep(
            step_id=f"{chain_id}_analysis",
            inference_type=inference_type,
            description=f"Analysis using {inference_type.value} inference",
            premises=(f"{chain_id}_evidence",) if evidence_ids else (),
            conclusions=(f"{chain_id}_conclusion",),
            hypothesis_id=hypothesis_id,
            confidence=ConfidenceScore(
                value=0.7,
                level=ConfidenceLevel.MODERATE,
                reasons=(f"Based on {len(evidence_ids)} evidence items",),
            ),
        )
        steps.append(analysis_step)

        # Create conclusion step
        conclusion_step = ReasoningStep(
            step_id=f"{chain_id}_conclusion",
            inference_type=inference_type,
            description=f"Conclusion for hypothesis {hypothesis_id}",
            premises=(f"{chain_id}_analysis",),
            hypothesis_id=hypothesis_id,
            confidence=ConfidenceScore(
                value=0.75,
                level=ConfidenceLevel.HIGH,
                reasons=("Inference completed",),
            ),
        )
        steps.append(conclusion_step)

        return ReasoningChain(
            chain_id=chain_id,
            hypothesis_id=hypothesis_id,
            steps=tuple(steps),
            start_evidence=tuple(evidence_ids),
            final_conclusion=f"{chain_id}_conclusion",
            overall_confidence=ConfidenceScore(
                value=0.72,
                level=ConfidenceLevel.HIGH,
                reasons=("Chain built successfully",),
            ),
        )


class ReasoningChainManager:
    """Manages multiple reasoning chains."""

    def __init__(self) -> None:
        """Initialize the chain manager."""
        self._chains: dict[str, ReasoningChain] = {}
        self._step_count = 0

    def build_chain(
        self,
        hypothesis_id: str,
        evidence_ids: list[str],
        inference_type: InferenceType = InferenceType.ABDUCTIVE,
    ) -> ReasoningChain:
        """Build and store a reasoning chain.

        Args:
            hypothesis_id: The hypothesis ID.
            evidence_ids: Evidence IDs.
            inference_type: Inference type.

        Returns:
            The built chain.
        """
        builder = ReasoningChainBuilder()
        chain = builder.build(hypothesis_id, evidence_ids, inference_type)

        self._chains[chain.chain_id] = chain
        self._step_count += len(chain.steps)

        return chain

    def get_chain(self, chain_id: str) -> ReasoningChain | None:
        """Get a chain by ID."""
        return self._chains.get(chain_id)

    def get_chains_for_hypothesis(self, hypothesis_id: str) -> list[ReasoningChain]:
        """Get all chains for a hypothesis."""
        return [
            c for c in self._chains.values()
            if c.hypothesis_id == hypothesis_id
        ]

    def get_step_count(self) -> int:
        """Get total number of steps across all chains."""
        return self._step_count

    def get_all_chains(self) -> list[ReasoningChain]:
        """Get all chains."""
        return list(self._chains.values())

    def validate_chain(self, chain_id: str) -> tuple[bool, list[str]]:
        """Validate a reasoning chain.

        Args:
            chain_id: The chain ID.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        chain = self._chains.get(chain_id)
        if not chain:
            return False, ["Chain not found"]

        errors = []

        # Check step references
        all_premises = set()
        all_conclusions = set()

        for step in chain.steps:
            all_premises.update(step.premises)
            all_conclusions.add(step.step_id)

        # Check all premises have conclusions
        for premise in all_premises:
            if premise not in all_conclusions:
                errors.append(f"Orphan premise: {premise}")

        # Check final conclusion exists
        if chain.final_conclusion not in all_conclusions:
            errors.append("Final conclusion not found in steps")

        return len(errors) == 0, errors
