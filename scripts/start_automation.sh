#!/bin/bash

# Start Webpage Tracker Automation Container
# This script starts the automation container that handles:
# - Morning runs at 9:00 AM daily
# - Git change detection every 5 minutes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting Webpage Tracker Automation...${NC}"

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Stop and remove existing automation container
echo -e "${YELLOW}Stopping existing automation container...${NC}"
docker-compose --profile automation down

# Build and start automation container
echo -e "${GREEN}Building and starting automation container...${NC}"
if docker-compose --profile automation up -d --build; then
    echo -e "${GREEN}Automation container started successfully!${NC}"
    echo -e "${GREEN}Morning tracker will run at 9:00 AM daily${NC}"
    echo -e "${GREEN}Git change detection will run every 5 minutes${NC}"
    echo -e "${GREEN}Health check: curl http://localhost:8080/health${NC}"
    
    # Show container status
    echo -e "${YELLOW}Container status:${NC}"
    docker-compose --profile automation ps
    
    # Show logs
    echo -e "${YELLOW}Recent logs:${NC}"
    docker-compose --profile automation logs --tail=10
else
    echo -e "${RED}Failed to start automation container${NC}"
    exit 1
fi 