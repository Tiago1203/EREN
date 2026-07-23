# EPIC 9: Medical Knowledge Repository

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Gestionar todas las fuentes biomédicas.

---

## Responsabilidad

**Administrar el repositorio de conocimiento.**

EPIC 9 es responsable de:
- Gestionar repositorios de conocimiento
- Control de versiones de documentos
- Gestión de colecciones
- Registro de fuentes
- Estadísticas del repositorio

---

## Dependencias

### EPICs
- **EPIC 8**: Consume Quality-filtered Evidence

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│              EPIC 9: Medical Knowledge Repository                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     Ranked Evidence (from EPIC 8)                       │   │
│  │     Knowledge Assets                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     REPOSITORY                              │   │
│  │  ├── Repository ───────────────────► Repository model      │   │
│  │  ├── InMemoryRepositoryManager ──► Manage repositories    │   │
│  │  └── SourceRegistryEntry ────────► Source tracking         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      VERSIONING                             │   │
│  │  ├── KnowledgeVersion ──────────────► Version model         │   │
│  │  ├── InMemoryVersionManager ────────► Manage versions      │   │
│  │  └── VersionComparator ─────────────► Compare versions      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      COLLECTIONS                             │   │
│  │  ├── Collection ──────────────────► Collection model       │   │
│  │  ├── InMemoryCollectionManager ────► Manage collections   │   │
│  │  └── CollectionSearcher ───────────► Search collections    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Repository (centralizado)                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic9_knowledge_repository/
├── __init__.py                    # Módulo principal
├── repository/                      # Gestión de repositorio
│   └── __init__.py               # Repository, RepositoryManager, etc.
├── versioning/                    # Control de versiones
│   └── __init__.py             # KnowledgeVersion, VersionManager, etc.
└── collections/                  # Gestión de colecciones
    └── __init__.py             # Collection, CollectionManager, etc.
```

---

## Componentes

### 1. Repository

| Componente | Descripción |
|------------|-------------|
| `Repository` | Modelo de repositorio |
| `RepositoryStats` | Estadísticas del repositorio |
| `InMemoryRepositoryManager` | Gestor de repositorios |
| `SourceRegistryEntry` | Entrada de registro de fuentes |

**Tipos de repositorio:**
- `PRIMARY` - Repo principal
- `ARCHIVE` - Archivo histórico
- `STAGING` - Pre-publicación
- `VALIDATION` - Para validación

### 2. Versioning

| Componente | Descripción |
|------------|-------------|
| `KnowledgeVersion` | Modelo de versión |
| `VersionHistory` | Historial de versiones |
| `InMemoryVersionManager` | Gestor de versiones |
| `VersionComparator` | Comparador de versiones |

**Tipos de versión:**
- `MAJOR` - Breaking changes
- `MINOR` - New features
- `PATCH` - Bug fixes

**Estados:**
- `DRAFT` - Borrador
- `REVIEW` - En revisión
- `PUBLISHED` - Publicada
- `ARCHIVED` - Archivada
- `DEPRECATED` - Deprecada

### 3. Collections

| Componente | Descripción |
|------------|-------------|
| `Collection` | Modelo de colección |
| `CollectionMetadata` | Metadatos de colección |
| `InMemoryCollectionManager` | Gestor de colecciones |
| `CollectionSearcher` | Buscador de colecciones |

**Tipos de colección:**
- `GUIDELINE` - Guías clínicas
- `PROTOCOL` - Protocolos
- `TRAINING` - Material de entrenamiento
- `REFERENCE` - Referencias
- `ARCHIVE` - Archivo
- `CUSTOM` - Personalizada

---

## Uso

### Gestión de repositorio

```python
from core.PHASE_4.epic9_knowledge_repository import (
    Repository,
    RepositoryType,
    InMemoryRepositoryManager,
)

manager = InMemoryRepositoryManager()

repo = Repository(
    repository_id="repo_1",
    name="Clinical Guidelines",
    repository_type=RepositoryType.PRIMARY,
)

await manager.create_repository(repo)
```

### Control de versiones

```python
from core.PHASE_4.epic9_knowledge_repository import (
    KnowledgeVersion,
    VersionType,
    InMemoryVersionManager,
)

manager = InMemoryVersionManager()

version = KnowledgeVersion(
    version_id="v1",
    document_id="doc_1",
    version_number="1.0.0",
    version_type=VersionType.MAJOR,
)

await manager.create_version(version)
await manager.publish_version("v1")
```

### Gestión de colecciones

```python
from core.PHASE_4.epic9_knowledge_repository import (
    Collection,
    CollectionType,
    InMemoryCollectionManager,
)

manager = InMemoryCollectionManager()

collection = Collection(
    collection_id="col_1",
    name="Cardiology Guidelines",
    collection_type=CollectionType.GUIDELINE,
)

await manager.create_collection(collection)
await manager.add_to_collection("col_1", "doc_1")
```

---

## Flujo de Repositorio

```
1. INPUT: Ranked Evidence (from EPIC 8)
          │
          ▼
2. REPOSITORY: InMemoryRepositoryManager
          │ Create/Update repository
          │ Register sources
          │
          ▼
3. VERSIONING: InMemoryVersionManager
          │ Create new version
          │ Track changes
          │ Publish/Archive
          │
          ▼
4. COLLECTION: InMemoryCollectionManager
          │ Organize into collections
          │ Add/Remove documents
          │ Search collections
          │
          ▼
5. OUTPUT: Repository (centralized)
          │
          ▼
6. NEXT: EPIC 10 (Knowledge Synchronization)
```

---

## Concatenación

```
EPIC 8 ──► EPIC 9 (consume RankedEvidence)
EPIC 0 ──► EPIC 9 (usa Foundation types)
EPIC 9 ──► EPIC 10 (provee Repository para sync)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 10: Knowledge Synchronization Engine
- EPIC 11: Knowledge Governance & Lifecycle

---

*EREN PHASE 4 - EPIC 9*
*Architecture Board - 2026-07-23*
