FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for layer caching)
COPY apps/api/pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy application code
# apps/api/ → /app/  (so FastAPI app is at /app/app/)
COPY apps/api/ /app/

# Copy core/ to /_core_temp then move into /app/core/
# This avoids the flatten-when-destination-exists issue
COPY core/ /_core_temp/
RUN mv /_core_temp /app/core

# Set PYTHONPATH so both /app (for app/) and /app/core (for core/) are importable
ENV PYTHONPATH=/app:/app/core

# Create non-root user
RUN useradd -m -u 1000 eren && chown -R eren:eren /app
USER eren

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
