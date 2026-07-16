"""Alembic migration environment.

Uses the application's settings and ORM metadata so migrations stay in sync with
``app.models`` and ``app.infrastructure.models``. A synchronous database URL is
derived from the app config so Alembic works even though the app itself uses an
async driver.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import models so every table is registered on Base.metadata for autogenerate.
import app.models  # noqa: F401
import app.infrastructure.models  # noqa: F401
from app.config.settings import get_settings
from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url_sync)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DBAPI connection (emit SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
