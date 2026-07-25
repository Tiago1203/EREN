FROM python:3.12-slim

LABEL maintainer="EREN Team <dev@orma.health>"
LABEL org.opencontainers.image.title="EREN - Cognitive Operating System"
LABEL org.opencontainers.image.description="Cognitive OS for Clinical Engineering"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    ENV=production

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Non-root user
RUN groupadd --gid 1001 eren && \
    useradd --uid 1001 --gid eren --shell /bin/bash --create-home eren

WORKDIR /app

# Install dependencies
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir gunicorn uvicorn fastapi

# Copy application (done in separate layer in CI)
COPY . .

# Permissions
RUN chown -R eren:eren /app

USER eren

# Expose port
EXPOSE 8000

# Health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", \
     "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", \
     "main:app"]
