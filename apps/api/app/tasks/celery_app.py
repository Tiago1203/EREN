"""Celery task queue for background processing.

Usage::

    # Run worker
    cd apps/api
    uv run celery -A app.tasks.celery_app worker --loglevel=INFO

    # Run beat scheduler (for periodic tasks)
    uv run celery -A app.tasks.celery_app beat --loglevel=INFO
"""

from __future__ import annotations

import logging
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

celery_app = Celery(
    "eren_tasks",
    broker="amqp://eren:eren@rabbitmq:5672/",
    backend="redis://redis:6379/1",
    include=[
        "app.tasks.device_tasks",
        "app.tasks.knowledge_tasks",
        "app.tasks.outbox_tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "aggregate-device-telemetry-hourly": {
        "task": "app.tasks.device_tasks.aggregate_telemetry_hourly",
        "schedule": crontab(minute=0),
    },
    "cleanup-old-outbox-events-daily": {
        "task": "app.tasks.outbox_tasks.cleanup_processed_events",
        "schedule": crontab(hour=2, minute=0),
    },
    "refresh-knowledge-cache-daily": {
        "task": "app.tasks.knowledge_tasks.refresh_popular_articles",
        "schedule": crontab(hour=3, minute=0),
    },
}

celery_app.conf.timezone = "UTC"
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_default_retry_delay = 30
celery_app.conf.task_max_retries = 3
