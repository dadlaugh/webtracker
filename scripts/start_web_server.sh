#!/bin/bash

# Start Webpage Tracker Web Server in Docker
# This script starts the web server container for team access

set -e

echo "🌐 Starting Webpage Tracker Web Server..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Always build the Docker image to ensure it's up to date
echo "🔨 Building Docker image..."
if ! docker build -t webtracker_web-server .; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Stop any existing web server container
echo "🛑 Stopping existing web server container..."
docker stop webpage-web-server 2>/dev/null || true
docker rm webpage-web-server 2>/dev/null || true

# Start the web server container
echo "🚀 Starting web server container..."
if ! docker run -d \
    --name webpage-web-server \
    -p 8080:8080 \
    -v "$(pwd)/webpage_versions:/app/webpage_versions:ro" \
    -v "$(pwd)/diffs:/app/diffs:ro" \
    -v "$(pwd)/logs:/app/logs:ro" \
    -v "$(pwd)/web_server.py:/app/web_server.py:ro" \
    -e PYTHONUNBUFFERED=1 \
    webtracker_web-server \
    python web_server.py; then
    echo "❌ Failed to start web server container"
    exit 1
fi

# Wait for the server to start
echo "⏳ Waiting for web server to start..."
sleep 5

# Check if the server is running
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Web server is running successfully!"
    echo "🌍 Access your files at: http://localhost:8080"
    echo "🌐 For remote access: http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
    echo "📊 Container status:"
    docker ps | grep webpage-web-server
else
    echo "❌ Web server failed to start"
    echo "📋 Container logs:"
    docker logs webpage-web-server
    exit 1
fi

echo ""
echo "🛑 To stop the web server: docker stop webpage-web-server"
echo "📋 To view logs: docker logs -f webpage-web-server" 