"""AI Dependency Injection - Inyección de dependencias del AI Core."""

from __future__ import annotations

from threading import RLock
from typing import Any, Callable, TypeVar

from core.ai.contracts import Container, Scope
from core.ai.exceptions import AIInjectionError

T = TypeVar("T")


class Dependency:
    """Representa una dependencia registrada."""

    def __init__(
        self,
        interface: type,
        factory: Callable[[], Any],
        *,
        singleton: bool = True,
    ) -> None:
        self.interface = interface
        self.factory = factory
        self.singleton = singleton
        self.instance: Any = None
        self._lock = RLock()


class ScopeImpl(Scope):
    """Implementación de Scope para inyección de dependencias."""

    def __init__(self, container: ContainerImpl) -> None:
        self._container = container
        self._instances: dict[type, Any] = {}

    def resolve(self, interface: type) -> Any:
        """Resuelve una dependencia en este scope."""
        if interface in self._instances:
            return self._instances[interface]

        instance = self._container._resolve_internal(interface)
        self._instances[interface] = instance
        return instance

    def close(self) -> None:
        """Cierra el scope y limpia recursos."""
        self._instances.clear()


class ContainerImpl(Container):
    """
    Contenedor de inyección de dependencias.
    
    Gestiona el registro y resolución de dependencias del AI Core.
    """

    def __init__(self) -> None:
        self._dependencies: dict[type, Dependency] = {}
        self._lock = RLock()

    def register(
        self,
        interface: type,
        implementation: type | Any,
        *,
        singleton: bool = True,
        **kwargs,
    ) -> None:
        """
        Registra una dependencia.
        
        Args:
            interface: Tipo de la interfaz/contrato
            implementation: Clase o callable que crea la implementación
            singleton: Si True, usa la misma instancia para todas las resoluciones
            **kwargs: Argumentos adicionales para pasar al factory
        """
        with self._lock:
            if isinstance(implementation, type):
                # It's a class, create a factory
                def factory() -> Any:
                    return implementation(**kwargs)
            else:
                # It's already an instance or callable
                factory = lambda: implementation

            self._dependencies[interface] = Dependency(
                interface=interface,
                factory=factory,
                singleton=singleton,
            )

    def register_instance(
        self,
        interface: type,
        instance: Any,
    ) -> None:
        """Registra una instancia existente."""
        with self._lock:
            self._dependencies[interface] = Dependency(
                interface=interface,
                factory=lambda: instance,
                singleton=True,
            )
            # Store the instance directly
            self._dependencies[interface].instance = instance

    def unregister(self, interface: type) -> bool:
        """Elimina una dependencia registrada."""
        with self._lock:
            if interface in self._dependencies:
                del self._dependencies[interface]
                return True
            return False

    def resolve(self, interface: type) -> Any:
        """Resuelve una dependencia."""
        return self._resolve_internal(interface)

    def resolve_optional(self, interface: type, default: Any = None) -> Any:
        """Resuelve una dependencia opcional."""
        try:
            return self.resolve(interface)
        except AIInjectionError:
            return default

    def create_scope(self) -> Scope:
        """Crea un nuevo scope para dependencias."""
        return ScopeImpl(self)

    def clear(self) -> None:
        """Limpia todas las dependencias registradas."""
        with self._lock:
            self._dependencies.clear()

    def _resolve_internal(self, interface: type) -> Any:
        """Resuelve una dependencia internamente (sin locks adicionales)."""
        with self._lock:
            if interface not in self._dependencies:
                raise AIInjectionError(
                    f"Dependency not registered: {interface}",
                    dependency=str(interface),
                )

            dep = self._dependencies[interface]

            # Return cached instance for singletons
            if dep.singleton and dep.instance is not None:
                return dep.instance

            # Create new instance
            try:
                instance = dep.factory()
            except Exception as e:
                raise AIInjectionError(
                    f"Failed to create instance for {interface}: {e}",
                    dependency=str(interface),
                )

            # Cache if singleton
            if dep.singleton:
                dep.instance = instance

            return instance

    def has(self, interface: type) -> bool:
        """Verifica si una dependencia está registrada."""
        with self._lock:
            return interface in self._dependencies

    def list_registered(self) -> list[type]:
        """Lista todas las interfaces registradas."""
        with self._lock:
            return list(self._dependencies.keys())


# ============== Decorators ==============

def injectable(
    interface: type | None = None,
    *,
    singleton: bool = True,
) -> Callable[[type], type]:
    """
    Decorador para marcar una clase como inyectable.
    
    Usage:
        @injectable(MyInterface)
        class MyImplementation:
            ...
    """
    def decorator(cls: type) -> type:
        # The registration should be done by the container
        # This is just a marker for documentation/inspection
        cls._injectable = True  # type: ignore
        cls._injectable_interface = interface  # type: ignore
        cls._injectable_singleton = singleton  # type: ignore
        return cls

    return decorator


def inject(interface: type[T]) -> Callable[[T], T]:
    """
    Decorador para inyección en __init__.
    
    Usage:
        class MyService:
            def __init__(self, other: Injected[OtherService]):
                self.other = other
    """
    class Injected:
        def __init__(self, original_cls: type[T]) -> type[T]:
            return original_cls

    return Injected


# ============== Auto-registration ==============

class AutoContainer(ContainerImpl):
    """
    Contenedor con auto-registro de dependencias.
    
    Escanea módulos y registra automáticamente clases marcadas
    con @injectable.
    """

    def auto_register(self, module_path: str) -> None:
        """
        Auto-registra todas las clases marcadas con @injectable
        en el módulo especificado.
        """
        import importlib

        try:
            module = importlib.import_module(module_path)

            for name in dir(module):
                obj = getattr(module, name)

                if isinstance(obj, type) and hasattr(obj, "_injectable"):
                    interface = getattr(obj, "_injectable_interface", obj)
                    singleton = getattr(obj, "_injectable_singleton", True)

                    self.register(
                        interface=interface,
                        implementation=obj,
                        singleton=singleton,
                    )

        except ImportError as e:
            raise AIInjectionError(
                f"Failed to import module for auto-registration: {e}",
                dependency=module_path,
            )


# ============== Global Container ==============

_container: ContainerImpl | None = None


def get_container() -> ContainerImpl:
    """Obtiene o crea el contenedor global de DI."""
    global _container
    if _container is None:
        _container = ContainerImpl()
    return _container


def set_container(container: ContainerImpl) -> None:
    """Establece el contenedor global de DI."""
    global _container
    _container = container


def reset_container() -> None:
    """Resetea el contenedor global de DI."""
    global _container
    if _container is not None:
        _container.clear()
    _container = None
