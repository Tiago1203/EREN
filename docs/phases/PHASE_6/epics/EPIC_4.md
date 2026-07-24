# EPIC 4: Knowledge Center

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Proporcionar acceso centralizado al conocimiento institucional y clínico.**

EPIC 4 es responsable de:
- Gestionar artículos de conocimiento
- Proveer búsqueda semántica
- Navegar taxonomy de equipos médicos
- Acceder a guías clínicas
- Consumir Knowledge Platform de PHASE 4

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        ├── PHASE 4 (Knowledge Platform)
        │       │
        │       ├── Embeddings
        │       ├── Qdrant
        │       ├── Knowledge Retriever
        │       └── Citation Engine
        │
        └── EPIC 13 (Evidence Lifecycle)
                │
                ▼
           PHASE 6 (Hospital Platform)
                │
                ▼
           EPIC 0 (Platform Foundation)
                │
                ▼
           EPIC 3 (AI Center & Chat)
                │
                ▼
           EPIC 4 (Knowledge Center)
                │
                ▼
           EPIC 5 (Analytics & Reports)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 4: Knowledge Center                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    KNOWLEDGE MODULE                                │   │
│  │  ├── components/ ─────────────── SearchBar, ArticleList, etc.   │   │
│  │  ├── pages/ ────────────────── page.tsx (Knowledge Center)       │   │
│  │  ├── hooks/ ────────────────── useKnowledge, useSearch          │   │
│  │  ├── services/ ─────────────── KnowledgeService, SearchService  │   │
│  │  ├── stores/ ──────────────── knowledge.store                    │   │
│  │  ├── types/ ──────────────── knowledge.types                     │   │
│  │  └── utils/ ──────────────── article-parser                     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION LAYER                               │   │
│  │  ├── PHASE 4 Knowledge ──────────── Knowledge Retriever           │   │
│  │  ├── PHASE 4 RAG ───────────────── RAG Pipeline                 │   │
│  │  ├── PHASE 4 Citations ──────────── Citation Engine              │   │
│  │  └── PHASE 5 Evidence ──────────── Evidence Lifecycle            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── knowledge/                        # Módulo Knowledge
│   ├── components/
│   │   ├── SearchBar.tsx
│   │   ├── SearchResults.tsx
│   │   ├── ArticleList.tsx
│   │   ├── ArticleCard.tsx
│   │   ├── ArticleDetail.tsx
│   │   ├── CategoryNav.tsx
│   │   ├── CategoryTree.tsx
│   │   ├── TagList.tsx
│   │   ├── CitationViewer.tsx
│   │   └── KnowledgeGraph.tsx
│   ├── hooks/
│   │   ├── useKnowledge.ts
│   │   └── useSearch.ts
│   ├── services/
│   │   ├── knowledge.service.ts
│   │   ├── search.service.ts
│   │   └── citation.service.ts
│   ├── stores/
│   │   └── knowledge.store.ts
│   ├── types/
│   │   └── knowledge.types.ts
│   └── pages/
│       └── page.tsx
```

---

## Componentes

### 1. SearchBar

Barra de búsqueda semántica.

```typescript
// modules/knowledge/components/SearchBar.tsx
export interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}
```

### 2. SearchResults

Resultados de búsqueda con relevancia.

```typescript
// modules/knowledge/components/SearchResults.tsx
export interface SearchResultsProps {
  results: SearchResult[];
  loading?: boolean;
  onResultClick?: (result: SearchResult) => void;
}

export interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  relevance: number;
  type: ArticleType;
  category?: string;
  tags?: string[];
  citations?: Citation[];
}
```

### 3. ArticleList / ArticleCard

Lista de artículos con cards.

```typescript
// modules/knowledge/components/ArticleCard.tsx
export interface ArticleCardProps {
  article: KnowledgeArticle;
  onClick?: () => void;
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  type: ArticleType;
  category: Category;
  tags: Tag[];
  author?: string;
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  citations: Citation[];
  relatedArticles?: KnowledgeArticle[];
}

export type ArticleType = 'procedure' | 'protocol' | 'guideline' | 'manual' | 'article' | 'other';
```

### 4. CategoryNav / CategoryTree

Navegación por categorías.

```typescript
// modules/knowledge/components/CategoryNav.tsx
export interface CategoryNavProps {
  categories: Category[];
  selectedId?: string;
  onSelect: (category: Category) => void;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  parentId?: string;
  children?: Category[];
  articleCount: number;
  icon?: string;
}
```

### 5. TagList

Lista de tags/etiquetas.

```typescript
// modules/knowledge/components/TagList.tsx
export interface TagListProps {
  tags: Tag[];
  selectedTags?: string[];
  onToggle?: (tagId: string) => void;
}

export interface Tag {
  id: string;
  name: string;
  color?: string;
  articleCount: number;
}
```

### 6. CitationViewer

Visualizador de citas y fuentes.

```typescript
// modules/knowledge/components/CitationViewer.tsx
export interface CitationViewerProps {
  citations: Citation[];
  showReferences?: boolean;
}

export interface Citation {
  id: string;
  title: string;
  authors?: string[];
  journal?: string;
  year?: number;
  doi?: string;
  url?: string;
  type: CitationType;
  relevance: number;
}

