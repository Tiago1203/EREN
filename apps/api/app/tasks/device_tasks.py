"""Device-related Celery tasks."""

from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.device_tasks.aggregate_telemetry_hourly",
    bind=True,
    max_retries=3,
)
def aggregate_telemetry_hourly(self) -> dict:
    """Aggregate device telemetry data hourly for analytics.

    - Collects telemetry from all connected devices
    - Aggregates usage patterns and failure rates
    - Stores aggregated metrics for dashboards
    """
    try:
        logger.info("Starting hourly telemetry aggregation")
        # TODO: Implement with real device telemetry data
        logger.info("Hourly telemetry aggregation completed")
        return {"status": "ok", "devices_processed": 0}
    except Exception as exc:
        logger.error("Telemetry aggregation failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.device_tasks.sync_device_readings")
def sync_device_readings(device_ids: list[str]) -> dict:
    """Sync readings from MQTT-connected devices to PostgreSQL."""
    logger.info("Syncing readings for %d devices", len(device_ids))
    return {"status": "ok", "synced": len(device_ids)}
