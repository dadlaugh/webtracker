#!/bin/bash

# Start Webpage Tracker Web Server using Docker Compose
# This script starts the web server container for team access

set -e

echo "🌐 Starting Webpage Tracker Web Server (Docker Compose)..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Stop any existing web server container
echo "🛑 Stopping existing web server container..."
docker-compose --profile web down

# Build and start the web server container
echo "🔨 Building and starting web server container..."
if docker-compose --profile web up -d --build; then
    echo "✅ Web server container started successfully!"
    
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
        docker-compose --profile web ps
    else
        echo "❌ Web server failed to start"
        echo "📋 Container logs:"
        docker-compose --profile web logs
        exit 1
    fi
else
    echo "❌ Failed to start web server container"
    docker-compose --profile web logs
    exit 1
fi

echo ""
echo "🛑 To stop the web server: docker-compose --profile web down"
echo "📋 To view logs: docker-compose --profile web logs -f" 