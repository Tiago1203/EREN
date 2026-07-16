# EREN Settings Model
## Configuration Architecture

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This document defines how EREN handles configuration across environments. It establishes the settings hierarchy, the environment-specific configuration model, and the conventions for adding new settings.

---

## Configuration Hierarchy

EREN uses a **priority-based configuration hierarchy** (highest wins):

```
1. Environment Variables (OS-level)         ← Most specific
2. Vault Secrets (dynamic credentials)       ← Per-environment secrets
3. Environment-specific config files          ← YAML per environment
4. Base config file (config.yaml.base)      ← Defaults
5. Code defaults (settings.py)              ← Fallback
```

### Why this hierarchy?

- **Environment variables:** Developers can override anything locally without changing files
- **Vault:** Dynamic credentials (DB passwords, API keys) are injected at runtime, never stored in files
- **YAML configs:** Environment-specific values (hosts, ports) version-controlled per environment
- **Code defaults:** Safe fallbacks for non-sensitive values

---

## Settings Structure

```python
# apps/eren-api/src/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pydantic import Field

class DatabaseSettings(BaseSettings):
    """Database configuration."""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="eren")
    password: str = Field(default="")  # From Vault in production
    database: str = Field(default="eren_dev")
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=10)

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class KafkaSettings(BaseSettings):
    """Kafka configuration."""
    bootstrap_servers: list[str] = Field(default=["localhost:9092"])
    consumer_group: str = Field(default="eren-api")
    auto_offset_reset: str = Field(default="earliest")
    enable_auto_commit: bool = Field(default=False)

class LLMSettings(BaseSettings):
    """LLM provider configuration."""
    provider: str = Field(default="openai")  # openai | anthropic | azure
    model: str = Field(default="gpt-4")
    api_key: str = Field(default="")  # From Vault
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.0)
    timeout_seconds: int = Field(default=30)

class Settings(BaseSettings):
    """Root settings — loads from environment + YAML."""

    # ─────────────────────────────────────────────────────────────
    # Environment
    # ─────────────────────────────────────────────────────────────
    eren_env: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ─────────────────────────────────────────────────────────────
    # API
    # ─────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    max_request_size_mb: int = Field(default=10)

    # ─────────────────────────────────────────────────────────────
    # Database
    # ─────────────────────────────────────────────────────────────
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # ─────────────────────────────────────────────────────────────
    # Redis
    # ─────────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_cache_ttl_seconds: int = Field(default=300)
    redis_session_ttl_seconds: int = Field(default=86400)

    # ─────────────────────────────────────────────────────────────
    # Kafka
    # ─────────────────────────────────────────────────────────────
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)

    # ─────────────────────────────────────────────────────────────
    # Neo4j
    # ─────────────────────────────────────────────────────────────
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="")

    # ─────────────────────────────────────────────────────────────
    # Qdrant
    # ─────────────────────────────────────────────────────────────
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_api_key: str = Field(default="")

    # ─────────────────────────────────────────────────────────────
    # S3/MinIO
    # ─────────────────────────────────────────────────────────────
    s3_endpoint: Optional[str] = Field(default=None)  # None = AWS S3
    s3_region: str = Field(default="us-east-1")
    s3_bucket: str = Field(default="eren-dev")
    s3_access_key: str = Field(default="")
    s3_secret_key: str = Field(default="")

    # ─────────────────────────────────────────────────────────────
    # LLM
    # ─────────────────────────────────────────────────────────────
    llm: LLMSettings = Field(default_factory=LLMSettings)

    # ─────────────────────────────────────────────────────────────
    # Multi-tenancy
    # ─────────────────────────────────────────────────────────────
    enforce_rls: bool = Field(default=True)

    # ─────────────────────────────────────────────────────────────
    # Observability
    # ─────────────────────────────────────────────────────────────
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    enable_tracing: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    trace_sample_rate: float = Field(default=0.05)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()
```

---

## Environment-Specific Configuration

### Development

```yaml
# apps/eren-api/config.development.yaml
erenv: development
debug: true
log_level: DEBUG

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins:
    - "http://localhost:3000"
    - "http://localhost:5173"

database:
  host: "localhost"
  port: 5432
  user: "eren"
  password: "${DATABASE_PASSWORD}"  # Injected from Vault
  database: "eren_dev"

redis_url: "redis://localhost:6379/0"

kafka:
  bootstrap_servers:
    - "localhost:9092"
  consumer_group: "eren-api-dev"

neo4j:
  uri: "bolt://localhost:7687"
  password: "neo4j_secret"

s3:
  endpoint: "http://localhost:9000"
  access_key: "minioadmin"
  secret_key: "minioadmin"

llm:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4"
```

