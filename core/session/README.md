# core/session - Session Manager

## Descripción

Gestión de sesiones de usuario en EREN OS.

## Responsabilidad

- Crear/borrar sesiones
- Gestionar estado de sesión
- Persistencia de sesión

## Uso

```python
from core.session import SessionManager

manager = SessionManager()
session = manager.create_session()
```

## Límites

- **Puede depender de:** events, storage
- **Nunca depende de:** UI

---
*Architecture only*
