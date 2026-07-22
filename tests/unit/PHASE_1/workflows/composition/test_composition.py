"""Tests for the Cognitive Composition Root."""

from core.composition import (
    CognitiveCompositionRoot,
    CompositionRootFactory,
    CompositionBuilder,
    ModuleDescriptor,
    ModuleRegistry,
    ModuleLoader,
    ModuleAlreadyRegisteredException,
)


class TestCompositionRoot:
    """Tests for CognitiveCompositionRoot."""

    def test_root_creation(self):
        root = CognitiveCompositionRoot()
        assert root is not None
        assert root.id is not None
        assert not root.is_built

    def test_with_default_modules(self):
        root = CognitiveCompositionRoot().with_default_modules()
        assert root is not None

    def test_build(self):
        root = CognitiveCompositionRoot().with_default_modules()
        runtime = root.build()
        assert root.is_built
        assert runtime is not None

    def test_module_count(self):
        root = CognitiveCompositionRoot().with_default_modules()
        runtime = root.build()
        assert runtime["module_count"] == 14

    def test_load_order(self):
        root = CognitiveCompositionRoot().with_default_modules()
        runtime = root.build()
        order = runtime["load_order"]
        assert "EventBusModule" in order
        assert "OrchestratorModule" in order


class TestCompositionBuilder:
    """Tests for CompositionBuilder."""

    def test_builder_creation(self):
        builder = CompositionBuilder()
        assert builder is not None

    def test_add_module(self):
        builder = CompositionBuilder()
        module = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        builder.add_module(module)
        assert builder.get_registry().is_registered("TestModule")

    def test_add_default_modules(self):
        builder = CompositionBuilder()
        builder.add_default_modules()
        assert builder.get_registry().module_count == 14

    def test_build(self):
        builder = CompositionBuilder()
        builder.add_default_modules()
        result = builder.build()
        assert result is not None
        assert result["module_count"] == 14


class TestModuleRegistry:
    """Tests for ModuleRegistry."""

    def test_registry_creation(self):
        registry = ModuleRegistry()
        assert registry is not None

    def test_register_module(self):
        registry = ModuleRegistry()
        module = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        registry.register(module)
        assert registry.is_registered("TestModule")

    def test_unregister_module(self):
        registry = ModuleRegistry()
        module = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        registry.register(module)
        registry.unregister("TestModule")
        assert not registry.is_registered("TestModule")

    def test_module_count(self):
        registry = ModuleRegistry()
        module1 = ModuleDescriptor(module_name="Module1")
        module2 = ModuleDescriptor(module_name="Module2")
        registry.register(module1)
        registry.register(module2)
        assert registry.module_count == 2


class TestModuleLoader:
    """Tests for ModuleLoader."""

    def test_loader_creation(self):
        registry = ModuleRegistry()
        loader = ModuleLoader(registry)
        assert loader is not None

    def test_load_module(self):
        registry = ModuleRegistry()
        loader = ModuleLoader(registry)
        module = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        registry.register(module)
        result = loader.load(module)
        assert result is True

    def test_load_order(self):
        registry = ModuleRegistry()
        loader = ModuleLoader(registry)
        module = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        registry.register(module)
        loader.load(module)
        assert "TestModule" in loader.get_load_order()


class TestModuleDescriptor:
    """Tests for ModuleDescriptor."""

    def test_descriptor_creation(self):
        desc = ModuleDescriptor(
            module_name="TestModule",
            module_type="core",
        )
        assert desc.module_name == "TestModule"
        assert desc.module_type == "core"

    def test_add_dependency(self):
        desc = ModuleDescriptor(module_name="TestModule")
        desc.add_dependency("DepModule")
        assert len(desc.dependencies) == 1

    def test_add_contract(self):
        desc = ModuleDescriptor(module_name="TestModule")
        desc.add_contract("IContract", dict)
        assert len(desc.contracts) == 1


class TestCompositionFactory:
    """Tests for CompositionRootFactory."""

    def test_create_default(self):
        root = CompositionRootFactory.create_default()
        assert root is not None

    def test_create_builder(self):
        builder = CompositionRootFactory.create_builder()
        assert builder is not None


if __name__ == "__main__":
    print("Running composition tests...")
    
    # Test CompositionRoot
    tc = TestCompositionRoot()
    tc.test_root_creation()
    tc.test_with_default_modules()
    tc.test_build()
    tc.test_module_count()
    tc.test_load_order()
    print("TestCompositionRoot: PASSED")
    
    # Test Builder
    tb = TestCompositionBuilder()
    tb.test_builder_creation()
    tb.test_add_module()
    tb.test_add_default_modules()
    tb.test_build()
    print("TestCompositionBuilder: PASSED")
    
    # Test Registry
    tr = TestModuleRegistry()
    tr.test_registry_creation()
    tr.test_register_module()
    tr.test_unregister_module()
    tr.test_module_count()
    print("TestModuleRegistry: PASSED")
    
    # Test Loader
    tl = TestModuleLoader()
    tl.test_loader_creation()
    tl.test_load_module()
    tl.test_load_order()
    print("TestModuleLoader: PASSED")
    
    # Test Descriptor
    td = TestModuleDescriptor()
    td.test_descriptor_creation()
    td.test_add_dependency()
    td.test_add_contract()
    print("TestModuleDescriptor: PASSED")
    
    # Test Factory
    tf = TestCompositionFactory()
    tf.test_create_default()
    tf.test_create_builder()
    print("TestCompositionFactory: PASSED")
    
    print("")
    print("=== All 20 tests passed! ===")
