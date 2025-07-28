#!/bin/bash

# Webpage Tracker Daily Execution Script
# This script is designed to be run by cron for daily webpage tracking

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Log file
LOG_FILE="log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting daily webpage tracker execution..." >> "$LOG_FILE"

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "$1"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    log_message "ERROR: Not in a git repository. Skipping git pull."
else
    # Pull latest changes
    log_message "Pulling latest code from git..."
    git pull >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log_message "Git pull successful"
    else
        log_message "WARNING: Git pull failed, continuing with existing code"
    fi
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_message "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    log_message "ERROR: docker-compose is not installed or not in PATH"
    exit 1
fi

# Stop any existing containers
log_message "Stopping existing containers..."
docker-compose down >> "$LOG_FILE" 2>&1

# Build the Docker image
log_message "Building Docker image..."
docker-compose build --no-cache >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "ERROR: Docker build failed"
    exit 1
fi

# Run the container
log_message "Starting webpage tracker..."
docker-compose up >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Check if execution was successful
if [ $EXIT_CODE -eq 0 ]; then
    log_message "Webpage tracker completed successfully"
else
    log_message "ERROR: Webpage tracker failed with exit code $EXIT_CODE"
fi

# Clean up containers
log_message "Cleaning up containers..."
docker-compose down >> "$LOG_FILE" 2>&1

# Optional: Clean up unused Docker images (uncomment if needed)
# log_message "Cleaning up unused Docker images..."
# docker image prune -f >> "$LOG_FILE" 2>&1

TIMESTAMP_END=$(date '+%Y-%m-%d %H:%M:%S')
log_message "Daily execution completed at $TIMESTAMP_END"
echo "---" >> "$LOG_FILE"

exit $EXIT_CODE 