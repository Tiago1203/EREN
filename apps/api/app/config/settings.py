"""Application settings loaded from the environment (Pydantic v2 / pydantic-settings).

All settings can be overridden with environment variables prefixed with
``EREN_API_`` (e.g. ``EREN_API_DEBUG=true``) or via a local ``.env`` file.
"""

from functools import lru_cache

from pydantic import Field
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
    database_url: str = Field(
        default="postgresql+asyncpg://eren:eren@localhost:5432/eren",
        description="Async PostgreSQL connection string (use sqlite+aiosqlite for local dev)",
    )

    @property
    def database_url_sync(self) -> str:
        """Synchronous URL for tools that don't support async drivers (e.g. Alembic)."""
        return self.database_url.replace("+asyncpg", "+psycopg2").replace("+aiosqlite", "")

    # --- Redis ---
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for caching",
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="Default cache TTL in seconds",
    )

    # --- RabbitMQ ---
    rabbitmq_url: str = Field(
        default="amqp://eren:eren@localhost:5672/",
        description="RabbitMQ AMQP URL for event messaging",
    )

    # --- Supabase ---
    supabase_url: str = "http://localhost:54321"
    supabase_anon_key: str = "your-anon-key"
    supabase_service_role_key: str | None = None

    # --- Observability ---
    otel_endpoint: str | None = Field(
        default=None,
        description="OpenTelemetry Collector endpoint (e.g. http://localhost:4317)",
    )
    service_name: str = "eren-api"


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (import-safe, single source of truth)."""
    return Settings()
