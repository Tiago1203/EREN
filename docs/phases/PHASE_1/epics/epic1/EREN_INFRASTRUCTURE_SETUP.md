# EREN Infrastructure Setup Guide
## Local Development Environment

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| uv | latest | Package manager |
| Docker | 24+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| PostgreSQL | 16+ | (via Docker) |
| Redis | 7+ | (via Docker) |
| RabbitMQ | 3.13+ | (via Docker) |
| Jaeger | 1.57 | (via Docker) |

---

## Quick Start

### 1. Clone and install dependencies

```bash
cd apps/api
uv sync --python 3.12
```

### 2. Configure environment

```bash
cp apps/api/.env.example apps/api/.env
# Edit .env with your values
```

### 3. Start infrastructure

```bash
docker compose up -d postgres redis rabbitmq jaeger
```

### 4. Run migrations

```bash
cd apps/api
uv run python scripts/migrate.py upgrade
```

### 5. Start the API

```bash
cd apps/api
uv run uvicorn app.main:app --reload --port 8000
```

### 6. Verify

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/ready
curl http://localhost:8000/api/v1/health/full
```

---

## Docker Compose Services

### PostgreSQL (port 5432)

```bash
docker compose up -d postgres
```

- User: `eren`
- Password: `eren`
- Database: `eren`
- Extensions: RLS enabled per schema
- Health check: `pg_isready -U eren`

### Redis (port 6379)

```bash
docker compose up -d redis
```

- Persistence: RDB snapshots
- Max memory: 256MB (development)
- Health check: `redis-cli ping`

### RabbitMQ (ports 5672 + 15672)

```bash
docker compose up -d rabbitmq
```

- User: `eren`
- Password: `eren`
- Management UI: http://localhost:15672
- Exchange: `eren.events` (topic)
- Health check: `rabbitmq-diagnostics check_port_connectivity`

### Jaeger (ports 16686 + 4317)

```bash
docker compose up -d jaeger
```

- UI: http://localhost:16686
- OTLP gRPC: `http://localhost:4317`
- OTLP HTTP: `http://localhost:14268`

---

## Database Schemas

Epic 1 uses **schema-per-bounded-context** in PostgreSQL:

| Schema | Bounded Context |
|--------|-----------------|
| `incident` | Engineering Incident |
| `device` | Device Registry |
| `recommendation` | AI Recommendation |
| `knowledge` | Knowledge Graph |
| `work_order` | Maintenance Work Order |
| `incident.outbox_events` | Outbox pattern |

Create schemas manually:

```bash
PGPASSWORD=eren psql -h localhost -U eren -d eren -c "
  CREATE SCHEMA IF NOT EXISTS incident AUTHORIZATION eren;
  CREATE SCHEMA IF NOT EXISTS device AUTHORIZATION eren;
  CREATE SCHEMA IF NOT EXISTS recommendation AUTHORIZATION eren;
  CREATE SCHEMA IF NOT EXISTS knowledge AUTHORIZATION eren;
  CREATE SCHEMA IF NOT EXISTS work_order AUTHORIZATION eren;
"
```

---

## Running Tests

```bash
cd apps/api

# Unit tests (no database required)
uv run pytest tests/unit/ -v

# Integration tests (database required)
uv run pytest tests/integration/ -v

# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=html
```

---

## Migration Commands

```bash
cd apps/api

# Upgrade to latest
uv run python scripts/migrate.py upgrade

# Show current version
uv run python scripts/migrate.py current

# Show migration history
uv run python scripts/migrate.py history

# Downgrade one step
uv run python scripts/migrate.py downgrade -1

# Generate new migration (after model changes)
uv run alembic revision --autogenerate -m "description"

# Dry run (show SQL without applying)
uv run python scripts/migrate.py upgrade --sql
```

---

## Environment Variables

All configuration is via environment variables with the `EREN_API_` prefix:

```bash
# Application
EREN_API_ENVIRONMENT=development
EREN_API_DEBUG=true
EREN_API_APP_NAME=EREN API
EREN_API_SERVICE_NAME=eren-api

# Database
EREN_API_DATABASE_URL=postgresql+asyncpg://eren:eren@localhost:5432/eren

# Redis
EREN_API_REDIS_URL=redis://localhost:6379/0
EREN_API_CACHE_TTL_SECONDS=300

# RabbitMQ
EREN_API_RABBITMQ_URL=amqp://eren:eren@localhost:5672/

# Supabase Auth
EREN_API_SUPABASE_URL=https://your-project.supabase.co
EREN_API_SUPABASE_ANON_KEY=your-anon-key

# Observability
EREN_API_OTEL_ENDPOINT=http://localhost:4317

# CORS
EREN_API_CORS_ORIGINS=["http://localhost:3000"]

# Vault (optional)
EREN_API_VAULT_ENABLED=false
EREN_API_VAULT_URL=http://vault:8200
EREN_API_VAULT_TOKEN=your-vault-token
EREN_API_VAULT_MOUNT=eren
EREN_API_VAULT_SECRET_PATH=api
```

---

## Development Workflow

### Starting fresh

```bash
# 1. Pull latest code
git pull

# 2. Update dependencies
cd apps/api && uv sync

# 3. Start infrastructure
docker compose up -d

# 4. Run migrations
uv run python scripts/migrate.py upgrade

# 5. Start API
uv run uvicorn app.main:app --reload

# 6. Run tests
uv run pytest tests/ -v
```

### Creating a new migration

```bash
# 1. Make model changes in app/infrastructure/models/
# 2. Generate migration
uv run alembic revision --autogenerate -m "add column to device"

# 3. Review generated file in migrations/versions/
# 4. Apply
uv run python scripts/migrate.py upgrade

# 5. Commit
git add migrations/versions/
git commit -m "migrations: add column to device"
```

---

## Troubleshooting

### PostgreSQL connection refused

```bash
docker compose ps postgres
docker compose logs postgres
# Check POSTGRES_USER and POSTGRES_PASSWORD match .env
```

### RabbitMQ connection refused

```bash
docker compose ps rabbitmq
docker compose logs rabbitmq
# Check RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS
```

### Alembic "Can't locate database"

```bash
# Ensure schemas exist
PGPASSWORD=eren psql -h localhost -U eren -d eren -c "SELECT schema_name FROM information_schema.schemata;"
```

### Outbox events not publishing

```bash
# Run OutboxWorker manually
cd apps/api
uv run python scripts/run_outbox_worker.py

# Check outbox table
PGPASSWORD=eren psql -h localhost -U eren -d eren -c "SELECT * FROM incident.outbox_events LIMIT 10;"
```

---

*EREN Infrastructure Setup Guide v1.0*
*Infrastructure Team - 2026-07-16*
