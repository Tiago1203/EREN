"""Routing Registry for EREN OS Cognitive Capability Router.

Manages pipeline metadata and routing rules.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.router.exceptions import (
    MetadataError,
    RuleAlreadyRegisteredError,
    RuleNotFoundError,
)
from core.router.types import (
    PipelineMetadata,
    RoutingRule,
)

if TYPE_CHECKING:
    pass


class RoutingRegistry:
    """Registry for pipeline metadata and routing rules.

    Provides:
    - Pipeline metadata registration
    - Routing rule registration
    - Pipeline discovery
    - Rule lookup
    """

    def __init__(self):
        """Initialize the registry."""
        self._pipeline_metadata: dict[str, PipelineMetadata] = {}
        self._rules: dict[str, RoutingRule] = {}
        self._rules_by_intent: dict[str, list[str]] = {}  # intent_type -> rule_ids
        self._factories: dict[str, Callable[[], PipelineMetadata]] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Pipeline Metadata
    # =========================================================================

    def register_pipeline(
        self,
        metadata: PipelineMetadata,
        replace: bool = False,
    ) -> None:
        """Register pipeline metadata.

        Args:
            metadata: Pipeline metadata.
            replace: Whether to replace existing.

        Raises:
            MetadataError: If pipeline already registered.
        """
        with self._lock:
            key = metadata.pipeline_id or metadata.pipeline_name

            if key in self._pipeline_metadata and not replace:
                raise MetadataError(
                    f"Pipeline '{metadata.pipeline_name}' already registered",
                    metadata.pipeline_name,
                )

            self._pipeline_metadata[key] = metadata

    def unregister_pipeline(self, pipeline_id: str) -> bool:
        """Unregister pipeline metadata.

        Args:
            pipeline_id: Pipeline ID or name.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if pipeline_id in self._pipeline_metadata:
                del self._pipeline_metadata[pipeline_id]
                return True
            return False

    def get_pipeline(self, pipeline_id: str) -> PipelineMetadata | None:
        """Get pipeline metadata.

        Args:
            pipeline_id: Pipeline ID or name.

        Returns:
            Pipeline metadata or None.
        """
        with self._lock:
            return self._pipeline_metadata.get(pipeline_id)

    def list_pipelines(self) -> list[PipelineMetadata]:
        """List all registered pipelines.

        Returns:
            List of pipeline metadata.
        """
        with self._lock:
            return list(self._pipeline_metadata.values())

    def get_pipelines_by_tag(self, tag: str) -> list[PipelineMetadata]:
        """Get pipelines with a specific tag.

        Args:
            tag: Tag to filter by.

        Returns:
            List of matching pipelines.
        """
        with self._lock:
            return [
                m for m in self._pipeline_metadata.values()
                if tag in m.tags
            ]

    def get_pipelines_by_intent(self, intent_type: str) -> list[PipelineMetadata]:
        """Get pipelines that handle a specific intent type.

        Args:
            intent_type: Intent type.

        Returns:
            List of matching pipelines.
        """
        with self._lock:
            return [
                m for m in self._pipeline_metadata.values()
                if intent_type in m.intent_types
            ]

    def get_pipeline_count(self) -> int:
        """Get number of registered pipelines.

        Returns:
            Pipeline count.
        """
        with self._lock:
            return len(self._pipeline_metadata)

    # =========================================================================
    # Routing Rules
    # =========================================================================

    def register_rule(
        self,
        rule: RoutingRule,
        replace: bool = False,
    ) -> None:
        """Register a routing rule.

        Args:
            rule: Routing rule.
            replace: Whether to replace existing.

        Raises:
            RuleAlreadyRegisteredError: If rule already exists.
        """
        with self._lock:
            if rule.rule_id in self._rules and not replace:
                raise RuleAlreadyRegisteredError(rule.rule_id)

            self._rules[rule.rule_id] = rule

            # Index by intent type
            if rule.intent_type:
                if rule.intent_type not in self._rules_by_intent:
                    self._rules_by_intent[rule.intent_type] = []
                if rule.rule_id not in self._rules_by_intent[rule.intent_type]:
                    self._rules_by_intent[rule.intent_type].append(rule.rule_id)

    def unregister_rule(self, rule_id: str) -> bool:
        """Unregister a routing rule.

        Args:
            rule_id: Rule ID.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if rule_id in self._rules:
                rule = self._rules[rule_id]

                # Remove from index
                if rule.intent_type and rule.intent_type in self._rules_by_intent:
                    if rule_id in self._rules_by_intent[rule.intent_type]:
                        self._rules_by_intent[rule.intent_type].remove(rule_id)

                del self._rules[rule_id]
                return True
            return False

    def get_rule(self, rule_id: str) -> RoutingRule:
        """Get a routing rule.

        Args:
            rule_id: Rule ID.

        Returns:
            Routing rule.

        Raises:
            RuleNotFoundError: If rule not found.
        """
        with self._lock:
            if rule_id not in self._rules:
                raise RuleNotFoundError(rule_id)
            return self._rules[rule_id]

    def get_rules_for_intent(self, intent_type: str) -> list[RoutingRule]:
        """Get rules for a specific intent type.

        Args:
            intent_type: Intent type.

        Returns:
            List of matching rules sorted by priority.
        """
        with self._lock:
            rule_ids = self._rules_by_intent.get(intent_type, [])
            rules = [self._rules[rid] for rid in rule_ids if rid in self._rules]
            return sorted(rules, key=lambda r: r.priority, reverse=True)

    def list_rules(self) -> list[RoutingRule]:
        """List all registered rules.

        Returns:
            List of routing rules.
        """
        with self._lock:
            return list(self._rules.values())

    def get_rule_count(self) -> int:
        """Get number of registered rules.

        Returns:
            Rule count.
        """
        with self._lock:
            return len(self._rules)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    def register_pipeline_factory(
        self,
        name: str,
        factory: Callable[[], PipelineMetadata],
        replace: bool = False,
    ) -> None:
        """Register a pipeline metadata factory.

        Args:
            name: Factory name.
            factory: Factory function.
            replace: Whether to replace existing.
        """
        with self._lock:
            if name in self._factories and not replace:
                raise RuleAlreadyRegisteredError(name)
            self._factories[name] = factory

    def create_pipeline_from_factory(self, name: str) -> PipelineMetadata | None:
        """Create pipeline metadata from factory.

        Args:
            name: Factory name.

        Returns:
            Created metadata or None.
        """
        with self._lock:
            factory = self._factories.get(name)
            if factory:
                return factory()
            return None

    # =========================================================================
    # Utility
    # =========================================================================

    def __len__(self) -> int:
        """Get total count."""
        with self._lock:
            return len(self._pipeline_metadata)

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._pipeline_metadata.clear()
            self._rules.clear()
            self._rules_by_intent.clear()
            self._factories.clear()


# Global registry instance
_global_registry: RoutingRegistry | None = None
_registry_lock = threading.Lock()


def get_routing_registry() -> RoutingRegistry:
    """Get the global routing registry.

    Returns:
        Global RoutingRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = RoutingRegistry()
            _register_default_pipelines(_global_registry)
        return _global_registry


