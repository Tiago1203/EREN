# EREN OS System Overview

**Fecha:** 2026-07-14  
**Versión:** 1.0

---

## 1. ARQUITECTURA GENERAL

### 1.1 Diagrama de Componentes

```mermaid
flowchart TB
    subgraph APPS["Aplicaciones"]
        API[API]
        WEB[Web]
        DESKTOP[Desktop]
    end
    
    subgraph SDK["SDK Layer"]
        CAPABILITY[Capability SDK]
    end
    
    subgraph ORCH["Orchestrator"]
        ORCH_ENGINE[Orchestrator Engine]
        ORCH_CONTRACTS[Orchestration Contracts]
    end
    
    subgraph PLATFORMS["Platforms"]
        MEMORY[Memory]
        REASONING[Reasoning]
        PLANNING[Planning]
        WORKFLOWS[Workflows]
        KNOWLEDGE[Knowledge]
        DIAGNOSTICS[Diagnostics]
        AGENTS[Agents]
        TOOLS[Tools]
    end
    
    subgraph ENGINES["Engines"]
        RETRIEVAL[Retrieval]
        DECISION[Decision]
        EXECUTION[Execution]
        EMBEDDINGS[Embeddings]
    end
    
    subgraph INFRA["Infrastructure"]
        CONTAINER[Container]
        EVENTS[Event Bus]
        COMPOSITION[Composition Root]
        BOOT[Boot Manager]
        RUNTIME[Runtime]
        LIFECYCLE[Lifecycle]
    end
    
    subgraph CONTRACTS["Contracts"]
        BASE[Base Contracts]
    end
    
    APPS --> SDK
    SDK --> ORCH
    ORCH --> PLATFORMS
    PLATFORMS --> ENGINES
    PLATFORMS --> INFRA
    ENGINES --> INFRA
    INFRA --> CONTRACTS
```

---

## 2. CICLO COGNITIVO

### 2.1 Diagrama del Ciclo

```mermaid
flowchart LR
    subgraph INPUT["Entrada"]
        USER[User Input]
        CONTEXT[Context]
    end
    
    subgraph PROCESS["Procesamiento"]
        ORCH[Orchestrator]
        PLAN[Planner]
        REASON[Reasoning]
        RETRIEVE[Retrieval]
        DECIDE[Decision]
    end
    
    subgraph OUTPUT["Salida"]
        RESPONSE[Response]
        ACTION[Action]
    end
    
    INPUT --> ORCH
    ORCH --> PLAN
    PLAN --> REASON
    REASON --> RETRIEVE
    RETRIEVE --> DECIDE
    DECIDE --> OUTPUT
```

---

## 3. ARQUITECTURA DE CAPAS

### 3.1 Diagrama de Capas

```mermaid
flowchart TB
    subgraph L7["Layer 7: Aplicaciones"]
        APP[Apps]
    end
    
    subgraph L6["Layer 6: SDK"]
        SDK[SDK]
    end
    
    subgraph L5["Layer 5: Orquestación"]
        ORCH[Orchestrator]
    end
    
    subgraph L4["Layer 4: Plataformas"]
        PLAT[Platforms]
    end
    
    subgraph L3["Layer 3: Motores"]
        ENG[Engines]
    end
    
    subgraph L2["Layer 2: Infraestructura"]
        INFRA[Infrastructure]
    end
    
    subgraph L1["Layer 1: Contratos"]
        CONTRACTS[Contracts]
    end
    
    L7 --> L6
    L6 --> L5
    L5 --> L4
    L4 --> L3
    L3 --> L2
    L2 --> L1
```

---

## 4. EVENT BUS

### 4.1 Diagrama de Eventos

```mermaid
flowchart LR
    subgraph PUBLISHERS["Publishers"]
        P1[Memory]
        P2[Reasoning]
        P3[Planning]
        P4[Workflows]
    end
    
    subgraph BUS["Event Bus"]
        CORE[Core Events]
        DIAG[Diagnostic Events]
        LIFECYCLE[Lifecycle Events]
    end
    
    subgraph SUBSCRIBERS["Subscribers"]
        S1[Orchestrator]
        S2[Metrics]
        S3[Logging]
        S4[Tracing]
    end
    
    PUBLISHERS --> BUS
    BUS --> SUBSCRIBERS
```

---

## 5. DEPENDENCY INJECTION

### 5.1 Diagrama del Container

```mermaid
flowchart TB
    subgraph ROOT["Composition Root"]
        CR[Composition Root]
    end
    
    subgraph CONTAINER["DI Container"]
        REGISTRY[Service Registry]
        GRAPH[Dependency Graph]
        VALIDATOR[Dependency Validator]
    end
    
    subgraph SCOPES["Scopes"]
        APP[Application Scope]
        REQUEST[Request Scope]
        SESSION[Session Scope]
    end
    
    CR --> CONTAINER
    CONTAINER --> REGISTRY
    CONTAINER --> GRAPH
    CONTAINER --> VALIDATOR
    REGISTRY --> SCOPES
```

