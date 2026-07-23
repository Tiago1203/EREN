"""
PHASE 4 - EPIC 10: Knowledge Synchronization Engine

Motor de sincronización:
- Actualizaciones periódicas
- Monitoreo de fuentes
- Sincronización con fuentes externas
- Detección de publicaciones nuevas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol, Callable
import asyncio


class SyncSource(str, Enum):
    """Fuentes de sincronización."""
    PUBMED = "pubmed"
    FDA = "fda"
    EMA = "ema"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    DEVICE_MANUFACTURERS = "device_manufacturers"
    STANDARDS_BODIES = "standards_bodies"


class SyncStatus(str, Enum):
    """Estado de sincronización."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncEvent(str, Enum):
    """Eventos de sincronización."""
    NEW_PUBLICATION = "sync.new_publication"
    UPDATED_RECORD = "sync.updated_record"
    REMOVED_RECORD = "sync.removed_record"
    SOURCE_UNAVAILABLE = "sync.source_unavailable"


@dataclass
class SyncConfig:
    """Configuración de sincronización."""
    source: SyncSource
    enabled: bool = True
    interval_seconds: int = 3600  # 1 hour
    batch_size: int = 100
    priority: int = 1  # 1 = high, 2 = medium, 3 = low


@dataclass
class SyncJob:
    """Job de sincronización."""
    job_id: str
    source: SyncSource
    status: SyncStatus
    started_at: datetime
    completed_at: datetime | None = None
    
    # Metrics
    records_processed: int = 0
    records_added: int = 0
    records_updated: int = 0
    records_failed: int = 0
    
    errors: list[str] = field(default_factory=list)


@dataclass
class SyncEvent:
    """Evento de sincronización."""
    event_id: str
    source: SyncSource
    event_type: SyncEvent
    record_id: str
    timestamp: datetime
    metadata: dict = field(default_factory=dict)


class ISyncSource(Protocol):
    """Protocolo para fuente de sincronización."""
    
    async def fetch_updates(self, since: datetime) -> list[dict]:
        """Obtiene actualizaciones desde última sincronización."""
        ...
    
    async def get_record(self, record_id: str) -> dict | None:
        """Obtiene registro específico."""
        ...


class PubMedSyncSource:
    """Fuente de sincronización PubMed."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
    
    async def fetch_updates(self, since: datetime) -> list[dict]:
        """Obtiene artículos PubMed actualizados."""
        # Placeholder - would call PubMed E-utilities
        return []
    
    async def get_record(self, pmid: str) -> dict | None:
        """Obtiene artículo por PMID."""
        return None


class FDASyncSource:
    """Fuente de sincronización FDA."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
    
    async def fetch_updates(self, since: datetime) -> list[dict]:
        """Obtiene actualizaciones de FDA."""
        # Placeholder - would call FDA API
        return []
    
    async def get_record(self, recall_id: str) -> dict | None:
        """Obtiene recall por ID."""
        return None


class SyncScheduler:
    """Programador de sincronizaciones."""
    
    def __init__(self):
        self._configs: dict[SyncSource, SyncConfig] = {}
        self._scheduled_tasks: dict[SyncSource, asyncio.Task] = {}
        self._running = False
        self._last_sync: dict[SyncSource, datetime] = {}
    
    def configure(self, config: SyncConfig) -> None:
        """Configura sincronización para fuente."""
        self._configs[config.source] = config
    
    def configure_all(
        self,
        sources: list[SyncSource],
        interval_seconds: int = 3600,
    ) -> None:
        """Configura todas las fuentes."""
        for source in sources:
            self.configure(SyncConfig(
                source=source,
                interval_seconds=interval_seconds,
            ))
    
    async def start(self, sync_callback: Callable) -> None:
        """Inicia programador."""
        self._running = True
        
        for source, config in self._configs.items():
            if config.enabled:
                task = asyncio.create_task(
                    self._run_sync_loop(source, config, sync_callback)
                )
                self._scheduled_tasks[source] = task
    
    async def stop(self) -> None:
        """Detiene programador."""
        self._running = False
        
        for task in self._scheduled_tasks.values():
            task.cancel()
        
        self._scheduled_tasks.clear()
    
    async def _run_sync_loop(
        self,
        source: SyncSource,
        config: SyncConfig,
        callback: Callable,
    ) -> None:
        """Ejecuta loop de sincronización."""
        while self._running:
            try:
                await asyncio.sleep(config.interval_seconds)
                
                last = self._last_sync.get(source, datetime.min)
                events = await self._sync_source(source, last)
                
                for event in events:
                    await callback(event)
                
                self._last_sync[source] = datetime.now(UTC)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue
                pass
    
    async def _sync_source(
        self,
        source: SyncSource,
        since: datetime,
    ) -> list[SyncEvent]:
        """Sincroniza fuente específica."""
        events = []
        
        # Placeholder - would fetch and process updates
        # For each update, create SyncEvent
        
        return events
    
    async def trigger_sync(self, source: SyncSource) -> SyncJob:
        """Dispara sincronización manual."""
        job = SyncJob(
            job_id="manual",
            source=source,
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.now(UTC),
        )
        
        try:
            await self._sync_source(source, datetime.min)
            job.status = SyncStatus.COMPLETED
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.errors.append(str(e))
        
        job.completed_at = datetime.now(UTC)
        return job


class SyncMonitor:
    """Monitor de sincronizaciones."""
    
    def __init__(self):
        self._jobs: list[SyncJob] = []
        self._events: list[SyncEvent] = []
        self._listeners: list[Callable] = []
    
    def record_job(self, job: SyncJob) -> None:
        """Registra job completado."""
        self._jobs.append(job)
    
    def record_event(self, event: SyncEvent) -> None:
        """Registra evento."""
        self._events.append(event)
        
        # Notify listeners
        for listener in self._listeners:
            try:
                asyncio.create_task(listener(event))
            except Exception:
                pass
    
    def add_listener(self, listener: Callable) -> None:
        """Agrega listener para eventos."""
        self._listeners.append(listener)
    
    def get_recent_jobs(self, limit: int = 10) -> list[SyncJob]:
        """Obtiene jobs recientes."""
        return sorted(
            self._jobs,
            key=lambda j: j.started_at,
            reverse=True,
        )[:limit]
    
    def get_events_for_source(
        self,
        source: SyncSource,
        limit: int = 100,
    ) -> list[SyncEvent]:
        """Obtiene eventos para fuente."""
        return [
            e for e in self._events
            if e.source == source
        ][:limit]
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas."""
        total_jobs = len(self._jobs)
        total_events = len(self._events)
        
        by_source = {}
        for job in self._jobs:
            source_key = job.source.value
            if source_key not in by_source:
                by_source[source_key] = {"jobs": 0, "records": 0}
            by_source[source_key]["jobs"] += 1
            by_source[source_key]["records"] += job.records_processed
        
        return {
            "total_jobs": total_jobs,
            "total_events": total_events,
            "by_source": by_source,
        }


__all__ = [
    "SyncSource",
    "SyncStatus",
    "SyncEvent",
    "SyncConfig",
    "SyncJob",
    "SyncEvent",
    "ISyncSource",
    "PubMedSyncSource",
    "FDASyncSource",
    "SyncScheduler",
    "SyncMonitor",
]
