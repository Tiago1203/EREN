# core/scheduler - Task Scheduler

## Descripción

Planificador de tareas para EREN OS.

## Responsabilidad

- Planificar tareas
- Gestionar prioridades
- Ejecutar tareas programadas

## Uso

```python
from core.scheduler import TaskScheduler

scheduler = TaskScheduler()
scheduler.schedule(task, delay=timedelta(hours=1))
```

## Límites

- **Puede depender de:** events, container
- **Nunca depende de:** UI

---
*Architecture only*
