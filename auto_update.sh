#!/bin/bash

# Auto Update Script for Webpage Tracker
# This script runs every 5 minutes to pull latest code and redeploy

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

# Function to check for changes
check_for_changes() {
    cd "$PROJECT_DIR"
    
    # Fetch latest changes
    git fetch origin $GIT_BRANCH > /dev/null 2>&1
    
    # Check if local is behind remote
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/$GIT_BRANCH)
    
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_message "${GREEN}New changes detected!${NC}"
        log_message "Local:  $LOCAL_COMMIT"
        log_message "Remote: $REMOTE_COMMIT"
        return 0
    else
        log_message "No new changes detected"
        return 1
    fi
}

# Function to update and deploy
update_and_deploy() {
    cd "$PROJECT_DIR"
    
    log_message "${GREEN}Starting update process...${NC}"
    
    # Pull latest changes
    log_message "Pulling latest code from Git..."
    if ! git pull origin $GIT_BRANCH; then
        log_message "${RED}Failed to pull latest code${NC}"
        return 1
    fi
    
    # Get the new commit hash
    NEW_COMMIT=$(git rev-parse HEAD)
    log_message "Updated to commit: $NEW_COMMIT"
    
    # Stop existing containers
    log_message "Stopping existing containers..."
    docker-compose down
    
    # Clean up old images to save space
    log_message "Cleaning up old Docker images..."
    docker image prune -f
    
    # Build and start new containers
    log_message "Building and starting new containers..."
    if docker-compose up -d --build; then
        log_message "${GREEN}Deployment completed successfully!${NC}"
        
        # Wait a moment and check container health
        sleep 10
        if docker-compose ps | grep -q "Up"; then
            log_message "${GREEN}Container health check passed${NC}"
        else
            log_message "${RED}Container health check failed${NC}"
            docker-compose logs --tail=20
            return 1
        fi
    else
        log_message "${RED}Deployment failed!${NC}"
        docker-compose logs --tail=20
        return 1
    fi
    
    return 0
}

# Function to run the webpage tracker
run_tracker() {
    log_message "Running webpage tracker..."
    if docker-compose run --rm webpage-tracker python webpage_tracker.py; then
        log_message "${GREEN}Webpage tracker completed successfully${NC}"
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
    
    # Check for changes
    if check_for_changes; then
        # Update and deploy
        if update_and_deploy; then
            log_message "${GREEN}Update and deployment completed successfully${NC}"
            
            # Optionally run the tracker after deployment
            # Uncomment the next line if you want to run tracker after each update
            # run_tracker
        else
            log_message "${RED}Update and deployment failed${NC}"
            exit 1
        fi
    else
        log_message "No updates needed"
    fi
    
    log_message "=== Auto Update Script Completed ==="
    echo "---" >> "$LOG_FILE"
}

# Run main function
main "$@" 