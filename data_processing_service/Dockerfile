# Stage 1: Base - Common setup and dependencies
FROM python:3.11-slim as base

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
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/

# Copy dependency files first for caching
COPY data_processing_service/pyproject.toml data_processing_service/uv.lock ./data_processing_service/
WORKDIR /app/data_processing_service

# Install Python dependencies using Docker Secrets for GITHUB_TOKEN
RUN --mount=type=secret,id=GITHUB_TOKEN \
    GITHUB_TOKEN=$(cat /run/secrets/GITHUB_TOKEN) && \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    uv sync --frozen --no-install-project

# Copy the rest of the application code
COPY data_processing_service ./

# Install the project itself
RUN uv sync --frozen

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "Data Processing Service is running" || exit 1

# Default command to run the data processing service using uv run
CMD ["uv", "run", "python", "-m", "data_processing_service.app"]