def _register_default_pipelines(registry: RoutingRegistry) -> None:
    """Register default pipeline metadata.

    Args:
        registry: Registry to register with.
    """
    from core.router.types import PipelineMetadata

    # Medical Pipeline
    registry.register_pipeline(PipelineMetadata(
        pipeline_name="MedicalPipeline",
        pipeline_id="medical_pipeline",
        description="Pipeline for medical diagnosis and treatment",
        tags=("medical", "diagnosis", "patient"),
        priority=100,
        required_capabilities=("knowledge", "memory", "reasoning", "decision"),
        intent_types=("diagnostic", "treatment", "prescription", "triage"),
    ))

    # Maintenance Pipeline
    registry.register_pipeline(PipelineMetadata(
        pipeline_name="MaintenancePipeline",
        pipeline_id="maintenance_pipeline",
        description="Pipeline for equipment maintenance",
        tags=("maintenance", "equipment", "repair"),
        priority=50,
        required_capabilities=("knowledge", "tool"),
        intent_types=("maintenance", "repair", "inspection"),
    ))

    # Research Pipeline
    registry.register_pipeline(PipelineMetadata(
        pipeline_name="ResearchPipeline",
        pipeline_id="research_pipeline",
        description="Pipeline for research queries",
        tags=("research", "analysis", "data"),
        priority=30,
        required_capabilities=("knowledge", "memory", "reasoning"),
        intent_types=("research", "analysis", "query"),
    ))

    # Emergency Pipeline
    registry.register_pipeline(PipelineMetadata(
        pipeline_name="EmergencyPipeline",
        pipeline_id="emergency_pipeline",
        description="Pipeline for emergency situations",
        tags=("emergency", "critical", "urgent"),
        priority=200,
        required_capabilities=("reasoning", "decision", "tool"),
        intent_types=("emergency", "critical", "alert"),
    ))
