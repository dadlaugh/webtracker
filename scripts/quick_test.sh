#!/bin/bash

# Quick Test Script for Automation
# Run this to quickly test automation components

echo "🔍 Quick Automation Test"

# Test 1: Check if we're in the right directory
echo "1. Checking project directory..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml found"
else
    echo "❌ docker-compose.yml not found"
    exit 1
fi

# Test 2: Check if scripts exist
echo "2. Checking automation scripts..."
if [ -f "scripts/morning_tracker.sh" ] && [ -f "scripts/auto_update.sh" ]; then
    echo "✅ Automation scripts found"
else
    echo "❌ Automation scripts missing"
    exit 1
fi

# Test 3: Check Docker
echo "3. Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running"
    exit 1
fi

# Test 4: Check Docker images
echo "4. Checking Docker images..."
if docker images | grep -q "webtracker"; then
    echo "✅ Webtracker images found"
else
    echo "❌ Webtracker images not found"
    echo "Building images..."
    docker-compose build
fi

# Test 5: Test automation container
echo "5. Testing automation container..."
if docker-compose --profile automation up -d --build; then
    echo "✅ Automation container started"
    
    # Wait a moment and check logs
    sleep 5
    echo "📋 Automation container logs:"
    docker-compose --profile automation logs --tail=10
    
    # Stop the container
    docker-compose --profile automation down
    echo "✅ Automation container stopped"
else
    echo "❌ Automation container failed to start"
    exit 1
fi

echo "🎉 Quick test completed successfully!" 