"""Conversation search service for EREN Conversation Memory Plugin.

Handles all search logic including text, date, session, and user searches.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from plugins.conversation.types import (
    ConversationEntry,
    ConversationSearch,
    ConversationSearchResult,
)

if TYPE_CHECKING:
    from plugins.conversation.contracts import ConversationRepositoryContract


class ConversationSearchService:
    """Service for conversation search operations.

    Responsibilities:
    - Text search
    - Date range search
    - Session search
    - User search
    - Future: hybrid search (text + semantic)
    """

    def __init__(self, repository: "ConversationRepositoryContract"):
        """Initialize search service.

        Args:
            repository: Conversation repository contract.
        """
        self._repository = repository

    def search(
        self,
        query: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        conversation_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ConversationSearchResult:
        """Search conversations.

        Args:
            query: Text query.
            user_id: Filter by user.
            session_id: Filter by session.
            conversation_id: Filter by conversation.
            date_from: Start date.
            date_to: End date.
            limit: Maximum results.
            offset: Result offset.

        Returns:
            Search result with matches.
        """
        # Build search parameters
        search = ConversationSearch(
            query=query or "",
            user_id=user_id,
            session_id=session_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )

        # Execute search
        entries = self._repository.search(search)

        # Filter by conversation if specified
        if conversation_id:
            entries = [
                e for e in entries
                if e.conversation_id == conversation_id
            ]

        return ConversationSearchResult(
            entries=entries,
            total=len(entries),
            query=query or "",
            filters_applied={
                "user_id": user_id,
                "session_id": session_id,
                "conversation_id": conversation_id,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
            },
        )

    def search_by_text(self, query: str, limit: int = 10) -> ConversationSearchResult:
        """Search by text.

        Args:
            query: Text query.
            limit: Maximum results.

        Returns:
            Search result.
        """
        return self.search(query=query, limit=limit)

    def search_by_date(
        self,
        date_from: datetime,
        date_to: datetime | None = None,
        limit: int = 10,
    ) -> ConversationSearchResult:
        """Search by date range.

        Args:
            date_from: Start date.
            date_to: End date (defaults to now).
            limit: Maximum results.

        Returns:
            Search result.
        """
        if date_to is None:
            date_to = datetime.now(timezone.utc)
        return self.search(date_from=date_from, date_to=date_to, limit=limit)

    def search_by_session(
        self,
        session_id: str,
        limit: int = 10,
    ) -> ConversationSearchResult:
        """Search by session.

        Args:
            session_id: Session ID.
            limit: Maximum results.

        Returns:
            Search result.
        """
        return self.search(session_id=session_id, limit=limit)

    def search_by_user(
        self,
        user_id: str,
        limit: int = 10,
    ) -> ConversationSearchResult:
        """Search by user.

        Args:
            user_id: User ID.
            limit: Maximum results.

        Returns:
            Search result.
        """
        return self.search(user_id=user_id, limit=limit)

    def get_recent_conversations(
        self,
        user_id: str | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Get recent conversation IDs.

        Args:
            user_id: Optional user filter.
            limit: Maximum results.

        Returns:
            List of conversation IDs.
        """
        conversations = self._repository.list_conversations(
            user_id=user_id,
            limit=limit,
        )
        return [c.conversation_id for c in conversations]