### Production

```yaml
# apps/eren-api/config.production.yaml
erenv: production
debug: false
log_level: "INFO"
enforce_rls: true

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins:
    - "https://eren.io"
    - "https://app.eren.io"

database:
  host: "${POSTGRES_HOST}"
  port: 5432
  user: "${POSTGRES_USER}"
  password: "${POSTGRES_PASSWORD}"  # From Vault
  database: "eren_prod"
  pool_size: 50
  max_overflow: 20

redis_url: "${REDIS_URL}"

kafka:
  bootstrap_servers:
    - "${KAFKA_BROKER_1}"
    - "${KAFKA_BROKER_2}"
    - "${KAFKA_BROKER_3}"
  consumer_group: "eren-api-prod"

neo4j:
  uri: "${NEO4J_URI}"
  password: "${NEO4J_PASSWORD}"  # From Vault

s3:
  region: "us-east-1"
  bucket: "eren-prod"
  access_key: "${AWS_ACCESS_KEY_ID}"
  secret_key: "${AWS_SECRET_ACCESS_KEY}"

llm:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"  # From Vault
  model: "gpt-4-turbo"
  timeout_seconds: 30

otel:
  exporter_otlp_endpoint: "https://otlp.eren.io:4317"
  enable_tracing: true
  enable_metrics: true
  trace_sample_rate: 0.05
```

---

## Settings Loading

```python
# apps/eren-api/src/main.py
from pathlib import Path
from config import Settings, get_settings

def load_yaml_config(env: str) -> dict:
    """Loads YAML config file for the current environment."""
    config_path = Path(__file__).parent.parent / f"config.{env}.yaml"
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

def create_app() -> FastAPI:
    settings = get_settings()

    # Load YAML config and merge
    yaml_config = load_yaml_config(settings.erenv)

    app = FastAPI(
        title="EREN API",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
    )

    return app
```

---

## Secrets Management with Vault

```python
# apps/eren-api/src/infrastructure/vault.py
import hvac

class VaultClient:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)

    def get_secret(self, path: str, key: str) -> str:
        """Reads a secret from Vault KV v2."""
        result = self.client.secrets.kv.v2.read_secret_version(path=path)
        return result["data"]["data"][key]

    def get_database_credentials(self, role: str = "app_user") -> dict:
        """Generates dynamic database credentials from Vault."""
        result = self.client.secrets.database.generate_credentials(
            name=role
        )
        return {
            "username": result["data"]["username"],
            "password": result["data"]["password"],
        }

# Usage in startup
@app.on_event("startup")
async def load_vault_secrets():
    if settings.erenv == "production":
        vault = VaultClient(
            url=settings.vault_addr,
            token=os.environ["VAULT_TOKEN"]
        )
        settings.database.password = vault.get_secret(
            path="eren/production/database",
            key="password"
        )
        settings.llm.api_key = vault.get_secret(
            path="eren/production/llm",
            key="api_key"
        )
```

---

## Adding a New Setting

**Step 1: Add to `Settings` class**

```python
# config.py
class LLMSettings(BaseSettings):
    # ... existing fields
    max_context_tokens: int = Field(default=128000)  # NEW
```

**Step 2: Add to YAML config**

```yaml
# config.development.yaml
llm:
  max_context_tokens: 128000
```

**Step 3: Document in this file**

**Step 4: Add to Vault (production)**

```bash
vault kv put eren/production/llm api_key="sk-..." max_context_tokens=128000
```

---

## Forbidden Practices

```python
# ❌ NEVER do this:
# 1. Hardcode secrets in code
API_KEY = "sk-1234567890"

# 2. Use default() for secrets
password: str = Field(default="password123")

# 3. Set debug=True in production
debug: bool = Field(default=True)

# 4. Expose sensitive settings via API
class Settings(BaseSettings):
    secret_key: str  # Will be exposed in /settings endpoint

# ✅ DO this:
# 1. Always use environment variables or Vault
password: str = Field(default="")  # Empty default, must come from env

# 2. Set debug=False as default
debug: bool = Field(default=False)

# 3. Exclude secrets from API
class SettingsPublic(BaseSettings):
    log_level: str
    version: str
    # Note: password, api_key NOT here
```

---

*Infrastructure Team - 2026-07-16*
