#!/bin/bash

# Environment Configuration Script for Webpage Tracker
# Use this script to set the environment for auto-update behavior

PROJECT_DIR="/opt/webtracker"
ENVIRONMENT_FILE="$PROJECT_DIR/.environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Environment Configuration Script${NC}"
    echo ""
    echo "Usage: $0 [environment]"
    echo ""
    echo "Environments:"
    echo "  production  - Auto-updates enabled (default)"
    echo "  development - Auto-updates disabled"
    echo "  dev         - Auto-updates disabled (alias for development)"
    echo ""
    echo "Examples:"
    echo "  $0 production    # Enable auto-updates"
    echo "  $0 development   # Disable auto-updates"
    echo "  $0 dev          # Disable auto-updates"
    echo ""
    echo "Current environment: $(get_current_environment)"
}

# Function to get current environment
get_current_environment() {
    if [ -f "$ENVIRONMENT_FILE" ]; then
        cat "$ENVIRONMENT_FILE"
    else
        echo "production (default)"
    fi
}

# Function to set environment
set_environment() {
    local env="$1"
    
    # Validate environment
    case "$env" in
        "production"|"development"|"dev")
            # Create project directory if it doesn't exist
            mkdir -p "$PROJECT_DIR"
            
            # Set environment
            echo "$env" > "$ENVIRONMENT_FILE"
            
            echo -e "${GREEN}Environment set to: $env${NC}"
            
            # Show what this means
            if [ "$env" = "development" ] || [ "$env" = "dev" ]; then
                echo -e "${YELLOW}Auto-updates will be disabled${NC}"
            else
                echo -e "${GREEN}Auto-updates will be enabled${NC}"
            fi
            ;;
        *)
            echo -e "${RED}Invalid environment: $env${NC}"
            echo "Valid environments: production, development, dev"
            exit 1
            ;;
    esac
}

# Function to show status
show_status() {
    echo -e "${BLUE}=== Environment Status ===${NC}"
    echo -e "Project Directory: $PROJECT_DIR"
    echo -e "Environment File: $ENVIRONMENT_FILE"
    echo -e "Current Environment: $(get_current_environment)"
    echo ""
    
    if [ -f "$ENVIRONMENT_FILE" ]; then
        ENV=$(cat "$ENVIRONMENT_FILE")
        if [ "$ENV" = "development" ] || [ "$ENV" = "dev" ]; then
            echo -e "${YELLOW}Status: Auto-updates DISABLED${NC}"
        else
            echo -e "${GREEN}Status: Auto-updates ENABLED${NC}"
        fi
    else
        echo -e "${GREEN}Status: Auto-updates ENABLED (default)${NC}"
    fi
}

# Main execution
main() {
    # Check if environment file exists and show current status
    if [ ! -f "$ENVIRONMENT_FILE" ]; then
        echo -e "${YELLOW}No environment file found. Using default: production${NC}"
    fi
    
    # If no arguments provided, show usage and status
    if [ $# -eq 0 ]; then
        show_usage
        echo ""
        show_status
        exit 0
    fi
    
    # Set environment
    set_environment "$1"
    echo ""
    show_status
}

# Run main function
main "$@" 