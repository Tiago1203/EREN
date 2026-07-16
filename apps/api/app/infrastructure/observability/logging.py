"""Structured JSON logging configuration."""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any

from pythonjsonlogger import jsonlogger

from app.config.settings import get_settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with EREN-specific fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = "eren-api"

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def configure_logging() -> None:
    """Configure structured JSON logging for the application."""
    settings = get_settings()

    level = "DEBUG" if settings.debug else "INFO"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    if settings.environment == "production":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            json_ensure_ascii=False,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    for lib in ["uvicorn.access", "sqlalchemy.engine", "aio_pika", "aiormq"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.getLogger(__name__).debug("Logging configured (level=%s, env=%s)", level, settings.environment)
