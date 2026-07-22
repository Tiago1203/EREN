"""Tests for the Cognitive Dependency Injection Container."""

from core.PHASE_1.infrastructure.container import (
    CognitiveContainer,
    ContainerFactory,
    ContainerBuilder,
    ServiceLifetime,
    ServiceRegistry,
    ServiceDescriptor,
    DependencyGraph,
    DependencyValidator,
    ServiceScope,
    ScopeType,
    ServiceFactory,
    ServiceNotFoundException,
    CircularDependencyException,
    ValidationException,
    ContainerDisposedException,
)


class TestServiceLifetime:
    """Tests for service lifetimes."""

    def test_all_lifetimes_defined(self):
        assert ServiceLifetime.SINGLETON
        assert ServiceLifetime.LAZY_SINGLETON
        assert ServiceLifetime.WEAK_SINGLETON
        assert ServiceLifetime.SCOPED
        assert ServiceLifetime.TRANSIENT
        assert ServiceLifetime.FACTORY

    def test_is_valid(self):
        assert ServiceLifetime.is_valid(ServiceLifetime.SINGLETON)
        assert not ServiceLifetime.is_valid("invalid")

    def test_requires_instance_storage(self):
        assert ServiceLifetime.requires_instance_storage(ServiceLifetime.SINGLETON)
        assert ServiceLifetime.requires_instance_storage(ServiceLifetime.SCOPED)
        assert not ServiceLifetime.requires_instance_storage(ServiceLifetime.TRANSIENT)


class TestContainer:
    """Tests for CognitiveContainer."""

    def test_container_creation(self):
        container = CognitiveContainer()
        assert container is not None
        assert container.id is not None
        assert not container.is_disposed

    def test_register_singleton(self):
        container = CognitiveContainer()
        container.register('TestContract', dict, lifetime=ServiceLifetime.SINGLETON)
        assert container.get_metrics()['services_registered'] == 1

    def test_resolve_singleton(self):
        container = CognitiveContainer()
        container.register('TestContract', dict, lifetime=ServiceLifetime.SINGLETON)
        
        instance1 = container.resolve('TestContract')
        instance2 = container.resolve('TestContract')
        
        assert instance1 is instance2

    def test_resolve_transient(self):
        container = CognitiveContainer()
        container.register('TestContract', dict, lifetime=ServiceLifetime.TRANSIENT)
        
        instance1 = container.resolve('TestContract')
        instance2 = container.resolve('TestContract')
        
        assert instance1 is not instance2

    def test_try_resolve(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        
        result = container.try_resolve('TestContract')
        assert result is not None
        
        result = container.try_resolve('NonExistent')
        assert result is None

    def test_service_not_found_exception(self):
        container = CognitiveContainer()
        try:
            container.resolve('NonExistent')
            assert False, "Should have raised"
        except ServiceNotFoundException:
            pass

    def test_disposed_exception(self):
        container = CognitiveContainer()
        container.dispose()
        
        try:
            container.resolve('TestContract')
            assert False, "Should have raised"
        except ContainerDisposedException:
            pass

    def test_dispose(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        container.dispose()
        assert container.is_disposed


class TestContainerBuilder:
    """Tests for ContainerBuilder."""

    def test_builder_creation(self):
        builder = ContainerFactory.create_builder()
        assert builder is not None

    def test_register_singleton(self):
        builder = ContainerFactory.create_builder()
        builder.register_singleton('TestContract', dict)
        assert builder.get_registry().registration_count == 1

    def test_register_scoped(self):
        builder = ContainerFactory.create_builder()
        builder.register_scoped('TestContract', dict)
        assert builder.get_registry().registration_count == 1

    def test_register_transient(self):
        builder = ContainerFactory.create_builder()
        builder.register_transient('TestContract', dict)
        assert builder.get_registry().registration_count == 1


class TestServiceRegistry:
    """Tests for ServiceRegistry."""

    def test_registry_creation(self):
        registry = ServiceRegistry()
        assert registry is not None

    def test_register(self):
        registry = ServiceRegistry()
        registry.register('TestContract', dict, ServiceLifetime.SINGLETON)
        assert registry.is_registered('TestContract')

    def test_unregister(self):
        registry = ServiceRegistry()
        registry.register('TestContract', dict)
        registry.unregister('TestContract')
        assert not registry.is_registered('TestContract')


class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_graph_creation(self):
        graph = DependencyGraph()
        assert graph is not None

    def test_add_node(self):
        graph = DependencyGraph()
        graph.add_node('A', 'AImpl', ['B'])
        assert 'A' in graph.get_all_contracts()

    def test_find_roots(self):
        graph = DependencyGraph()
        graph.add_node('A', 'AImpl', ['B'])
        graph.add_node('B', 'BImpl')
        
        roots = graph.find_roots()
        assert 'B' in roots

    def test_find_leaves(self):
        graph = DependencyGraph()
        graph.add_node('A', 'AImpl', ['B'])
        graph.add_node('B', 'BImpl')
        
        leaves = graph.find_leaves()
        assert 'B' in leaves


class TestDependencyValidator:
    """Tests for DependencyValidator."""

    def test_validator_creation(self):
        registry = ServiceRegistry()
        graph = DependencyGraph()
        validator = DependencyValidator(registry, graph)
        assert validator is not None

    def test_validate_no_dependencies(self):
        registry = ServiceRegistry()
        graph = DependencyGraph()
        validator = DependencyValidator(registry, graph)
        
        registry.register('A', dict)
        
        result = validator.validate()
        assert result.is_valid

    def test_validate_with_dependencies(self):
        registry = ServiceRegistry()
        graph = DependencyGraph()
        validator = DependencyValidator(registry, graph)
        
        registry.register('A', dict)
        registry.register('B', dict, dependencies=['A'])
        
        result = validator.validate()
        assert result.is_valid

    def test_validate_orphan(self):
        registry = ServiceRegistry()
        graph = DependencyGraph()
        validator = DependencyValidator(registry, graph)
        
        registry.register('A', dict, dependencies=['B'])
        
        result = validator.validate()
        assert not result.is_valid
        assert len(result.errors) > 0


class TestServiceScope:
    """Tests for ServiceScope."""

    def test_scope_creation(self):
        scope = ServiceScope('test', ScopeType.SESSION)
        assert scope is not None
        assert scope.scope_id == 'test'
        assert scope.scope_type == ScopeType.SESSION

    def test_create_child(self):
        parent = ServiceScope('parent', ScopeType.APPLICATION)
        child = parent.create_child(ScopeType.SESSION, 'child')
        
        assert child in parent.children
        assert child.parent is parent

    def test_dispose(self):
        scope = ServiceScope('test', ScopeType.SESSION)
        scope.dispose()
        assert scope.is_disposed


class TestMetrics:
    """Tests for container metrics."""

    def test_metrics_after_registration(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        
        metrics = container.get_metrics()
        assert metrics['services_registered'] == 1

    def test_metrics_after_resolution(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        container.resolve('TestContract')
        
        metrics = container.get_metrics()
        assert metrics['services_resolved'] >= 1


class TestTracing:
    """Tests for container tracing."""

    def test_trace_after_registration(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        
        traces = container.get_trace()
        assert len(traces) > 0

    def test_trace_after_resolution(self):
        container = CognitiveContainer()
        container.register('TestContract', dict)
        container.resolve('TestContract')
        
        traces = container.get_trace()
        resolve_traces = [t for t in traces if t.operation == 'resolve']
        assert len(resolve_traces) > 0
