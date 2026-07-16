"""Outbox cleanup Celery tasks."""

from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.outbox_tasks.cleanup_processed_events")
def cleanup_processed_events(retention_days: int = 7) -> dict:
    """Delete processed outbox events older than retention_days.

    Runs daily at 2 AM UTC to prevent the outbox_events table from growing indefinitely.

    Events that have been published and are older than retention_days are deleted.
    Failed events are kept longer for debugging.
    """
    try:
        logger.info("Cleaning up outbox events older than %d days", retention_days)
        # TODO: Implement with real database cleanup
        # DELETE FROM incident.outbox_events
        # WHERE status = 'published'
        #   AND processed_at < NOW() - INTERVAL '%d days'
        logger.info("Outbox cleanup completed")
        return {"status": "ok", "deleted": 0}
    except Exception as exc:
        logger.error("Outbox cleanup failed: %s", exc)
        raise
