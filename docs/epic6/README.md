# EREN Epic 6 — Integrations

*Version 1.0 - 2026-07-20*

**Conectar EREN con el mundo.**

Epic 6 implementa la **Integration Layer** — conecta EREN con sistemas hospitalarios, dispositivos médicos y software empresarial.

---

## Purpose

Integrations proporciona:

- **Hospital Systems** — HL7, FHIR, DICOM
- **Medical Devices** — Philips, GE, Dräger, Mindray
- **Enterprise** — SAP, ServiceNow, Maximo, Azure AD

---

## Dependencies

**DEPENDE de:** EPIC 0, EPIC 1, EPIC 4, EPIC 5

**PREREQ de:** EPIC 7

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                            │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Hospital   │  │   Devices    │  │    Enterprise    │   │
│  │   Systems   │  │   Adapters   │  │     Adapters     │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────┐     ┌──────────────┐
│     EPIC 4       │  │  EPIC 3  │     │    EPIC 5    │
│   Cognitive      │  │  Hospital │     │   Clinical    │
│    Runtime       │  │  Contexts │     │  Intelligence │
└─────────────────┘  └──────────┘     └──────────────┘
```

---

## Components

### 1. Hospital Systems

| Component | Protocol | Description |
|-----------|----------|-------------|
| FHIR Client | REST | EHR interoperability |
| HL7 Listener | MLLP | ADT, MDM, ORU |
| DICOM Client | DICOM | Imaging PACS |

### 2. Medical Device Adapters

| Device | Protocol | Data |
|--------|----------|------|
| Philips IntelliVue | MQTT | Vitals, alarms |
| GE CARESCAPE | MQTT | Monitoring |
| Dräger Infinity | Network | Ventilation |
| Mindray eGateway | REST | Telemetry |

### 3. Enterprise Adapters

| System | Protocol | Use Case |
|--------|----------|----------|
| ServiceNow | REST | ITSM tickets |
| SAP | RFC/BAPI | ERP sync |
| Maximo | OSLC | Asset management |
| Azure AD | OAuth | SSO |

---

## ADR Index

12 ADRs document the architectural decisions:

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0600 | Integration Architecture | Accepted |
| ADR-0601 | FHIR R4 | Accepted |
| ADR-0602 | HL7 V2 | Accepted |
| ADR-0603 | DICOM | Accepted |
| ADR-0604 | Philips | Accepted |
| ADR-0605 | GE Healthcare | Accepted |
| ADR-0606 | Dräger | Accepted |
| ADR-0607 | Mindray | Accepted |
| ADR-0608 | ServiceNow | Accepted |
| ADR-0609 | SAP | Accepted |
| ADR-0610 | Maximo | Accepted |
| ADR-0611 | Azure AD | Accepted |

---

## Status

**Epic 6 Status:** IN PROGRESS 🚧 v1.0

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅
- EPIC 2 (Core Business Domain) — COMPLETE ✅
- EPIC 3 (Hospital Management) — COMPLETE ✅
- EPIC 4 (AI Core) — COMPLETE ✅
- EPIC 5 (Clinical Intelligence) — COMPLETE ✅
- **EPIC 6 (Integrations) — IN PROGRESS 🚧**
- EPIC 7 (User Experience) — Pending
- EPIC 8 (Production Readiness) — Pending
- EPIC 9 (Machine Learning) — Pending
- EPIC 10 (Enterprise Release) — Pending

---

## Reference Documents

| Document | Path |
|----------|------|
| EPIC 4 AI Core | `../epic4/README.md` |
| EPIC 5 Clinical | `../epic5/README.md` |
| ADR Index | `../adr/README.md` |

---

*EREN Epic 6 v1.0 - Integrations*
*Architecture Board - 2026-07-20*
