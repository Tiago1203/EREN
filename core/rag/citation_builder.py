"""RAG Citation Builder for EREN OS.

Builds citations from retrieved chunks.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.rag.types import (
    Citation,
    RetrievedChunk,
    RAGResponse,
)

if TYPE_CHECKING:
    pass


class CitationBuilder:
    """Builds citations for RAG responses.

    Links response content to source chunks.
    """

    def __init__(self):
        """Initialize citation builder."""
        pass

    def build_citations(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        """Build citations from chunks.

        Args:
            chunks: Retrieved chunks.

        Returns:
            Built citations.
        """
        citations = []

        for chunk in chunks:
            citation = self._build_citation(chunk)
            citations.append(citation)

        return citations

    def _build_citation(self, chunk: RetrievedChunk) -> Citation:
        """Build single citation from chunk."""
        return Citation(
            citation_id=str(uuid.uuid4()),
            text=self._extract_relevant_text(chunk),
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            title=chunk.title,
            start_char=0,
            end_char=len(chunk.content),
            source_type=chunk.source_type,
            source_uri=chunk.source_uri,
            author=chunk.author,
            institution=chunk.institution,
            published_date="",
            relevance_score=chunk.relevance_score,
            page_number="",
            url=chunk.source_uri,
        )

    def _extract_relevant_text(self, chunk: RetrievedChunk) -> str:
        """Extract relevant text from chunk."""
        # Return first 200 chars as citation text
        if len(chunk.content) <= 200:
            return chunk.content
        return chunk.content[:200] + "..."

    def attach_citations_to_response(
        self,
        response: RAGResponse,
        chunks: list[RetrievedChunk],
    ) -> RAGResponse:
        """Attach citations to existing response.

        Args:
            response: Response to annotate.
            chunks: Source chunks.

        Returns:
            Annotated response.
        """
        citations = self.build_citations(chunks)
        response.citations = citations
        response.sources_used = self._extract_sources(citations)
        return response
