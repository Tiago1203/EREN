"""Unit tests for pipeline registry module."""

import pytest

from core.pipeline.registry import (
    PipelineRegistry,
    PipelineNotFoundError,
    PipelineAlreadyRegisteredError,
)
from core.pipeline.pipeline import CognitivePipeline


class TestPipelineRegistry:
    """Tests for PipelineRegistry."""

    def test_creation(self):
        """Test registry creation."""
        registry = PipelineRegistry()
        assert len(registry) == 0

    def test_register(self):
        """Test registering pipeline."""
        registry = PipelineRegistry()
        pipeline = CognitivePipeline(name="test")

        registry.register("test", pipeline)
        assert "test" in registry

    def test_register_duplicate(self):
        """Test registering duplicate raises error."""
        registry = PipelineRegistry()
        pipeline = CognitivePipeline(name="test")

        registry.register("test", pipeline)

        with pytest.raises(PipelineAlreadyRegisteredError):
            registry.register("test", CognitivePipeline(name="test2"))

    def test_register_with_replace(self):
        """Test registering with replace."""
        registry = PipelineRegistry()

        registry.register("test", CognitivePipeline(name="test1"))
        registry.register("test", CognitivePipeline(name="test2"), replace=True)

        assert registry.get("test").name == "test2"

    def test_get(self):
        """Test getting pipeline."""
        registry = PipelineRegistry()
        pipeline = CognitivePipeline(name="test")

        registry.register("test", pipeline)
        assert registry.get("test") is pipeline

    def test_get_not_found(self):
        """Test getting non-existent pipeline."""
        registry = PipelineRegistry()

        with pytest.raises(PipelineNotFoundError):
            registry.get("nonexistent")

    def test_unregister(self):
        """Test unregistering pipeline."""
        registry = PipelineRegistry()
        pipeline = CognitivePipeline(name="test")

        registry.register("test", pipeline)
        assert registry.unregister("test") is True
        assert "test" not in registry

    def test_list_pipelines(self):
        """Test listing pipelines."""
        registry = PipelineRegistry()

        registry.register("test1", CognitivePipeline(name="test1"))
        registry.register("test2", CognitivePipeline(name="test2"))

        pipelines = registry.list_pipelines()
        assert "test1" in pipelines
        assert "test2" in pipelines

    def test_clear(self):
        """Test clearing registry."""
        registry = PipelineRegistry()

        registry.register("test", CognitivePipeline(name="test"))
        registry.clear()

        assert len(registry) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
