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
    uuid-runtime \
    sed \
    libnss3 \
    libnspr4 \
    ca-certificates \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/
ENV PATH="/uv/bin:${PATH}"

# Install Hatchling (build backend) using uv
RUN uv pip install --system hatchling

# Configure git to use the GITHUB_TOKEN for private dependencies securely
ARG GITHUB_TOKEN
RUN if [ -n "$GITHUB_TOKEN" ]; then \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi

# Copy all services and commons
COPY commons/ ./commons/
COPY user_service/ ./user_service/
COPY data_collector_service/ ./data_collector_service/
COPY data_processing_service/ ./data_processing_service/
COPY newspaper_service/ ./newspaper_service/

# Create venvs and install dependencies for each service
# Note: Keeping git dependencies as requested by the user
RUN for service in user_service data_collector_service data_processing_service newspaper_service; do \
        echo "Setting up venv for $service..." && \
        uv venv --clear $service/.venv && \
        uv pip install -e ./$service --python ./$service/.venv/bin/python; \
    done && \
    git config --global --unset url."https://github.com/".insteadOf || true

# Copy essential runner scripts and configuration
COPY run_unhook_pipeline.sh ./run_unhook_pipeline.sh
COPY setup_cookies.sh ./setup_cookies.sh
COPY cookies/ ./cookies/
RUN chmod +x ./run_unhook_pipeline.sh ./setup_cookies.sh

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
