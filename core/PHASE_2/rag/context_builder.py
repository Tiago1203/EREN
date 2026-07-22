"""RAG Context Builder for EREN OS.

Builds context from retrieved chunks and conversation history.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.rag.types import (
    RAGContext,
    RAGQuery,
    RetrievalResult,
    RetrievedChunk,
)

if TYPE_CHECKING:
    pass


class ContextBuilder:
    """Builds context for RAG from retrieved content.

    Combines retrieved chunks with conversation history.
    """

    def __init__(self):
        """Initialize context builder."""
        pass

    async def build_context(
        self,
        query: RAGQuery,
        retrieval_result: RetrievalResult | None = None,
        conversation_history: list[dict] | None = None,
    ) -> RAGContext:
        """Build RAG context.

        Args:
            query: RAG query.
            retrieval_result: Retrieved chunks.
            conversation_history: Conversation history.

        Returns:
            Built context.
        """
        context = RAGContext(
            query=query,
            retrieved_chunks=[],
            conversation_history=conversation_history or [],
        )

        # Add retrieved chunks
        if retrieval_result:
            context.retrieved_chunks = retrieval_result.chunks

        # Calculate available tokens
        context.available_tokens = query.max_tokens

        # Build context text
        context.context_text = self._build_context_text(context)

        # Calculate tokens
        context.context_tokens = self._estimate_tokens(context.context_text)

        return context

    def _build_context_text(self, context: RAGContext) -> str:
        """Build context text from chunks."""
        parts = []

        # Add conversation history if present
        if context.conversation_history:
            history_text = self._format_conversation(context.conversation_history)
            if history_text:
                parts.append(f"## Conversation History\n\n{history_text}")

        # Add retrieved content
        if context.retrieved_chunks:
            chunks_text = self._format_chunks(context.retrieved_chunks)
            parts.append(f"## Relevant Knowledge\n\n{chunks_text}")

        return "\n\n".join(parts)

    def _format_conversation(self, history: list[dict]) -> str:
        """Format conversation history."""
        if not history:
            return ""

        lines = []
        for entry in history[-5:]:  # Last 5 entries
            role = entry.get("role", "user")
            content = entry.get("content", "")
            if content:
                lines.append(f"**{role.capitalize()}**: {content}")

        return "\n".join(lines)

    def _format_chunks(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks."""
        if not chunks:
            return "No relevant knowledge found."

        sections = []
        for i, chunk in enumerate(chunks[:10], 1):  # Top 10
            section = f"### Source {i}: {chunk.title or 'Unknown'}\n\n"
            section += f"{chunk.content}\n\n"

            # Add metadata if present
            meta_parts = []
            if chunk.author:
                meta_parts.append(f"Author: {chunk.author}")
            if chunk.institution:
                meta_parts.append(f"Institution: {chunk.institution}")
            if chunk.hospital:
                meta_parts.append(f"Hospital: {chunk.hospital}")

            if meta_parts:
                section += f"_{'; '.join(meta_parts)}_\n\n"

            sections.append(section)

        return "\n".join(sections)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation).

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        # Rough approximation: ~4 chars per token for English
        return len(text) // 4


class Deduplicator:
    """Deduplicates retrieved chunks."""

    def __init__(self, similarity_threshold: float = 0.9):
        """Initialize deduplicator.

        Args:
            similarity_threshold: Threshold for considering duplicates.
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Remove duplicate chunks.

        Args:
            chunks: List of chunks to deduplicate.

        Returns:
            Deduplicated chunks.
        """
        if not chunks:
            return []

        unique_chunks = []
        seen_content = set()

        for chunk in chunks:
            # Normalize content for comparison
            normalized = self._normalize(chunk.content)

            if normalized not in seen_content:
                seen_content.add(normalized)
                unique_chunks.append(chunk)

        return unique_chunks

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        # Simple normalization: lowercase, remove extra spaces
        return " ".join(text.lower().split())
