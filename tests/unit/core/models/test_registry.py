"""Unit tests for model registry."""

import pytest

from core.models import (
    ModelRegistry,
    ModelDescriptor,
    ModelCatalog,
    ModelCategory,
    ModelState,
    ModelSelectionPolicy,
    ModelPricing,
    get_model_registry,
    reset_model_registry,
)
from core.models.exceptions import (
    ModelNotFoundError,
    ModelAlreadyRegisteredError,
)


class TestModelRegistry:
    """Tests for ModelRegistry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_model_registry()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return ModelRegistry()

    @pytest.fixture
    def sample_model(self):
        """Create sample model."""
        return ModelDescriptor(
            model_id="test-model",
            provider_id="test-provider",
            display_name="Test Model",
            category=ModelCategory.GENERAL,
            pricing=ModelPricing(cost_per_input_token=0.01),
            state=ModelState.AVAILABLE,
        )

    def test_register(self, registry, sample_model):
        """Test registering a model."""
        registry.register(sample_model)
        assert registry.has("test-model")

    def test_register_duplicate_raises(self, registry, sample_model):
        """Test duplicate registration raises error."""
        registry.register(sample_model)
        with pytest.raises(ModelAlreadyRegisteredError):
            registry.register(sample_model)

    def test_unregister(self, registry, sample_model):
        """Test unregistering a model."""
        registry.register(sample_model)
        result = registry.unregister("test-model")
        assert result is True
        assert not registry.has("test-model")

    def test_get(self, registry, sample_model):
        """Test getting a model."""
        registry.register(sample_model)
        retrieved = registry.get("test-model")
        assert retrieved.model_id == "test-model"

    def test_get_not_found_raises(self, registry):
        """Test getting non-existent model raises error."""
        with pytest.raises(ModelNotFoundError):
            registry.get("non-existent")

    def test_get_or_none(self, registry, sample_model):
        """Test getting model or None."""
        registry.register(sample_model)
        assert registry.get_or_none("test-model") is not None
        assert registry.get_or_none("non-existent") is None

    def test_list_all(self, registry, sample_model):
        """Test listing all models."""
        registry.register(sample_model)
        models = registry.list_all()
        assert len(models) == 1

    def test_list_by_provider(self, registry, sample_model):
        """Test listing by provider."""
        registry.register(sample_model)
        models = registry.list_by_provider("test-provider")
        assert len(models) == 1

    def test_list_by_category(self, registry, sample_model):
        """Test listing by category."""
        registry.register(sample_model)
        models = registry.list_by_category(ModelCategory.GENERAL)
        assert len(models) == 1

    def test_list_available(self, registry, sample_model):
        """Test listing available models."""
        registry.register(sample_model)
        models = registry.list_available()
        assert len(models) == 1

    def test_list_by_capability(self, registry, sample_model):
        """Test listing by capability."""
        sample_model.supports_reasoning = True
        registry.register(sample_model)
        models = registry.list_by_capability("reasoning")
        assert len(models) == 1

    def test_list_by_context_window(self, registry, sample_model):
        """Test listing by context window."""
        sample_model.context_window = 128000
        registry.register(sample_model)
        models = registry.list_by_context_window(64000)
        assert len(models) == 1

    def test_enable(self, registry, sample_model):
        """Test enabling a model."""
        registry.register(sample_model)
        result = registry.enable("test-model")
        assert result is True
        assert registry.get("test-model").state == ModelState.AVAILABLE

    def test_disable(self, registry, sample_model):
        """Test disabling a model."""
        registry.register(sample_model)
        result = registry.disable("test-model")
        assert result is True
        assert registry.get("test-model").state == ModelState.DISABLED

    def test_deprecate(self, registry, sample_model):
        """Test deprecating a model."""
        registry.register(sample_model)
        result = registry.deprecate("test-model")
        assert result is True
        assert registry.get("test-model").state == ModelState.DEPRECATED

    def test_register_from_catalog(self, registry):
        """Test registering from catalog."""
        count = registry.register_from_catalog()
        assert count > 0
        assert len(registry) > 0

    def test_find_best_fastest(self, registry):
        """Test finding best by latency."""
        m1 = ModelDescriptor(
            model_id="fast",
            provider_id="p1",
            display_name="Fast",
            latency_ms=100,
            state=ModelState.AVAILABLE,
        )
        m2 = ModelDescriptor(
            model_id="slow",
            provider_id="p1",
            display_name="Slow",
            latency_ms=500,
            state=ModelState.AVAILABLE,
        )
        registry.register(m1)
        registry.register(m2)

        best = registry.find_best(ModelSelectionPolicy.FASTEST)
        assert best.model_id == "fast"

    def test_find_best_cheapest(self, registry):
        """Test finding best by cost."""
        m1 = ModelDescriptor(
            model_id="cheap",
            provider_id="p1",
            display_name="Cheap",
            pricing=ModelPricing(cost_per_input_token=0.001),
            state=ModelState.AVAILABLE,
        )
        m2 = ModelDescriptor(
            model_id="expensive",
            provider_id="p1",
            display_name="Expensive",
            pricing=ModelPricing(cost_per_input_token=0.01),
            state=ModelState.AVAILABLE,
        )
        registry.register(m1)
        registry.register(m2)

        best = registry.find_best(ModelSelectionPolicy.CHEAPEST)
        assert best.model_id == "cheap"

    def test_find_best_longest_context(self, registry):
        """Test finding best by context window."""
        m1 = ModelDescriptor(
            model_id="small",
            provider_id="p1",
            display_name="Small",
            context_window=32000,
            state=ModelState.AVAILABLE,
        )
        m2 = ModelDescriptor(
            model_id="large",
            provider_id="p1",
            display_name="Large",
            context_window=128000,
            state=ModelState.AVAILABLE,
        )
        registry.register(m1)
        registry.register(m2)

        best = registry.find_best(ModelSelectionPolicy.LONGEST_CONTEXT)
        assert best.model_id == "large"

    def test_find_best_reasoning(self, registry):
        """Test finding best reasoning model."""
        m1 = ModelDescriptor(
            model_id="no-reasoning",
            provider_id="p1",
            display_name="No Reasoning",
            supports_reasoning=False,
            quality_score=0.9,
            state=ModelState.AVAILABLE,
        )
        m2 = ModelDescriptor(
            model_id="reasoning",
            provider_id="p1",
            display_name="Reasoning",
            supports_reasoning=True,
            quality_score=0.8,
            state=ModelState.AVAILABLE,
        )
        registry.register(m1)
        registry.register(m2)

        best = registry.find_best(ModelSelectionPolicy.REASONING)
        assert best.model_id == "reasoning"

    def test_event_handlers(self, registry, sample_model):
        """Test event handlers."""
        events = []

        def handler(data):
            events.append(data)

        registry.on("ModelRegistered", handler)
        registry.register(sample_model)

        assert len(events) == 1

    def test_clear(self, registry, sample_model):
        """Test clearing all registrations."""
        registry.register(sample_model)
        registry.clear()
        assert len(registry) == 0

    def test_len(self, registry, sample_model):
        """Test length."""
        assert len(registry) == 0
        registry.register(sample_model)
        assert len(registry) == 1

    def test_contains(self, registry, sample_model):
        """Test contains."""
        registry.register(sample_model)
        assert "test-model" in registry
        assert "non-existent" not in registry


class TestModelCatalog:
    """Tests for ModelCatalog."""

    def test_get_all_descriptors(self):
        """Test getting all descriptors."""
        descriptors = ModelCatalog.get_all_descriptors()
        assert len(descriptors) > 0

    def test_get_by_provider(self):
        """Test getting by provider."""
        openai_models = ModelCatalog.get_by_provider("openai")
        assert len(openai_models) > 0
        assert all(m.provider_id == "openai" for m in openai_models)

    def test_get_by_category(self):
        """Test getting by category."""
        reasoning_models = ModelCatalog.get_by_category(ModelCategory.REASONING)
        assert all(m.category == ModelCategory.REASONING for m in reasoning_models)

    def test_get_by_capability(self):
        """Test getting by capability."""
        reasoning_models = ModelCatalog.get_by_capability("reasoning")
        assert all(m.supports_reasoning for m in reasoning_models)

    def test_get_by_id(self):
        """Test getting by ID."""
        model = ModelCatalog.get_by_id("gpt-5-mini")
        assert model is not None
        assert model.model_id == "gpt-5-mini"


class TestModelSelector:
    """Tests for ModelSelector."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_model_registry()

    def test_select_default(self):
        """Test default selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(
            model_id="fast",
            provider_id="test",
            display_name="Fast",
            state=ModelState.AVAILABLE,
        )
        m2 = ModelDescriptor(
            model_id="slow",
            provider_id="test",
            display_name="Slow",
            state=ModelState.AVAILABLE,
        )
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry, "fast")
        selected = selector.select()
        assert selected.model_id == "fast"

    def test_select_fastest(self):
        """Test fastest selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="fast", provider_id="test", display_name="Fast",
                           latency_ms=100, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="slow", provider_id="test", display_name="Slow",
                           latency_ms=500, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.FASTEST)
        assert selected.model_id == "fast"

    def test_select_cheapest(self):
        """Test cheapest selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="cheap", provider_id="test", display_name="Cheap",
                           pricing=ModelPricing(cost_per_input_token=0.001), state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="expensive", provider_id="test", display_name="Expensive",
                           pricing=ModelPricing(cost_per_input_token=0.01), state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.CHEAPEST)
        assert selected.model_id == "cheap"

    def test_select_highest_quality(self):
        """Test highest quality selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="low", provider_id="test", display_name="Low",
                           quality_score=0.5, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="high", provider_id="test", display_name="High",
                           quality_score=0.95, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.HIGHEST_QUALITY)
        assert selected.model_id == "high"

    def test_select_longest_context(self):
        """Test longest context selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="small", provider_id="test", display_name="Small",
                           context_window=32000, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="large", provider_id="test", display_name="Large",
                           context_window=128000, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.LONGEST_CONTEXT)
        assert selected.model_id == "large"

    def test_select_reasoning(self):
        """Test reasoning selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="no-reasoning", provider_id="test", display_name="NoReasoning",
                           supports_reasoning=False, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="reasoning", provider_id="test", display_name="Reasoning",
                           supports_reasoning=True, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.REASONING)
        assert selected.model_id == "reasoning"

    def test_select_multimodal(self):
        """Test multimodal selection."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="text", provider_id="test", display_name="Text",
                           supports_multimodal=False, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="multi", provider_id="test", display_name="Multi",
                           supports_multimodal=True, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(ModelSelectionPolicy.MULTIMODAL)
        assert selected.model_id == "multi"

    def test_select_with_category(self):
        """Test selection with category filter."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="general", provider_id="test", display_name="General",
                           category=ModelCategory.GENERAL, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="medical", provider_id="test", display_name="Medical",
                           category=ModelCategory.MEDICAL, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(category=ModelCategory.MEDICAL)
        assert selected.model_id == "medical"

    def test_select_with_capabilities(self):
        """Test selection with capability filter."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="basic", provider_id="test", display_name="Basic",
                           supports_reasoning=False, state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="reasoning", provider_id="test", display_name="Reasoning",
                           supports_reasoning=True, state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(capabilities=["reasoning"])
        assert selected.model_id == "reasoning"

    def test_select_exclude_models(self):
        """Test selection with exclusion."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="fast", provider_id="test", display_name="Fast",
                           state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="slow", provider_id="test", display_name="Slow",
                           state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)

        selector = ModelSelector(registry)
        selected = selector.select(exclude_models=["fast"])
        assert selected.model_id == "slow"

    def test_select_multiple(self):
        """Test selecting multiple models."""
        from core.models import ModelSelector
        registry = ModelRegistry()
        
        m1 = ModelDescriptor(model_id="m1", provider_id="test", display_name="M1",
                           state=ModelState.AVAILABLE)
        m2 = ModelDescriptor(model_id="m2", provider_id="test", display_name="M2",
                           state=ModelState.AVAILABLE)
        m3 = ModelDescriptor(model_id="m3", provider_id="test", display_name="M3",
                           state=ModelState.AVAILABLE)
        registry.register(m1)
        registry.register(m2)
        registry.register(m3)

        selector = ModelSelector(registry)
        selected = selector.select_multiple(2)
        assert len(selected) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
