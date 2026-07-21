# ADR-2119: Gateway Methods Implementation

**Estado:** ACEPTADO  
**Fecha:** Julio 2026  
**Decisor:** Arquitectura EREN  
**Epic:** EPIC 11.1

---

## 📋 Resumen

Decidir qué hacer con los 11 métodos `NotImplementedError` encontrados en los gateways durante la auditoría.

---

## 🎯 Métodos Identificados

| # | Gateway | Método | Criticidad | Decisión |
|---|---------|--------|------------|-----------|
| 1 | IncidentGateway | get_history | 🟡 MODERADA | Implementar |
| 2 | IncidentGateway | analyze | 🟡 MODERADA | Implementar |
| 3 | KnowledgeGateway | get_related | 🟢 BAJA | Mantener (justificado) |
| 4 | KnowledgeGateway | get_by_confidence | 🟢 BAJA | Mantener (justificado) |
| 5 | RecommendationGateway | generate | 🟡 MODERADA | Implementar |
| 6 | RecommendationGateway | get_by_device | 🟡 MODERADA | Implementar |
| 7 | HospitalGateway | get_by_id | 🔴 ALTA | Implementar |
| 8 | HospitalGateway | get_capacity | 🔴 ALTA | Implementar |
| 9 | HospitalGateway | get_available_beds | 🟡 MODERADA | Implementar |
| 10 | WorkOrderGateway | get_sla_breached | 🟡 MODERADA | Implementar |
| 11 | WorkOrderGateway | get_sla_breached | 🟡 MODERADA | Implementar |

---

## 📊 Análisis por Criticidad

### 🔴 ALTA - Implementar Inmediatamente

#### HospitalGateway.get_by_id

**Razón:** HospitalContextProvider usa este método para mostrar información del campus.

```python
# En HospitalContextProvider._get_hospital_safe()
hospital = await self._hospital.get_by_id(hospital_id, tenant_id)
```

**Implementación requerida:**
```python
async def get_by_id(
    self,
    hospital_id: str,
    tenant_id: str,
) -> "HospitalDTO | None":
    """Obtiene campus/hospital por ID."""
    self._validate_tenant(tenant_id, "get_by_id")
    from core.ai.domain import HospitalDTO

    async with self._uow_factory() as uow:
        model = await uow.capacity.get_hospital_by_id(hospital_id, tenant_id)
        if model is None:
            return None
        return HospitalDTO(
            id=str(model.id),
            name=model.name,
            address=model.address,
            campus_type=model.campus_type,
        )
```

#### HospitalGateway.get_capacity

**Razón:** Es la funcionalidad core de HospitalContextProvider.

```python
# En HospitalContextProvider.get_context()
capacity = await self._hospital.get_capacity(campus_id, tenant_id)
```

**Implementación requerida:**
```python
async def get_capacity(
    self,
    campus_id: str,
    tenant_id: str,
) -> dict:
    """Obtiene información de capacidad."""
    self._validate_tenant(tenant_id, "get_capacity")

    async with self._uow_factory() as uow:
        # Obtener floors
        floors, _ = await uow.capacity.list_floors(campus_id, tenant_id)
        
        # Calcular ocupación
        total_beds = 0
        occupied_beds = 0
        available_beds = 0
        
        for floor in floors:
            beds, _ = await uow.capacity.list_beds(floor.id, tenant_id)
            for bed in beds:
                total_beds += 1
                if bed.status == "occupied":
                    occupied_beds += 1
                elif bed.status == "available":
                    available_beds += 1
        
        return {
            "campus_id": campus_id,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "occupancy_rate": occupied_beds / total_beds if total_beds > 0 else 0,
        }
```

---

### 🟡 MODERADA - Implementar en EPIC 11.1

#### IncidentGateway.get_history

**Razón:** Útil para análisis de tendencias.

```python
# Implementación requerida
async def get_history(
    self,
    device_id: str,
    tenant_id: str,
    limit: int = 50,
) -> list["IncidentDTO"]:
    """Obtiene historial de incidentes para un dispositivo."""
    self._validate_tenant(tenant_id, "get_history")
    
    async with self._uow_factory() as uow:
        models, _ = await uow.incidents.list_by_tenant(
            tenant_id=tenant_id,
            page=1,
            page_size=limit,
            device_id_filter=device_id,
        )
        return [self._incident_to_dto(m) for m in models]
```

#### IncidentGateway.analyze

**Razón:** Para generar insights de incidentes.

```python
async def analyze(
    self,
    incident_id: str,
    tenant_id: str,
) -> dict:
    """Analiza incidente y devuelve insights."""
    self._validate_tenant(tenant_id, "analyze")
    
    async with self._uow_factory() as uow:
        incident = await uow.incidents.get_by_id(incident_id, tenant_id)
        if not incident:
            return {"error": "Incident not found"}
        
        # Análisis de patrones
        similar, _ = await uow.incidents.list_by_tenant(
            tenant_id=tenant_id,
            device_id_filter=str(incident.device_id),
            severity_filter=incident.severity,
        )
        
        return {
            "incident_id": incident_id,
            "patterns_found": len(similar),
            "similar_incidents": [str(s.id) for s in similar[:5]],
            "suggestions": self._generate_suggestions(incident, similar),
        }
```

#### RecommendationGateway.get_by_device

**Razón:** Para mostrar recomendaciones específicas de dispositivo.

