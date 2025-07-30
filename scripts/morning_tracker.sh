#!/bin/bash

# Morning Webpage Tracker Script
# This script runs webpage_tracker every morning at 9:00 AM

# Configuration
PROJECT_DIR="/opt/webtracker"
LOG_FILE="$PROJECT_DIR/logs/morning_tracker.log"

# Environment detection
ENVIRONMENT_FILE="$PROJECT_DIR/.environment"
DEFAULT_ENVIRONMENT="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1" | tee -a "$LOG_FILE"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_message "${RED}Docker is not running!${NC}"
        return 1
    fi
    return 0
}

# Function to check environment
check_environment() {
    # Read environment from file, default to production
    if [ -f "$ENVIRONMENT_FILE" ]; then
        ENVIRONMENT=$(cat "$ENVIRONMENT_FILE" | tr '[:upper:]' '[:lower:]')
    else
        ENVIRONMENT="$DEFAULT_ENVIRONMENT"
    fi
    
    # Check if we're in development environment
    if [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "dev" ]; then
        log_message "${YELLOW}Running in development environment ($ENVIRONMENT) - skipping morning tracker${NC}"
        return 1
    fi
    
    log_message "Running in environment: $ENVIRONMENT"
    return 0
}

# Function to run the webpage tracker
run_tracker() {
    log_message "${BLUE}Running morning webpage tracker...${NC}"
    
    cd "$PROJECT_DIR"
    
    if docker run --rm \
        -v $(pwd)/webpagesv2.xlsx:/app/webpages.xlsx:ro \
        -v $(pwd)/webpage_versions:/app/webpage_versions \
        -v $(pwd)/diffs:/app/diffs \
        -v $(pwd)/logs:/app/logs \
        webtracker_web-server; then
        log_message "${GREEN}Morning webpage tracker completed successfully${NC}"
        return 0
    else
        log_message "${RED}Morning webpage tracker failed${NC}"
        return 1
    fi
}

# Main execution
main() {
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log_message "=== Morning Webpage Tracker Started ==="
    
    # Check prerequisites
    if ! check_docker; then
        log_message "${RED}Prerequisites check failed${NC}"
        exit 1
    fi
    
    # Check environment
    if ! check_environment; then
        log_message "${YELLOW}Morning tracker skipped due to environment settings${NC}"
        exit 0
    fi
    
    # Run tracker
    if run_tracker; then
        log_message "${GREEN}Morning webpage tracker completed successfully${NC}"
    else
        log_message "${RED}Morning webpage tracker failed${NC}"
        exit 1
    fi
    
    log_message "=== Morning Webpage Tracker Completed ==="
    echo "---" >> "$LOG_FILE"
}

# Run main function
main "$@" 