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

# Note: .env file is not copied here as Railway injects environment variables at runtime
# For local development, ensure .env file is present before building

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

# Copy user_service directory
COPY user_service/ ./user_service/
COPY commons/ ./commons/

# Change to user_service directory and install Python dependencies
WORKDIR /app/user_service
RUN uv pip install --system hatchling

# GITHUB_TOKEN is injected by Railway as a build-time variable
ARG GITHUB_TOKEN
RUN if [ -z "${GITHUB_TOKEN}" ]; then echo "ERROR: GITHUB_TOKEN build arg is required" && exit 1; fi && \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" && \
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
# Run from /app directory using full module path: user_service.api.app
# Railway sets PORT env var, but uvicorn defaults to 8000 if not set
CMD uvicorn user_service.api.app:app --host 0.0.0.0 --port ${PORT:-8000}

