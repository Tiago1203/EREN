# app/schemas

**Data contracts** — Pydantic v2 models used for request and response bodies.

Schemas (DTOs) are distinct from `models` (persistence): they define the shape
of the public API and handle validation/serialization. Keep them free of ORM or
database concerns.

Currently only `health.py` (`HealthResponse`) exists.
