# Stage 1: Base - Common setup and dependencies
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_CACHE_DIR=/app/.uv_cache \
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
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/.venv /app/.uv_cache \
    && chown -R app:app /app

# Copy dependency files first for caching
COPY --chown=app:app data_collector_service/pyproject.toml data_collector_service/uv.lock* ./data_collector_service/
WORKDIR /app/data_collector_service

# Install Python dependencies using GITHUB_TOKEN as build argument
ARG GITHUB_TOKEN
USER app
RUN if [ -n "$GITHUB_TOKEN" ]; then \
        git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi && \
    uv sync --frozen --no-install-project && \
    if [ -n "$GITHUB_TOKEN" ]; then \
        git config --global --unset url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi

# Copy the rest of the application code
USER root
COPY --chown=app:app data_collector_service/ ./

# Install the project itself
USER app
RUN uv sync --frozen

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "Data Collector Service is running" || exit 1

# Default command to run the data collector service using uv run --no-sync
CMD ["uv", "run", "--no-sync", "python", "-m", "data_collector_service.app"]
