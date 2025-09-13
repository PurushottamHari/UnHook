#!/bin/bash

# Setup YouTube cookies script
# This script decompresses the YouTube cookies file if it exists

set -e  # Exit on any error

echo "🍪 Setting up YouTube cookies..."

# Check if compressed cookies file exists
if [ -f "/app/youtube_cookies_compressed.txt" ]; then
    echo "📦 Found compressed cookies file, decompressing..."
    
    # Decompress the cookies file
    base64 -d /app/youtube_cookies_compressed.txt | gunzip > /app/youtube_cookies.txt
    
    # Set proper permissions
    chmod 644 /app/youtube_cookies.txt
    
    # Verify the file was created and has content
    if [ -s "/app/youtube_cookies.txt" ]; then
        echo "✅ YouTube cookies decompressed successfully"
        echo "📊 Cookies file size: $(wc -l < /app/youtube_cookies.txt) lines"
    else
        echo "❌ ERROR: Cookies file is empty after decompression"
        exit 1
    fi
else
    echo "⚠️  No compressed cookies file found at /app/youtube_cookies_compressed.txt"
    echo "🔄 Proceeding without YouTube authentication"
fi

echo "🍪 Cookie setup completed"
