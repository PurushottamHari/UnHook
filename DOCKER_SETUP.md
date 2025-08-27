# Docker Setup for UnHook Services

This document explains how to containerize and run the UnHook microservices using Docker.

## Services Overview

The UnHook platform consists of four main services:

1. **user_service** - User management and authentication (FastAPI web service)
2. **data_collector_service** - Collects data from various sources (batch processing)
3. **data_processing_service** - Processes and analyzes collected data (batch processing)
4. **newspaper_service** - Creates curated newspapers (batch processing)

## Prerequisites

- Docker installed on your system
- `.env` file with proper environment variables for each service
- Access to the required databases (MongoDB, etc.)

## Environment Variables

Each service requires a `.env` file with the following variables:

### Common Variables
```bash
# Database Configuration
MONGODB_URI=mongodb://localhost:27017/unhook
MONGODB_DATABASE=unhook

# User Service Configuration
USER_SERVICE_URL=http://user-service:8000
USER_SERVICE_API_KEY=your_api_key_here
```

### Service-Specific Variables
```bash
# Data Collector Service
YOUTUBE_API_KEY=your_youtube_api_key
COLLECTION_INTERVAL=3600

# Data Processing Service
AI_MODEL_API_KEY=your_ai_model_key
PROCESSING_BATCH_SIZE=100

# Newspaper Service
NEWSPAPER_GENERATION_TIME=06:00
MAX_ARTICLES_PER_NEWSPAPER=20
```

## Building and Running Services

### 1. User Service (Web Service)

```bash
cd user_service
docker build -t unhook-user-service .
docker run -d \
  --name unhook-user-service \
  --env-file .env \
  -p 8000:8000 \
  unhook-user-service
```

### 2. Data Collector Service (Batch Processing)

```bash
cd data_collector_service
docker build -t unhook-data-collector .
docker run -d \
  --name unhook-data-collector \
  --env-file .env \
  unhook-data-collector
```

### 3. Data Processing Service (Batch Processing)

```bash
cd data_processing_service
docker build -t unhook-data-processor .
docker run -d \
  --name unhook-data-processor \
  --env-file .env \
  unhook-data-processor
```

### 4. Newspaper Service (Batch Processing)

```bash
cd newspaper_service
docker build -t unhook-newspaper-service .
docker run -d \
  --name unhook-newspaper-service \
  --env-file .env \
  unhook-newspaper-service
```

## Docker Compose Setup

For easier management, you can use Docker Compose. Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  user-service:
    build: ./user_service
    container_name: unhook-user-service
    env_file: ./user_service/.env
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    networks:
      - unhook-network

  data-collector:
    build: ./data_collector_service
    container_name: unhook-data-collector
    env_file: ./data_collector_service/.env
    depends_on:
      - mongodb
      - user-service
    networks:
      - unhook-network

  data-processor:
    build: ./data_processing_service
    container_name: unhook-data-processor
    env_file: ./data_processing_service/.env
    depends_on:
      - mongodb
      - user-service
    networks:
      - unhook-network

  newspaper-service:
    build: ./newspaper_service
    container_name: unhook-newspaper-service
    env_file: ./newspaper_service/.env
    depends_on:
      - mongodb
      - user-service
    networks:
      - unhook-network

  mongodb:
    image: mongo:6.0
    container_name: unhook-mongodb
    environment:
      MONGO_INITDB_DATABASE: unhook
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - unhook-network

networks:
  unhook-network:
    driver: bridge

volumes:
  mongodb_data:
```

Run with:
```bash
docker-compose up -d
```

## Service-Specific Notes

### Data Collector Service
- Includes `ffmpeg` for video processing
- Runs as a batch job to collect data from YouTube and other sources
- Can be scheduled using cron or Kubernetes CronJob

### Data Processing Service
- Processes collected data using AI models
- Runs various processing pipelines (moderation, categorization, etc.)
- Can be run on-demand or scheduled

### Newspaper Service
- Creates curated newspapers from processed content
- Runs as a scheduled job (typically daily)
- Generates newspapers for all active users

## Health Checks

Each service includes a basic health check:
- **User Service**: HTTP endpoint at `/health`
- **Batch Services**: Simple echo command to verify the container is running

## Logging

All services use Python's standard logging. Logs can be viewed with:
```bash
docker logs <container-name>
```

## Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all required environment variables are set in the `.env` file
2. **Dependencies**: Make sure all services can connect to their dependencies (MongoDB, User Service)
3. **File Permissions**: The Dockerfiles create a non-root user for security
4. **Network Connectivity**: Ensure services can communicate with each other

### Debug Mode

To run services in debug mode, override the CMD:
```bash
docker run -it --env-file .env unhook-data-collector /bin/bash
```

## Production Considerations

1. **Security**: Use secrets management for sensitive environment variables
2. **Monitoring**: Implement proper logging and monitoring
3. **Scaling**: Use Kubernetes or Docker Swarm for production orchestration
4. **Backup**: Ensure database backups are configured
5. **Resource Limits**: Set appropriate CPU and memory limits

## Development

For development, you can mount the source code as volumes:
```bash
docker run -it \
  --env-file .env \
  -v $(pwd):/app \
  unhook-data-collector
```

This allows for live code changes without rebuilding the container.
