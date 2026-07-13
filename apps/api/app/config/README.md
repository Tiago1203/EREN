# app/config

**Typed application configuration.**

`settings.py` defines a Pydantic v2 `Settings` model (via `pydantic-settings`)
loaded from environment variables prefixed with `EREN_API_` and/or a local
`.env` file. Use `get_settings()` (cached) as the single source of truth for
config anywhere in the app.

Add new settings as typed fields here — never read `os.environ` directly
elsewhere.
