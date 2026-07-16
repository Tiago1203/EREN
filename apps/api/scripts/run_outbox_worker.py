#!/usr/bin/env python3
"""Outbox Worker — publishes domain events from the outbox table to RabbitMQ.

Run as a separate process::

    python scripts/run_outbox_worker.py

Environment::

    EREN_API_DATABASE_URL     # PostgreSQL connection string
    EREN_API_RABBITMQ_URL     # RabbitMQ AMQP URL

The worker polls the outbox table, publishes pending events to RabbitMQ,
and marks them as published. Failed events are retried up to MAX_RETRIES
times before being moved to the DLQ.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

# Ensure the app package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import get_settings
from app.infrastructure.messaging.outbox import OutboxWorker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [outbox] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()

    logger.info("Starting Outbox Worker")
    logger.info("  Database: %s", settings.database_url)
    logger.info("  Poll interval: %ss", 1.0)
    logger.info("  Batch size: %s", 100)
    logger.info("  Max retries: %s", 3)

    worker = OutboxWorker(
        poll_interval=1.0,
        batch_size=100,
        max_retries=3,
    )

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Outbox Worker stopped by SIGINT")


if __name__ == "__main__":
    asyncio.run(main())
