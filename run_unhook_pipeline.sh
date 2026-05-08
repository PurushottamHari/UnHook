#!/bin/bash

# Default user ID if not provided, allowing it to be overridden via arguments
USER_ID="607d95f0-47ef-444c-89d2-d05f257d1265"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --user-id) USER_ID="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Generate pipeline ID for metrics tracking
PIPELINE_ID=$(uuidgen)
export PIPELINE_ID
export USER_ID

echo "🚀 Running UnHook Pipeline (ID: $PIPELINE_ID) for User (ID: $USER_ID)..."

# Run data collector service
echo "Starting Data Collector Service..."
./data_collector_service/.venv/bin/python -m data_collector_service.service --user-id "$USER_ID"

# Run moderation (content rejection)
echo "Running Content Moderation (Rejection)..."
./data_collector_service/.venv/bin/python -m data_collector_service.services.rejection.reject_content_service

# Run processing moderated content
echo "Processing Moderated Content..."
./data_processing_service/.venv/bin/python -m data_processing_service.services.processing.process_moderated_content_service

# Run generating required data for YouTube Video
echo "Generating Required Data for YouTube Video..."
./data_processing_service/.venv/bin/python -m data_processing_service.services.processing.youtube.generate_required_content.generate_required_youtube_content_service

# Run categorizing generated content
echo "Categorizing Generated Content..."
./data_processing_service/.venv/bin/python -m data_processing_service.services.processing.youtube.categorize_content.categorize_youtube_content_service

# Run generating final article
echo "Generating Final Article..."
./data_processing_service/.venv/bin/python -m data_processing_service.services.processing.youtube.generate_complete_content.generate_complete_youtube_content_service

# Run creating newspaper
echo "Creating Newspaper..."
./newspaper_service/.venv/bin/python -m newspaper_service.services.create_newspaper_service

echo "✅ All done!" 