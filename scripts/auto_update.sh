#!/bin/bash

# Auto Update Script for Webpage Tracker
# This script runs every 5 minutes to check for Git changes and run tracker
# Also runs webpage_tracker every morning at 9:00 AM

# Configuration
PROJECT_DIR="/opt/webtracker"
LOG_FILE="$PROJECT_DIR/logs/auto_update.log"
LOCK_FILE="$PROJECT_DIR/.update_lock"
GIT_BRANCH="main"  # or "master" depending on your default branch

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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if update is already running
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_message "${YELLOW}Update already running (PID: $PID), skipping...${NC}"
            exit 0
        else
            log_message "${YELLOW}Stale lock file found, removing...${NC}"
            rm -f "$LOCK_FILE"
        fi
    fi
}

# Function to create lock file
create_lock() {
    echo $$ > "$LOCK_FILE"
}

# Function to remove lock file
remove_lock() {
    rm -f "$LOCK_FILE"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_message "${RED}Docker is not running!${NC}"
        return 1
    fi
    return 0
}

# Function to check if git repository exists
check_git_repo() {
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        log_message "${RED}Git repository not found at $PROJECT_DIR${NC}"
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
        log_message "${YELLOW}Running in development environment ($ENVIRONMENT) - skipping auto-update${NC}"
        return 1
    fi
    
    log_message "Running in environment: $ENVIRONMENT"
    return 0
}

# Function to check if it's 9:00 AM
is_morning_run() {
    local current_hour=$(date '+%H')
    local current_minute=$(date '+%M')
    
    # Check if it's between 9:00 AM and 9:05 AM (allowing some flexibility)
    if [ "$current_hour" = "09" ] && [ "$current_minute" -ge 0 ] && [ "$current_minute" -le 5 ]; then
        return 0
    fi
    
    return 1
}

# Function to check for Git changes
check_for_changes() {
    cd "$PROJECT_DIR"
    
    # Fetch latest changes
    git fetch origin $GIT_BRANCH > /dev/null 2>&1
    
    # Check if local is behind remote
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/$GIT_BRANCH)
    
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_message "${GREEN}New Git changes detected!${NC}"
        log_message "Local:  $LOCAL_COMMIT"
        log_message "Remote: $REMOTE_COMMIT"
        return 0
    else
        log_message "No new Git changes detected"
        return 1
    fi
}

# Function to pull latest Git changes
pull_latest_changes() {
    cd "$PROJECT_DIR"
    
    log_message "${BLUE}Pulling latest code from Git...${NC}"
    if ! git pull origin $GIT_BRANCH; then
        log_message "${RED}Failed to pull latest code${NC}"
        return 1
    fi
    
    # Get the new commit hash
    NEW_COMMIT=$(git rev-parse HEAD)
    log_message "Updated to commit: $NEW_COMMIT"
    
    # Rebuild Docker image with latest code
    log_message "Rebuilding Docker image with latest code..."
    if ! docker build -t webpage-tracker .; then
        log_message "${RED}Failed to rebuild Docker image${NC}"
        return 1
    fi
    
    return 0
}

# Function to run the webpage tracker
run_tracker() {
    local reason="$1"
    log_message "${BLUE}Running webpage tracker ($reason)...${NC}"
    
    cd "$PROJECT_DIR"
    
    if docker run --rm \
        -v $(pwd)/webpagesv2.xlsx:/app/webpages.xlsx:ro \
        -v $(pwd)/webpage_versions:/app/webpage_versions \
        -v $(pwd)/diffs:/app/diffs \
        -v $(pwd)/logs:/app/logs \
        webpage-tracker; then
        log_message "${GREEN}Webpage tracker completed successfully${NC}"
        return 0
    else
        log_message "${RED}Webpage tracker failed${NC}"
        return 1
    fi
}

# Main execution
main() {
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log_message "=== Auto Update Script Started ==="
    
    # Check for lock file
    check_lock
    create_lock
    
    # Ensure we clean up lock file on exit
    trap remove_lock EXIT
    
    # Check prerequisites
    if ! check_docker; then
        log_message "${RED}Prerequisites check failed${NC}"
        exit 1
    fi
    
    if ! check_git_repo; then
        log_message "${RED}Git repository check failed${NC}"
        exit 1
    fi
    
    # Check environment
    if ! check_environment; then
        log_message "${YELLOW}Auto-update skipped due to environment settings${NC}"
        exit 0
    fi
    
    # Check if it's morning run time (9:00 AM)
    if is_morning_run; then
        log_message "${GREEN}Morning run detected (9:00 AM) - running webpage tracker${NC}"
        if run_tracker "morning_schedule"; then
            log_message "${GREEN}Morning webpage tracker completed successfully${NC}"
        else
            log_message "${RED}Morning webpage tracker failed${NC}"
            exit 1
        fi
    fi
    
    # Check for Git changes
    if check_for_changes; then
        log_message "${GREEN}Git changes detected - updating and running tracker${NC}"
        
        # Pull latest changes and rebuild
        if pull_latest_changes; then
            log_message "${GREEN}Git update completed successfully${NC}"
            
            # Run tracker after Git changes
            if run_tracker "git_changes"; then
                log_message "${GREEN}Git-triggered webpage tracker completed successfully${NC}"
            else
                log_message "${RED}Git-triggered webpage tracker failed${NC}"
                exit 1
            fi
        else
            log_message "${RED}Git update failed${NC}"
            exit 1
        fi
    else
        log_message "No Git changes detected - no action needed"
    fi
    
    log_message "=== Auto Update Script Completed ==="
    echo "---" >> "$LOG_FILE"
}

# Run main function
main "$@" 