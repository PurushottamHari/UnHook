# Stage 1: Base - Common setup and dependencies
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/uv/bin:${PATH}"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    git \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/

# Copy dependency files first for caching
COPY newspaper_service/pyproject.toml ./newspaper_service/
WORKDIR /app/newspaper_service

# Install Python dependencies using Docker Secrets for GITHUB_TOKEN
# We use uv sync --no-install-project to cache dependencies
ARG GITHUB_TOKEN
RUN if [ -n "$GITHUB_TOKEN" ]; then \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi && \
    uv sync --no-install-project && \
    git config --global --unset url."https://github.com/".insteadOf || true

# Copy the rest of the application code
COPY newspaper_service/ ./

# Install the project itself
RUN uv sync

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Stage 2: API - Specific to the FastAPI application
FROM base AS api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command to run the FastAPI application using uv run
CMD ["uv", "run", "uvicorn", "newspaper_service.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3: Worker - Specific to the messaging consumer
FROM base AS worker
# Default command to run the worker using uv run
CMD ["uv", "run", "python", "-m", "newspaper_service.app"]
