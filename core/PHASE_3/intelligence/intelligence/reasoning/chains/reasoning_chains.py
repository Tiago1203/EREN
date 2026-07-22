"""
Reasoning Chains Module

Complete implementation for building, validating, and exporting
reasoning chains in clinical decision support.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class ChainType(Enum):
    """Types of reasoning chains."""
    DEDUCTIVE = "deductive"           # General to specific
    INDUCTIVE = "inductive"         # Specific to general
    ABDUCTIVE = "abductive"         # Best explanation
    CAUSAL = "causal"               # Cause-effect


class StepType(Enum):
    """Types of steps in reasoning chain."""
    PREMISE = "premise"           # Initial fact
    EVIDENCE = "evidence"         # Supporting evidence
    INFERENCE = "inference"       # Logical inference
    CONCLUSION = "conclusion"     # Final conclusion


@dataclass(frozen=True)
class ReasoningStep:
    """A step in a reasoning chain."""
    step_id: str
    step_type: StepType
    content: str
    confidence: float = 1.0
    supporting_premises: list[str] = field(default_factory=list)
    inference_rule: Optional[str] = None
    evidence_ids: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ReasoningChain:
    """A complete reasoning chain."""
    chain_id: str
    chain_type: ChainType
    steps: list[ReasoningStep]
    premises: list[str] = field(default_factory=list)
    conclusions: list[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.chain_type, str):
            object.__setattr__(self, 'chain_type', ChainType(self.chain_type))


class ChainBuilder:
    """Builds reasoning chains from premises and evidence."""
    
    async def build_from_premises(
        self,
        premises: list[str],
        chain_type: ChainType = ChainType.DEDUCTIVE,
    ) -> ReasoningChain:
        """Build chain from premises."""
        steps = []
        
        for i, premise in enumerate(premises):
            steps.append(ReasoningStep(
                step_id=f"step_{i}",
                step_type=StepType.PREMISE,
                content=premise,
                confidence=1.0,
            ))
        
        return ReasoningChain(
            chain_id=f"chain_{datetime.now().timestamp()}",
            chain_type=chain_type,
            steps=steps,
            premises=list(premises),
            overall_confidence=1.0,
        )
    
    async def add_inference_step(
        self,
        chain: ReasoningChain,
        inference: str,
        rule: str,
        supporting_steps: list[int],
    ) -> ReasoningChain:
        """Add an inference step to chain."""
        supporting_ids = [chain.steps[i].step_id for i in supporting_steps]
        
        step = ReasoningStep(
            step_id=f"step_{len(chain.steps)}",
            step_type=StepType.INFERENCE,
            content=inference,
            supporting_premises=supporting_ids,
            inference_rule=rule,
            confidence=0.8,
        )
        
        return ReasoningChain(
            chain_id=chain.chain_id,
            chain_type=chain.chain_type,
            steps=chain.steps + [step],
            premises=chain.premises,
            conclusions=chain.conclusions,
            overall_confidence=chain.overall_confidence * step.confidence,
            is_valid=chain.is_valid,
            validation_errors=chain.validation_errors,
            created_at=chain.created_at,
            metadata=chain.metadata,
        )
    
    async def add_conclusion(
        self,
        chain: ReasoningChain,
        conclusion: str,
        supporting_steps: list[int],
    ) -> ReasoningChain:
        """Add conclusion step to chain."""
        supporting_ids = [chain.steps[i].step_id for i in supporting_steps]
        
        # Calculate confidence based on supporting steps
        supporting_confidence = 1.0
        for i in supporting_steps:
            supporting_confidence *= chain.steps[i].confidence
        
        step = ReasoningStep(
            step_id=f"step_{len(chain.steps)}",
            step_type=StepType.CONCLUSION,
            content=conclusion,
            supporting_premises=supporting_ids,
            confidence=supporting_confidence,
        )
        
        return ReasoningChain(
            chain_id=chain.chain_id,
            chain_type=chain.chain_type,
            steps=chain.steps + [step],
            premises=chain.premises,
            conclusions=chain.conclusions + [conclusion],
            overall_confidence=supporting_confidence,
            is_valid=chain.is_valid,
            validation_errors=chain.validation_errors,
            created_at=chain.created_at,
            metadata=chain.metadata,
        )


class ChainValidator:
    """Validates reasoning chains for logical consistency."""
    
    async def validate(self, chain: ReasoningChain) -> tuple[bool, list[str]]:
        """Validate chain for logical consistency."""
        errors = []
        
        # Check for circular reasoning
        if await self._has_circular_reasoning(chain):
            errors.append("Chain contains circular reasoning")
        
        # Check for unsupported conclusions
        unsupported = await self._find_unsupported_conclusions(chain)
        if unsupported:
            errors.append(f"Conclusions without support: {unsupported}")
        
        # Check confidence threshold
        if chain.overall_confidence < 0.5:
            errors.append(f"Overall confidence too low: {chain.overall_confidence}")
        
        # Check premise coverage
        missing_premises = await self._find_missing_premises(chain)
        if missing_premises:
            errors.append(f"Missing premises referenced: {missing_premises}")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    async def _has_circular_reasoning(self, chain: ReasoningChain) -> bool:
        """Check for circular reasoning."""
        # Simple check: conclusion references itself
        for step in chain.steps:
            if step.step_type == StepType.CONCLUSION:
                for premise in chain.premises:
                    if step.content.lower() in premise.lower():
                        return True
        return False
    
    async def _find_unsupported_conclusions(
        self,
        chain: ReasoningChain,
    ) -> list[str]:
        """Find conclusions without supporting steps."""
        unsupported = []
        
        for step in chain.steps:
            if step.step_type == StepType.CONCLUSION:
                if not step.supporting_premises:
                    unsupported.append(step.content)
        
        return unsupported
    
    async def _find_missing_premises(
        self,
        chain: ReasoningChain,
    ) -> list[str]:
        """Find premises referenced but not defined."""
        defined_premises = set(chain.premises)
        referenced_premises = set()
        
        for step in chain.steps:
            referenced_premises.update(step.supporting_premises)
        
        # Check if referenced premises exist in chain
        step_ids = {s.step_id for s in chain.steps}
        missing = referenced_premises - step_ids
        
        return list(missing)


class ChainExporter:
    """Exports reasoning chains in various formats."""
    
    async def to_natural_language(self, chain: ReasoningChain) -> str:
        """Export chain as natural language."""
        lines = []
        lines.append(f"## Reasoning Chain ({chain.chain_type.value})")
        lines.append("")
        
        for step in chain.steps:
            if step.step_type == StepType.PREMISE:
                lines.append(f"**Premise:** {step.content}")
            elif step.step_type == StepType.INFERENCE:
                rule = step.inference_rule or "inference"
                lines.append(f"**Inference ({rule}):** {step.content}")
            elif step.step_type == StepType.CONCLUSION:
                lines.append(f"**Conclusion:** {step.content}")
            lines.append("")
        
        lines.append(f"*Confidence: {chain.overall_confidence:.2%}*")
        return "\n".join(lines)
    
    async def to_json(self, chain: ReasoningChain) -> dict:
        """Export chain as JSON."""
        return {
            "chain_id": chain.chain_id,
            "chain_type": chain.chain_type.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_type": s.step_type.value,
                    "content": s.content,
                    "confidence": s.confidence,
                    "supporting_premises": s.supporting_premises,
                    "inference_rule": s.inference_rule,
                }
                for s in chain.steps
            ],
            "premises": chain.premises,
            "conclusions": chain.conclusions,
            "overall_confidence": chain.overall_confidence,
            "is_valid": chain.is_valid,
            "validation_errors": chain.validation_errors,
            "created_at": chain.created_at.isoformat(),
        }


__all__ = [
    "ChainType",
    "StepType",
    "ReasoningStep",
    "ReasoningChain",
    "ChainBuilder",
    "ChainValidator",
    "ChainExporter",
]