export type CitationType = 'article' | 'book' | 'guideline' | 'protocol' | 'web' | 'other';
```

### 7. KnowledgeGraph

Visualización de grafo de conocimiento.

```typescript
// modules/knowledge/components/KnowledgeGraph.tsx
export interface KnowledgeGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'article' | 'category' | 'tag' | 'device';
  connections: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}
```

---

## Implementaciones

### KnowledgeService

```typescript
// modules/knowledge/services/knowledge.service.ts
export class KnowledgeService {
  // Articles
  async getArticles(filters?: ArticleFilters): Promise<KnowledgeArticle[]>;
  async getArticle(id: string): Promise<KnowledgeArticle | null>;
  async createArticle(data: CreateArticleDTO): Promise<KnowledgeArticle>;
  async updateArticle(id: string, data: UpdateArticleDTO): Promise<KnowledgeArticle>;
  async deleteArticle(id: string): Promise<void>;

  // Categories
  async getCategories(): Promise<Category[]>;
  async getCategoryTree(): Promise<CategoryTree>;

  // Tags
  async getTags(): Promise<Tag[]>;

  // Related
  async getRelatedArticles(articleId: string): Promise<KnowledgeArticle[]>;
  async getPopularArticles(limit?: number): Promise<KnowledgeArticle[]>;
}
```

### SearchService

```typescript
// modules/knowledge/services/search.service.ts
export class SearchService {
  async search(
    query: string,
    filters?: SearchFilters
  ): Promise<SearchResult[]>;

  async suggest(query: string): Promise<string[]>;

  async getSearchHistory(): Promise<SearchQuery[]>;

  async clearSearchHistory(): Promise<void>;
}
```

### CitationService

```typescript
// modules/knowledge/services/citation.service.ts
export class CitationService {
  async getCitations(articleId: string): Promise<Citation[]>;
  async formatCitation(citation: Citation, style: CitationStyle): string;
  async exportCitations(articleId: string, format: ExportFormat): Promise<string>;
}

export type CitationStyle = 'apa' | 'mla' | 'chicago' | 'vancouver';
export type ExportFormat = 'bibtex' | 'ris' | 'json';
```

---

## Domain Objects

### KnowledgeArticle

```typescript
// modules/knowledge/types/knowledge.types.ts
export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  type: ArticleType;
  category: Category;
  tags: Tag[];
  author?: Author;
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  status: 'draft' | 'review' | 'published' | 'archived';
  citations: Citation[];
  relatedArticles?: KnowledgeArticle[];
  metadata: ArticleMetadata;
}

export interface ArticleMetadata {
  language: string;
  version: string;
  lastReviewed?: Date;
  nextReview?: Date;
  difficulty?: 'basic' | 'intermediate' | 'advanced';
  estimatedReadTime?: number;
}

export interface Author {
  id: string;
  name: string;
  email?: string;
  role?: string;
}

export type ArticleType = 'procedure' | 'protocol' | 'guideline' | 'manual' | 'article' | 'faq' | 'other';
```

### Category

```typescript
export interface Category {
  id: string;
  name: string;
  description?: string;
  parentId?: string;
  children?: Category[];
  articleCount: number;
  icon?: string;
  color?: string;
  path?: string[];
}
```

### SearchFilters

```typescript
export interface SearchFilters {
  query?: string;
  types?: ArticleType[];
  categoryIds?: string[];
  tagIds?: string[];
  authorId?: string;
  dateFrom?: Date;
  dateTo?: Date;
  status?: ArticleStatus[];
}
```

---

## Integración con PHASE 4

```
PHASE 4 (Knowledge Platform)
        │
        ├── embeddings/ ────────── Medical Embeddings
        ├── qdrant/ ──────────── Vector DB
        ├── knowledge/ ────────── Knowledge Retriever
        ├── rag/ ──────────────── RAG Pipeline
        └── citations/ ─────────── Citation Engine
                │
                ▼
           EPIC 4 (Knowledge Center)
                │
                ├── SearchBar → SearchService → PHASE_4/knowledge
                ├── ArticleList → KnowledgeService → PHASE_4/rag
                └── CitationViewer → CitationService → PHASE_4/citations
```

### RAG Pipeline Integration

```typescript
// modules/knowledge/services/search.service.ts
export class SearchService {
  async search(query: string, filters?: SearchFilters): Promise<SearchResult[]> {
    // 1. Embed query using PHASE_4/embeddings
    const embedding = await embeddingService.embed(query);
    
    // 2. Search vector DB using PHASE_4/qdrant
    const vectorResults = await qdrantClient.search({
      collection: 'knowledge_articles',
      vector: embedding,
      limit: 20,
    });
    
    // 3. Retrieve full articles
    const articles = await knowledgeService.getArticlesByIds(
      vectorResults.map(r => r.id)
    );
    
    // 4. Rerank using PHASE_4/rag
    const reranked = await reranker.rerank(query, articles);
    
    return reranked.map(toSearchResult);
  }
}
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 4 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 4
- [x] Crear tipos para knowledge
- [x] Crear servicios del módulo
- [x] Crear store Zustand
- [x] Crear hooks
- [x] Crear componentes
- [x] Crear página de Knowledge Center
- [ ] Crear tests unitarios
- [ ] Integrar con PHASE 4

---

## Próximos Pasos

- EPIC 5: Analytics & Reports
- EPIC 6: Notifications & Workspace

---

*EREN PHASE 6 - EPIC 4*
*Architecture Board - 2026-07-24*
