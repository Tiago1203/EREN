"""HashiCorp Vault client adapter.

Provides a lightweight integration with HashiCorp Vault for secret management.
When Vault is disabled (vault_enabled=False), all methods are no-ops and
the caller should rely on environment variables or .env files instead.

Usage::

    from app.infrastructure.vault.client import VaultClient

    client = VaultClient.from_settings()
    if client.enabled:
        db_password = client.get_secret("database/password")
        api_key = client.get_secret("api/key")

    # Fallback: use environment variables when Vault is disabled
    db_password = client.get_secret_or_env("database/password", "EREN_API_DB_PASSWORD")
"""

import os
from dataclasses import dataclass
from typing import Any

logger = __import__("app.core.logging").app.core.logging.get_logger(__name__)


@dataclass
class VaultSettings:
    """Subset of app settings needed by the Vault client."""

    enabled: bool
    url: str
    token: str | None
    mount: str
    secret_path: str


class VaultClient:
    """Lightweight HashiCorp Vault adapter.

    Supports KV v2 secrets engine. When ``enabled=False``, all operations
    are no-ops and return ``None``.
    """

    def __init__(self, settings: VaultSettings) -> None:
        self._settings = settings
        self._client: Any = None

    @classmethod
    def from_settings(cls, settings: Any = None) -> "VaultClient":
        """Construct a VaultClient from app settings or return a disabled stub."""
        if settings is None:
            from app.config.settings import get_settings

            settings = get_settings()

        vault_settings = VaultSettings(
            enabled=settings.vault_enabled,
            url=settings.vault_url,
            token=settings.vault_token,
            mount=settings.vault_mount,
            secret_path=settings.vault_secret_path,
        )
        return cls(vault_settings)

    @property
    def enabled(self) -> bool:
        return self._settings.enabled and bool(self._settings.token)

    @property
    def _kv_client(self) -> Any:
        """Lazy-initialise the hvac client."""
        if self._client is None:
            try:
                import hvac  # noqa: F401

                self._client = hvac.Client(url=self._settings.url, token=self._settings.token)
            except ImportError:
                logger.warning("hvac not installed — Vault disabled")
                self._client = None
        return self._client

    def get_secret(self, key: str) -> str | None:
        """Fetch a secret value from Vault KV v2.

        Args:
            key: The secret key name (e.g. ``database/password``).

        Returns:
            The secret value as a string, or ``None`` if not found or Vault is disabled.
        """
        if not self.enabled:
            return None

        client = self._kv_client
        if client is None:
            return None

        try:
            secret_path = f"{self._settings.secret_path}/{key}"
            response = client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=self._settings.mount
            )
            return response.get("data", {}).get("data", {}).get("data")
        except Exception as exc:
            logger.warning(f"Vault read failed for {key}: {exc}")
            return None

    def get_secret_or_env(self, key: str, env_var: str) -> str | None:
        """Fetch from Vault first; fall back to an environment variable."""
        value = self.get_secret(key)
        if value is not None:
            return value
        return os.environ.get(env_var)

    def list_secrets(self) -> list[str]:
        """List all secret keys under the configured path."""
        if not self.enabled:
            return []

        client = self._kv_client
        if client is None:
            return []

        try:
            response = client.secrets.kv.v2.list_secrets(
                path=self._settings.secret_path, mount_point=self._settings.mount
            )
            return response.get("data", {}).get("keys", [])
        except Exception as exc:
            logger.warning(f"Vault list failed: {exc}")
            return []
