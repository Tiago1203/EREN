# infrastructure/

**Operational infrastructure** for EREN — everything needed to provision, run
and operate the system, kept separate from application and cognition code.

Intended scope (to grow over time):

- Infrastructure-as-code (containers, deployment manifests, cloud resources).
- CI/CD pipeline definitions.
- Database provisioning, migrations and operational SQL.
- Observability and environment configuration.

## Contents

- [`database/`](./database) — database schema, migration and diagnostic scripts
  (moved here from the former top-level `scripts/`).

> **Status:** scaffolding. Beyond the existing database scripts, this area is a
> placeholder for future IaC and pipelines.
