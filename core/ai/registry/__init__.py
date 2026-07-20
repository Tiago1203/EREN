"""Model Registry - Registro de modelos de IA."""

from __future__ import annotations

from threading import RLock

from core.ai.contracts import ModelRegistry as ModelRegistryContract
from core.ai.dto import ModelCapabilities, ModelInfo
from core.ai.exceptions import AIModelNotFoundError


class ModelRegistry(ModelRegistryContract):
    """
    Registro de modelos de IA.
    
    Gestiona el registro, descubrimiento y selección de modelos
    disponibles en el AI Core.
    """

    def __init__(self, default_model: str | None = None) -> None:
        self._models: dict[str, ModelInfo] = {}
        self._default_model: str | None = default_model
        self._lock = RLock()

    def register_model(self, model: ModelInfo) -> None:
        """Registra un nuevo modelo."""
        with self._lock:
            self._models[model.id] = model
            # Auto-set as default if no default exists
            if self._default_model is None:
                self._default_model = model.id

    def unregister_model(self, model_id: str) -> bool:
        """Elimina un modelo del registro."""
        with self._lock:
            if model_id in self._models:
                del self._models[model_id]
                if self._default_model == model_id:
                    # Set new default if current was removed
                    self._default_model = next(iter(self._models), None)
                return True
            return False

    def get_model(self, model_id: str) -> ModelInfo | None:
        """Obtiene información de un modelo."""
        with self._lock:
            return self._models.get(model_id)

    def list_models(self, provider: str | None = None) -> list[ModelInfo]:
        """Lista todos los modelos, opcionalmente filtrados por proveedor."""
        with self._lock:
            models = list(self._models.values())
            if provider:
                models = [m for m in models if m.provider == provider]
            return models

    def find_models(
        self,
        capability: str | None = None,
        max_tokens: int | None = None,
    ) -> list[ModelInfo]:
        """Encuentra modelos que cumplan ciertos criterios."""
        with self._lock:
            models = list(self._models.values())

            if capability:
                if capability == "functions":
                    models = [m for m in models if m.supports_functions]
                elif capability == "vision":
                    models = [m for m in models if m.supports_vision]
                elif capability == "streaming":
                    models = [m for m in models if m.supports_streaming]

            if max_tokens is not None:
                models = [m for m in models if m.max_tokens >= max_tokens]

            return models

    def get_default_model(self) -> ModelInfo | None:
        """Obtiene el modelo por defecto."""
        with self._lock:
            if self._default_model:
                return self._models.get(self._default_model)
            return None

    def set_default_model(self, model_id: str) -> None:
        """Establece el modelo por defecto."""
        with self._lock:
            if model_id not in self._models:
                raise AIModelNotFoundError(model_id)
            self._default_model = model_id

    def get_capabilities(self, model_id: str) -> ModelCapabilities | None:
        """Obtiene las capacidades de un modelo."""
        model = self.get_model(model_id)
        if model is None:
            return None

        return ModelCapabilities(
            supports_functions=model.supports_functions,
            supports_vision=model.supports_vision,
            supports_streaming=model.supports_streaming,
            max_context_tokens=model.max_tokens,
            max_output_tokens=model.max_tokens,
        )

    def clear(self) -> None:
        """Limpia todos los modelos registrados."""
        with self._lock:
            self._models.clear()
            self._default_model = None


# ============== Provider Registry ==============

class ProviderRegistry:
    """
    Registro de proveedores de IA.
    
    Gestiona los proveedores disponibles y su selección.
    """

    def __init__(self) -> None:
        self._providers: dict[str, type] = {}
        self._instances: dict[str, object] = {}
        self._lock = RLock()

    def register_provider(self, provider_id: str, provider_class: type) -> None:
        """Registra una clase de proveedor."""
        with self._lock:
            self._providers[provider_id] = provider_class

    def unregister_provider(self, provider_id: str) -> bool:
        """Elimina un proveedor registrado."""
        with self._lock:
            if provider_id in self._providers:
                del self._providers[provider_id]
                if provider_id in self._instances:
                    del self._instances[provider_id]
                return True
            return False

    def get_provider_class(self, provider_id: str) -> type | None:
        """Obtiene la clase de un proveedor."""
        with self._lock:
            return self._providers.get(provider_id)

    def list_providers(self) -> list[str]:
        """Lista todos los proveedores registrados."""
        with self._lock:
            return list(self._providers.keys())

    def clear(self) -> None:
        """Limpia todos los proveedores registrados."""
        with self._lock:
            self._providers.clear()
            self._instances.clear()
