"""Context builder for EREN Semantic Retrieval Engine.

Builds context strings from retrieval results for LLM consumption.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.retrieval.types import (
    RetrievalQuery,
    RetrievalResult,
    RetrievalResponse,
)

if TYPE_CHECKING:
    pass


class ContextBuilder:
    """Builds context from retrieval results.

    Responsibilities:
    - Combine results into context
    - Truncate to token limits
    - Format for LLM consumption
    - Include metadata
    """

    # Average tokens per character (rough estimate for English)
    TOKENS_PER_CHAR = 0.25

    def build(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> str:
        """Build context string.

        Args:
            results: Retrieval results.
            query: Original query.

        Returns:
            Context string.
        """
        if not results:
            return ""

        # Sort results by relevance
        sorted_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)

        # Build context parts
        context_parts = []

        for i, result in enumerate(sorted_results):
            part = self._format_result(result, i + 1, query.include_metadata)
            part_tokens = len(part) * self.TOKENS_PER_CHAR

            # Check if adding this would exceed limit
            current_tokens = sum(len(p) * self.TOKENS_PER_CHAR for p in context_parts)
            if current_tokens + part_tokens > query.max_context_tokens:
                break

            context_parts.append(part)

        # Join with separators
        return "\n\n---\n\n".join(context_parts)

    def _format_result(
        self,
        result: RetrievalResult,
        index: int,
        include_metadata: bool,
    ) -> str:
        """Format a single result.

        Args:
            result: Result to format.
            index: Result index.
            include_metadata: Whether to include metadata.

        Returns:
            Formatted string.
        """
        parts = []

        # Add header
        parts.append(f"[Source {index}: {result.source.value}]")

        # Add content
        parts.append(result.content)

        # Add metadata if requested
        if include_metadata and result.metadata:
            meta_parts = []
            for key, value in result.metadata.items():
                if key not in ["content", "source"]:
                    meta_parts.append(f"{key}: {value}")
            if meta_parts:
                parts.append(f"Metadata: {', '.join(meta_parts)}")

        return "\n".join(parts)


class StructuredContextBuilder(ContextBuilder):
    """Structured context builder.

    Builds context in a more structured format.
    """

    def build(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> str:
        """Build structured context.

        Args:
            results: Retrieval results.
            query: Original query.

        Returns:
            Structured context string.
        """
        if not results:
            return ""

        # Sort results
        sorted_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)

        # Build structured context
        lines = ["# Retrieved Context\n"]

        for i, result in enumerate(sorted_results):
            lines.append(f"## Result {i + 1} (Score: {result.relevance_score:.2f})")
            lines.append(f"**Source:** {result.source.value}")
            lines.append(f"**Content:**\n{result.content}")

            if query.include_metadata and result.metadata:
                lines.append("**Metadata:**")
                for key, value in result.metadata.items():
                    if key not in ["content", "source"]:
                        lines.append(f"- {key}: {value}")

            lines.append("")

        return "\n".join(lines)


class CompactContextBuilder(ContextBuilder):
    """Compact context builder.

    Builds minimal context for token efficiency.
    """

    def build(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> str:
        """Build compact context.

        Args:
            results: Retrieval results.
            query: Original query.

        Returns:
            Compact context string.
        """
        if not results:
            return ""

        # Sort results
        sorted_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)

        # Build compact context
        parts = []

        for result in sorted_results:
            # Estimate tokens
            content_tokens = len(result.content) * self.TOKENS_PER_CHAR
            current_tokens = sum(len(p) * self.TOKENS_PER_CHAR for p in parts)

            if current_tokens + content_tokens > query.max_context_tokens:
                break

            parts.append(result.content)

        return "\n\n".join(parts)


# Factory for creating context builders
class ContextBuilderFactory:
    """Factory for context builders."""

    _builders = {
        "default": ContextBuilder,
        "structured": StructuredContextBuilder,
        "compact": CompactContextBuilder,
    }

    @classmethod
    def create(cls, name: str = "default") -> ContextBuilder:
        """Create a context builder by name.

        Args:
            name: Builder name.

        Returns:
            ContextBuilder instance.
        """
        builder_class = cls._builders.get(name, ContextBuilder)
        return builder_class()

    @classmethod
    def register(cls, name: str, builder_class: type[ContextBuilder]) -> None:
        """Register a new builder.

        Args:
            name: Builder name.
            builder_class: Builder class.
        """
        cls._builders[name] = builder_class

    @classmethod
    def list_builders(cls) -> list[str]:
        """List available builders.

        Returns:
            List of builder names.
        """
        return list(cls._builders.keys())
