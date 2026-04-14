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
RUN --mount=type=secret,id=GITHUB_TOKEN \
    GITHUB_TOKEN=$(cat /run/secrets/GITHUB_TOKEN) && \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

# Install all services directly from GitHub (Pure Git Build)
# This ensures that the services are completely separated and environment-agnostic.
# Note: This will build using the code currently pushed to GitHub.
RUN --mount=type=secret,id=GITHUB_TOKEN \
    uv pip install --system \
    "commons @ git+https://github.com/PurushottamHari/UnHook.git#subdirectory=commons" \
    "user-service @ git+https://github.com/PurushottamHari/UnHook.git#subdirectory=user_service" \
    "data-collector-service @ git+https://github.com/PurushottamHari/UnHook.git#subdirectory=data_collector_service" \
    "data-processing-service @ git+https://github.com/PurushottamHari/UnHook.git#subdirectory=data_processing_service" \
    "newspaper-service @ git+https://github.com/PurushottamHari/UnHook.git#subdirectory=newspaper_service"

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
