# tests/

Cross-cutting **test suites** that span more than one app or core engine
(integration, end-to-end, contract tests).

> **Status:** placeholder. No suites are implemented yet.

## Guidance

- **Unit tests** live next to the code they cover, inside each `apps/*`,
  `core/*` or `packages/*` workspace.
- **This directory** is for tests that cross workspace boundaries — e.g.
  end-to-end flows through `apps/web` + `apps/api`, or contract tests between
  `packages/schemas` and consumers.

Suggested layout as it grows:

```
tests/
├── integration/
├── e2e/
└── contract/
```
