#!/bin/bash

# Start Webpage Tracker Web Server in Docker
# This script starts the web server container for team access

set -e

echo "🌐 Starting Webpage Tracker Web Server..."

# Build the Docker image if it doesn't exist
if ! docker images | grep -q webpage-tracker; then
    echo "🔨 Building Docker image..."
    docker build -t webpage-tracker .
fi

# Stop any existing web server container
echo "🛑 Stopping existing web server container..."
docker stop webpage-web-server 2>/dev/null || true
docker rm webpage-web-server 2>/dev/null || true

# Start the web server container
echo "🚀 Starting web server container..."
docker run -d \
    --name webpage-web-server \
    -p 8080:8080 \
    -v "$(pwd)/webpage_versions:/app/webpage_versions:ro" \
    -v "$(pwd)/diffs:/app/diffs:ro" \
    -v "$(pwd)/logs:/app/logs:ro" \
    -v "$(pwd)/web_server.py:/app/web_server.py:ro" \
    -e PYTHONUNBUFFERED=1 \
    webpage-tracker \
    python web_server.py

# Wait for the server to start
echo "⏳ Waiting for web server to start..."
sleep 3

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