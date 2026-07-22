"""Reasoning domain services."""
from typing import Optional
from dataclasses import dataclass

from core.PHASE_2.cognitive.reasoning.domain.entities import (
    ReasoningEngine,
    ReasoningMode,
    ReasoningResult,
    ReasoningTrace,
    ReasoningStep,
)
from core.PHASE_2.cognitive.reasoning.domain.contracts import LLMContract


@dataclass
class ReasoningContext:
    """Context for reasoning."""
    query: str
    evidence: list[str]
    conversation_history: list[dict]
    user_id: str
    domain: str


class ReasoningService:
    """Service for orchestrating reasoning."""
    
    def __init__(
        self,
        llm: LLMContract,
        prompt_builder,  # PromptBuilder
    ):
        self.llm = llm
        self.prompt_builder = prompt_builder
    
    async def reason(
        self,
        context: ReasoningContext,
        mode: ReasoningMode = ReasoningMode.CHAIN_OF_THOUGHT,
    ) -> ReasoningResult:
        """Execute reasoning based on mode."""
        
        if mode == ReasoningMode.DIRECT:
            return await self._reason_direct(context)
        elif mode == ReasoningMode.CHAIN_OF_THOUGHT:
            return await self._reason_cot(context)
        elif mode == ReasoningMode.REACT:
            return await self._reason_react(context)
        else:
            return await self._reason_direct(context)
    
    async def _reason_direct(self, context: ReasoningContext) -> ReasoningResult:
        """Direct reasoning - single response."""
        prompt = self.prompt_builder.build_direct_prompt(context)
        
        response = await self.llm.complete(
            prompt=prompt,
            temperature=0.7,
        )
        
        trace = ReasoningTrace(mode=ReasoningMode.DIRECT)
        trace.complete()
        
        return ReasoningResult(
            trace=trace,
            final_answer=response.content,
            confidence=0.8,
        )
    
    async def _reason_cot(self, context: ReasoningContext) -> ReasoningResult:
        """Chain-of-Thought reasoning."""
        prompt = self.prompt_builder.build_cot_prompt(context)
        
        response = await self.llm.complete(
            prompt=prompt,
            temperature=0.5,
            stop_sequences=["Final Answer:"],
        )
        
        trace = ReasoningTrace(mode=ReasoningMode.CHAIN_OF_THOUGHT)
        # Parse steps from response
        steps = self._parse_reasoning_steps(response.content)
        for step in steps:
            trace.add_step(step)
        trace.complete()
        
        return ReasoningResult(
            trace=trace,
            final_answer=steps[-1].description if steps else response.content,
            confidence=0.85,
        )
    
    async def _reason_react(self, context: ReasoningContext) -> ReasoningResult:
        """ReAct reasoning - Reason + Act."""
        trace = ReasoningTrace(mode=ReasoningMode.REACT)
        
        # Simplified ReAct - in production would iterate with tools
        prompt = self.prompt_builder.build_react_prompt(context)
        
        response = await self.llm.complete(
            prompt=prompt,
            temperature=0.3,
        )
        
        trace.add_step(ReasoningStep(
            step_number=1,
            description=response.content[:200],
            operation="reasoned",
        ))
        trace.complete()
        
        return ReasoningResult(
            trace=trace,
            final_answer=response.content,
            confidence=0.9,
        )
    
    def _parse_reasoning_steps(self, content: str) -> list[ReasoningStep]:
        """Parse reasoning steps from LLM output."""
        steps = []
        lines = content.split("\n")
        step_num = 1
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith("Final"):
                steps.append(ReasoningStep(
                    step_number=step_num,
                    description=line,
                    operation="reasoned",
                ))
                step_num += 1
        
        return steps
