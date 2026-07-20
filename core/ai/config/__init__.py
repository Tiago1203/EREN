"""AI Configuration - Configuración del AI Core."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from core.ai.contracts import AIConfiguration
from core.ai.dto import AIConfig, ProviderConfig
from core.ai.exceptions import AIConfigurationError


class FileAIConfiguration(AIConfiguration):
    """
    Configuración del AI Core basada en archivos.
    
    Lee y escribe configuración desde archivos YAML.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config: AIConfig = AIConfig()
        self._config_path = Path(config_path) if config_path else None
        self._provider_configs: dict[str, ProviderConfig] = {}
        self._model_configs: dict[str, dict[str, Any]] = {}

        if self._config_path and self._config_path.exists():
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Carga configuración desde archivo."""
        try:
            with open(self._config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            # Load AI Config
            if "ai" in data:
                ai_config = data["ai"]
                self._config.default_provider = ai_config.get("default_provider", "openai")
                self._config.default_model = ai_config.get("default_model", "gpt-4")
                self._config.temperature = ai_config.get("temperature", 0.7)
                self._config.max_tokens = ai_config.get("max_tokens")
                self._config.timeout = ai_config.get("timeout", 60)
                self._config.max_retries = ai_config.get("max_retries", 3)
                self._config.features = ai_config.get("features", {})

            # Load Provider Configs
            if "providers" in data:
                for provider_id, provider_data in data["providers"].items():
                    self._provider_configs[provider_id] = ProviderConfig(
                        provider_id=provider_id,
                        api_key=provider_data.get("api_key"),
                        base_url=provider_data.get("base_url"),
                        organization=provider_data.get("organization"),
                        default_model=provider_data.get("default_model"),
                        timeout=provider_data.get("timeout", 60),
                        max_retries=provider_data.get("max_retries", 3),
                        headers=provider_data.get("headers", {}),
                    )

            # Load Model Configs
            if "models" in data:
                self._model_configs = data["models"]

        except Exception as e:
            raise AIConfigurationError(f"Failed to load config: {e}")

    def _save_to_file(self) -> None:
        """Guarda configuración a archivo."""
        if not self._config_path:
            return

        data = {
            "ai": {
                "default_provider": self._config.default_provider,
                "default_model": self._config.default_model,
                "temperature": self._config.temperature,
                "max_tokens": self._config.max_tokens,
                "timeout": self._config.timeout,
                "max_retries": self._config.max_retries,
                "features": self._config.features,
            },
            "providers": {},
            "models": self._model_configs,
        }

        for provider_id, config in self._provider_configs.items():
            data["providers"][provider_id] = {
                "api_key": config.api_key,
                "base_url": config.base_url,
                "organization": config.organization,
                "default_model": config.default_model,
                "timeout": config.timeout,
                "max_retries": config.max_retries,
                "headers": config.headers,
            }

        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        parts = key.split(".")
        value = self._config

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict):
                value = value.get(part)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Establece un valor de configuración."""
        parts = key.split(".")
        obj = self._config

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict):
                obj = obj[part]
            else:
                raise AIConfigurationError(f"Cannot set {key}: invalid path")

        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise AIConfigurationError(f"Cannot set {key}: invalid key")

        # Save to file if path is set
        self._save_to_file()

    def get_provider_config(self, provider_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un proveedor."""
        config = self._provider_configs.get(provider_id)
        if config is None:
            return None

        return {
            "provider_id": config.provider_id,
            "api_key": config.api_key,
            "base_url": config.base_url,
            "organization": config.organization,
            "default_model": config.default_model,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "headers": config.headers,
            "metadata": config.metadata,
        }

    def set_provider_config(self, provider_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un proveedor."""
        self._provider_configs[provider_id] = ProviderConfig(
            provider_id=provider_id,
            **{k: v for k, v in config.items() if k != "provider_id"},
        )
        self._save_to_file()

    def get_model_config(self, model_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un modelo."""
        return self._model_configs.get(model_id)

    def set_model_config(self, model_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un modelo."""
        self._model_configs[model_id] = config
        self._save_to_file()

    def validate(self) -> list[str]:
        """Valida la configuración y retorna errores."""
        errors = []

        # Validate providers
        for provider_id, config in self._provider_configs.items():
            if not config.api_key:
                errors.append(f"Provider '{provider_id}': missing API key")

        # Validate default model
        default_model = self._config.default_model
        if default_model and default_model not in self._model_configs:
            # This is not necessarily an error, model may be in registry
            pass

        # Validate features
        if not isinstance(self._config.features, dict):
            errors.append("features must be a dictionary")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "ai": {
                "default_provider": self._config.default_provider,
                "default_model": self._config.default_model,
                "temperature": self._config.temperature,
                "max_tokens": self._config.max_tokens,
                "timeout": self._config.timeout,
                "max_retries": self._config.max_retries,
                "features": self._config.features,
            },
            "providers": {
                pid: self.get_provider_config(pid)
                for pid in self._provider_configs
            },
            "models": self._model_configs,
        }


class DictAIConfiguration(AIConfiguration):
    """
    Configuración del AI Core basada en diccionario.
    
    Útil para configuración programática.
    """

    def __init__(self, initial_config: dict[str, Any] | None = None) -> None:
        self._config: dict[str, Any] = initial_config or {}
        self._provider_configs: dict[str, dict[str, Any]] = {}
        self._model_configs: dict[str, dict[str, Any]] = {}

        # Initialize from initial config
        if initial_config:
            if "providers" in initial_config:
                self._provider_configs = initial_config["providers"]
            if "models" in initial_config:
                self._model_configs = initial_config["models"]

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Establece un valor de configuración."""
        parts = key.split(".")
        obj = self._config

        for part in parts[:-1]:
            if part not in obj:
                obj[part] = {}
            obj = obj[part]

        obj[parts[-1]] = value

    def get_provider_config(self, provider_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un proveedor."""
        return self._provider_configs.get(provider_id)

    def set_provider_config(self, provider_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un proveedor."""
        self._provider_configs[provider_id] = config

    def get_model_config(self, model_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un modelo."""
        return self._model_configs.get(model_id)

    def set_model_config(self, model_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un modelo."""
        self._model_configs[model_id] = config

    def validate(self) -> list[str]:
        """Valida la configuración y retorna errores."""
        errors = []

        # Validate providers have API keys
        for provider_id, config in self._provider_configs.items():
            if not config.get("api_key"):
                errors.append(f"Provider '{provider_id}': missing API key")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            **self._config,
            "providers": self._provider_configs,
            "models": self._model_configs,
        }
