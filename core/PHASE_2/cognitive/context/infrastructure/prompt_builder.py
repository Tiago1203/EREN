"""Prompt Builder - constructs prompts for LLM."""
from dataclasses import dataclass
from typing import Any

from core.PHASE_2.cognitive.context.domain import Context
from core.PHASE_2.cognitive.reasoning.domain.entities import ReasoningMode


@dataclass
class PromptConfig:
    """Configuration for prompt building."""
    include_reasoning_steps: bool = True
    include_citations: bool = True
    max_context_length: int = 8000
    include_confidence_warning: bool = True


class PromptBuilder:
    """
    Builds optimized prompts for LLM.
    
    Constructs system prompts, user prompts, and reasoning prompts
    based on context and configuration.
    """
    
    # System prompt template
    SYSTEM_PROMPT_TEMPLATE = """You are EREN, an AI assistant specialized in biomedical engineering and hospital management.

Your role is to assist biomedical engineers and hospital staff with:
- Troubleshooting medical device issues
- Managing incidents and work orders
- Answering questions about medical equipment
- Providing recommendations based on best practices
- Explaining technical concepts in accessible language

## Guidelines:
1. Always prioritize patient safety
2. Be precise and cite your sources when available
3. If you're uncertain, say so and recommend professional consultation
4. Follow HIPAA guidelines - never discuss specific patients
5. Suggest actions only when you're confident in the recommendation
6. Explain your reasoning when it might help the user

## Safety Rules:
- Never provide medical diagnoses
- Never recommend bypassing safety features
- Always suggest consulting specialists for complex medical issues
- Flag critical safety concerns prominently
"""
    
    # Few-shot examples
    FEW_SHOT_EXAMPLES = """
## Examples:

Example 1:
User: "The infusion pump in room 302 is showing error E45"
Thought: The user is reporting a specific device error. I should look up this error code and provide troubleshooting steps.
Response: "Error E45 on the [Infusion Pump Model] typically indicates an occlusion in the infusion line. Here are the troubleshooting steps:
1. Check the tubing for kinks or blockages
2. Verify the cassette is properly seated
3. Check for air bubbles in the line
4. If the error persists, the occlusion sensor may need calibration.

Source: Medical Equipment Service Manual - Chapter 4, Section 4.2"

Example 2:
User: "What should I do about a faulty defibrillator?"
Thought: This is a critical safety issue. I should provide clear safety guidance and recommend immediate action.
Response: "⚠️ CRITICAL SAFETY ISSUE

For a faulty defibrillator, follow this protocol immediately:

1. TAKE OUT OF SERVICE - Tag the device as do not use
2. Notify biomedical engineering supervisor
3. Document the fault with serial number and model
4. Contact manufacturer support
5. Ensure backup defibrillator is available

Defibrillators are Class III critical devices. Never attempt repairs without proper certification.

Do you need help with any specific fault symptoms?"
"""
    
    def __init__(self, config: PromptConfig | None = None):
        self.config = config or PromptConfig()
    
    def build_system_prompt(
        self,
        domain: str = "biomedical",
        user_expertise: str = "intermediate",
    ) -> str:
        """
        Build system prompt based on domain and user expertise.
        
        Args:
            domain: Primary domain (biomedical, clinical, hospital)
            user_expertise: User expertise level (beginner, intermediate, expert)
        
        Returns:
            System prompt string
        """
        prompt = self.SYSTEM_PROMPT_TEMPLATE
        
        # Add domain-specific instructions
        if domain == "clinical":
            prompt += "\n\n## Clinical Domain Focus:\n"
            prompt += "- Assist with clinical decision support\n"
            prompt += "- Provide evidence-based recommendations\n"
            prompt += "- Focus on patient outcomes\n"
        
        elif domain == "hospital":
            prompt += "\n\n## Hospital Management Focus:\n"
            prompt += "- Assist with capacity planning\n"
            prompt += "- Help with staff scheduling questions\n"
            prompt += "- Support department organization queries\n"
        
        # Add expertise-specific instructions
        if user_expertise == "beginner":
            prompt += "\n\n## Communication Style:\n"
            prompt += "- Use simple language, avoid jargon\n"
            prompt += "- Explain technical terms\n"
            prompt += "- Provide step-by-step guidance\n"
        
        elif user_expertise == "expert":
            prompt += "\n\n## Communication Style:\n"
            prompt += "- Use technical terminology freely\n"
            prompt += "- Provide concise, detailed responses\n"
            prompt += "- Assume knowledge of standard procedures\n"
        
        prompt += self.FEW_SHOT_EXAMPLES
        
        return prompt
    
    def build_user_prompt(
        self,
        query: str,
        context: Context,
        reasoning_mode: ReasoningMode = ReasoningMode.DIRECT,
    ) -> str:
        """
        Build user prompt with context.
        
        Args:
            query: User's question or request
            context: Context from ContextBuilder
            reasoning_mode: Reasoning mode to use
        
        Returns:
            User prompt string
        """
        prompt_parts = []
        
        # Add context if available
        if context.items:
            prompt_parts.append("## Context Information")
            prompt_parts.append(context.to_prompt_context())
            prompt_parts.append("")
        
        # Add reasoning mode instructions
        if reasoning_mode == ReasoningMode.CHAIN_OF_THOUGHT:
            prompt_parts.append("## Reasoning Instructions")
            prompt_parts.append("Think step by step before answering. Show your reasoning process.")
            prompt_parts.append("")
        
        elif reasoning_mode == ReasoningMode.REACT:
            prompt_parts.append("## Reasoning Instructions")
            prompt_parts.append("Think (Reason) about what action to take, then Act to retrieve information if needed.")
            prompt_parts.append("")
        
        elif reasoning_mode == ReasoningMode.PLAN:
            prompt_parts.append("## Reasoning Instructions")
            prompt_parts.append("First make a plan, then execute the plan step by step.")
            prompt_parts.append("")
        
        # Add the user's query
        prompt_parts.append("## User Question")
        prompt_parts.append(query)
        
        # Truncate if too long
        full_prompt = "\n".join(prompt_parts)
        if len(full_prompt) > self.config.max_context_length:
            # Simple truncation
            full_prompt = full_prompt[:self.config.max_context_length] + "\n\n[Context truncated due to length]"
        
        return full_prompt
    
    def build_direct_prompt(self, query: str, context: Context) -> str:
        """Build a direct (non-reasoning) prompt."""
        return self.build_user_prompt(query, context, ReasoningMode.DIRECT)
    
    def build_cot_prompt(self, query: str, context: Context) -> str:
        """Build a chain-of-thought prompt."""
        prompt = self.build_user_prompt(query, context, ReasoningMode.CHAIN_OF_THOUGHT)
        prompt += "\n\nLet's think step by step:"
        return prompt
    
    def build_react_prompt(self, query: str, context: Context) -> str:
        """Build a ReAct (Reason + Act) prompt."""
        prompt = self.build_user_prompt(query, context, ReasoningMode.REACT)
        prompt += "\n\nFormat your response as:\nThought: [what you're thinking]\nAction: [action to take, if needed]\nObservation: [result of action]\nAnswer: [final answer]"
        return prompt
    
    def build_plan_prompt(self, query: str, context: Context) -> str:
        """Build a plan-based prompt."""
        prompt = self.build_user_prompt(query, context, ReasoningMode.PLAN)
        prompt += "\n\nFirst, create a plan to answer this question:"
        return prompt


def create_prompt_builder(config: PromptConfig | None = None) -> PromptBuilder:
    """Create a prompt builder."""
    return PromptBuilder(config=config)
