# app/services

**Application / use-case layer** — the business logic of EREN.

Services orchestrate `models` (persistence) and enforce domain rules. Routers
call services; **services never import routers**. Keep services framework-
agnostic where possible so they remain unit-testable in isolation.

No services are implemented yet — add one module per use case as the product
grows.
