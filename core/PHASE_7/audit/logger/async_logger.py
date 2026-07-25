"""
PHASE 7 - EPIC 1: Async Audit Logger

Logger asíncrono no bloqueante para auditoría:
- Cola de eventos asíncronos
- Flush periódico
- Fallback a logging síncrono
- Backpressure handling
"""

from __future__ import annotations

import asyncio
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Callable, Any
import time
import uuid


class FlushStrategy(str, Enum):
    """Estrategia de flush."""
    IMMEDIATE = "immediate"          # Flush después de cada evento
    BATCH = "batch"                  # Flush cada N eventos
    TIMED = "timed"                   # Flush cada N segundos
    ADAPTIVE = "adaptive"            # Basado en volumen


@dataclass
class AsyncAuditConfig:
    """Configuración del logger asíncrono."""
    batch_size: int = 100              # Flush cada 100 eventos
    flush_interval_seconds: float = 5.0  # O cada 5 segundos
    max_queue_size: int = 10000       # Máximo eventos en cola
    flush_strategy: FlushStrategy = FlushStrategy.ADAPTIVE
    on_flush_error: Optional[Callable] = None  # Callback en error
    enable_backpressure: bool = True   # Bloquear si cola llena


class AsyncAuditLogger:
    """Logger de auditoría asíncrono y no bloqueante."""

    def __init__(
        self,
        sync_logger: Any,            # AuditLogger instance
        config: Optional[AsyncAuditConfig] = None,
    ):
        from core.PHASE_7.audit.logger.audit_logger import AuditLogger
        self._sync_logger: AuditLogger = sync_logger
        self._config = config or AsyncAuditConfig()

        self._queue: asyncio.Queue = asyncio.Queue(
            maxsize=self._config.max_queue_size if self._config.enable_backpressure else 0
        )
        self._buffer: list = []
        self._buffer_size: int = 0
        self._last_flush: float = time.time()
        self._running: bool = False
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()

        # Statistics
        self._events_logged: int = 0
        self._events_flushed: int = 0
        self._flush_count: int = 0
        self._errors: int = 0

    async def start(self) -> None:
        """Inicia el worker de flush."""
        if self._running:
            return
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())

    async def stop(self) -> None:
        """Detiene el logger y hace flush final."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        # Final flush
        await self._flush()

    async def log_async(self, event_data: dict) -> str:
        """
        Registra evento de manera asíncrona (no bloqueante).
        Retorna el event_id generado.
        """
        event_id = event_data.get("event_id") or f"audit-{uuid.uuid4().hex[:16]}"
        event_data["event_id"] = event_id

        try:
            # Non-blocking put
            if self._config.enable_backpressure:
                try:
                    self._queue.put_nowait(event_data)
                except asyncio.QueueFull:
                    # Queue full - do immediate sync write
                    self._sync_logger.log(**self._event_data_to_kwargs(event_data))
                    self._errors += 1
            else:
                self._queue.put_nowait(event_data)

            self._events_logged += 1

            # Check if we should flush
            if self._should_flush():
                asyncio.create_task(self._flush())

        except Exception as e:
            # Fallback to sync write
            self._sync_logger.log(**self._event_data_to_kwargs(event_data))
            self._errors += 1

        return event_id

    def log_sync(self, **kwargs) -> Any:
        """Log síncrono (para fallback o uso directo)."""
        return self._sync_logger.log(**kwargs)

    def _should_flush(self) -> bool:
        """Determina si debe hacer flush."""
        if self._config.flush_strategy == FlushStrategy.IMMEDIATE:
            return True
        elif self._config.flush_strategy == FlushStrategy.BATCH:
            return len(self._buffer) >= self._config.batch_size
        elif self._config.flush_strategy == FlushStrategy.TIMED:
            return (time.time() - self._last_flush) >= self._config.flush_interval_seconds
        elif self._config.flush_strategy == FlushStrategy.ADAPTIVE:
            return (
                len(self._buffer) >= self._config.batch_size
                or (time.time() - self._last_flush) >= self._config.flush_interval_seconds
            )
        return False

    async def _flush_loop(self) -> None:
        """Loop principal de flush."""
        while self._running:
            try:
                await asyncio.sleep(self._config.flush_interval_seconds)
                await self._flush()
            except asyncio.CancelledError:
                break
            except Exception:
                self._errors += 1

    async def _flush(self) -> None:
        """Hace flush del buffer al storage."""
        if not self._buffer:
            return

        events_to_flush = list(self._buffer)
        self._buffer.clear()
        self._last_flush = time.time()

        try:
            for event_data in events_to_flush:
                self._sync_logger.log(**self._event_data_to_kwargs(event_data))

            self._events_flushed += len(events_to_flush)
            self._flush_count += 1
        except Exception as e:
            self._errors += 1
            if self._config.on_flush_error:
                self._config.on_flush_error(e, events_to_flush)

    def _event_data_to_kwargs(self, event_data: dict) -> dict:
        """Convierte event_data dict a kwargs para AuditLogger.log."""
        from core.PHASE_7.audit.logger.audit_logger import (
            AuditCategory, AuditAction, AuditSeverity,
        )

        kwargs = dict(event_data)

        # Convert string enums
        if isinstance(kwargs.get("category"), str):
            kwargs["category"] = AuditCategory(kwargs["category"])
        if isinstance(kwargs.get("action"), str):
            kwargs["action"] = AuditAction(kwargs["action"])
        if isinstance(kwargs.get("severity"), str):
            kwargs["severity"] = AuditSeverity(kwargs["severity"])

        return kwargs

    def get_stats(self) -> dict:
        """Obtiene estadísticas del logger."""
        return {
            "events_logged": self._events_logged,
            "events_flushed": self._events_flushed,
            "events_pending": len(self._buffer),
            "flush_count": self._flush_count,
            "errors": self._errors,
            "running": self._running,
            "queue_size": self._queue.qsize(),
            "config": {
                "batch_size": self._config.batch_size,
                "flush_interval": self._config.flush_interval_seconds,
                "strategy": self._config.flush_strategy.value,
            },
        }


class SyncAuditLogger:
    """Wrapper síncrono para AsyncAuditLogger."""

    def __init__(self, async_logger: AsyncAuditLogger):
        self._async = async_logger

    def log(self, **kwargs) -> Any:
        """Log síncrono que delega al async logger."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in async context - use async log
                asyncio.create_task(self._async.log_async(kwargs))
            else:
                # Not in async context - use sync fallback
                return self._async.log_sync(**kwargs)
        except RuntimeError:
            # No event loop - use sync
            return self._async.log_sync(**kwargs)
