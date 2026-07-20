# EREN Local Development Setup
## Docker Compose for Local Development

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This document defines the local development environment for EREN. It enables developers to run the entire stack locally using Docker Compose, with all required services (PostgreSQL, Redis, Neo4j, Qdrant, Kafka, MinIO) pre-configured.

The local environment mirrors the production architecture as closely as possible, using the same images and configuration patterns.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Tiago1203/EREN.git
cd EREN

# Start all services
docker compose up -d

# Wait for services to be healthy
docker compose ps

# Run migrations
docker compose exec eren-api alembic upgrade head

# Seed development data
docker compose exec eren-api python -m eren.seed

# Open the application
open http://localhost:8000
```

---

## Docker Compose Services

### Core Services

```yaml
# docker-compose.yml

version: "3.9"

services:
  # ──────────────────────────────────────────────────────────
  # EREN API (FastAPI)
  # ──────────────────────────────────────────────────────────
  eren-api:
    build:
      context: .
      dockerfile: apps/eren-api/Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      - EREN_ENV=development
      - DATABASE_URL=postgresql+asyncpg://eren:eren_secret@postgres:5432/eren_dev
      - REDIS_URL=redis://redis:6379/0
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=neo4j_secret
      - QDRANT_URL=http://qdrant:6333
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - VAULT_ADDR=http://vault:8200
      - LOG_LEVEL=DEBUG
    volumes:
      - ./apps/eren-api:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
      kafka:
        condition: service_healthy
      minio:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ──────────────────────────────────────────────────────────
  # EREN Celery Worker
  # ──────────────────────────────────────────────────────────
  eren-worker:
    build:
      context: .
      dockerfile: apps/eren-worker/Dockerfile
      target: development
    environment:
      - EREN_ENV=development
      - DATABASE_URL=postgresql+asyncpg://eren:eren_secret@postgres:5432/eren_dev
      - REDIS_URL=redis://redis:6379/0
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    volumes:
      - ./apps/eren-worker:/app
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy

  # ──────────────────────────────────────────────────────────
  # EREN Celery Beat (Scheduler)
  # ──────────────────────────────────────────────────────────
  eren-beat:
    build:
      context: .
      dockerfile: apps/eren-worker/Dockerfile
      target: development
    command: celery -A eren.worker beat
    environment:
      - EREN_ENV=development
      - DATABASE_URL=postgresql+asyncpg://eren:eren_secret@postgres:5432/eren_dev
      - REDIS_URL=redis://redis:6379/0
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    volumes:
      - ./apps/eren-worker:/app
    depends_on:
      - eren-worker

  # ──────────────────────────────────────────────────────────
  # PostgreSQL
  # ──────────────────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: eren_dev
      POSTGRES_USER: eren
      POSTGRES_PASSWORD: eren_secret
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eren -d eren_dev"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c work_mem=16MB
      -c maintenance_work_mem=128MB
      -c wal_buffers=16MB
      -c log_min_duration_statement=100

  # ──────────────────────────────────────────────────────────
  # Redis
  # ──────────────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --save "" --appendonly no
    volumes:
      - redis_data:/data

  # ──────────────────────────────────────────────────────────
  # Neo4j (Graph Database)
  # ──────────────────────────────────────────────────────────
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/neo4j_secret
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 2g
      NEO4J_dbms_memory_pagecache_size: 1g
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

  # ──────────────────────────────────────────────────────────
  # Qdrant (Vector Store)
  # ──────────────────────────────────────────────────────────
  qdrant:
    image: qdrant/qdrant:v1.7.0
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC
    volumes:
      - qdrant_data:/qdrant/storage

  # ──────────────────────────────────────────────────────────
  # Kafka (KRaft mode, no Zookeeper)
  # ──────────────────────────────────────────────────────────
  kafka:
    image: bitnami/kafka:3.6
    ports:
      - "9092:9092"  # Internal
    environment:
      KAFKA_CFG_NODE_ID: 1
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CFG_LISTENER_NAME_EXTERNAL_PORT: 9094
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_CFG_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_CFG_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_CFG_TRANSACTION_STATE_LOG_MIN_ISR: 1
    volumes:
      - kafka_data:/bitnami/kafka
    healthcheck:
      test: ["CMD-SHELL", "kafka-topics.sh --bootstrap-server localhost:9092 --list"]
      interval: 30s
      timeout: 10s
      retries: 5

  # ──────────────────────────────────────────────────────────
  # Schema Registry (for Kafka Avro/JSON Schema)
  # ──────────────────────────────────────────────────────────
  schema-registry:
    image: confluentinc/cp-schema-registry:7.6.0
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: PLAINTEXT://kafka:9092
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
    depends_on:
      - kafka

  # ──────────────────────────────────────────────────────────
  # MinIO (S3-compatible object storage)
  # ──────────────────────────────────────────────────────────
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"   # API
      - "9001:9001"   # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  # ──────────────────────────────────────────────────────────
  # Kafka UI (for local development)
  # ──────────────────────────────────────────────────────────
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_SCHEMA_REGISTRY: http://schema-registry:8081
    depends_on:
      - kafka
      - schema-registry

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  neo4j_logs:
  qdrant_data:
  kafka_data:
  minio_data:
