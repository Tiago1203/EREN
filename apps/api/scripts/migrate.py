#!/usr/bin/env python3
"""Run Alembic database migrations.

Usage::

    python scripts/migrate.py upgrade          # apply all migrations
    python scripts/migrate.py upgrade --sql   # show SQL without applying
    python scripts/migrate.py downgrade -1    # roll back one revision
    python scripts/migrate.py history         # show migration history

Environment::

    EREN_API_DATABASE_URL  # PostgreSQL connection string
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the app package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import CommandLine

from app.config.settings import get_settings


def main() -> None:
    settings = get_settings()

    # Pass database URL via environment variable for env.py to pick up
    original_url = os.environ.get("EREN_API_DATABASE_URL")
    os.environ["EREN_API_DATABASE_URL"] = settings.database_url_sync

    try:
        # Change to the app directory so alembic.ini is found relative to it
        app_dir = Path(__file__).parent.parent
        original_cwd = os.getcwd()
        os.chdir(app_dir)

        cli = CommandLine()
        cli.main(argv=sys.argv[1:])
    finally:
        os.chdir(original_cwd)
        if original_url is not None:
            os.environ["EREN_API_DATABASE_URL"] = original_url
        else:
            os.environ.pop("EREN_API_DATABASE_URL", None)


if __name__ == "__main__":
    main()


