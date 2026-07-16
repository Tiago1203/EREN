"""Unit of Work pattern for transactional consistency across bounded contexts.

Usage::

    async with UnitOfWork() as uow:
        incident = await uow.incidents.save(incident)
        recommendation = await uow.recommendations.save(recommendation)
        # Domain events are registered via outbox.append(...)
        await uow.commit()          # persists data + outbox in same TX
        return incident

    # Background OutboxWorker publishes events to RabbitMQ after commit.

On exit (success): commit + flush outbox
On exit (exception): rollback + discard outbox
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory

if TYPE_CHECKING:
    from app.infrastructure.messaging.outbox import TransactionalOutbox
    from app.infrastructure.repositories.device import DeviceRepositoryImpl
    from app.infrastructure.repositories.incident import IncidentRepositoryImpl
    from app.infrastructure.repositories.knowledge import KnowledgeRepositoryImpl
    from app.infrastructure.repositories.recommendation import RecommendationRepositoryImpl

logger = logging.getLogger(__name__)


class UnitOfWork:
    """Unit of Work — coordinates repositories + outbox within a single transaction."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session
        self._owned_session = False
        self._committed = False

        # Repository placeholders
        self.incidents: IncidentRepositoryImpl | None = None
        self.devices: DeviceRepositoryImpl | None = None
        self.recommendations: RecommendationRepositoryImpl | None = None
        self.knowledge: KnowledgeRepositoryImpl | None = None

    async def __aenter__(self) -> UnitOfWork:
        if self._session is None:
            factory = get_session_factory()
            self._session = factory()
            self._owned_session = True

        # Import here to avoid circular deps
        from app.infrastructure.messaging.outbox import TransactionalOutbox
        from app.infrastructure.repositories.device import DeviceRepositoryImpl
        from app.infrastructure.repositories.incident import IncidentRepositoryImpl
        from app.infrastructure.repositories.knowledge import KnowledgeRepositoryImpl
        from app.infrastructure.repositories.recommendation import RecommendationRepositoryImpl

        self.incidents = IncidentRepositoryImpl(self._session)
        self.devices = DeviceRepositoryImpl(self._session)
        self.recommendations = RecommendationRepositoryImpl(self._session)
        self.knowledge = KnowledgeRepositoryImpl(self._session)

        # Outbox is scoped to this transaction
        self._outbox = TransactionalOutbox(self._session)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool | None:
        if exc_type is not None:
            if self._session is not None:
                await self._session.rollback()
            logger.debug("UnitOfWork rolled back due to %s", exc_type.__name__)
            return None  # Don't suppress exceptions

        if not self._committed:
            await self.commit()

        if self._session is not None and self._owned_session:
            await self._session.close()

        return None

    def outbox(self) -> TransactionalOutbox:
        """Access the transactional outbox for registering domain events."""
        if self._outbox is None:
            raise RuntimeError("UnitOfWork not initialized")
        return self._outbox

    async def commit(self) -> None:
        """Commit the transaction.

        The outbox is flushed inside the transaction before commit.
        The actual RabbitMQ publish happens asynchronously via OutboxWorker.
        """
        if self._session is None:
            raise RuntimeError("No session available")

        # Flush pending domain events to outbox table (same transaction)
        if self._outbox is not None:
            await self._outbox.flush()

        await self._session.commit()
        self._committed = True
        logger.debug("UnitOfWork committed with outbox events")

    async def rollback(self) -> None:
        """Rollback the transaction and discard all pending events."""
        if self._session is not None:
            await self._session.rollback()
        logger.debug("UnitOfWork rolled back (outbox discarded)")


@asynccontextmanager
async def unit_of_work() -> AsyncGenerator[UnitOfWork, None]:
    """Convenience async context manager for Unit of Work."""
    async with UnitOfWork() as uow:
        yield uow
