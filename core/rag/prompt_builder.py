"""RAG Prompt Builder for EREN OS.

Builds prompts for LLM from context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.rag.types import (
    RAGQuery,
    RAGContext,
    RAGPrompt,
)

if TYPE_CHECKING:
    pass


class PromptBuilder:
    """Builds prompts for RAG queries.

    Constructs system and user prompts with context.
    """

    def __init__(self):
        """Initialize prompt builder."""
        self._default_system_prompt = self._get_default_system_prompt()

    def build_prompt(
        self,
        query: RAGQuery,
        context: RAGContext,
    ) -> RAGPrompt:
        """Build RAG prompt.

        Args:
            query: RAG query.
            context: Built context.

        Returns:
            Built prompt.
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(query, context)

        # Build user prompt
        user_prompt = self._build_user_prompt(query, context)

        # Calculate tokens
        system_tokens = self._estimate_tokens(system_prompt)
        user_tokens = self._estimate_tokens(user_prompt)
        context_tokens = context.context_tokens
        total_tokens = system_tokens + user_tokens + context_tokens

        return RAGPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context.context_text,
            system_tokens=system_tokens,
            user_tokens=user_tokens,
            context_tokens=context_tokens,
            total_tokens=total_tokens,
            max_tokens=query.max_tokens,
        )

    def _build_system_prompt(
        self,
        query: RAGQuery,
        context: RAGContext,
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

        return prompt

    def _build_user_prompt(
        self,
        query: RAGQuery,
        context: RAGContext,
    ) -> str:
        """Build user prompt."""
        parts = []

        # Add context
        if context.context_text:
            parts.append(f"## Context\n\n{context.context_text}\n")

        # Add conversation history
        if context.conversation_history:
            history_text = self._format_history(context.conversation_history)
            if history_text:
                parts.append(f"## Conversation\n\n{history_text}\n")

        # Add question
        parts.append(f"## Question\n\n{query.question}\n")

        # Add instruction
        parts.append("## Answer\n\n")

        return "".join(parts)

    def _format_history(self, history: list[dict]) -> str:
        """Format conversation history."""
        if not history:
            return ""

        lines = []
        for entry in history[-5:]:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            if content:
                lines.append(f"{role.upper()}: {content}")

        return "\n".join(lines)

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
