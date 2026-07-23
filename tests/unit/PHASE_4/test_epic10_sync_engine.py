"""Unit tests for EPIC 10: Knowledge Synchronization Engine."""

import pytest
import asyncio


class TestEPIC10Imports:
    """Tests for EPIC 10 module imports."""

    def test_import_epic10(self):
        """Test EPIC 10 module imports."""
        from core.PHASE_4.epic10_sync_engine import (
            SyncJob,
            ScheduleConfig,
            SourceHealth,
        )
        assert SyncJob is not None
        assert ScheduleConfig is not None

    def test_import_sync(self):
        """Test sync module imports."""
        from core.PHASE_4.epic10_sync_engine.sync import (
            SyncSource,
            SyncStatus,
            InMemorySyncManager,
        )
        assert SyncSource is not None
        assert SyncStatus is not None

    def test_import_schedule(self):
        """Test schedule module imports."""
        from core.PHASE_4.epic10_sync_engine.schedule import (
            ScheduleFrequency,
            ScheduleConfig,
            InMemoryScheduler,
        )
        assert ScheduleFrequency is not None
        assert ScheduleConfig is not None

    def test_import_monitor(self):
        """Test monitor module imports."""
        from core.PHASE_4.epic10_sync_engine.monitor import (
            MonitorStatus,
            SourceHealth,
            InMemorySourceMonitor,
        )
        assert MonitorStatus is not None
        assert SourceHealth is not None


class TestSyncJob:
    """Tests for SyncJob."""

    def test_job_creation(self):
        """Test sync job creation."""
        from core.PHASE_4.epic10_sync_engine import SyncJob, SyncSource, SyncStatus
        
        job = SyncJob(
            job_id="job_1",
            source=SyncSource.PUBMED,
        )
        
        assert job.job_id == "job_1"
        assert job.source == SyncSource.PUBMED
        assert job.status == SyncStatus.PENDING

    def test_job_progress(self):
        """Test job progress."""
        from core.PHASE_4.epic10_sync_engine import SyncJob, SyncSource
        
        job = SyncJob(
            job_id="job_1",
            source=SyncSource.PUBMED,
            items_to_sync=100,
            items_synced=50,
        )
        
        assert job.get_progress() == 0.5


class TestSyncManager:
    """Tests for InMemorySyncManager."""

    @pytest.mark.asyncio
    async def test_start_sync(self):
        """Test starting sync."""
        from core.PHASE_4.epic10_sync_engine import (
            InMemorySyncManager,
            SyncSource,
            SyncStatus,
        )
        
        manager = InMemorySyncManager()
        job = await manager.start_sync(SyncSource.PUBMED)
        
        assert job.job_id is not None
        assert job.source == SyncSource.PUBMED
        assert job.status == SyncStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """Test getting job status."""
        from core.PHASE_4.epic10_sync_engine import InMemorySyncManager, SyncSource
        
        manager = InMemorySyncManager()
        job = await manager.start_sync(SyncSource.FDA)
        
        retrieved = await manager.get_job_status(job.job_id)
        
        assert retrieved is not None
        assert retrieved.source == SyncSource.FDA


class TestScheduleConfig:
    """Tests for ScheduleConfig."""

    def test_config_creation(self):
        """Test schedule config creation."""
        from core.PHASE_4.epic10_sync_engine.schedule import (
            ScheduleConfig,
            ScheduleFrequency,
        )
        
        config = ScheduleConfig(
            schedule_id="daily_sync",
            frequency=ScheduleFrequency.DAILY,
            hour=2,
            minute=30,
        )
        
        assert config.schedule_id == "daily_sync"
        assert config.frequency == ScheduleFrequency.DAILY
        assert config.hour == 2


