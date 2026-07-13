"""
EREN API — FastAPI entrypoint.

Architecture scaffolding only. No business logic, AI, or agents are
implemented here. This file exists so the service is ready to grow into
the programmatic gateway of the EREN Cognitive Operating System.

Run (once dependencies are installed):
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

app = FastAPI(
    title="EREN API",
    description="Programmatic gateway into the EREN Cognitive Operating System.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness probe. Placeholder endpoint — no business logic."""
    return {"status": "ok"}
