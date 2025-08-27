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

# Copy .env file first and source all environment variables
COPY .env .env
RUN if [ ! -f ".env" ]; then \
        echo "ERROR: .env file not found"; \
        echo "Please create a .env file with your environment variables"; \
        exit 1; \
    fi && \
    export $(cat .env | grep -v '^#' | xargs) && \
    echo "Environment variables loaded from .env file" && \
    rm .env

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install Python dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install hatchling \
    && pip install -e .

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check (optional for batch processing service)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "Data Processing Service is running" || exit 1

# Default command to run the data processing service
# You can override this with specific service scripts as needed
CMD ["python", "-m", "services.processing.process_moderated_content_service"]
