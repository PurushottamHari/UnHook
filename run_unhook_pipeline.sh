#!/bin/bash

# Generate pipeline ID for metrics tracking
PIPELINE_ID=$(uuidgen)
export PIPELINE_ID

echo "🚀 Running UnHook Pipeline (ID: $PIPELINE_ID)..."

# Run data collector service
echo "Starting Data Collector Service..."
python -m data_collector_service.service

# Run moderation (content rejection)
echo "Running Content Moderation (Rejection)..."
python -m data_processing_service.services.rejection.reject_content_service

# Run processing moderated content
echo "Processing Moderated Content..."
python -m data_processing_service.services.processing.process_moderated_content_service

# Run generating required data for YouTube Video
echo "Generating Required Data for YouTube Video..."
python -m data_processing_service.services.processing.youtube.generate_required_content.generate_required_youtube_content_service

# Run categorizing generated content
echo "Categorizing Generated Content..."
python -m data_processing_service.services.processing.youtube.categorize_content.categorize_youtube_content_service

# Run generating final article
echo "Generating Final Article..."
python -m data_processing_service.services.processing.youtube.generate_complete_content.generate_complete_youtube_content_service

# Run creating newspaper
echo "Creating Newspaper..."
python -m newspaper_service.services.create_newspaper_service

echo "✅ All done!" 