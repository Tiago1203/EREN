"""Cognitive RAG Pipeline for EREN OS.

Main RAG pipeline that orchestrates retrieval and generation.
The Pipeline ONLY coordinates - it does NOT know how context is built.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

# Import CCE directly from engine module to avoid circular imports
from core.context.engine.engine import (
    CognitiveContextEngine,
    get_context_engine,
)
from core.context.engine.types import ContextPackage
from core.rag.citation_builder import CitationBuilder
from core.rag.prompt_builder import PromptBuilder
from core.rag.response_builder import ResponseBuilder
from core.rag.types import (
    PipelineStatistics,
    RAGQuery,
    RAGResponse,
    RAGResult,
)

if TYPE_CHECKING:
    from core.memory import MemoryCoordinator
    from core.retrieval import RetrievalEngine


class CognitiveRAGPipeline:
    """Cognitive RAG Pipeline.

    The Pipeline ONLY coordinates. It does NOT know how context is built.

    Responsibilities:
        1. Coordinate with Cognitive Context Engine
        2. Receive Context Package
        3. Build prompt from Context Package
        4. Generate response
        5. Build final response

    Philosophy:
        The Pipeline NEVER knows about:
        - How context is built
        - Which sources are queried
        - How deduplication works
        - How compression works
        - Vector databases
        - Providers

        All context building goes through the Cognitive Context Engine.
    """

    def __init__(
        self,
        context_engine: CognitiveContextEngine | None = None,
        retrieval_engine: RetrievalEngine | None = None,
        memory_coordinator: MemoryCoordinator | None = None,
    ):
        """Initialize RAG pipeline.

        Args:
            context_engine: Cognitive Context Engine for building context.
            retrieval_engine: Optional retrieval engine (passed to CCE).
            memory_coordinator: Optional memory coordinator (passed to CCE).
        """
        # Use provided CCE or get global
        self._context_engine = context_engine or get_context_engine()

        # Components for downstream processing
        self._prompt_builder = PromptBuilder()
        self._response_builder = ResponseBuilder()
        self._citation_builder = CitationBuilder()

        # Statistics
        self._statistics = PipelineStatistics()

    async def query(
        self,
        question: str,
        conversation_id: str = "",
        user_id: str = "",
        session_id: str = "",
        context: dict | None = None,
        **kwargs,
    ) -> RAGResult:
        """Process a RAG query.

        The Pipeline coordinates with CCE for context building.

        Args:
            question: User question.
            conversation_id: Conversation ID.
            user_id: User ID.
            session_id: Session ID.
            context: Additional context.
            **kwargs: Additional query parameters.

        Returns:
            RAG result with response.
        """
        start_time = time.time()

        # Create query
        query = RAGQuery(
            query_id=str(uuid.uuid4()),
            question=question,
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id,
            context=context or {},
            **kwargs,
        )

        try:
            # Step 1: Build context using CCE (Pipeline does NOT know how)
            context_package = await self._context_engine.build_context(
                query=question,
                query_id=query.query_id,
                max_tokens=query.max_tokens,
                include_conversation=bool(conversation_id),
                include_knowledge=True,
                include_clinical=kwargs.get("include_clinical", True),
                include_device=kwargs.get("include_device", True),
                **kwargs,
            )

            # Step 2: Build prompt from Context Package
            # The Pipeline receives ContextPackage and builds prompt
            prompt = self._prompt_builder.build_prompt_from_package(
                query=query,
                package=context_package,
            )

            # Step 3: Generate response (placeholder)
            response = await self._generate_response(
                query,
                prompt,
                context_package,
            )

            total_time = int((time.time() - start_time) * 1000)

            # Update statistics
            self._update_statistics(query, response, total_time)

            return RAGResult(
                query=query,
                response=response,
                success=True,
                total_time_ms=total_time,
            )

        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            return RAGResult(
                query=query,
                response=RAGResponse(
                    query_id=query.query_id,
                    response_id=str(uuid.uuid4()),
                    answer=f"I encountered an error processing your question: {e!s}",
                ),
                success=False,
                error=str(e),
                total_time_ms=total_time,
            )

    async def _generate_response(
        self,
        query: RAGQuery,
        prompt,
        context_package: ContextPackage,
    ) -> RAGResponse:
        """Generate response from LLM.

        This is a placeholder - actual implementation would call LLM provider.
        """
        start_time = time.time()

        # Placeholder response
        answer = self._generate_placeholder_response(query, context_package)

        generation_time = int((time.time() - start_time) * 1000)

        # Build citations from context items
        citations = self._citation_builder.build_citations_from_package(context_package)

        # Build response
        response = self._response_builder.build_response(
            query=query,
            prompt=prompt,
            llm_output=answer,
            citations=citations,
            generation_time_ms=generation_time,
            retrieval_time_ms=0,
        )

        return response

    def _generate_placeholder_response(
        self,
        query: RAGQuery,
        context_package: ContextPackage,
    ) -> str:
        """Generate placeholder response for testing."""
        if not context_package.items:
            return f"Based on your question about '{query.question}', I couldn't find specific information in the knowledge base. Please provide more details or rephrase your question."

        items = context_package.items
        return f"Based on the available information, here's what I found regarding '{query.question}':\n\n" + "\n".join(f'- {item.content[:100]}...' for item in items[:3]) + f"\n\nThis information comes from {len(items)} relevant sources."

    def _update_statistics(
        self,
        query: RAGQuery,
        response: RAGResponse,
        total_time: int,
    ) -> None:
        """Update pipeline statistics."""
        self._statistics.queries_processed += 1

        if response:
            self._statistics.successful_queries += 1
            self._statistics.total_citations += len(response.citations)
        else:
            self._statistics.failed_queries += 1

        # Update strategy counts
        strategy = query.retrieval_strategy.value
        self._statistics.by_retrieval_strategy[strategy] = (
            self._statistics.by_retrieval_strategy.get(strategy, 0) + 1
        )

        # Update format counts
        format_key = query.response_format.value
        self._statistics.by_response_format[format_key] = (
            self._statistics.by_response_format.get(format_key, 0) + 1
        )

    def get_statistics(self) -> PipelineStatistics:
        """Get pipeline statistics."""
        return self._statistics