---

## 6. PLATAFORMAS

### 6.1 Cognitive Memory Platform

```mermaid
flowchart TB
    subgraph MEMORY["Memory Platform"]
        ENGINE[Cognitive Memory Engine]
        COORD[Memory Coordinator]
        REGISTRY[Memory Registry]
        SELECTOR[Memory Selector]
    end
    
    subgraph STORES["Stores"]
        WORKING[Working Memory]
        SHORT[Short Term]
        LONG[Long Term]
    end
    
    ENGINE --> COORD
    COORD --> REGISTRY
    COORD --> SELECTOR
    SELECTOR --> STORES
```

### 6.2 Cognitive Reasoning Platform

```mermaid
flowchart TB
    subgraph REASONING["Reasoning Platform"]
        PLATFORM[Reasoning Platform]
        INFERENCE[Inference Engine]
        EVIDENCE[Evidence Engine]
        HYPOTHESIS[Hypothesis Manager]
        CONFIDENCE[Confidence Engine]
    end
    
    PLATFORM --> INFERENCE
    PLATFORM --> EVIDENCE
    PLATFORM --> HYPOTHESIS
    PLATFORM --> CONFIDENCE
```

---

## 7. WORKFLOW PLATFORM

### 7.1 Arquitectura de Workflows

```mermaid
flowchart LR
    subgraph CREATE["Creación"]
        DEF[Definition]
        GRAPH[Execution Graph]
    end
    
    subgraph EXECUTE["Ejecución"]
        RUNTIME[Runtime]
        SCHEDULER[Scheduler]
        EXECUTOR[Executor]
    end
    
    subgraph MANAGE["Gestión"]
        STATE[State Store]
        CHECKPOINT[Checkpoint Manager]
        RECOVERY[Recovery Manager]
    end
    
    CREATE --> EXECUTE
    EXECUTE --> MANAGE
    MANAGE --> EXECUTE
```

---

## 8. AGENT RUNTIME

### 8.1 Arquitectura de Agentes

```mermaid
flowchart TB
    subgraph RUNTIME["Agent Runtime"]
        AGENT[Agent Runtime]
        REGISTRY[Agent Registry]
        SCHEDULER[Agent Scheduler]
        COMM[Agent Communicator]
    end
    
    subgraph LIFECYCLE["Lifecycle"]
        STARTUP[Startup]
        HEALTH[Health Manager]
        SHUTDOWN[Shutdown]
    end
    
    subgraph CAPABILITIES["Capabilities"]
        REG[Capability Registry]
        RESOLVER[Capability Resolver]
    end
    
    RUNTIME --> REGISTRY
    RUNTIME --> SCHEDULER
    RUNTIME --> COMM
    RUNTIME --> LIFECYCLE
    RUNTIME --> CAPABILITIES
```

---

## 9. PROVIDER LAYER

### 9.1 Multi-Provider Architecture

```mermaid
flowchart TB
    subgraph MANAGER["Provider Manager"]
        SELECTOR[Provider Selector]
        REGISTRY[Provider Registry]
    end
    
    subgraph PROVIDERS["Providers"]
        OPENAI[OpenAI]
        CLAUDE[Claude]
        OLLAMA[Ollama]
        AZURE[Azure]
    end
    
    subgraph CONSUMERS["Consumers"]
        ENGINES[Engines]
        PLATFORMS[Platforms]
    end
    
    MANAGER --> PROVIDERS
    CONSUMERS --> MANAGER
```

---

## 10. BOOT SEQUENCE

### 10.1 Diagrama de Boot

```mermaid
flowchart TB
    START([Start]) --> CONFIG[Load Configuration]
    CONFIG --> CONTAINER[Create Container]
    CONTAINER --> EVENTS[Create Event Bus]
    EVENTS --> REGISTRY[Create Capability Registry]
    REGISTRY --> CONTEXT[Create Context Manager]
    CONTEXT --> MEMORY[Create Memory Engine]
    MEMORY --> KNOWLEDGE[Create Knowledge Engine]
    KNOWLEDGE --> TOOLS[Create Tool Engine]
    TOOLS --> PLANNER[Create Planner]
    PLANNER --> REASONING[Create Reasoning Engine]
    REASONING --> DECISION[Create Decision Engine]
    DECISION --> ORCHESTRATOR[Create Orchestrator]
    ORCHESTRATOR --> READY([Ready])
```

---

## 11. ESTADÍSTICAS

| Métrica | Valor |
|---------|-------|
| Módulos | 41 |
| Plataformas | 9 |
| Motores | 6 |
| Contratos | 9 |
| Líneas de código | ~107,000 |
| Archivos Python | 459 |

---

*Generado por Architecture Review Board*
