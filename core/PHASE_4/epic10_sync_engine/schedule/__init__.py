"""
PHASE 4 - EPIC 10: Schedule Module

Programación de sincronización:
- Update Scheduler
- Schedule Config
- Cron Jobs
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class ScheduleFrequency(str, Enum):
    """Frecuencia de programación."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


class ScheduleStatus(str, Enum):
    """Estado de programación."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


@dataclass
class ScheduleConfig:
    """Configuración de programación."""
    schedule_id: str
    frequency: ScheduleFrequency
    
    # Time config
    hour: int = 0       # Hour of day (0-23)
    minute: int = 0     # Minute (0-59)
    day_of_week: int = 0  # 0=Monday, 6=Sunday
    
    # Status
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    
    # Source
    source: str = ""  # SyncSource value
    
    # Execution
    last_run: str = ""
    next_run: str = ""
    run_count: int = 0
    
    def __post_init__(self):
        self._calculate_next_run()
    
    def _calculate_next_run(self) -> None:
        """Calcula próxima ejecución."""
        now = datetime.now()
        
        if self.frequency == ScheduleFrequency.HOURLY:
            next_run = now.replace(minute=self.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(hours=1)
        elif self.frequency == ScheduleFrequency.DAILY:
            next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            days_ahead = self.day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        else:
            next_run = now + timedelta(days=1)
        
        self.next_run = next_run.isoformat()


@dataclass
class ScheduledJob:
    """Trabajo programado."""
    job_id: str
    schedule_id: str
    
    # Schedule info
    frequency: ScheduleFrequency
    source: str
    
    # Status
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    is_running: bool = False
    
    # Execution
    last_execution: str = ""
    next_execution: str = ""
    execution_count: int = 0
    
    # Results
    last_result: str = ""
    success_count: int = 0
    failure_count: int = 0


class BaseScheduler(ABC):
    """Clase base para schedulers."""
    
    @abstractmethod
    async def schedule(self, config: ScheduleConfig) -> ScheduledJob:
        """Programa trabajo."""
        ...
    
    @abstractmethod
    async def unschedule(self, schedule_id: str) -> bool:
        """Elimina programación."""
        ...
    
    @abstractmethod
    async def pause(self, schedule_id: str) -> ScheduleConfig:
        """Pausa programación."""
        ...
    
    @abstractmethod
    async def resume(self, schedule_id: str) -> ScheduleConfig:
        """Reanuda programación."""
        ...


class InMemoryScheduler(BaseScheduler):
    """Scheduler en memoria."""
    
    def __init__(self):
        self._schedules: dict[str, ScheduleConfig] = {}
        self._jobs: dict[str, ScheduledJob] = {}
    
    async def schedule(self, config: ScheduleConfig) -> ScheduledJob:
        """Programa trabajo."""
        self._schedules[config.schedule_id] = config
        
        job = ScheduledJob(
            job_id=config.schedule_id,
            schedule_id=config.schedule_id,
            frequency=config.frequency,
            source=config.source,
            next_execution=config.next_run,
        )
        
        self._jobs[config.schedule_id] = job
        return job
    
    async def unschedule(self, schedule_id: str) -> bool:
        """Elimina programación."""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
        if schedule_id in self._jobs:
            del self._jobs[schedule_id]
        return True
    
    async def pause(self, schedule_id: str) -> ScheduleConfig:
        """Pausa programación."""
        config = self._schedules.get(schedule_id)
        if not config:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        config.status = ScheduleStatus.PAUSED
        
        job = self._jobs.get(schedule_id)
        if job:
            job.status = ScheduleStatus.PAUSED
        
        return config
    
    async def resume(self, schedule_id: str) -> ScheduleConfig:
        """Reanuda programación."""
        config = self._schedules.get(schedule_id)
        if not config:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        config.status = ScheduleStatus.ACTIVE
        config._calculate_next_run()
        
        job = self._jobs.get(schedule_id)
        if job:
            job.status = ScheduleStatus.ACTIVE
            job.next_execution = config.next_run
        
        return config
    
    async def get_schedule(self, schedule_id: str) -> ScheduleConfig | None:
        """Obtiene programación."""
        return self._schedules.get(schedule_id)
    
    async def list_schedules(self) -> list[ScheduleConfig]:
        """Lista programaciones."""
        return list(self._schedules.values())
    
    async def get_due_schedules(self) -> list[ScheduleConfig]:
        """Obtiene programaciones pendientes."""
        now = datetime.now()
        due = []
        
        for config in self._schedules.values():
            if config.status != ScheduleStatus.ACTIVE:
                continue
            
            next_run = datetime.fromisoformat(config.next_run)
            if next_run <= now:
                due.append(config)
        
        return due


class CronParser:
    """Parser de expresiones cron."""
    
    @staticmethod
    def parse(expression: str) -> ScheduleConfig:
        """Parsea expresión cron."""
        parts = expression.split()
        
        if len(parts) < 5:
            raise ValueError("Invalid cron expression")
        
        minute, hour, day, month, dow = parts[:5]
        
        config = ScheduleConfig(
            schedule_id="",
            frequency=ScheduleFrequency.DAILY,
            minute=int(minute) if minute.isdigit() else 0,
            hour=int(hour) if hour.isdigit() else 0,
        )
        
        return config
    
    @staticmethod
    def format(config: ScheduleConfig) -> str:
        """Formatea a expresión cron."""
        return f"{config.minute} {config.hour} * * {config.day_of_week}"


__all__ = [
    "ScheduleFrequency",
    "ScheduleStatus",
    "ScheduleConfig",
    "ScheduledJob",
    "BaseScheduler",
    "InMemoryScheduler",
    "CronParser",
]
