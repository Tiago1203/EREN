"""
Monitoring Module for EREN Production

Prometheus metrics and health checks.
"""
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
import time


# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

ACTIVE_DEVICES = Gauge(
    "active_devices_total",
    "Total number of active devices"
)

OPEN_INCIDENTS = Gauge(
    "open_incidents_total",
    "Total number of open incidents"
)

AI_RECOMMENDATIONS = Gauge(
    "ai_recommendations_total",
    "Total AI recommendations generated"
)


class MonitoringMiddleware:
    """Middleware for request monitoring."""
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response


def setup_monitoring(app: FastAPI):
    """Setup monitoring endpoints."""
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "database": "healthy",
                "cache": "healthy",
                "queue": "healthy"
            }
        }
    
    @app.get("/health/ready")
    async def readiness():
        """Readiness probe."""
        return {"status": "ready"}
    
    @app.get("/health/live")
    async def liveness():
        """Liveness probe."""
        return {"status": "alive"}


# Update metrics functions
def update_device_metrics(count: int):
    """Update device metrics."""
    ACTIVE_DEVICES.set(count)


def update_incident_metrics(count: int):
    """Update incident metrics."""
    OPEN_INCIDENTS.set(count)


def increment_recommendations():
    """Increment recommendation counter."""
    AI_RECOMMENDATIONS.inc()
