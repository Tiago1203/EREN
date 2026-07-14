"""Conversation repository for EREN Conversation Memory Plugin.

SQLite implementation for conversation storage.
Can be replaced with PostgreSQL in production without modifying the Kernel.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Generator

from plugins.conversation.types import (
    ConversationEntry,
    ConversationMetadata,
    ConversationSummary,
    ConversationSearch,
    ConversationMetrics,
    ConversationConfiguration,
    ConversationRole,
    ConversationType,
    ConversationState,
)
from plugins.conversation.exceptions import (
    ConversationNotFoundError,
    EntryNotFoundError,
    ConversationExistsError,
    StorageError,
)

if TYPE_CHECKING:
    pass


class ConversationRepository:
    """Repository for conversation storage.

    SQLite implementation. Replaceable with PostgreSQL, etc.
    """

    def __init__(self, config: ConversationConfiguration):
        """Initialize repository.

        Args:
            config: Configuration.
        """
        self._config = config
        self._lock = threading.RLock()
        # For in-memory database, use a shared connection
        self._in_memory = config.database_path == ":memory:"
        if self._in_memory:
            self._conn = sqlite3.connect(config.database_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        else:
            self._conn = None
        # Always initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT,
                    conversation_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    entries_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    state TEXT NOT NULL,
                    tags TEXT,
                    context_window INTEGER DEFAULT 10
                )
            """)

            # Entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    entry_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    tokens INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)

            # Summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    conversation_id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    key_points TEXT,
                    created_at TEXT NOT NULL,
                    entries_count INTEGER DEFAULT 0,
                    tokens_saved INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)

            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_conversation
                ON entries(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_timestamp
                ON entries(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user
                ON conversations(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection."""
        if self._in_memory and self._conn:
            # For in-memory, use shared connection
            yield self._conn
        else:
            # For file-based, create new connection
            conn = sqlite3.connect(self._config.database_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    # =========================================================================
    # Conversations
    # =========================================================================

    def create_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        """Create a new conversation.

        Args:
            metadata: Conversation metadata.

        Returns:
            Created conversation metadata.

        Raises:
            ConversationExistsError: If conversation already exists.
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO conversations (
                            conversation_id, title, conversation_type,
                            user_id, session_id, created_at, updated_at,
                            last_activity, entries_count, total_tokens,
                            state, tags, context_window
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            metadata.conversation_id,
                            metadata.title,
                            metadata.conversation_type.value,
                            metadata.user_id,
                            metadata.session_id,
                            metadata.created_at.isoformat(),
                            metadata.updated_at.isoformat(),
                            metadata.last_activity.isoformat(),
                            metadata.entries_count,
                            metadata.total_tokens,
                            metadata.state.value,
                            ",".join(metadata.tags),
                            metadata.context_window,
                        ),
                    )
                    conn.commit()
                    return metadata
            except sqlite3.IntegrityError:
                raise ConversationExistsError(metadata.conversation_id)

    def get_conversation(self, conversation_id: str) -> ConversationMetadata:
        """Get conversation metadata.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Conversation metadata.

        Raises:
            ConversationNotFoundError: If not found.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM conversations WHERE conversation_id = ?",
                    (conversation_id,),
                )
                row = cursor.fetchone()

                if not row:
                    raise ConversationNotFoundError(conversation_id)

                return self._row_to_metadata(row)

    def update_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        """Update conversation metadata.

        Args:
            metadata: Updated metadata.

        Returns:
            Updated metadata.
        """
        with self._lock:
            metadata.updated_at = datetime.now(timezone.utc)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE conversations SET
                        title = ?,
                        entries_count = ?,
                        total_tokens = ?,
                        state = ?,
                        tags = ?,
                        context_window = ?,
                        last_activity = ?,
                        updated_at = ?
                    WHERE conversation_id = ?
                    """,
                    (
                        metadata.title,
                        metadata.entries_count,
                        metadata.total_tokens,
                        metadata.state.value,
                        ",".join(metadata.tags),
                        metadata.context_window,
                        metadata.last_activity.isoformat(),
                        metadata.updated_at.isoformat(),
                        metadata.conversation_id,
                    ),
                )
                conn.commit()
                return metadata

    def list_conversations(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        state: ConversationState | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ConversationMetadata]:
        """List conversations.

        Args:
            user_id: Filter by user.
            session_id: Filter by session.
            state: Filter by state.
            limit: Maximum results.
            offset: Result offset.

        Returns:
            List of conversations.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM conversations WHERE 1=1"
                params: list = []

                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                if session_id:
                    query += " AND session_id = ?"
                    params.append(session_id)
                if state:
                    query += " AND state = ?"
                    params.append(state.value)

                query += " ORDER BY last_activity DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_metadata(row) for row in rows]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation and all entries.

        Args:
            conversation_id: Conversation ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM entries WHERE conversation_id = ?",
                    (conversation_id,),
                )
                cursor.execute(
                    "DELETE FROM summaries WHERE conversation_id = ?",
                    (conversation_id,),
                )
                cursor.execute(
                    "DELETE FROM conversations WHERE conversation_id = ?",
                    (conversation_id,),
                )
                conn.commit()
                return True

    # =========================================================================
    # Entries
    # =========================================================================

    def add_entry(self, entry: ConversationEntry) -> ConversationEntry:
        """Add entry to conversation.

        Args:
            entry: Entry to add.

        Returns:
            Added entry.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO entries (
                        entry_id, conversation_id, role, content,
                        timestamp, metadata, tokens
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.entry_id,
                        entry.conversation_id,
                        entry.role.value,
                        entry.content,
                        entry.timestamp.isoformat(),
                        str(entry.metadata),
                        entry.tokens,
                    ),
                )

                # Update conversation metadata
                cursor.execute(
                    """
                    UPDATE conversations SET
                        entries_count = entries_count + 1,
                        total_tokens = total_tokens + ?,
                        last_activity = ?,
                        updated_at = ?
                    WHERE conversation_id = ?
                    """,
                    (
                        entry.tokens,
                        entry.timestamp.isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                        entry.conversation_id,
                    ),
                )
                conn.commit()
                return entry

    def get_entries(
        self,
        conversation_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ConversationEntry]:
        """Get entries for conversation.

        Args:
            conversation_id: Conversation ID.
            limit: Maximum entries.
            offset: Entry offset.

        Returns:
            List of entries.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM entries
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                    """,
                    (conversation_id, limit, offset),
                )
                rows = cursor.fetchall()

                entries = [self._row_to_entry(row) for row in rows]
                entries.reverse()  # Return in chronological order
                return entries

    def get_entry(self, entry_id: str) -> ConversationEntry:
        """Get entry by ID.

        Args:
            entry_id: Entry ID.

        Returns:
            Entry.

        Raises:
            EntryNotFoundError: If not found.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM entries WHERE entry_id = ?",
                    (entry_id,),
                )
                row = cursor.fetchone()

                if not row:
                    raise EntryNotFoundError(entry_id)

                return self._row_to_entry(row)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete entry.

        Args:
            entry_id: Entry ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM entries WHERE entry_id = ?",
                    (entry_id,),
                )
                conn.commit()
                return True

    # =========================================================================
    # Summaries
    # =========================================================================

    def save_summary(self, summary: ConversationSummary) -> ConversationSummary:
        """Save conversation summary.

        Args:
            summary: Summary to save.

        Returns:
            Saved summary.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO summaries (
                        conversation_id, summary, key_points,
                        created_at, entries_count, tokens_saved
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        summary.conversation_id,
                        summary.summary,
                        ",".join(summary.key_points),
                        summary.created_at.isoformat(),
                        summary.entries_count,
                        summary.tokens_saved,
                    ),
                )
                conn.commit()
                return summary

    def get_summary(self, conversation_id: str) -> ConversationSummary | None:
        """Get conversation summary.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Summary or None.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM summaries WHERE conversation_id = ?",
                    (conversation_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return None

                return self._row_to_summary(row)

    # =========================================================================
    # Search
    # =========================================================================

    def search(self, search: ConversationSearch) -> list[ConversationEntry]:
        """Search entries.

        Args:
            search: Search parameters.

        Returns:
            Matching entries.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM entries WHERE 1=1"
                params: list = []

                if search.query:
                    query += " AND content LIKE ?"
                    params.append(f"%{search.query}%")

                if search.user_id:
                    query += " AND conversation_id IN (SELECT conversation_id FROM conversations WHERE user_id = ?)"
                    params.append(search.user_id)

                if search.session_id:
                    query += " AND conversation_id IN (SELECT conversation_id FROM conversations WHERE session_id = ?)"
                    params.append(search.session_id)

                if search.date_from:
                    query += " AND timestamp >= ?"
                    params.append(search.date_from.isoformat())

                if search.date_to:
                    query += " AND timestamp <= ?"
                    params.append(search.date_to.isoformat())

                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([search.limit, search.offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_entry(row) for row in rows]

    # =========================================================================
    # Metrics
    # =========================================================================

    def get_metrics(self) -> ConversationMetrics:
        """Get metrics.

        Returns:
            Metrics.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM entries")
                total_entries = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM summaries")
                total_summaries = cursor.fetchone()[0]

                cursor.execute("SELECT SUM(total_tokens) FROM conversations")
                total_tokens = cursor.fetchone()[0] or 0

                avg_entries = total_conversations > 0 and total_entries / total_conversations or 0
                avg_tokens = total_entries > 0 and total_tokens / total_entries or 0

                return ConversationMetrics(
                    total_conversations=total_conversations,
                    total_entries=total_entries,
                    total_summaries=total_summaries,
                    total_tokens=total_tokens,
                    average_entries_per_conversation=avg_entries,
                    average_tokens_per_entry=avg_tokens,
                )

    # =========================================================================
    # Helpers
    # =========================================================================

    def _row_to_metadata(self, row: sqlite3.Row) -> ConversationMetadata:
        """Convert row to metadata."""
        return ConversationMetadata(
            conversation_id=row["conversation_id"],
            title=row["title"] or "",
            conversation_type=ConversationType(row["conversation_type"]),
            user_id=row["user_id"] or "",
            session_id=row["session_id"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_activity=datetime.fromisoformat(row["last_activity"]),
            entries_count=row["entries_count"],
            total_tokens=row["total_tokens"],
            state=ConversationState(row["state"]),
            tags=row["tags"].split(",") if row["tags"] else [],
            context_window=row["context_window"],
        )

    def _row_to_entry(self, row: sqlite3.Row) -> ConversationEntry:
        """Convert row to entry."""
        metadata = {}
        if row["metadata"]:
            try:
                metadata = eval(row["metadata"])  # Safe in this context
            except Exception:
                pass

        return ConversationEntry(
            entry_id=row["entry_id"],
            conversation_id=row["conversation_id"],
            role=ConversationRole(row["role"]),
            content=row["content"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            metadata=metadata,
            tokens=row["tokens"],
        )

    def _row_to_summary(self, row: sqlite3.Row) -> ConversationSummary:
        """Convert row to summary."""
        return ConversationSummary(
            conversation_id=row["conversation_id"],
            summary=row["summary"],
            key_points=row["key_points"].split(",") if row["key_points"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            entries_count=row["entries_count"],
            tokens_saved=row["tokens_saved"],
        )