```

---

## Makefile Commands

```makefile
# Makefile

.PHONY: help install dev test test-unit test-integration lint format clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker compose up -d
	@echo "Waiting for services..."
	@sleep 10
	@docker compose exec eren-api alembic upgrade head
	@echo "Running seed data..."
	@docker compose exec eren-api python -m eren.seed
	@echo ""
	@echo "EREN is running at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"
	@echo "Kafka UI at http://localhost:8080"
	@echo "Neo4j Browser at http://localhost:7474"

dev-logs: ## Tail development logs
	docker compose logs -f eren-api eren-worker

dev-shell: ## Open a shell in the API container
	docker compose exec eren-api /bin/bash

migrate: ## Run Alembic migrations
	docker compose exec eren-api alembic upgrade head

migrate-create: ## Create a new migration
	docker compose exec eren-api alembic revision --autogenerate -m "$(MSG)"

test: ## Run all tests
	docker compose exec eren-api pytest

test-unit: ## Run unit tests only
	docker compose exec eren-api pytest tests/unit

test-integration: ## Run integration tests only
	docker compose exec eren-api pytest tests/integration

lint: ## Run linters
	docker compose exec eren-api ruff check .
	docker compose exec eren-api mypy src/

format: ## Format code
	docker compose exec eren-api ruff format .
	docker compose exec eren-api ruff check --fix .

clean: ## Stop and remove all containers and volumes
	docker compose down -v --remove-orphans

db-reset: ## Reset database (WARNING: destroys all data)
	docker compose exec postgres dropdb --force -U eren eren_dev
	docker compose exec postgres createdb -U eren eren_dev
	docker compose exec eren-api alembic upgrade head

minio-console: ## Open MinIO console (user: minioadmin, pass: minioadmin)
	open http://localhost:9001
```

---

## Database Initialization

```sql
-- scripts/init-db.sql
-- Runs on first PostgreSQL startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application user (not superuser)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eren_app') THEN
        CREATE ROLE eren_app NOLOGIN;
        GRANT CONNECT ON DATABASE eren_dev TO eren_app;
        GRANT USAGE ON SCHEMA public TO eren_app;
    END IF;
END
$$;

-- Create test tenant
INSERT INTO tenants (id, name, slug, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Development Hospital',
    'dev-hospital',
    NOW()
) ON CONFLICT (id) DO NOTHING;
```

---

## Environment Variables Reference

```bash
# .env.development (local defaults)
EREN_ENV=development

# Database
DATABASE_URL=postgresql+asyncpg://eren:eren_secret@localhost:5432/eren_dev

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/1
REDIS_SESSION_URL=redis://localhost:6379/2
REDIS_QUEUE_URL=redis://localhost:6379/3

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8081

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secret

# Qdrant
QDRANT_URL=http://localhost:6333

# S3/MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=eren-dev

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
LOG_LEVEL=DEBUG
```

---

## VS Code Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug: EREN API",
      "type": "debugpy",
      "request": "attach",
      "connect": {"host": "localhost", "port": 5678},
      "pathMappings": [
        {"localRoot": "${workspaceFolder}/apps/eren-api", "remoteRoot": "/app"}
      ],
      "preLaunchTask": "docker compose up -d eren-api"
    }
  ]
}
```

---

*Infrastructure Team - 2026-07-16*
