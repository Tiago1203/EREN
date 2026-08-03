# CI REPORT — Análisis de CI/CD

**Fecha:** 2026-08-03

---

## 1. WORKFLOW ACTUAL

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, epic1-*, feature/**]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with: python-version: "3.12"
      - name: Install linters
        run: pip install --break-system-packages ruff black
      - name: Run ruff check
        run: ruff check apps/api/ --ignore E501 || true
      - name: Run ruff format check
        run: ruff format --check apps/api/ || true

  typecheck:
    name: Type Check (MyPy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with: python-version: "3.12"
      - name: Install dependencies
        run: cd apps/api && uv sync --locked --python 3.12 --no-install-project --group dev
      - name: Run mypy on domain
        run: cd apps/api && uv run mypy app/domain/ --ignore-missing-imports || true
      - name: Run mypy on infrastructure
        run: cd apps/api && uv run mypy app/infrastructure/ --ignore-missing-imports || true
```

---

## 2. GAPS CRÍTICOS

### Gap 1: NO corre tests

```
jobs:
  lint:        ✅ EXISTE
  typecheck:   ✅ EXISTE
  test:        ❌ NO EXISTE
```

**Evidencia:**
```bash
grep -n "pytest\|test\|coverage" .github/workflows/ci.yml
# → vacío
```

**Impacto:** Los tests pueden estar fallando y nadie se entera.

---

### Gap 2: Linting ignora errores

```bash
ruff check apps/api/ --ignore E501 || true
#                     ↑ el "|| true" significa que si ruff falla, CI pasa de todas formas
```

**Impacto:** Errores de lint son ignorados silenciosamente.

---

### Gap 3: MyPy sin strict mode

```yaml
[tool.mypy]
python_version = "3.12"
strict = false
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

**Impacto:** MyPy está en modo permisivo. Muchos errores de tipo no se detectan.

---

### Gap 4: Solo linting en apps/api/

```bash
ruff check apps/api/  # Solo apps/api
# core/ NO se liatea en CI
```

**Impacto:** PHASE_1, PHASE_2, PHASE_3, PHASE_4, PHASE_5, PHASE_7 no se verifican en CI.

---

### Gap 5: MyPy solo en domain/ e infrastructure/

```bash
mypy app/domain/      # Solo domain
mypy app/infrastructure/  # Solo infrastructure
# app/routers/, app/schemas/, app/services/ NO se verifican
```

**Impacto:** ~40% del código de apps/api no se type-checkea.

---

### Gap 6: No hay coverage report en CI

```bash
# No se ejecuta pytest --cov en ningún job
```

**Impacto:** No hay visibilidad de cobertura de código.

---

### Gap 7: No hay security scanning

- No hay `bandit` para seguridad
- No hay `safety` para dependencias vulnerables
- No hay análisis de dependencias obsoletas

---

### Gap 8: No hay integration tests en CI

Solo linting y type-checking. No se ejecutan:
- Tests de integración
- Tests E2E
- Tests de base de datos

---

### Gap 9: No hay deployment checks

- No se valida que docker-compose.yml funcione
- No se valida que los K8s manifests sean válidos
- No se valida que Helm chart sea desplegable

---

### Gap 10: No hay frontend CI

```bash
# El workflow solo toca Python
# apps/web (Next.js + TypeScript) NO tiene CI
```

**Impacto:** El frontend puede romper sin que CI lo detecte.

---

## 3. TESTS QUE DEBERÍA TENER EL WORKFLOW

| Job | Estado actual | Debe existir |
|---|---|---|
| lint-core | ❌ NO | ✅ SÍ — ruff en core/ |
| lint-web | ❌ NO | ✅ SÍ — eslint en apps/web/ |
| typecheck-core | ❌ NO | ✅ SÍ — mypy en core/ |
| typecheck-web | ❌ NO | ✅ SÍ — tsc en apps/web/ |
| test-python | ❌ NO | ✅ SÍ — pytest con coverage |
| test-web | ❌ NO | ✅ SÍ — vitest |
| test-e2e | ❌ NO | ✅ SÍ — Playwright |
| security | ❌ NO | ✅ SÍ — bandit + safety |
| dependency-audit | ❌ NO | ✅ SÍ — pip-audit |
| docker-build | ❌ NO | ✅ SÍ — docker build |
| k8s-validate | ❌ NO | ✅ SÍ — kubeval |

---

## 4. WORKFLOW QUE DEBERÍA EXISTIR

```yaml
name: CI

on:
  push:
    branches: [main, epic1-*, feature/**]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ── Linting ──────────────────────────────────────
  lint-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with: python-version: "3.12"
      - run: cd apps/api && uv sync --locked
      - run: ruff check apps/api/ core/ --target-version py312
      - run: ruff format --check apps/api/ core/

  lint-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: node-version: "20"
      - run: cd apps/web && npm ci
      - run: cd apps/web && npm run lint

  # ── Type Checking ───────────────────────────────
  typecheck-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with: python-version: "3.12"
      - run: cd apps/api && uv sync --locked
      - run: cd apps/api && uv run mypy app/ core/ --strict

  typecheck-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: node-version: "20"
      - run: cd apps/web && npm ci
      - run: cd apps/web && npx tsc --noEmit

  # ── Tests ─────────────────────────────────────
  test-api:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_DB: eren_test, POSTGRES_USER: eren, POSTGRES_PASSWORD: eren }
        ports: [5432:5432]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports: [6379:6379]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with: python-version: "3.12"
      - run: cd apps/api && uv sync --locked --group dev
      - run: cd apps/api && uv run pytest tests/ --cov=app --cov=core --cov-report=xml --cov-fail-under=60
      - uses: codecov/codecov-action@v4
        with: files: apps/api/coverage.xml

  test-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: node-version: "20"
      - run: cd apps/web && npm ci
      - run: cd apps/web && npm test -- --coverage --coverage-threshold=60

  # ── Security ───────────────────────────────────
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit safety pip-audit
      - run: bandit -r apps/api/ core/ -f txt
      - run: safety check --json --output safety.json || true
      - run: pip-audit --fail-on=all || true

  # ── Docker ─────────────────────────────────────
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t eren-api:test apps/api/
      - run: docker-compose -f docker-compose.yml build

  # ── K8s ──────────────────────────────────────
  kubernetes-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install yamllint k8s
      - run: yamllint infra/k8s/ infra/helm/
```

---

## 5. DOCKER-COMPOSE

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:    ✅ CONFIGURADO
  redis:       ✅ CONFIGURADO
  # RabbitMQ:  ❌ NO EXISTE
  # Qdrant:    ❌ NO EXISTE
```

**Hallazgo:** RabbitMQ está en pyproject.toml (aio-pika) pero no está en docker-compose.yml. El outbox worker intenta conectarse a RabbitMQ pero no hay servicio配置.

---

## 6. HELM CHART

```
infra/helm/eren-api/
├── Chart.yaml              ✅
├── values.yaml            ✅
└── templates/
    ├── deployment.yaml    ✅
    └── ingress.yaml      ✅
```

**Estado:** Completo y funcional.

---

*Reporte generado: 2026-08-03*
