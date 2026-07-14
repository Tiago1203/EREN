"""RAG Prompt Builder for EREN OS.

Builds prompts for LLM from Context Package.
The Prompt Builder ONLY receives ContextPackage and builds the prompt.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Import CCE types directly from engine types module
from core.context.engine.types import ContextPackage
from core.rag.types import (
    RAGPrompt,
    RAGQuery,
)

if TYPE_CHECKING:
    pass


class PromptBuilder:
    """Builds prompts for RAG queries.

    The Prompt Builder ONLY receives ContextPackage and builds the prompt.
    It does NOT know how context is built.
    """

    def __init__(self):
        """Initialize prompt builder."""
        self._default_system_prompt = self._get_default_system_prompt()

    def build_prompt_from_package(
        self,
        query: RAGQuery,
        package: ContextPackage,
    ) -> RAGPrompt:
        """Build RAG prompt from Context Package.

        This is the main entry point.
        The Prompt Builder receives ContextPackage only.

        Args:
            query: RAG query.
            package: Context Package from CCE.

        Returns:
            Built prompt.
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(query, package)

        # Build user prompt
        user_prompt = self._build_user_prompt(query, package)

        # Calculate tokens
        system_tokens = self._estimate_tokens(system_prompt)
        user_tokens = self._estimate_tokens(user_prompt)
        context_tokens = package.context_tokens
        total_tokens = system_tokens + user_tokens + context_tokens

        return RAGPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=package.context_text,
            system_tokens=system_tokens,
            user_tokens=user_tokens,
            context_tokens=context_tokens,
            total_tokens=total_tokens,
            max_tokens=query.max_tokens,
        )

    def _build_system_prompt(
        self,
        query: RAGQuery,
        package: ContextPackage,
    ) -> str:
        """Build system prompt."""
        prompt = self._default_system_prompt

        # Add response format instructions
        if query.response_format.value == "markdown":
            prompt += "\n\nUse Markdown formatting for your response."
        elif query.response_format.value == "json":
            prompt += "\n\nRespond in valid JSON format."

        # Add citation instructions
        if query.include_citations:
            prompt += "\n\nAlways cite your sources using the provided context."

        # Add context quality info
        if package.has_clinical_context:
            prompt += "\n\n[Clinical context available]"

        return prompt

    def _build_user_prompt(
        self,
        query: RAGQuery,
        package: ContextPackage,
    ) -> str:
        """Build user prompt."""
        parts = []

        # Add context
        if package.context_text:
            parts.append(f"## Context\n\n{package.context_text}\n")

        # Add question
        parts.append(f"## Question\n\n{query.question}\n")

        # Add instruction
        parts.append("## Answer\n\n")

        return "".join(parts)

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt."""
        return """You are EREN, a medical AI assistant. Your role is to provide accurate, helpful information based on the provided context.

Guidelines:
1. Answer questions using ONLY the context provided
2. If the context doesn't contain enough information, say so
3. Never make up information not in the context
4. Be clear about limitations and uncertainties
5. Prioritize accuracy over completeness
6. Use appropriate medical terminology when available
7. Include relevant caveats and disclaimers when needed

Your responses should be:
- Accurate and evidence-based
- Clear and understandable
- Appropriately qualified
- Structured and well-organized"""

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count.

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        # Rough approximation: ~4 chars per token
        return len(text) // 4
