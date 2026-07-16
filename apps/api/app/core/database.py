"""Database access: SQLAlchemy 2 async engine, session factory and FastAPI dependency.

The engine is created lazily so importing this module never opens a connection.
Swap ``database_url`` (see ``app.config.settings``) to point at Postgres in
production (e.g. ``postgresql+asyncpg://...``).
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, creating it on first use."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            future=True,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session and closes it afterwards."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create database schemas for all bounded contexts (development only)."""
    engine = get_engine()
    async with engine.begin() as conn:
        # Create schemas
        for schema in ["incident", "device", "recommendation", "knowledge"]:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

        # Create all tables — models must be imported to register with Base.metadata
        from app.infrastructure.models import (  # noqa: F401
            ActionModel,
            ConversationMessageModel,
            DeviceModel,
            DomainEventModel,
            EvidenceModel,
            IncidentModel,
            InvestigationModel,
            KnowledgeArticleModel,
            RecommendationModel,
        )
        from app.models.base import Base

        Base.metadata.create_all(conn)


async def close_db() -> None:
    """Close database connections gracefully."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
