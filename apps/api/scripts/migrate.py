#!/usr/bin/env python3
"""Run Alembic database migrations.

Usage::

    python scripts/migrate.py --help
    python scripts/migrate.py upgrade --sql      # show SQL without applying
    python scripts/migrate.py upgrade            # apply all migrations
    python scripts/migrate.py downgrade -1        # roll back one revision

Environment::

    EREN_API_DATABASE_URL  # PostgreSQL connection string (default: postgresql+psycopg2://eren:eren@localhost:5432/eren)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the app package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import CommandLine
from app.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    url = settings.database_url_sync

    # Point Alembic at our config file
    alembic_cfg_path = Path(__file__).parent.parent / "alembic.ini"
    cli = CommandLine()
    cli.main(
        argv=sys.argv[1:],
        extra_globals={"alembic_config_url": url},
        prog="migrate",
        cwd=alembic_cfg_path.parent,
    )


if __name__ == "__main__":
    main()
