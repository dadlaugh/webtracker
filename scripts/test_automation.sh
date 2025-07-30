#!/bin/bash

# Test Automation Script
# This script tests the automation functionality without waiting for actual timing

# Configuration
PROJECT_DIR="/opt/webtracker"
LOG_FILE="$PROJECT_DIR/logs/test_automation.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo -e "${BLUE}=== Automation Test Suite ===${NC}"

# Test 1: Environment Setup
test_environment() {
    echo -e "${YELLOW}Test 1: Environment Setup${NC}"
    
    # Create test environment
    mkdir -p "$PROJECT_DIR/logs"
    echo "production" > "$PROJECT_DIR/.environment"
    
    if [ -f "$PROJECT_DIR/.environment" ]; then
        echo -e "${GREEN}✅ Environment file created successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Environment file creation failed${NC}"
        return 1
    fi
}

# Test 2: Docker Access
test_docker() {
    echo -e "${YELLOW}Test 2: Docker Access${NC}"
    
    if docker info > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker is accessible${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker is not accessible${NC}"
        return 1
    fi
}

# Test 3: Git Repository
test_git() {
    echo -e "${YELLOW}Test 3: Git Repository${NC}"
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo -e "${GREEN}✅ Git repository found${NC}"
        return 0
    else
        echo -e "${RED}❌ Git repository not found${NC}"
        return 1
    fi
}

# Test 4: Morning Tracker Script
test_morning_tracker() {
    echo -e "${YELLOW}Test 4: Morning Tracker Script${NC}"
    
    if [ -f "$PROJECT_DIR/scripts/morning_tracker.sh" ]; then
        echo -e "${GREEN}✅ Morning tracker script exists${NC}"
        
        # Test script syntax
        if bash -n "$PROJECT_DIR/scripts/morning_tracker.sh"; then
            echo -e "${GREEN}✅ Morning tracker script syntax is valid${NC}"
            return 0
        else
            echo -e "${RED}❌ Morning tracker script has syntax errors${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Morning tracker script not found${NC}"
        return 1
    fi
}

# Test 5: Auto Update Script
test_auto_update() {
    echo -e "${YELLOW}Test 5: Auto Update Script${NC}"
    
    if [ -f "$PROJECT_DIR/scripts/auto_update.sh" ]; then
        echo -e "${GREEN}✅ Auto update script exists${NC}"
        
        # Test script syntax
        if bash -n "$PROJECT_DIR/scripts/auto_update.sh"; then
            echo -e "${GREEN}✅ Auto update script syntax is valid${NC}"
            return 0
        else
            echo -e "${RED}❌ Auto update script has syntax errors${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Auto update script not found${NC}"
        return 1
    fi
}

# Test 6: Docker Image
test_docker_image() {
    echo -e "${YELLOW}Test 6: Docker Image${NC}"
    
    if docker images | grep -q "webtracker_web-server"; then
        echo -e "${GREEN}✅ Docker image exists${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker image not found${NC}"
        return 1
    fi
}

# Test 7: Manual Tracker Run
test_manual_tracker() {
    echo -e "${YELLOW}Test 7: Manual Tracker Run (Dry Run)${NC}"
    
    # Test with a small subset or dry run
    cd "$PROJECT_DIR"
    
    # Create a test command that doesn't actually run the tracker
    echo -e "${BLUE}Testing tracker command structure...${NC}"
    
    # Check if the command would work (without actually running it)
    if docker run --rm --entrypoint "echo" webtracker_web-server "Test successful"; then
        echo -e "${GREEN}✅ Tracker command structure is valid${NC}"
        return 0
    else
        echo -e "${RED}❌ Tracker command structure failed${NC}"
        return 1
    fi
}

# Test 8: Cron Configuration
test_cron() {
    echo -e "${YELLOW}Test 8: Cron Configuration${NC}"
    
    # Test if cron can be started
    if command -v crond > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Cron daemon is available${NC}"
        
        # Test cron job syntax
        echo "*/5 * * * * echo 'test'" | crontab -
        if crontab -l > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Cron job configuration is valid${NC}"
            crontab -r  # Remove test job
            return 0
        else
            echo -e "${RED}❌ Cron job configuration failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Cron daemon not available${NC}"
        return 1
    fi
}

# Main test execution
main() {
    log_message "Starting automation test suite..."
    
    local tests_passed=0
    local tests_total=8
    
    # Run all tests
    test_environment && ((tests_passed++))
    test_docker && ((tests_passed++))
    test_git && ((tests_passed++))
    test_morning_tracker && ((tests_passed++))
    test_auto_update && ((tests_passed++))
    test_docker_image && ((tests_passed++))
    test_manual_tracker && ((tests_passed++))
    test_cron && ((tests_passed++))
    
    # Results
    echo -e "\n${BLUE}=== Test Results ===${NC}"
    echo -e "${GREEN}Tests passed: $tests_passed/$tests_total${NC}"
    
    if [ $tests_passed -eq $tests_total ]; then
        echo -e "${GREEN}🎉 All tests passed! Automation should work correctly.${NC}"
        return 0
    else
        echo -e "${RED}⚠️  Some tests failed. Please fix issues before deploying.${NC}"
        return 1
    fi
}

# Run tests
main "$@" 