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
        sed \
    && rm -rf /var/lib/apt/lists/*

# Copy other service directories (for path dependencies)
# Railway builds from repo root, so these should be available
COPY commons/ ./commons/
COPY data_processing_service/ ./data_processing_service/
COPY user_service/ ./user_service/
COPY data_collector_service/ ./data_collector_service/

# Copy newspaper_service directory
COPY newspaper_service/ ./newspaper_service/

# Fix path references in pyproject.toml for Docker container
# Replace local paths with Docker container paths
RUN sed -i 's|file:///Users/puru/Workspace/UnHook/|file:///app/|g' newspaper_service/pyproject.toml || true

# Change to newspaper_service directory and install Python dependencies
WORKDIR /app/newspaper_service
RUN pip install --upgrade pip \
    && pip install hatchling \
    && pip install -e .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set working directory for the app user
WORKDIR /app/newspaper_service

# Expose the port (Railway will set PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command to run the FastAPI application
# Railway sets PORT env var, but uvicorn defaults to 8000 if not set
CMD uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}
