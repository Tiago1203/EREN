# Arquitectura Completa de EREN

> **Diagramas y descripción detallada de la arquitectura de EREN**

---

## Tabla de Contenidos

1. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
2. [Arquitectura Frontend](#arquitectura-frontend)
3. [Arquitectura Backend](#arquitectura-backend)
4. [Sistema Multiagente](#sistema-multiagente)
5. [Sistema de Conocimiento](#sistema-de-conocimiento)
6. [Base de Datos](#base-de-datos)
7. [Autenticación y Autorización](#autenticación-y-autorización)
8. [Observabilidad](#observabilidad)
9. [Seguridad](#seguridad)
10. [Infraestructura](#infraestructura)

---

## Arquitectura de Alto Nivel

### Diagrama General

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Browser / Mobile]
    end
    
    subgraph "Frontend Layer"
        NextJS[Next.js 14]
        React[React Components]
        Tailwind[TailwindCSS]
        Shadcn[shadcn/ui]
    end
    
    subgraph "API Gateway"
        APIGateway[API Gateway / Load Balancer]
    end
    
    subgraph "Backend Layer"
        FastAPI[FastAPI]
        Domain[Domain Layer]
        Application[Application Layer]
        Infrastructure[Infrastructure Layer]
    end
    
    subgraph "Agent System"
        Orchestrator[Agent Orchestrator]
        Agent1[Diagnosis Agent]
        Agent2[Documentation Agent]
        Agent3[History Agent]
    end
    
    subgraph "Knowledge System"
        KB[Knowledge Base]
        CB[Case Base]
        MB[Memory Base]
        DB[Document Base]
    end
    
    subgraph "Data Layer"
        Supabase[(Supabase PostgreSQL)]
        Qdrant[(Qdrant Vector DB)]
        Redis[(Redis Cache)]
        Storage[Supabase Storage]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Email[Email Service]
        Notifications[Notification Service]
    end
    
    subgraph "Observability"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Sentry[Sentry]
        Logs[Log Aggregation]
    end
    
    Browser --> NextJS
    NextJS --> APIGateway
    APIGateway --> FastAPI
    
    FastAPI --> Domain
    FastAPI --> Application
    FastAPI --> Infrastructure
    
    Application --> Orchestrator
    Orchestrator --> Agent1
    Orchestrator --> Agent2
    Orchestrator --> Agent3
    
    Agent1 --> KB
    Agent2 --> KB
    Agent3 --> CB
    Orchestrator --> MB
    
    Infrastructure --> Supabase
    Infrastructure --> Qdrant
    Infrastructure --> Redis
    Infrastructure --> Storage
    
    Agent1 --> OpenAI
    Agent2 --> OpenAI
    Agent3 --> OpenAI
    
    FastAPI --> Email
    FastAPI --> Notifications
    
    FastAPI --> Prometheus
    FastAPI --> Sentry
    NextJS --> Sentry
```

### Flujo de Datos

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Agent
    participant Knowledge
    participant Database
    
    User->>Frontend: Request
    Frontend->>Backend: API Call
    Backend->>Backend: Validate Auth
    Backend->>Agent: Invoke Agent
    Agent->>Knowledge: Search Knowledge
    Knowledge->>Database: Query
    Database-->>Knowledge: Results
    Knowledge-->>Agent: Context
    Agent->>Agent: Process with LLM
    Agent-->>Backend: Response
    Backend->>Database: Store Interaction
    Backend-->>Frontend: Response
    Frontend-->>User: Display
```

---

## Arquitectura Frontend

### Estructura de Componentes

```mermaid
graph TB
    subgraph "Next.js App Router"
        Layout[Layout]
        Page[Pages]
        Loading[Loading States]
        Error[Error Boundaries]
    end
    
    subgraph "Components"
        UI[shadcn/ui Components]
        Forms[Form Components]
        Tables[Data Tables]
        Charts[Visualizations]
    end
    
    subgraph "State Management"
        Zustand[Zustand Store]
        ReactQuery[React Query]
        Context[React Context]
    end
    
    subgraph "Services"
        API[API Client]
        Auth[Auth Service]
        WebSocket[WebSocket Client]
    end
    
    subgraph "Hooks"
        Custom[Custom Hooks]
        Data[Data Hooks]
        UI[UI Hooks]
    end
    
    Layout --> Page
    Page --> UI
    Page --> Forms
    Page --> Tables
    Page --> Charts
    
    UI --> Zustand
    Forms --> Zustand
    Tables --> ReactQuery
    
    Page --> API
    Page --> Auth
    Page --> WebSocket
    
    Page --> Custom
    Custom --> Data
    Custom --> UI
```

### Arquitectura de Rutas

```mermaid
graph LR
    A[/] --> B[Dashboard]
    A --> C[Equipos]
    A --> D[Mantenimiento]
    A --> E[Casos]
    A --> F[Conocimiento]
    A --> G[Configuración]
    
    B --> B1[Overview]
    B --> B2[Alertas]
    B --> B3[Métricas]
    
    C --> C1[Inventario]
    C --> C2[Detalles]
    C --> C3[Historial]
    
    D --> D1[Órdenes]
    D --> D2[Calendario]
    D --> D3[Reportes]
    
    E --> E1[Buscar Casos]
    E --> E2[Crear Caso]
    E --> E3[Similares]
    
    F --> F1[Manuales]
    F --> F2[Protocolos]
    F --> F3[Normativas]
    
    G --> G1[Usuarios]
    G --> G2[Permisos]
    G --> G3[Integraciones]
```

---

## Arquitectura Backend

### Capas de Clean Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        HTTP[HTTP Endpoints]
        WebSocket[WebSocket Endpoints]
        DTOs[DTOs]
        Validators[Validators]
    end
    
    subgraph "Application Layer"
        UseCases[Use Cases]
        Commands[Commands]
        Queries[Queries]
        Handlers[Handlers]
    end
    
    subgraph "Domain Layer"
        Entities[Entities]
        ValueObjects[Value Objects]
        DomainServices[Domain Services]
        Events[Domain Events]
        Repositories[Repository Interfaces]
    end
    
    subgraph "Infrastructure Layer"
        DBRepositories[DB Repositories]
        ExternalServices[External Services]
        MessageQueue[Message Queue]
        Cache[Cache Implementation]
    end
    
    HTTP --> DTOs
    HTTP --> Validators
    HTTP --> UseCases
    
    WebSocket --> UseCases
    
    UseCases --> Commands
    UseCases --> Queries
    UseCases --> Handlers
    
    Commands --> DomainServices
    Queries --> DomainServices
    
    DomainServices --> Entities
    DomainServices --> ValueObjects
    DomainServices --> Events
    DomainServices --> Repositories
    
    Repositories --> DBRepositories
    Repositories --> ExternalServices
    Repositories --> Cache
    
    Events --> MessageQueue
```

### Vertical Slice Architecture

```mermaid
graph LR
    subgraph "Equipment Slice"
        EAPI[Equipment API]
        EUC[Equipment Use Cases]
        ED[Equipment Domain]
        EI[Equipment Infrastructure]
    end
    
    subgraph "Maintenance Slice"
        MAPI[Maintenance API]
        MUC[Maintenance Use Cases]
        MD[Maintenance Domain]
        MI[Maintenance Infrastructure]
    end
    
    subgraph "Case Slice"
        CAPI[Case API]
        CUC[Case Use Cases]
        CD[Case Domain]
        CI[Case Infrastructure]
    end
    
    subgraph "Shared"
        SharedDomain[Shared Domain]
        SharedInfra[Shared Infrastructure]
    end
    
    EAPI --> EUC
    EUC --> ED
    EUC --> EI
    ED --> SharedDomain
    
    MAPI --> MUC
    MUC --> MD
    MUC --> MI
    MD --> SharedDomain
    
    CAPI --> CUC
    CUC --> CD
    CUC --> CI
    CD --> SharedDomain
    
    EI --> SharedInfra
    MI --> SharedInfra
    CI --> SharedInfra
```

---

## Sistema Multiagente

### Arquitectura de Agentes

```mermaid
graph TB
    subgraph "User Request"
        Input[User Input]
        Context[Context]
    end
    
    subgraph "Orchestrator"
        Router[Intent Router]
        Planner[Task Planner]
        Coordinator[Agent Coordinator]
        Synthesizer[Response Synthesizer]
    end
    
    subgraph "Specialist Agents"
        Diagnosis[Diagnosis Agent]
        Documentation[Documentation Agent]
        History[History Agent]
        Prediction[Prediction Agent]
        Purchasing[Purchasing Agent]
    end
    
    subgraph "Tool Registry"
        Tool1[Equipment Search]
        Tool2[Manual Retrieval]
        Tool3[Case Search]
        Tool4[Data Analysis]
        Tool5[Inventory Check]
    end
    
    subgraph "Memory System"
        ShortTerm[Short-term Memory]
        LongTerm[Long-term Memory]
        Episodic[Episodic Memory]
    end
    
    subgraph "Permission System"
        Auth[Authentication]
        Authz[Authorization]
        Audit[Audit Logging]
    end
    
    Input --> Router
    Context --> Router
    
    Router --> Planner
    Planner --> Coordinator
    
    Coordinator --> Diagnosis
    Coordinator --> Documentation
    Coordinator --> History
    Coordinator --> Prediction
    Coordinator --> Purchasing
    
    Diagnosis --> Tool1
    Diagnosis --> Tool2
    Documentation --> Tool2
    History --> Tool3
    Prediction --> Tool4
    Purchasing --> Tool5
    
    Diagnosis --> ShortTerm
    Documentation --> ShortTerm
    History --> LongTerm
    
    Coordinator --> Synthesizer
    Synthesizer --> Authz
    Authz --> Audit
```

### Flujo de Orquestación

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Agent1
    participant Agent2
    participant Tool
    participant Memory
    participant LLM
    
    User->>Orchestrator: Query
    Orchestrator->>Orchestrator: Analyze Intent
    Orchestrator->>Agent1: Invoke
    Agent1->>Tool: Use Tool
    Tool-->>Agent1: Result
    Agent1->>Memory: Store Context
    Agent1->>LLM: Process
    LLM-->>Agent1: Response
    Agent1-->>Orchestrator: Result
    Orchestrator->>Agent2: Invoke
    Agent2->>Memory: Retrieve Context
    Agent2->>LLM: Process
    LLM-->>Agent2: Response
    Agent2-->>Orchestrator: Result
    Orchestrator->>Orchestrator: Synthesize
    Orchestrator-->>User: Final Response
```

---

## Sistema de Conocimiento

### Arquitectura de Bases de Conocimiento

```mermaid
graph TB
    subgraph "Knowledge Base (KB)"
        Manuals[Technical Manuals]
        Specs[Equipment Specs]
        Procedures[Procedures]
        KBIndex[Vector Index]
    end
    
    subgraph "Case Base (CB)"
        Cases[Solved Cases]
        Solutions[Solutions]
        Patterns[Failure Patterns]
        CBIndex[Vector Index]
    end
    
    subgraph "Memory Base (MB)"
        Conversations[Conversation History]
        Context[User Context]
        Preferences[User Preferences]
        MBIndex[Vector Index]
    end
    
    subgraph "Learning Base (LB)"
        Models[ML Models]
        Features[Extracted Features]
        Predictions[Predictions]
        LBIndex[Vector Index]
    end
    
    subgraph "Document Base (DB)"
        Protocols[Protocols]
        Regulations[Regulations]
        Standards[Standards]
        DBIndex[Vector Index]
    end
    
    subgraph "Unified Search"
        SearchRouter[Search Router]
        HybridSearch[Hybrid Search]
        Reranker[Reranker]
    end
    
    subgraph "Qdrant"
        Collections[Vector Collections]
        Payload[Payload Data]
        Filters[Filters]
    end
    
    Manuals --> KBIndex
    Specs --> KBIndex
    Procedures --> KBIndex
    
    Cases --> CBIndex
    Solutions --> CBIndex
    Patterns --> CBIndex
    
    Conversations --> MBIndex
    Context --> MBIndex
    Preferences --> MBIndex
    
    Models --> LBIndex
    Features --> LBIndex
    Predictions --> LBIndex
    
    Protocols --> DBIndex
    Regulations --> DBIndex
    Standards --> DBIndex
    
    KBIndex --> SearchRouter
    CBIndex --> SearchRouter
    MBIndex --> SearchRouter
    LBIndex --> SearchRouter
    DBIndex --> SearchRouter
    
    SearchRouter --> HybridSearch
    HybridSearch --> Collections
    Collections --> Reranker
    Reranker --> Payload
    Payload --> Filters
```

### Flujo de Búsqueda de Conocimiento

```mermaid
sequenceDiagram
    participant Agent
    participant SearchRouter
    participant KB
    participant CB
    participant Qdrant
    participant Reranker
    participant Agent
    
    Agent->>SearchRouter: Query
    SearchRouter->>SearchRouter: Classify Query
    SearchRouter->>KB: Search KB
    SearchRouter->>CB: Search CB
    
    KB->>Qdrant: Vector Search
    CB->>Qdrant: Vector Search
    
    Qdrant-->>KB: Results
    Qdrant-->>CB: Results
    
    KB-->>SearchRouter: KB Results
    CB-->>SearchRouter: CB Results
    
    SearchRouter->>Reranker: Rerank Results
    Reranker-->>SearchRouter: Ranked Results
    SearchRouter-->>Agent: Final Results
```

---

## Base de Datos

### Arquitectura de Datos

```mermaid
graph TB
    subgraph "Supabase PostgreSQL"
        Users[Users Table]
        Hospitals[Hospitals Table]
        Equipment[Equipment Table]
        Maintenance[Maintenance Orders]
        Cases[Cases Table]
        Documents[Documents Table]
        Audit[Audit Log]
    end
    
    subgraph "Qdrant Vector DB"
        KBVectors[KB Vectors]
        CBVectors[CB Vectors]
        MBVectors[MB Vectors]
        DBVectors[DB Vectors]
    end
    
    subgraph "Redis Cache"
        SessionCache[Session Cache]
        QueryCache[Query Cache]
        RateLimit[Rate Limiting]
    end
    
    subgraph "Supabase Storage"
        Manuals[Manuals Bucket]
        Documents[Documents Bucket]
        Images[Images Bucket]
    end
    
    Users --> Hospitals
    Equipment --> Hospitals
    Equipment --> Maintenance
    Maintenance --> Cases
    Documents --> Equipment
    
    Equipment --> KBVectors
    Cases --> CBVectors
    Audit --> MBVectors
    Documents --> DBVectors
    
    Users --> SessionCache
    Equipment --> QueryCache
    API --> RateLimit
    
    Equipment --> Manuals
    Documents --> Documents
    Equipment --> Images
```

### Esquema de Base de Datos Relacional

```mermaid
erDiagram
    HOSPITALS ||--o{ USERS : has
    HOSPITALS ||--o{ EQUIPMENT : owns
    HOSPITALS ||--o{ MAINTENANCE_ORDERS : manages
    HOSPITALS ||--o{ CASES : records
    
    USERS ||--o{ MAINTENANCE_ORDERS : creates
    USERS ||--o{ CASES : submits
    USERS ||--o{ AUDIT_LOG : generates
    
    EQUIPMENT ||--o{ MAINTENANCE_ORDERS : requires
    EQUIPMENT ||--o{ CASES : involves
    EQUIPMENT ||--o{ DOCUMENTS : has
    
    MAINTENANCE_ORDERS ||--|| CASES : resolves
    
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : has
    
    HOSPITALS {
        uuid id PK
        string name
        string code
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    USERS {
        uuid id PK
        uuid hospital_id FK
        string email
        string name
        string role
        jsonb permissions
        timestamp created_at
        timestamp updated_at
    }
    
    EQUIPMENT {
        uuid id PK
        uuid hospital_id FK
        string serial_number
        string model
        string manufacturer
        string category
        jsonb specifications
        timestamp purchased_at
        timestamp created_at
        timestamp updated_at
    }
    
    MAINTENANCE_ORDERS {
        uuid id PK
        uuid equipment_id FK
        uuid hospital_id FK
        uuid assigned_to FK
        string status
        string priority
        text description
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    CASES {
        uuid id PK
        uuid equipment_id FK
        uuid hospital_id FK
        uuid submitted_by FK
        uuid maintenance_order_id FK
        text symptoms
        text diagnosis
        text solution
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    DOCUMENTS {
        uuid id PK
        uuid equipment_id FK
        string title
        string type
        string storage_path
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    AUDIT_LOG {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        jsonb changes
        timestamp created_at
    }
```

---

## Autenticación y Autorización

### Flujo de Autenticación

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant SupabaseAuth
    participant Backend
    participant Database
    
    User->>Frontend: Login Request
    Frontend->>SupabaseAuth: Auth Request
    SupabaseAuth->>SupabaseAuth: Validate Credentials
    SupabaseAuth-->>Frontend: JWT Token
    Frontend->>Frontend: Store Token
    Frontend->>Backend: API Request + Token
    Backend->>Backend: Validate JWT
    Backend->>Database: Fetch User + Permissions
    Database-->>Backend: User Data
    Backend->>Backend: Check Permissions
    Backend-->>Frontend: Response
    Frontend-->>User: Display
```

### Modelo de Autorización

```mermaid
graph TB
    subgraph "Roles"
        Admin[Admin]
        Manager[Manager]
        Engineer[Engineer]
        Technician[Technician]
        Viewer[Viewer]
    end
    
    subgraph "Permissions"
        P1[Create Equipment]
        P2[Edit Equipment]
        P3[Delete Equipment]
        P4[View Equipment]
        P5[Create Maintenance]
        P6[Edit Maintenance]
        P7[Delete Maintenance]
        P8[View Maintenance]
        P9[Create Cases]
        P10[View Cases]
        P11[Use AI Agents]
        P12[Manage Users]
    end
    
    subgraph "Resources"
        R1[Equipment]
        R2[Maintenance Orders]
        R3[Cases]
        R4[Documents]
        R5[Users]
    end
    
    Admin --> P1
    Admin --> P2
    Admin --> P3
    Admin --> P4
    Admin --> P5
    Admin --> P6
    Admin --> P7
    Admin --> P8
    Admin --> P9
    Admin --> P10
    Admin --> P11
    Admin --> P12
    
    Manager --> P1
    Manager --> P2
    Manager --> P4
    Manager --> P5
    Manager --> P6
    Manager --> P8
    Manager --> P9
    Manager --> P10
    Manager --> P11
    
    Engineer --> P4
    Engineer --> P5
    Engineer --> P8
    Engineer --> P9
    Engineer --> P10
    Engineer --> P11
    
    Technician --> P4
    Technician --> P5
    Technician --> P8
    Technician --> P9
    Technician --> P10
    
    Viewer --> P4
    Viewer --> P8
    Viewer --> P10
    
    P1 --> R1
    P2 --> R1
    P3 --> R1
    P4 --> R1
    
    P5 --> R2
    P6 --> R2
    P7 --> R2
    P8 --> R2
    
    P9 --> R3
    P10 --> R3
    
    P12 --> R5
```

---

## Observabilidad

### Stack de Observabilidad

```mermaid
graph TB
    subgraph "Application"
        Frontend[Frontend Logs]
        Backend[Backend Logs]
        AgentLogs[Agent Logs]
    end
    
    subgraph "Logging"
        StructLog[Structured Logging]
        Context[Context Injection]
        Correlation[Correlation IDs]
    end
    
    subgraph "Tracing"
        OpenTelemetry[OpenTelemetry]
        Spans[Spans]
        Traces[Traces]
    end
    
    subgraph "Metrics"
        Prometheus[Prometheus]
        Counters[Counters]
        Gauges[Gauges]
        Histograms[Histograms]
    end
    
    subgraph "Error Tracking"
        Sentry[Sentry]
        Errors[Errors]
        Performance[Performance]
    end
    
    subgraph "Visualization"
        Grafana[Grafana Dashboards]
        Alerts[Alerts]
    end
    
    Frontend --> StructLog
    Backend --> StructLog
    AgentLogs --> StructLog
    
    StructLog --> Context
    Context --> Correlation
    
    Backend --> OpenTelemetry
    OpenTelemetry --> Spans
    Spans --> Traces
    
    Backend --> Prometheus
    Prometheus --> Counters
    Prometheus --> Gauges
    Prometheus --> Histograms
    
    Frontend --> Sentry
    Backend --> Sentry
    Sentry --> Errors
    Sentry --> Performance
    
    Prometheus --> Grafana
    Traces --> Grafana
    Errors --> Grafana
    
    Grafana --> Alerts
```

### Métricas Clave

```mermaid
graph LR
    subgraph "Business Metrics"
        BM1[Active Users]
        BM2[Cases Solved]
        BM3[Agent Accuracy]
        BM4[Response Time]
    end
    
    subgraph "Technical Metrics"
        TM1[Request Rate]
        TM2[Error Rate]
        TM3[Latency]
        TM4[Memory Usage]
    end
    
    subgraph "Infrastructure Metrics"
        IM1[CPU Usage]
        IM2[Disk Usage]
        IM3[Network I/O]
        IM4[Container Health]
    end
    
    subgraph "AI Metrics"
        AIM1[Token Usage]
        AIM2[Agent Success Rate]
        AIM3[Confidence Scores]
        AIM4[Hallucination Rate]
    end
```

---

## Seguridad

### Capas de Seguridad

```mermaid
graph TB
    subgraph "Network Security"
        Firewall[Firewall]
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]
        SSL[TLS/SSL]
    end
    
    subgraph "Application Security"
        Auth[Authentication]
        Authz[Authorization]
        InputValidation[Input Validation]
        OutputEncoding[Output Encoding]
    end
    
    subgraph "Data Security"
        EncryptionAtRest[Encryption at Rest]
        EncryptionInTransit[Encryption in Transit]
        RLS[Row Level Security]
        BackupEncryption[Backup Encryption]
    end
    
    subgraph "AI Security"
        PromptInjection[Prompt Injection Protection]
        RateLimiting[Rate Limiting]
        ContentFiltering[Content Filtering]
        AuditLogging[Audit Logging]
    end
    
    subgraph "Compliance"
        HIPAA[HIPAA Compliance]
        GDPR[GDPR Compliance]
        Audit[Audit Trails]
        Retention[Data Retention]
    end
    
    Firewall --> Auth
    WAF --> InputValidation
    DDoS --> RateLimiting
    SSL --> EncryptionInTransit
    
    Auth --> Authz
    Authz --> RLS
    
    InputValidation --> OutputEncoding
    
    EncryptionAtRest --> BackupEncryption
    EncryptionInTransit --> RLS
    
    PromptInjection --> ContentFiltering
    RateLimiting --> AuditLogging
    
    RLS --> HIPAA
    AuditLogging --> GDPR
    AuditLogging --> Audit
    BackupEncryption --> Retention
```

---

## Infraestructura

### Arquitectura de Despliegue

```mermaid
graph TB
    subgraph "Development"
        DevLocal[Local Development]
        DockerCompose[Docker Compose]
        DevEnv[Dev Environment]
    end
    
    subgraph "Staging"
        StagingCluster[Staging Cluster]
        StagingDB[Staging Database]
        StagingCache[Staging Cache]
    end
    
    subgraph "Production"
        LoadBalancer[Load Balancer]
        WebServers[Web Servers]
        AppServers[App Servers]
        WorkerNodes[Worker Nodes]
        DatabaseCluster[Database Cluster]
        CacheCluster[Cache Cluster]
        CDN[CDN]
    end
    
    subgraph "CI/CD"
        GitHubActions[GitHub Actions]
        Build[Build]
        Test[Test]
        Deploy[Deploy]
        Monitor[Monitor]
    end
    
    DevLocal --> DockerCompose
    DockerCompose --> DevEnv
    
    DevEnv --> GitHubActions
    GitHubActions --> Build
    Build --> Test
    Test --> StagingCluster
    Test --> Deploy
    
    Deploy --> LoadBalancer
    LoadBalancer --> WebServers
    LoadBalancer --> AppServers
    
    AppServers --> WorkerNodes
    AppServers --> DatabaseCluster
    AppServers --> CacheCluster
    
    WebServers --> CDN
    
    StagingCluster --> Monitor
    Production --> Monitor
```

### Arquitectura de Contenedores

```mermaid
graph TB
    subgraph "Docker Containers"
        FrontendContainer[Frontend Container]
        BackendContainer[Backend Container]
        WorkerContainer[Worker Container]
        QdrantContainer[Qdrant Container]
        RedisContainer[Redis Container]
        PrometheusContainer[Prometheus Container]
        GrafanaContainer[Grafana Container]
    end
    
    subgraph "Docker Networks"
        FrontendNetwork[Frontend Network]
        BackendNetwork[Backend Network]
        DataNetwork[Data Network]
        MonitoringNetwork[Monitoring Network]
    end
    
    subgraph "Volumes"
        FrontendVolume[Frontend Volume]
        BackendVolume[Backend Volume]
        QdrantVolume[Qdrant Volume]
        RedisVolume[Redis Volume]
        LogsVolume[Logs Volume]
    end
    
    FrontendContainer --> FrontendNetwork
    BackendContainer --> FrontendNetwork
    BackendContainer --> BackendNetwork
    WorkerContainer --> BackendNetwork
    
    BackendContainer --> DataNetwork
    QdrantContainer --> DataNetwork
    RedisContainer --> DataNetwork
    
    PrometheusContainer --> MonitoringNetwork
    GrafanaContainer --> MonitoringNetwork
    
    FrontendContainer --> FrontendVolume
    BackendContainer --> BackendVolume
    QdrantContainer --> QdrantVolume
    RedisContainer --> RedisVolume
    BackendContainer --> LogsVolume
    WorkerContainer --> LogsVolume
```

---

## Resumen

Esta arquitectura está diseñada para:

1. **Escalabilidad Horizontal**: Cada componente puede escalar independientemente
2. **Seguridad Robusta**: Múltiples capas de seguridad y compliance
3. **IA Responsable**: Toda acción trazable y auditable
4. **Mantenibilidad**: Arquitectura limpia con separación de responsabilidades
5. **Observabilidad Completa**: Logging, tracing, y metrics en todos los niveles
6. **Flexibilidad**: Preparado para evolución a microservicios si necesario

La arquitectura sigue principios de Clean Architecture, DDD, y Vertical Slice Architecture, asegurando que el proyecto pueda evolucionar durante 10+ años sin reescrituras mayores.

---

**Última actualización**: 2026-07-10
**Autor**: Lead Architect (Cascade)
**Versión**: 1.0.0
