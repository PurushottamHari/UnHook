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
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/
ENV PATH="/uv/bin:${PATH}"

# Copy only what is needed for installing dependencies first (caching)
COPY data_processing_service/pyproject.toml ./data_processing_service/
RUN uv pip install --system hatchling

# Configure git and install dependencies
RUN --mount=type=secret,id=GITHUB_TOKEN \
    GITHUB_TOKEN=$(cat /run/secrets/GITHUB_TOKEN) \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" \
    && uv pip install --system -e ./data_processing_service

# Copy the rest of the application
COPY data_processing_service ./data_processing_service/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "Data Processing Service is running" || exit 1

# Default command to run the data processing service
CMD ["python", "-m", "data_processing_service.app"]
