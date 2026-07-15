# Dependency Review
## EREN OS — Audit 13

---

## Executive Summary

EREN OS usa pyproject.toml para gestión de dependencias con Python 3.12+. Las dependencias son managed por uv.

**Dependency Score: 65/100**

Las dependencias están bien definidas pero faltan análisis de seguridad y licencia.

---

## Dependencies Analysis

### pyproject.toml Structure
```toml
[project]
name = "eren-os"
version = "0.3.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115,<1.0",
    "uvicorn[standard]>=0.30,<1.0",
    "pydantic>=2.7,<3.0",
    "pydantic-settings>=2.3,<3.0",
    "sqlalchemy>=2.0,<3.0",
    "alembic>=1.13,<2.0",
    "aiosqlite>=0.20,<1.0",
]
```

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115+ | API framework |
| uvicorn | 0.30+ | ASGI server |
| pydantic | 2.7+ | Data validation |
| sqlalchemy | 2.0+ | ORM |
| alembic | 1.13+ | Migrations |
| aiosqlite | 0.20+ | Async SQLite |

---

## Dev Dependencies
```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "ruff>=0.6,<1.0",
]
```

---

## Critical Issues

### 1. No Security Audit
**Severidad: ALTA**

- ❌ No pip-audit
- ❌ No safety check
- ❌ No dependency review

### 2. No License Audit
**Severidad: MEDIA**

- ❌ No license checker
- ❌ No GPL warning
- ❌ Medical software needs careful licensing

### 3. No SBOM
**Severidad: MEDIA**

- ❌ No Software Bill of Materials
- ❌ No vulnerability tracking

---

## Version Pinning

### Current State
```toml
dependencies = [
    "fastapi>=0.115,<1.0",  # ⚠️ Range
    "uvicorn[standard]>=0.30,<1.0",  # ⚠️ Range
    "pydantic>=2.7,<3.0",  # ⚠️ Range
]
```

### Recommendations
```toml
dependencies = [
    "fastapi==0.115.0",  # Exact pin for prod
]
```

---

## Supply Chain Analysis

### Issues
- ❌ No lock file
- ❌ No hash verification
- ❌ No reproducible builds

### Recommendations
```bash
# Generate lock file
uv lock

# Verify hashes
uv pip check
```

---

## Dependency Conflicts

### Current Status
- ✅ uv manages resolution
- ❌ No conflicts check

---

## Outdated Dependencies

### Check Command
```bash
uv pip list --outdated
```

### Recommendations
- Regular updates
- Security patches within 24h
- Major updates quarterly

---

## Transitive Dependencies

### Issues
- ❌ No audit of transitive deps
- ❌ Potential vulnerable sub-deps

### Recommendations
```bash
# List all dependencies
uv pip tree
```

---

## Recommendations

### 1. Add pip-audit
```yaml
- name: Security audit
  run: pip-audit
```

### 2. Add pip-compile
```bash
uv pip compile requirements.in
```

### 3. Generate SBOM
```bash
pip install cyclonedx
cyclonedx-py -r
```

### 4. License Check
```bash
pip install licensecheck
licensecheck
```

---

## Conclusion

EREN OS tiene gestión básica de dependencias pero necesita:
1. Security auditing
2. License compliance
3. SBOM generation
4. Lock file

**Recomendación: Implementar pip-audit en CI y generar SBOM.**

---

*Audit realizado: 2026-07-15*
