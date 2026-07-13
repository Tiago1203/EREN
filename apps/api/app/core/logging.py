"""Minimal, centralized logging configuration.

Call :func:`configure_logging` once during application startup.
"""

import logging
from logging.config import dictConfig

from app.config.settings import get_settings


def configure_logging() -> None:
    """Configure root logging based on the current environment."""
    settings = get_settings()
    level = "DEBUG" if settings.debug else "INFO"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
    logging.getLogger(__name__).debug("Logging configured (level=%s)", level)
