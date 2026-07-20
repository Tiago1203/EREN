# Fases del Proyecto EREN

Índice de fases del proyecto.

---

## 📋 Fases

| Fase | Estado | Épicas | Carpeta |
|------|--------|--------|---------|
| **FASE 1** | ✅ COMPLETO | EPIC 0-3 | `PHASE_1/` |
| **FASE 2** | 🔜 PRÓXIMO | EPIC 4-6 | `PHASE_2/` |
| **FASE 3** | ⏳ PENDIENTE | EPIC 7 | `PHASE_3/` |
| **FASE 4** | ⏳ PENDIENTE | EPIC 8-10 | `PHASE_4/` |

---

## 📁 Estructura de Cada Fase

```
docs/phases/PHASE_X/
├── README.md           # Índice de la fase
├── PHASE_X_*.md       # Documento principal
├── epics/
│   ├── epic0/
│   ├── epic1/
│   └── ...
└── adr/
    ├── epic0/
    ├── epic1/
    └── ...
```

---

## 🚀 Empezar Nueva Fase

1. Leer el documento de la fase en `docs/phases/PHASE_X/README.md`
2. Revisar ADRs en `docs/phases/PHASE_X/adr/epicX/`
3. Revisar documentación en `docs/phases/PHASE_X/epics/epicX/`
4. Implementar código en `apps/api/app/` o `core/`
5. Crear PR

---

## 📂 Acceso Rápido

### FASE 1 (Completa)
- [README](./PHASE_1/README.md)
- [Documento Principal](./PHASE_1_FOUNDATION.md)
- [Épicas](./PHASE_1/epics/)
- [ADRs](./PHASE_1/adr/)

### FASE 2 (Próximo)
- [README](./PHASE_2/README.md)

### FASE 3
- [README](./PHASE_3/README.md)

### FASE 4
- [README](./PHASE_4/README.md)
