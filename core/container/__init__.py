"""Cognitive Dependency Injection Container (CDIC).

The official component for dependency injection in EREN.

Architecture only -- no implementations, no business logic.
"""

from core.container.container import CognitiveContainer, ContainerFactory
from core.container.container_builder import ContainerBuilder
from core.container.container_events import ContainerEventPublisher, ContainerEventType
from core.container.container_metrics import ContainerMetricsCollector
from core.container.container_trace import ContainerTraceCollector, ContainerTraceEntry
from core.container.dependency_graph import DependencyGraph, DependencyNode, DependencyEdge
from core.container.dependency_validator import (
    DependencyValidator,
    ValidationError,
    ValidationResult,
)
from core.container.exceptions import (
    CircularDependencyException,
    ContainerDisposedException,
    ContainerException,
    DependencyResolutionException,
    DuplicateServiceException,
    FactoryExecutionException,
    InvalidLifetimeException,
    InvalidScopeException,
    OrphanDependencyException,
    RegistrationException,
    ScopeDisposedException,
    ServiceDescriptorException,
    ServiceNotFoundException,
    ValidationException,
)
from core.container.service_descriptor import ServiceDescriptor, ServiceInstance
from core.container.service_factory import ServiceFactory
from core.container.service_lifetime import ServiceLifetime
from core.container.service_provider import ServiceProvider
from core.container.service_registry import ServiceRegistry
from core.container.service_scope import ScopeType, ServiceScope

__all__ = [
    # Main Container
    "CognitiveContainer",
    "ContainerFactory",
    "ContainerBuilder",
    # Service Lifetime
    "ServiceLifetime",
    # Service Registry
    "ServiceRegistry",
    # Service Descriptor
    "ServiceDescriptor",
    "ServiceInstance",
    # Service Factory
    "ServiceFactory",
    # Service Provider
    "ServiceProvider",
    # Service Scope
    "ScopeType",
    "ServiceScope",
    # Dependency Graph
    "DependencyGraph",
    "DependencyNode",
    "DependencyEdge",
    # Dependency Validator
    "DependencyValidator",
    "ValidationError",
    "ValidationResult",
    # Container Events
    "ContainerEventType",
    "ContainerEventPublisher",
    # Container Metrics
    "ContainerMetricsCollector",
    # Container Trace
    "ContainerTraceCollector",
    "ContainerTraceEntry",
    # Exceptions
    "ContainerException",
    "ServiceNotFoundException",
    "DuplicateServiceException",
    "InvalidLifetimeException",
    "CircularDependencyException",
    "DependencyResolutionException",
    "ContainerDisposedException",
    "ScopeDisposedException",
    "FactoryExecutionException",
    "RegistrationException",
    "ValidationException",
    "InvalidScopeException",
    "ServiceDescriptorException",
    "OrphanDependencyException",
]
