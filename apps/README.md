# apps/

Deployable, user-facing **applications** — the delivery surfaces of EREN.

Apps are thin: they compose capability from `core/*` and `packages/*` and
expose it through a specific interface. Business logic and cognition live in
`core/`, not here.

| App | Interface | Stack | Status |
| --- | --- | --- | --- |
| [`web/`](./web) | Browser UI | Next.js | Active (migrated from repo root) |
| [`api/`](./api) | HTTP API | FastAPI (Python) | Scaffolded |
| [`desktop/`](./desktop) | Desktop client | TBD | Placeholder |

## Conventions

- Each app is independently buildable and deployable.
- Apps depend **inward** (on `core/` and `packages/`), never on each other.
- Keep interface-specific concerns (routing, rendering, transport) in the app.
