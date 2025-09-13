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
        sed \
    && rm -rf /var/lib/apt/lists/*

# Copy all service directories
COPY data_collector_service/ ./data_collector_service/
COPY data_processing_service/ ./data_processing_service/
COPY newspaper_service/ ./newspaper_service/
COPY user_service/ ./user_service/
COPY commons/ ./commons/

# Fix path references in pyproject.toml files for Docker container
RUN sed -i 's|file:///Users/puru/Workspace/UnHook/|file:///app/|g' data_processing_service/pyproject.toml && \
    sed -i 's|file:///Users/puru/Workspace/UnHook/|file:///app/|g' data_collector_service/pyproject.toml && \
    sed -i 's|file:///Users/puru/Workspace/UnHook/|file:///app/|g' newspaper_service/pyproject.toml

# Install Python dependencies for all services
RUN pip install --upgrade pip \
    && pip install hatchling

# Install all services from project root to handle relative dependencies
RUN pip install -e ./user_service
RUN pip install -e ./data_collector_service
RUN pip install -e ./data_processing_service
RUN pip install -e ./newspaper_service

# Copy the pipeline script
COPY run_unhook_pipeline.sh ./run_unhook_pipeline.sh
RUN chmod +x ./run_unhook_pipeline.sh

# Copy the cookies setup script
COPY setup_cookies.sh ./setup_cookies.sh
RUN chmod +x ./setup_cookies.sh

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Setup cookies first\n\
./setup_cookies.sh\n\
# Execute the original command\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Set entrypoint to handle cookies decompression
ENTRYPOINT ["/entrypoint.sh"]
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD echo "UnHook Pipeline is ready" || exit 1

# Default command to run the entire pipeline
CMD ["./run_unhook_pipeline.sh"]
