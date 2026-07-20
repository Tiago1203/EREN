"""
UnitOfWork Factory para AI Core.

Provee acceso al UnitOfWork de la API desde el AI Core
sin coupling directo.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AIUnitOfWork:
    """
    Wrapper alrededor de UnitOfWork que expone solo
    lo que el AI Core necesita.
    
    Provee acceso tipado a los repositorios.
    """
    
    def __init__(self, session: "AsyncSession"):
        self._session = session
        self._committed = False
        
        # Lazy loading de repositorios
        self._devices: "DeviceRepositoryImpl | None" = None
        self._incidents: "IncidentRepositoryImpl | None" = None
        self._knowledge: "KnowledgeRepositoryImpl | None" = None
        self._recommendations: "RecommendationRepositoryImpl | None" = None
        self._capacity: "CapacityRepositoryImpl | None" = None
        self._work_orders: "WorkOrderRepositoryImpl | None" = None
    
    @property
    def devices(self) -> "DeviceRepositoryImpl":
        """Acceso al repositorio de dispositivos."""
        if self._devices is None:
            from apps.api.app.domain.device.repository import DeviceRepositoryImpl
            self._devices = DeviceRepositoryImpl(self._session)
        return self._devices
    
    @property
    def incidents(self) -> "IncidentRepositoryImpl":
        """Acceso al repositorio de incidentes."""
        if self._incidents is None:
            from apps.api.app.domain.incident.repository import IncidentRepositoryImpl
            self._incidents = IncidentRepositoryImpl(self._session)
        return self._incidents
    
    @property
    def knowledge(self) -> "KnowledgeRepositoryImpl":
        """Acceso al repositorio de conocimiento."""
        if self._knowledge is None:
            from apps.api.app.domain.knowledge.repository import KnowledgeRepositoryImpl
            self._knowledge = KnowledgeRepositoryImpl(self._session)
        return self._knowledge
    
    @property
    def recommendations(self) -> "RecommendationRepositoryImpl":
        """Acceso al repositorio de recomendaciones."""
        if self._recommendations is None:
            from apps.api.app.domain.recommendation.repository import RecommendationRepositoryImpl
            self._recommendations = RecommendationRepositoryImpl(self._session)
        return self._recommendations
    
    @property
    def capacity(self) -> "CapacityRepositoryImpl":
        """Acceso al repositorio de capacidad."""
        if self._capacity is None:
            from apps.api.app.domain.capacity.repository import CapacityRepositoryImpl
            self._capacity = CapacityRepositoryImpl(self._session)
        return self._capacity
    
    @property
    def work_orders(self) -> "WorkOrderRepositoryImpl":
        """Acceso al repositorio de órdenes de trabajo."""
        if self._work_orders is None:
            from apps.api.app.domain.work_order.repository import WorkOrderRepositoryImpl
            self._work_orders = WorkOrderRepositoryImpl(self._session)
        return self._work_orders
    
    async def commit(self) -> None:
        """Confirma los cambios."""
        await self._session.commit()
        self._committed = True
    
    async def rollback(self) -> None:
        """Revierte los cambios."""
        await self._session.rollback()
        self._committed = False
    
    async def flush(self) -> None:
        """Flush cambios sin commit."""
        await self._session.flush()


class AIUnitOfWorkFactory:
    """
    Factory para crear UnitOfWork desde el AI Core.
    
    Este factory expone el UnitOfWork de la API de forma
    que el AI Core pueda usar sin coupling directo.
    
    Usage:
        # En DI setup
        factory = AIUnitOfWorkFactory()
        
        # En gateway
        async with factory() as uow:
            devices = await uow.devices.list_by_tenant(...)
    """
    
    def __init__(self, session_factory=None):
        """
        Args:
            session_factory: Función que crea AsyncSession.
                             Si es None, usa la default de la app.
        """
        self._session_factory = session_factory
    
    @asynccontextmanager
    async def __call__(
        self,
    ) -> AsyncGenerator[AIUnitOfWork, None]:
        """
        Crea un UnitOfWork para usar en contexto async.
        
        Usage:
            async with factory() as uow:
                devices = await uow.devices.list_by_tenant(...)
        """
        from sqlalchemy.ext.asyncio import AsyncSession
        
        if self._session_factory:
            session = self._session_factory()
        else:
            try:
                from apps.api.app.core.database import get_session_factory
                factory = get_session_factory()
                session = factory()
            except ImportError:
                # En testing o cuando la API no está disponible
                raise RuntimeError(
                    "AIUnitOfWorkFactory requires session_factory or API to be available"
                )
        
        try:
            uow = AIUnitOfWork(session)
            yield uow
            await uow.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Instancia global para la aplicación
_global_factory: AIUnitOfWorkFactory | None = None


def get_uow_factory() -> AIUnitOfWorkFactory:
    """Obtiene la instancia global del factory."""
    global _global_factory
    if _global_factory is None:
        _global_factory = AIUnitOfWorkFactory()
    return _global_factory


def set_uow_factory(factory: AIUnitOfWorkFactory) -> None:
    """Establece la instancia global del factory."""
    global _global_factory
    _global_factory = factory
