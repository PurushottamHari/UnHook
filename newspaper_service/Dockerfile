# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

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
ENV PATH="/uv/bin:${PATH}"

# Copy newspaper_service directory (commons is fetched via Git dependency)
COPY newspaper_service/ ./newspaper_service/

# Change to newspaper_service directory and install Python dependencies
WORKDIR /app/newspaper_service
RUN uv pip install --system hatchling

# GITHUB_TOKEN is injected by Railway as a build-time variable
ARG GITHUB_TOKEN
RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    uv pip install --system -e .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set working directory to /app (parent directory) so relative imports work correctly
WORKDIR /app

# Expose the port (Railway will set PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command to run the FastAPI application
# Run from /app directory using full module path: newspaper_service.api.app
# Railway sets PORT env var, but uvicorn defaults to 8000 if not set
CMD uvicorn newspaper_service.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
