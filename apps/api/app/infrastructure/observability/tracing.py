"""OpenTelemetry tracing and metrics initialization."""
from __future__ import annotations

import logging
from typing import Any

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def setup_tracing() -> Any:
    """Initialize OpenTelemetry tracing based on settings."""
    settings = get_settings()

    if not settings.otel_endpoint:
        logger.info("No OTEL endpoint configured, skipping tracing setup")
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {
                "service.name": settings.service_name,
                "deployment.environment": settings.environment,
            }
        )

        exporter = OTLPSpanExporter(endpoint=settings.otel_endpoint, insecure=True)
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        logger.info("Tracing initialized: %s -> %s", settings.service_name, settings.otel_endpoint)
        return trace.get_tracer(settings.service_name)
    except ImportError:
        logger.warning("OpenTelemetry packages not installed")
        return None


def setup_instrumentation(app: Any) -> None:
    """Instrument FastAPI and SQLAlchemy with OpenTelemetry."""
    settings = get_settings()
    if not settings.otel_endpoint:
        return

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        logger.info("FastAPI and SQLAlchemy instrumentation enabled")
    except ImportError:
        logger.warning("OpenTelemetry instrumentation packages not installed")
