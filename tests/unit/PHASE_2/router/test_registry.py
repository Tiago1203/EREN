"""Unit tests for router registry module."""

import pytest

from core.PHASE_2.router.registry import RoutingRegistry
from core.PHASE_2.router.types import PipelineMetadata, RoutingRule
from core.PHASE_2.router.exceptions import (
    MetadataError,
    RuleNotFoundError,
    RuleAlreadyRegisteredError,
)


class TestRoutingRegistry:
    """Tests for RoutingRegistry."""

    def test_creation(self):
        """Test registry creation."""
        registry = RoutingRegistry()
        assert len(registry) == 0

    def test_register_pipeline(self):
        """Test pipeline registration."""
        registry = RoutingRegistry()
        metadata = PipelineMetadata(
            pipeline_name="TestPipeline",
            pipeline_id="test_pipeline",
        )

        registry.register_pipeline(metadata)
        assert registry.get_pipeline_count() == 1

    def test_register_duplicate_pipeline(self):
        """Test registering duplicate pipeline raises error."""
        registry = RoutingRegistry()
        metadata = PipelineMetadata(
            pipeline_name="TestPipeline",
            pipeline_id="test_pipeline",
        )

        registry.register_pipeline(metadata)
        with pytest.raises(MetadataError):
            registry.register_pipeline(metadata)

    def test_get_pipeline(self):
        """Test getting pipeline."""
        registry = RoutingRegistry()
        metadata = PipelineMetadata(
            pipeline_name="TestPipeline",
            pipeline_id="test_pipeline",
        )

        registry.register_pipeline(metadata)
        retrieved = registry.get_pipeline("test_pipeline")
        assert retrieved is not None
        assert retrieved.pipeline_name == "TestPipeline"

    def test_unregister_pipeline(self):
        """Test unregistering pipeline."""
        registry = RoutingRegistry()
        metadata = PipelineMetadata(
            pipeline_name="TestPipeline",
            pipeline_id="test_pipeline",
        )

        registry.register_pipeline(metadata)
        assert registry.unregister_pipeline("test_pipeline") is True
        assert registry.get_pipeline_count() == 0

    def test_list_pipelines(self):
        """Test listing pipelines."""
        registry = RoutingRegistry()

        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Pipeline1",
            pipeline_id="p1",
        ))
        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Pipeline2",
            pipeline_id="p2",
        ))

        pipelines = registry.list_pipelines()
        assert len(pipelines) == 2

    def test_get_pipelines_by_tag(self):
        """Test getting pipelines by tag."""
        registry = RoutingRegistry()

        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Medical",
            pipeline_id="medical",
            tags=("medical", "diagnosis"),
        ))
        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Research",
            pipeline_id="research",
            tags=("research",),
        ))

        medical = registry.get_pipelines_by_tag("medical")
        assert len(medical) == 1
        assert medical[0].pipeline_name == "Medical"

    def test_get_pipelines_by_intent(self):
        """Test getting pipelines by intent."""
        registry = RoutingRegistry()

        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Diagnostic",
            pipeline_id="diagnostic",
            intent_types=("diagnostic", "diagnosis"),
        ))

        diagnostic = registry.get_pipelines_by_intent("diagnostic")
        assert len(diagnostic) == 1

    def test_register_rule(self):
        """Test rule registration."""
        registry = RoutingRegistry()
        rule = RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
            intent_type="diagnostic",
            pipeline_name="DiagnosticPipeline",
        )

        registry.register_rule(rule)
        assert registry.get_rule_count() == 1

    def test_get_rule(self):
        """Test getting rule."""
        registry = RoutingRegistry()
        rule = RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
        )

        registry.register_rule(rule)
        retrieved = registry.get_rule("rule_001")
        assert retrieved.rule_id == "rule_001"

    def test_get_rule_not_found(self):
        """Test getting non-existent rule."""
        registry = RoutingRegistry()

        with pytest.raises(RuleNotFoundError):
            registry.get_rule("nonexistent")

    def test_unregister_rule(self):
        """Test unregistering rule."""
        registry = RoutingRegistry()
        rule = RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
        )

        registry.register_rule(rule)
        assert registry.unregister_rule("rule_001") is True
        assert registry.get_rule_count() == 0

    def test_clear(self):
        """Test clearing registry."""
        registry = RoutingRegistry()

        registry.register_pipeline(PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
        ))
        registry.register_rule(RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
        ))

        registry.clear()
        assert registry.get_pipeline_count() == 0
        assert registry.get_rule_count() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
