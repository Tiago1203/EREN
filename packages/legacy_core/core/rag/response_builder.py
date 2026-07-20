"""RAG Response Builder for EREN OS.

Builds responses from LLM output.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.rag.types import (
    Citation,
    ConfidenceLevel,
    RAGPrompt,
    RAGQuery,
    RAGResponse,
    ResponseFormat,
)

if TYPE_CHECKING:
    pass


class ResponseBuilder:
    """Builds RAG responses.

    Constructs responses from LLM output with citations and metadata.
    """

    def __init__(self):
        """Initialize response builder."""
        pass

    def build_response(
        self,
        query: RAGQuery,
        prompt: RAGPrompt,
        llm_output: str,
        citations: list[Citation] | None = None,
        model_used: str = "",
        provider_used: str = "",
        generation_time_ms: int = 0,
        retrieval_time_ms: int = 0,
    ) -> RAGResponse:
        """Build RAG response.

        Args:
            query: Original query.
            prompt: Built prompt.
            llm_output: LLM output text.
            citations: Extracted citations.
            model_used: Model used for generation.
            provider_used: Provider used.
            generation_time_ms: Generation time.
            retrieval_time_ms: Retrieval time.

        Returns:
            Built response.
        """
        # Format response
        formatted_response = self._format_response(llm_output, query.response_format)

        # Calculate confidence
        confidence_level, confidence_value = self._calculate_confidence(
            llm_output,
            query,
            citations or [],
        )

        # Build sources list
        sources = self._extract_sources(citations or [])

        # Calculate tokens
        prompt_tokens = prompt.total_tokens
        completion_tokens = self._estimate_tokens(llm_output)

        return RAGResponse(
            query_id=query.query_id,
            response_id=str(uuid.uuid4()),
            answer=formatted_response,
            format=query.response_format,
            confidence=confidence_level,
            confidence_score=confidence_value,
            citations=citations or [],
            sources_used=sources,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model_used=model_used,
            provider_used=provider_used,
            retrieval_time_ms=retrieval_time_ms,
            generation_time_ms=generation_time_ms,
            total_time_ms=retrieval_time_ms + generation_time_ms,
        )

    def _format_response(
        self,
        text: str,
        format: ResponseFormat,
    ) -> str:
        """Format response according to format."""
        if format == ResponseFormat.MARKDOWN:
            return self._format_markdown(text)
        elif format == ResponseFormat.JSON:
            return self._format_json(text)
        elif format == ResponseFormat.HTML:
            return self._format_html(text)
        else:
            return text.strip()

    def _format_markdown(self, text: str) -> str:
        """Format as markdown."""
        return text.strip()

    def _format_json(self, text: str) -> str:
        """Format as JSON."""
        import json

        # Try to parse as JSON first
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # Wrap text in JSON structure
            return json.dumps({"answer": text.strip()}, indent=2)

    def _format_html(self, text: str) -> str:
        """Format as HTML."""
        # Simple markdown-like to HTML conversion
        html = text.strip()
        html = html.replace("## ", "<h2>").replace("\n", "</h2>\n", 1) if "## " in html else html
        html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1) if "**" in html else html
        html = html.replace("\n\n", "</p>\n<p>")
        return f"<p>{html}</p>"

    def _calculate_confidence(
        self,
        text: str,
        query: RAGQuery,
        citations: list[Citation],
    ) -> tuple[ConfidenceLevel, float]:
        """Calculate confidence level."""
        # Base confidence on citations
        if not citations:
            return (ConfidenceLevel.UNKNOWN, 0.0)

        # High confidence if multiple high-relevance sources
        avg_relevance = sum(c.relevance_score for c in citations) / len(citations)

        if avg_relevance >= 0.8:
            return (ConfidenceLevel.HIGH, 0.9)
        elif avg_relevance >= 0.6:
            return (ConfidenceLevel.MEDIUM, 0.7)
        elif avg_relevance >= 0.4:
            return (ConfidenceLevel.LOW, 0.5)
        else:
            return (ConfidenceLevel.UNKNOWN, 0.3)

    def _extract_sources(self, citations: list[Citation]) -> list[str]:
        """Extract unique source identifiers."""
        sources = set()

        for citation in citations:
            if citation.source_uri:
                sources.add(citation.source_uri)
            elif citation.title:
                sources.add(citation.title)
            else:
                sources.add(citation.document_id)

        return list(sources)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate completion tokens."""
        return len(text) // 4
