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
        uuid-runtime \
    && rm -rf /var/lib/apt/lists/*

# Copy all service directories
COPY data_collector_service/ ./data_collector_service/
COPY data_processing_service/ ./data_processing_service/
COPY newspaper_service/ ./newspaper_service/
COPY user_service/ ./user_service/
COPY commons/ ./commons/

# Install Python dependencies for all services
RUN pip install --upgrade pip \
    && pip install hatchling

# Install user-service first (base dependency)
RUN cd user_service && pip install -e .

# Install data-collector-service
RUN cd data_collector_service && pip install -e .

# Install data-processing-service
RUN cd data_processing_service && pip install -e .

# Install newspaper-service
RUN cd newspaper_service && pip install -e .

# Copy the pipeline script
COPY run_unhook_pipeline.sh ./run_unhook_pipeline.sh
RUN chmod +x ./run_unhook_pipeline.sh

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "UnHook Pipeline is ready" || exit 1

# Default command to run the entire pipeline
CMD ["./run_unhook_pipeline.sh"]
