#!/bin/bash

# Simple Deployment Script for Webpage Tracker
# Run this on your remote server to deploy the application

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/opt/webtracker"
GIT_REPO="git@github.com:dadlaugh/webtracker.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Webpage Tracker Deployment ===${NC}"

# Function to log messages
log_message() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    log_message "${YELLOW}Creating project directory...${NC}"
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Clone or pull repository
if [ ! -d ".git" ]; then
    log_message "${YELLOW}Cloning repository...${NC}"
    git clone "$GIT_REPO" .
else
    log_message "${YELLOW}Pulling latest changes...${NC}"
    git pull origin main
fi

# Create sample Excel file if it doesn't exist
if [ ! -f "webpagesv2.xlsx" ]; then
    log_message "${YELLOW}Creating sample Excel file...${NC}"
    python3 create_sample_excel_simple.py
fi

# Build Docker image
log_message "${YELLOW}Building Docker image...${NC}"
docker build -t webpage-tracker .

# Create necessary directories
mkdir -p webpage_versions diffs logs

# Run the container
log_message "${YELLOW}Running webpage tracker...${NC}"
docker run --rm \
    -v "$(pwd)/webpagesv2.xlsx:/app/webpages.xlsx:ro" \
    -v "$(pwd)/webpage_versions:/app/webpage_versions" \
    -v "$(pwd)/diffs:/app/diffs" \
    webpage-tracker

log_message "${GREEN}Deployment completed successfully!${NC}"

# Show results
echo ""
echo -e "${BLUE}=== Deployment Results ===${NC}"
echo -e "Project Directory: $PROJECT_DIR"
echo -e "Webpage Versions: $(ls -1 webpage_versions/*/ 2>/dev/null | wc -l) sites tracked"
echo -e "Diffs Generated: $(ls -1 diffs/*/ 2>/dev/null | wc -l) sites with diffs"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Edit webpagesv2.xlsx to add your URLs"
echo -e "2. Run this script again to update tracking"
echo -e "3. Set up auto-updates: see REMOTE_DOCKER_DEPLOYMENT.md" 