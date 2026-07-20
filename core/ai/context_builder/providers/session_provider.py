"""
Session Context Provider.

Provides session context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.ai.sessions import SessionManager


class SessionContextProvider(BaseContextProvider):
    """
    Provides session context for the AI.
    
    Retrieves session state, user preferences, and token budget.
    """
    
    def __init__(
        self,
        session_manager: SessionManager | None = None,
    ):
        self._session = session_manager
    
    @property
    def name(self) -> str:
        return "session"
    
    @property
    def priority(self) -> int:
        return 10  # Critical priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get session context."""
        items = []
        
        # Get session info
        session_info = await self._get_session_safe(query.user_id, query.tenant_id)
        if session_info:
            items.append(self._session_to_context(session_info))
        
        return items
    
    async def _get_session_safe(self, user_id: str, tenant_id: str) -> dict | None:
        """Safely get session info."""
        if self._session is None:
            return self._mock_get_session()
        try:
            # This would get the current session
            return {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "session_active": True,
            }
        except Exception:
            return None
    
    def _session_to_context(self, session: dict) -> ContextItem:
        """Create session context."""
        return self._create_item(
            content=f"Session: User {session.get('user_id')} in tenant {session.get('tenant_id')}",
            relevance_score=0.95,
            metadata={"type": "session"},
        )
    
    def _mock_get_session(self) -> dict:
        """Mock session for testing."""
        return {
            "user_id": "user-001",
            "tenant_id": "tenant-001",
            "session_active": True,
        }
