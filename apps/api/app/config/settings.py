"""Application settings loaded from the environment (Pydantic v2 / pydantic-settings).

All settings can be overridden with environment variables prefixed with
``EREN_API_`` (e.g. ``EREN_API_DEBUG=true``) or via a local ``.env`` file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration. Extend as the backend grows."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EREN_API_",
        extra="ignore",
        case_sensitive=False,
    )

    # --- General ---
    app_name: str = "EREN API"
    environment: str = "development"
    debug: bool = False

    # --- HTTP / API ---
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # --- Persistence ---
    # Async driver URL used by the app (SQLAlchemy async engine).
    database_url: str = "sqlite+aiosqlite:///./eren_api.db"

    @property
    def database_url_sync(self) -> str:
        """Synchronous URL for tools that don't support async drivers (e.g. Alembic)."""
        return self.database_url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg")


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (import-safe, single source of truth)."""
    return Settings()
