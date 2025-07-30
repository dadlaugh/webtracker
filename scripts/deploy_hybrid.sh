#!/bin/bash

# Hybrid Approach Deployment Script
# This script archives historical data and implements the new Excel-based structure

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

echo -e "${BLUE}=== Hybrid Approach Deployment ===${NC}"

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

# Switch to hybrid approach branch
log_message "${YELLOW}Switching to hybrid approach branch...${NC}"
git checkout hybrid-approach 2>/dev/null || git checkout -b hybrid-approach

# Archive historical data
log_message "${YELLOW}Archiving historical data...${NC}"
if [ -f "scripts/archive_historical_data.py" ]; then
    python3 scripts/archive_historical_data.py
else
    log_message "${YELLOW}Archive script not found, creating basic archive...${NC}"
    timestamp=$(date +%Y%m%d_%H%M%S)
    archive_dir="historical_archive_${timestamp}"
    mkdir -p "$archive_dir"
    
    # Archive existing data
    if [ -d "webpage_versions" ]; then
        cp -r webpage_versions "$archive_dir/"
        log_message "✅ Archived webpage_versions"
    fi
    if [ -d "diffs" ]; then
        cp -r diffs "$archive_dir/"
        log_message "✅ Archived diffs"
    fi
fi

# Create sample Excel file if it doesn't exist
if [ ! -f "webpagesv2.xlsx" ]; then
    log_message "${YELLOW}Creating sample Excel file...${NC}"
    if [ -f "create_sample_excel_simple.py" ]; then
        python3 create_sample_excel_simple.py
    else
        log_message "${YELLOW}Please create webpagesv2.xlsx manually${NC}"
    fi
fi

# Build Docker image
log_message "${YELLOW}Building Docker image...${NC}"
docker build -t webpage-tracker .

# Create necessary directories
mkdir -p webpage_versions diffs logs

# Run the tracker with new structure
log_message "${YELLOW}Running webpage tracker with new structure...${NC}"
docker run --rm \
    -v "$(pwd)/webpagesv2.xlsx:/app/webpagesv2.xlsx:ro" \
    -v "$(pwd)/webpage_versions:/app/webpage_versions" \
    -v "$(pwd)/diffs:/app/diffs" \
    webpage-tracker

log_message "${GREEN}Hybrid deployment completed successfully!${NC}"

# Show results
echo ""
echo -e "${BLUE}=== Deployment Results ===${NC}"
echo -e "Project Directory: $PROJECT_DIR"
echo -e "Archive Location: $archive_dir"
echo -e "New Structure: Excel-based numbering with en/zh folders"
echo -e "Historical Data: Preserved in archive"

# Show new structure
echo ""
echo -e "${BLUE}=== New File Structure ===${NC}"
if [ -d "webpage_versions" ]; then
    echo -e "webpage_versions/"
    for dir in webpage_versions/*/; do
        if [ -d "$dir" ]; then
            echo -e "  $(basename "$dir")/"
            for subdir in "$dir"*/; do
                if [ -d "$subdir" ]; then
                    echo -e "    $(basename "$subdir")/"
                fi
            done
        fi
    done
fi

echo ""
echo -e "${GREEN}✅ Hybrid approach deployment complete!${NC}"
echo -e "📁 Historical data archived"
echo -e "🆕 New structure implemented"
echo -e "🌐 Access web interface at: http://localhost:8080" 