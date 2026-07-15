"""Domain Events for EREN."""

from .domain import (
    # Incident events
    IncidentReported,
    IncidentTriaged,
    IncidentOpened,
    IncidentProgressed,
    IncidentEscalated,
    IncidentResolved,
    IncidentClosed,
    # AI events
    RecommendationGenerated,
    RecommendationAccepted,
    RecommendationRejected,
    FeedbackReceived,
    # Device events
    DeviceRegistered,
    DeviceStatusChanged,
    DeviceLocationChanged,
    # Maintenance events
    MaintenanceScheduled,
    MaintenanceCompleted,
    # Base class
    DomainEvent,
)

__all__ = [
    # Base
    "DomainEvent",
    # Incident
    "IncidentReported",
    "IncidentTriaged",
    "IncidentOpened",
    "IncidentProgressed",
    "IncidentEscalated",
    "IncidentResolved",
    "IncidentClosed",
    # AI
    "RecommendationGenerated",
    "RecommendationAccepted",
    "RecommendationRejected",
    "FeedbackReceived",
    # Device
    "DeviceRegistered",
    "DeviceStatusChanged",
    "DeviceLocationChanged",
    # Maintenance
    "MaintenanceScheduled",
    "MaintenanceCompleted",
]
