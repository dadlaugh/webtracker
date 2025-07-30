#!/bin/bash

# Setup Automation Environment Script
# This script sets up the proper environment for automation

# Configuration
PROJECT_DIR="/opt/webtracker"
ENVIRONMENT_FILE="$PROJECT_DIR/.environment"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Setting up Automation Environment ===${NC}"

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Creating project directory...${NC}"
    mkdir -p "$PROJECT_DIR"
fi

# Set environment to production
echo -e "${GREEN}Setting environment to production...${NC}"
echo "production" > "$ENVIRONMENT_FILE"

# Create necessary directories
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/webpage_versions"
mkdir -p "$PROJECT_DIR/diffs"

# Set proper permissions
echo -e "${GREEN}Setting permissions...${NC}"
chmod 755 "$PROJECT_DIR"
chmod 644 "$ENVIRONMENT_FILE"

echo -e "${GREEN}=== Automation Environment Setup Complete ===${NC}"
echo -e "${GREEN}Environment file: $ENVIRONMENT_FILE${NC}"
echo -e "${GREEN}Project directory: $PROJECT_DIR${NC}" 