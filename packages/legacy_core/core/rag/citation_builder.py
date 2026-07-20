"""RAG Citation Builder for EREN OS.

Builds citations from Context Package.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

# Import CCE types directly from engine types module
from core.context.engine.types import ContextItem, ContextPackage
from core.rag.types import (
    Citation,
    RAGResponse,
)

if TYPE_CHECKING:
    pass


class CitationBuilder:
    """Builds citations from Context Package.

    Links response content to source items.
    """

    def __init__(self):
        """Initialize citation builder."""
        pass

    def build_citations_from_package(
        self,
        package: ContextPackage,
    ) -> list[Citation]:
        """Build citations from Context Package.

        Args:
            package: Context Package from CCE.

        Returns:
            Built citations.
        """
        citations = []

        for item in package.items:
            citation = self._build_citation_from_item(item)
            citations.append(citation)

        return citations

    def _build_citation_from_item(self, item: ContextItem) -> Citation:
        """Build single citation from context item."""
        return Citation(
            citation_id=str(uuid.uuid4()),
            text=self._extract_relevant_text(item.content),
            chunk_id=item.chunk_id,
            document_id=item.document_id,
            title=item.title,
            start_char=0,
            end_char=len(item.content),
            source_type=item.source.value,
            source_uri="",
            author=item.author,
            institution="",
            published_date="",
            relevance_score=item.relevance_score,
            page_number="",
            url="",
        )

    def _extract_relevant_text(self, content: str) -> str:
        """Extract relevant text for citation."""
        if len(content) <= 200:
            return content
        return content[:200] + "..."

    def attach_citations_to_response(
        self,
        response: RAGResponse,
        citations: list[Citation],
    ) -> RAGResponse:
        """Attach citations to existing response.

        Args:
            response: Response to annotate.
            citations: Source citations.

        Returns:
            Annotated response.
        """
        response.citations = citations
        response.sources_used = self._extract_sources(citations)
        return response

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