```python
async def get_by_device(
    self,
    device_id: str,
    tenant_id: str,
    min_confidence: float = 0.5,
    limit: int = 10,
) -> list["RecommendationDTO"]:
    """Obtiene recomendaciones para un dispositivo."""
    self._validate_tenant(tenant_id, "get_by_device")
    
    async with self._uow_factory() as uow:
        models, _ = await uow.recommendations.list_by_tenant(
            tenant_id=tenant_id,
            page=1,
            page_size=limit,
            device_id_filter=device_id,
            min_confidence=min_confidence,
        )
        return [self._model_to_dto(m) for m in models]
```

#### RecommendationGateway.generate

**Razón:** Core functionality para AI recommendations.

```python
async def generate(
    self,
    device_id: str,
    tenant_id: str,
    context: dict | None = None,
) -> "RecommendationDTO":
    """Genera nueva recomendación para dispositivo."""
    self._validate_tenant(tenant_id, "generate")
    
    # Esta es la funcionalidad "AI" real
    # Por ahora, generar mock con lógica simple
    from uuid import uuid4
    
    return RecommendationDTO(
        id=str(uuid4()),
        device_id=device_id,
        title="Recommended Maintenance",
        description=f"Based on device history, maintenance is recommended.",
        confidence_score=0.75,
        model_version="v1.0",
        created_at=datetime.utcnow().isoformat(),
    )
```

#### HospitalGateway.get_available_beds

**Razón:** Para gestión de capacidad.

```python
async def get_available_beds(
    self,
    campus_id: str,
    tenant_id: str,
    floor_id: str | None = None,
) -> list[dict]:
    """Obtiene camas disponibles."""
    self._validate_tenant(tenant_id, "get_available_beds")
    
    async with self._uow_factory() as uow:
        beds, _ = await uow.capacity.list_beds(floor_id or campus_id, tenant_id)
        available = [b for b in beds if b.status == "available"]
        return [
            {
                "id": str(b.id),
                "bed_number": b.bed_number,
                "floor_id": str(b.floor_id),
                "room": b.room,
            }
            for b in available
        ]
```

#### WorkOrderGateway.get_sla_breached

**Razón:** Para dashboard de KPIs.

```python
async def get_sla_breached(
    self,
    tenant_id: str,
    limit: int = 20,
) -> list["WorkOrderDTO"]:
    """Obtiene órdenes con SLA incumplido."""
    self._validate_tenant(tenant_id, "get_sla_breached")
    
    async with self._uow_factory() as uow:
        # WorkOrderRepository tiene list_overdue()
        models = await uow.work_orders.list_overdue(tenant_id)
        return [self._model_to_dto(m) for m in models[:limit]]
```

---

### 🟢 BAJA - Mantener con Justificación

#### KnowledgeGateway.get_related

**Razón:** No es usado por ningún provider actualmente.

**Justificación para mantener NotImplementedError:**
```python
async def get_related(
    self,
    article_id: str,
    tenant_id: str,
    limit: int = 5,
) -> list["KnowledgeArticleDTO"]:
    """
    Obtiene artículos relacionados.
    
    NOT IMPLEMENTED: No hay provider que use este método.
    Si en el futuro KnowledgeContextProvider necesita artículos
    relacionados, implementar usando KnowledgeRepository.get_related().
    """
    raise NotImplementedError(
        "get_related not implemented. "
        "Implement when KnowledgeContextProvider needs related articles."
    )
```

#### KnowledgeGateway.get_by_confidence

**Razón:** No hay caso de uso claro.

**Justificación:**
```python
async def get_by_confidence(
    self,
    tenant_id: str,
    min_confidence: float = 0.8,
    limit: int = 10,
) -> list["KnowledgeArticleDTO"]:
    """
    Obtiene artículos por confidence score.
    
    NOT IMPLEMENTED: No hay caso de uso para filtrar por confidence.
    Knowledge articles no tienen scores de confidence.
    """
    raise NotImplementedError(
        "get_by_confidence not implemented. "
        "Knowledge articles don't have confidence scores."
    )
```

---

## 📋 Resumen de Implementación

| Método | Prioridad | Archivo |
|--------|-----------|---------|
| HospitalGateway.get_by_id | 🔴 ALTA | domain_adapter.py |
| HospitalGateway.get_capacity | 🔴 ALTA | domain_adapter.py |
| IncidentGateway.get_history | 🟡 MODERADA | domain_adapter.py |
| IncidentGateway.analyze | 🟡 MODERADA | domain_adapter.py |
| RecommendationGateway.get_by_device | 🟡 MODERADA | domain_adapter.py |
| RecommendationGateway.generate | 🟡 MODERADA | domain_adapter.py |
| HospitalGateway.get_available_beds | 🟡 MODERADA | domain_adapter.py |
| WorkOrderGateway.get_sla_breached | 🟡 MODERADA | domain_adapter.py |
| KnowledgeGateway.get_related | 🟢 BAJA | Mantener con justificación |
| KnowledgeGateway.get_by_confidence | 🟢 BAJA | Mantener con justificación |
| WorkOrderGateway.get_sla_breached (duplicado) | 🟡 MODERADA | Ya listado arriba |

---

## ✅ Verificación

```python
# Verificar que métodos existen y no lanzan NotImplementedError
async with uow_factory() as uow:
    gateway = HospitalGatewayImpl(uow)
    
    # Estos deben funcionar
    hospital = await gateway.get_by_id("campus-1", "tenant-1")
    capacity = await gateway.get_capacity("campus-1", "tenant-1")
    
    # Este debe lanzar NotImplementedError con mensaje claro
    try:
        await gateway.get_related("article-1", "tenant-1")
    except NotImplementedError as e:
        assert "get_related not implemented" in str(e)
```
