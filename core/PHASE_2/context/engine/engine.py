"""Cognitive Context Engine (CCE) for EREN OS.

Main engine for building context packages.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.PHASE_2.context.engine.builder import ContextBuilder
from core.PHASE_2.context.engine.compressor import ContextCompressor
from core.PHASE_2.context.engine.deduplicator import ContextDeduplicator
from core.PHASE_2.context.engine.merger import ContextMerger
from core.PHASE_2.context.engine.ranking import ContextRanker
from core.PHASE_2.context.engine.types import (
    ContextItem,
    ContextPackage,
    ContextQuery,
    ContextRetrievalResult,
    ContextSource,
)

if TYPE_CHECKING:
    from core.PHASE_2.memory import MemoryCoordinator
    from core.PHASE_2.retrieval import RetrievalEngine


class CognitiveContextEngine:
    """Cognitive Context Engine (CCE).

    Responsible ONLY for building the best possible context for a task.

    Philosophy:
        The CCE NEVER:
        - Generates responses
        - Executes models
        - Builds prompts

        It ONLY:
        - Retrieves information
        - Merges results
        - Removes duplicates
        - Ranks context
        - Limits tokens
        - Compresses context
        - Prioritizes clinical information
        - Generates Context Package
    """

    def __init__(
        self,
        retrieval_engine: RetrievalEngine | None = None,
        memory_coordinator: MemoryCoordinator | None = None,
    ):
        """Initialize CCE.

        Args:
            retrieval_engine: Retrieval engine for knowledge.
            memory_coordinator: Memory coordinator for conversation.
        """
        self._retrieval_engine = retrieval_engine
        self._memory_coordinator = memory_coordinator

        # Components
        self._builder = ContextBuilder()
        self._merger = ContextMerger()
        self._deduplicator = ContextDeduplicator()
        self._compressor = ContextCompressor()
        self._ranker = ContextRanker()

    async def build_context(
        self,
        query: str,
        query_id: str | None = None,
        max_tokens: int = 4000,
        **kwargs,
    ) -> ContextPackage:
        """Build context package.

        This is the main entry point for building context.

        Args:
            query: User query.
            query_id: Optional query ID.
            max_tokens: Maximum tokens for context.
            **kwargs: Additional context query options.

        Returns:
            ContextPackage ready for Prompt Builder.
        """
        query_id = query_id or str(uuid.uuid4())

        # Create context query
        context_query = ContextQuery(
            query_id=query_id,
            query_text=query,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Step 1: Retrieve from all sources
        retrieval_result = await self._retrieve_all(context_query)

        # Step 2: Deduplicate
        unique_items, duplicates = self._deduplicator.deduplicate(
            retrieval_result.items
        )
        retrieval_result.unique_items = len(unique_items)
        retrieval_result.duplicates_removed = duplicates

        # Step 3: Rank
        ranked_items = self._ranker.rank(
            unique_items,
            prioritize_clinical=context_query.prioritize_clinical,
            prioritize_recent=context_query.prioritize_recent,
        )

        # Step 4: Compress to fit budget
        compressed_items = self._compressor.compress(
            ranked_items,
            max_tokens - context_query.reserved_tokens,
        )

        # Step 5: Build package
        package = self._build_package(
            query_id=query_id,
            query=query,
            items=compressed_items,
            max_tokens=max_tokens,
        )

        return package

    async def _retrieve_all(
        self,
        query: ContextQuery,
    ) -> ContextRetrievalResult:
        """Retrieve from all sources."""
        return await self._builder.build_from_query(
            query,
            self._retrieval_engine,
            self._memory_coordinator,
        )

    def _build_package(
        self,
        query_id: str,
        query: str,
        items: list[ContextItem],
        max_tokens: int,
    ) -> ContextPackage:
        """Build context package."""
        # Calculate statistics
        total_items = len(items)
        total_tokens = sum(item.tokens for item in items)

        items_by_source = {}
        avg_relevance = 0.0
        max_relevance = 0.0

        has_clinical = False
        has_conversation = False
        has_knowledge = False

        for item in items:
            source_key = item.source.value
            items_by_source[source_key] = items_by_source.get(source_key, 0) + 1

            avg_relevance += item.relevance_score
            max_relevance = max(max_relevance, item.relevance_score)

            if item.source == ContextSource.CLINICAL:
                has_clinical = True
            elif item.source == ContextSource.CONVERSATION:
                has_conversation = True
            elif item.source == ContextSource.KNOWLEDGE:
                has_knowledge = True

        if total_items > 0:
            avg_relevance /= total_items

        # Build context text
        context_text = self._build_context_text(items)

        return ContextPackage(
            package_id=str(uuid.uuid4()),
            query=query,
            items=items,
            context_text=context_text,
            context_tokens=total_tokens,
            total_items=total_items,
            items_by_source=items_by_source,
            avg_relevance=avg_relevance,
            max_relevance=max_relevance,
            has_clinical_context=has_clinical,
            has_conversation_history=has_conversation,
            has_knowledge_context=has_knowledge,
            available_tokens=max_tokens,
            used_tokens=total_tokens,
            reserved_tokens=500,
        )

    def _build_context_text(self, items: list[ContextItem]) -> str:
        """Build context text from items."""
        if not items:
            return ""

        sections = []

        # Group by source
        by_source: dict[str, list[ContextItem]] = {}
        for item in items:
            source = item.source.value
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(item)

        # Format sections
        for source, source_items in by_source.items():
            section = f"## {source.upper()} CONTEXT\n\n"
            for item in source_items:
                section += f"{item.content}\n\n"

            sections.append(section)

        return "\n".join(sections)


# Global engine instance
_global_engine: CognitiveContextEngine | None = None
_engine_lock = __import__("threading").Lock()


def get_context_engine() -> CognitiveContextEngine:
    """Get the global context engine.

    Returns:
        Global CognitiveContextEngine instance.
    """
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = CognitiveContextEngine()
        return _global_engine


def reset_context_engine() -> None:
    """Reset the global context engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
