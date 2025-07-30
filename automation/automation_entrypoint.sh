#!/bin/bash

# Automation Entrypoint Script
# This script starts the cron daemon and provides a health check endpoint

# Configuration
PROJECT_DIR="/opt/webtracker"
LOG_DIR="$PROJECT_DIR/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1"
}

# Function to start cron daemon
start_cron() {
    log_message "${GREEN}Starting cron daemon...${NC}"
    
    # Start cron daemon
    crond -f -d 8 &
    CRON_PID=$!
    
    log_message "${GREEN}Cron daemon started with PID: $CRON_PID${NC}"
    
    # Wait for cron to be ready
    sleep 2
    
    # List cron jobs
    log_message "${YELLOW}Current cron jobs:${NC}"
    crontab -l
}

# Function to start health check server
start_health_server() {
    log_message "${GREEN}Starting health check server...${NC}"
    
    # Create a simple HTTP server for health checks
    while true; do
        echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nAutomation container is running" | nc -l -p 8080
    done &
    
    HEALTH_PID=$!
    log_message "${GREEN}Health check server started with PID: $HEALTH_PID${NC}"
}

# Function to check if we're in the right environment
check_environment() {
    # Check if we're running in Docker
    if [ ! -f /.dockerenv ]; then
        log_message "${YELLOW}Warning: Not running in Docker container${NC}"
    fi
    
    # Check if we have access to the project directory
    if [ ! -d "$PROJECT_DIR" ]; then
        log_message "${YELLOW}Warning: Project directory $PROJECT_DIR not found${NC}"
        log_message "${YELLOW}Make sure to mount the project directory as a volume${NC}"
    fi
    
    # Check if we have access to Docker socket
    if [ ! -S /var/run/docker.sock ]; then
        log_message "${YELLOW}Warning: Docker socket not found${NC}"
        log_message "${YELLOW}Make sure to mount /var/run/docker.sock as a volume${NC}"
    fi
    
    # Create environment file if it doesn't exist
    if [ ! -f "$PROJECT_DIR/.environment" ]; then
        log_message "${YELLOW}Creating environment file...${NC}"
        echo "production" > "$PROJECT_DIR/.environment"
    fi
}

# Function to monitor processes
monitor_processes() {
    log_message "${GREEN}Starting process monitor...${NC}"
    
    while true; do
        # Check if cron is still running
        if ! kill -0 $CRON_PID 2>/dev/null; then
            log_message "${YELLOW}Cron daemon stopped, restarting...${NC}"
            start_cron
        fi
        
        # Check if health server is still running
        if ! kill -0 $HEALTH_PID 2>/dev/null; then
            log_message "${YELLOW}Health server stopped, restarting...${NC}"
            start_health_server
        fi
        
        # Sleep for 30 seconds
        sleep 30
    done
}

# Main execution
main() {
    log_message "${GREEN}=== Automation Container Starting ==="
    
    # Check environment
    check_environment
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    
    # Start cron daemon
    start_cron
    
    # Start health check server
    start_health_server
    
    log_message "${GREEN}=== Automation Container Started Successfully ==="
    log_message "${GREEN}Morning tracker will run at 9:00 AM daily${NC}"
    log_message "${GREEN}Git change detection will run every 5 minutes${NC}"
    log_message "${GREEN}Health check available at http://localhost:8080/health${NC}"
    
    # Start process monitor
    monitor_processes
}

# Handle signals
trap 'log_message "Received signal, shutting down..."; exit 0' SIGTERM SIGINT

# Run main function
main "$@" 