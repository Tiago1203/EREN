# packages/

**Shared libraries** consumed by `apps/*` and `core/*`. Packages hold reusable,
cross-cutting code — no deployable surface of their own.

| Package | Purpose |
| --- | --- |
| [`shared/`](./shared) | Cross-cutting utilities, types and constants. |
| [`sdk/`](./sdk) | Typed client SDK for programmatic access to EREN. |
| [`prompts/`](./prompts) | Versioned prompt library for cognitive engines. |
| [`schemas/`](./schemas) | Canonical data contracts and validation schemas. |

> **Status:** placeholder scaffolding. Each package exposes a placeholder entry
> point and no functionality yet.

## Conventions

- Packages are npm workspaces named `@eren/<name>`.
- Packages may depend on each other but must **not** depend on `apps/*`.
- Keep them small, focused, and independently versionable.
