"""Cognitive Knowledge Engine.

The knowledge component of EREN. Manages knowledge retrieval
and storage through a unified interface.

Architecture only -- no AI, no implementations, no real search.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .knowledge_metrics import KnowledgeMetricsCollector
from .knowledge_registry import KnowledgeRegistry
from .knowledge_router import KnowledgeRouter
from .knowledge_types import (
    KnowledgeEvidence,
    KnowledgeFilters,
    KnowledgeQuery,
    KnowledgeSession,
    KnowledgeSource,
    QueryPriority,
    QueryType,
)

# EventBus integration (optional)
try:
    from core.PHASE_1.infrastructure.events import Event, get_global_bus
    _HAS_EVENT_BUS = True
except ImportError:
    _HAS_EVENT_BUS = False

# CapabilityRegistry integration (optional)
try:
    from core.PHASE_2.capabilities import Capability, CapabilityRegistry
    _HAS_CAPABILITIES = True
except ImportError:
    _HAS_CAPABILITIES = False

if TYPE_CHECKING:
    pass


# =============================================================================
# Knowledge Session (Immutable)
# =============================================================================


@dataclass(frozen=True)
class KnowledgeSessionData:
    """Data for a knowledge session."""

    session_id: str
    query_id: str
    query_type: str
    sources_consulted: tuple[str, ...]
    results_count: int
    status: str
    created_at: str
    completed_at: str


# =============================================================================
# Capability Registration
# =============================================================================


class KnowledgeCapabilityRegistrar:
    """Handles automatic capability registration for knowledge."""

    def __init__(self) -> None:
        """Initialize the registrar."""
        self._registered = False
        self._enabled = _HAS_CAPABILITIES

    def register(self, registry: Any | None = None) -> None:
        """Register knowledge capabilities."""
        if not self._enabled or self._registered:
            return

        try:
            if registry is None:
                return

            capabilities = [
                ("knowledge.retrieve", "Knowledge Retrieval", "Retrieve knowledge from sources"),
                ("knowledge.store", "Knowledge Storage", "Store new knowledge evidence"),
                ("knowledge.route", "Knowledge Routing", "Route queries to appropriate sources"),
                ("knowledge.verify", "Knowledge Verification", "Verify knowledge accuracy"),
                ("knowledge.search", "Knowledge Search", "Search across all knowledge sources"),
            ]

            for cap_id, name, desc in capabilities:
                capability = Capability(
                    capability_id=cap_id,
                    name=name,
                    description=desc,
                    category="knowledge",
                )
                registry.register(capability)

            self._registered = True
        except Exception:
            pass

    @property
    def is_registered(self) -> bool:
        """Check if capabilities are registered."""
        return self._registered


# =============================================================================
# Event Publisher (Uses Global EventBus)
# =============================================================================


class KnowledgeEventPublisher:
    """Publishes events to the global EventBus."""

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._enabled = _HAS_EVENT_BUS

    def publish(self, event_type: str, **data: Any) -> None:
        """Publish an event to the global EventBus."""
        if not self._enabled:
            return

        try:
            bus = get_global_bus()
            if bus:
                event = Event(event_type=event_type, data=data)
                bus.publish(event)
        except Exception:
            pass

    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False

    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = _HAS_EVENT_BUS


# =============================================================================
# Main Knowledge Engine
# =============================================================================


class CognitiveKnowledgeEngine:
    """The main knowledge engine.

    Responsibilities:
    - Route queries to appropriate knowledge sources
    - Retrieve knowledge from registered sources
    - Store knowledge evidence
    - Maintain knowledge session history
    - Publish events to global EventBus
    """

    def __init__(
        self,
        registry: KnowledgeRegistry | None = None,
        router: KnowledgeRouter | None = None,
    ) -> None:
        """Initialize the knowledge engine.

        Args:
            registry: Knowledge registry for source registration.
            router: Knowledge router for query routing.
        """
        # Registry and router
        self._registry = registry or KnowledgeRegistry()
        self._router = router or KnowledgeRouter(self._registry)

        # Metrics
        self._metrics = KnowledgeMetricsCollector()

        # Event publisher
        self._event_publisher = KnowledgeEventPublisher()

        # Capability registrar
        self._capability_registrar = KnowledgeCapabilityRegistrar()

        # Session state
        self._sessions: dict[str, KnowledgeSession] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Capability Registration
    # =========================================================================

    def register_capabilities(self, registry: Any | None = None) -> None:
        """Register knowledge capabilities to the Capability Registry."""
        self._capability_registrar.register(registry)

    @property
    def capabilities_registered(self) -> bool:
        """Check if capabilities are registered."""
        return self._capability_registrar.is_registered

    # =========================================================================
    # Source Management
    # =========================================================================

    def register_source(self, source: KnowledgeSource) -> None:
        """Register a knowledge source.

        Args:
            source: The knowledge source to register.
        """
        self._registry.register(source)
        self._publish("knowledge_source_registered", source_id=source.source_id)

    def unregister_source(self, source_id: str) -> bool:
        """Unregister a knowledge source.

        Args:
            source_id: The source ID to unregister.

        Returns:
            True if unregistered.
        """
        result = self._registry.unregister(source_id)
        if result:
            self._publish("knowledge_source_unregistered", source_id=source_id)
        return result

    def get_registered_sources(self) -> list[str]:
        """Get IDs of registered sources."""
        return self._registry.list_sources()

    def get_sources_for_query(self, query: KnowledgeQuery) -> list[KnowledgeSource]:
        """Get sources that can answer a query.

        Args:
            query: The knowledge query.

        Returns:
            List of suitable sources.
        """
        return self._router.get_sources_for_query(query)

    # =========================================================================
    # Query Processing
    # =========================================================================

    async def retrieve(
        self,
        query_text: str,
        query_type: QueryType,
        priority: QueryPriority = QueryPriority.MEDIUM,
        context: dict | None = None,
        filters: KnowledgeFilters | None = None,
    ) -> KnowledgeSession:
        """Retrieve knowledge for a query.

        Args:
            query_text: The query text.
            query_type: Type of query.
            priority: Query priority.
            context: Additional context.
            filters: Query filters.

        Returns:
            Knowledge session with results.
        """
        # Create query
        query = KnowledgeQuery(
            query_id=f"q_{uuid.uuid4().hex[:16]}",
            query_text=query_text,
            query_type=query_type,
            priority=priority,
            context=context or {},
            filters=filters or KnowledgeFilters(),
        )

        # Create session
        session = KnowledgeSession(
            session_id=f"ks_{uuid.uuid4().hex[:16]}",
            query=query,
        )

        self._publish("knowledge_query_started", query_id=query.query_id)

        try:
            # Get sources for this query
            sources = self._router.get_sources_for_query(query)

            # Route query to sources
            results = await self._router.route_query(query, sources)

            # Create completed session
            completed_session = KnowledgeSession(
                session_id=session.session_id,
                query=session.query,
                results=tuple(results),
                sources_consulted=tuple(s.source_id for s in sources),
                routing_decision=self._router.get_routing_decision(query),
                status="completed",
            )

            with self._lock:
                self._sessions[completed_session.session_id] = completed_session

            self._publish(
                "knowledge_query_completed",
                query_id=query.query_id,
                results_count=len(results),
            )

            # Update metrics
            self._metrics.record_query(query_type, len(results))

            return completed_session

        except Exception as e:
            self._publish("knowledge_query_failed", query_id=query.query_id, error=str(e))
            self._metrics.record_error()
            raise

    def get_session(self, session_id: str) -> KnowledgeSession | None:
        """Get a knowledge session by ID.

        Args:
            session_id: The session ID.

        Returns:
            The session or None.
        """
        return self._sessions.get(session_id)

    # =========================================================================
    # Knowledge Storage
    # =========================================================================

    async def store(
        self,
        content: str | dict,
        source_type: str,
        source_id: str,
        confidence: float = 0.5,
    ) -> str:
        """Store knowledge evidence.

        Args:
            content: Knowledge content.
            source_type: Type of source.
            source_id: Source identifier.
            confidence: Confidence level.

        Returns:
            Evidence ID.
        """
        evidence = KnowledgeEvidence(
            evidence_id=f"ke_{uuid.uuid4().hex[:16]}",
            content=content,
            source_type=source_type,
            source_id=source_id,
            confidence=confidence,
        )

        self._publish(
            "knowledge_stored",
            evidence_id=evidence.evidence_id,
            source_id=source_id,
        )

        return evidence.evidence_id

    # =========================================================================
    # Metrics
    # =========================================================================

    def get_metrics(self) -> KnowledgeMetricsCollector:
        """Get knowledge metrics collector."""
        return self._metrics

    # =========================================================================
    # Event Publishing
    # =========================================================================

    def _publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish an event to the global EventBus."""
        self._event_publisher.publish(event_type, **kwargs)