class TestScheduler:
    """Tests for InMemoryScheduler."""

    @pytest.mark.asyncio
    async def test_schedule(self):
        """Test scheduling a job."""
        from core.PHASE_4.epic10_sync_engine.schedule import (
            InMemoryScheduler,
            ScheduleConfig,
            ScheduleFrequency,
        )
        
        scheduler = InMemoryScheduler()
        config = ScheduleConfig(
            schedule_id="test",
            frequency=ScheduleFrequency.DAILY,
        )
        
        job = await scheduler.schedule(config)
        
        assert job.job_id == "test"

    @pytest.mark.asyncio
    async def test_pause_resume(self):
        """Test pause and resume."""
        from core.PHASE_4.epic10_sync_engine.schedule import (
            InMemoryScheduler,
            ScheduleConfig,
            ScheduleFrequency,
            ScheduleStatus,
        )
        
        scheduler = InMemoryScheduler()
        config = ScheduleConfig(
            schedule_id="test",
            frequency=ScheduleFrequency.DAILY,
        )
        
        await scheduler.schedule(config)
        await scheduler.pause("test")
        
        paused = await scheduler.get_schedule("test")
        assert paused.status == ScheduleStatus.PAUSED
        
        await scheduler.resume("test")
        
        resumed = await scheduler.get_schedule("test")
        assert resumed.status == ScheduleStatus.ACTIVE


class TestSourceHealth:
    """Tests for SourceHealth."""

    def test_health_creation(self):
        """Test source health creation."""
        from core.PHASE_4.epic10_sync_engine.monitor import (
            SourceHealth,
            MonitorStatus,
        )
        
        health = SourceHealth(
            source="pubmed",
            status=MonitorStatus.HEALTHY,
            response_time_ms=150.0,
        )
        
        assert health.source == "pubmed"
        assert health.status == MonitorStatus.HEALTHY
        assert health.is_healthy()


class TestSourceMonitor:
    """Tests for InMemorySourceMonitor."""

    @pytest.mark.asyncio
    async def test_check_health(self):
        """Test checking source health."""
        from core.PHASE_4.epic10_sync_engine.monitor import InMemorySourceMonitor
        
        monitor = InMemorySourceMonitor()
        health = await monitor.check_health("pubmed")
        
        assert health.source == "pubmed"

    @pytest.mark.asyncio
    async def test_record_change(self):
        """Test recording change event."""
        from core.PHASE_4.epic10_sync_engine.monitor import (
            InMemorySourceMonitor,
            ChangeEvent,
            ChangeType,
        )
        
        monitor = InMemorySourceMonitor()
        
        event = ChangeEvent(
            event_id="evt_1",
            source="pubmed",
            change_type=ChangeType.NEW,
            document_id="doc_1",
        )
        
        await monitor.record_change(event)
        
        changes = await monitor.get_recent_changes("pubmed")
        assert len(changes) == 1


class TestChangeEvent:
    """Tests for ChangeEvent."""

    def test_event_creation(self):
        """Test change event creation."""
        from core.PHASE_4.epic10_sync_engine.monitor import (
            ChangeEvent,
            ChangeType,
        )
        
        event = ChangeEvent(
            event_id="evt_1",
            source="fda",
            change_type=ChangeType.UPDATED,
            priority="high",
        )
        
        assert event.event_id == "evt_1"
        assert event.change_type == ChangeType.UPDATED

    def test_is_critical(self):
        """Test critical check."""
        from core.PHASE_4.epic10_sync_engine.monitor import ChangeEvent, ChangeType
        
        critical = ChangeEvent(
            event_id="1",
            source="fda",
            change_type=ChangeType.DEPRECATED,
            priority="critical",
        )
        
        non_critical = ChangeEvent(
            event_id="2",
            source="pubmed",
            change_type=ChangeType.NEW,
            priority="normal",
        )
        
        assert critical.is_critical()
        assert not non_critical.is_critical()


class TestSyncSources:
    """Tests for SyncSource."""

    def test_sync_sources(self):
        """Test sync source enum."""
        from core.PHASE_4.epic10_sync_engine.sync import SyncSource
        
        assert SyncSource.PUBMED.value == "pubmed"
        assert SyncSource.FDA.value == "fda"
        assert SyncSource.EMA.value == "ema"


class TestScheduleFrequency:
    """Tests for ScheduleFrequency."""

    def test_frequencies(self):
        """Test frequency enum."""
        from core.PHASE_4.epic10_sync_engine.schedule import ScheduleFrequency
        
        assert ScheduleFrequency.HOURLY.value == "hourly"
        assert ScheduleFrequency.DAILY.value == "daily"
        assert ScheduleFrequency.WEEKLY.value == "weekly"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
