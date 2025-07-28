#!/bin/bash

# Remote Server Setup Script for Webpage Tracker
# Run this on your remote server to set up the auto-update system

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/opt/webtracker"
GIT_REPO="https://github.com/your-username/webtracker.git"  # Update this
GIT_BRANCH="main"  # or "master"
UPDATE_USER="webtracker"
UPDATE_GROUP="webtracker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Remote Server Setup for Webpage Tracker ===${NC}"

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}This script must be run as root${NC}"
        exit 1
    fi
}

# Function to update system packages
update_system() {
    echo -e "${YELLOW}Updating system packages...${NC}"
    apt-get update
    apt-get upgrade -y
}

# Function to install required packages
install_packages() {
    echo -e "${YELLOW}Installing required packages...${NC}"
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
}

# Function to install Docker
install_docker() {
    echo -e "${YELLOW}Installing Docker...${NC}"
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo -e "${GREEN}Docker installed successfully${NC}"
}

# Function to install Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    
    # Install Docker Compose v2 (included with Docker)
    ln -sf /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose
    
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
}

# Function to create user and group
create_user() {
    echo -e "${YELLOW}Creating user and group...${NC}"
    
    # Create group if it doesn't exist
    if ! getent group $UPDATE_GROUP > /dev/null 2>&1; then
        groupadd $UPDATE_GROUP
    fi
    
    # Create user if it doesn't exist
    if ! id $UPDATE_USER > /dev/null 2>&1; then
        useradd -m -s /bin/bash -g $UPDATE_GROUP $UPDATE_USER
    fi
    
    # Add user to docker group
    usermod -aG docker $UPDATE_USER
    
    echo -e "${GREEN}User and group created successfully${NC}"
}

# Function to set up project directory
setup_project() {
    echo -e "${YELLOW}Setting up project directory...${NC}"
    
    # Create project directory
    mkdir -p $PROJECT_DIR
    
    # Clone repository if it doesn't exist
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        echo -e "${YELLOW}Cloning repository...${NC}"
        git clone -b $GIT_BRANCH $GIT_REPO $PROJECT_DIR
    else
        echo -e "${YELLOW}Repository already exists, pulling latest...${NC}"
        cd $PROJECT_DIR
        git pull origin $GIT_BRANCH
    fi
    
    # Create necessary directories
    mkdir -p $PROJECT_DIR/webpage_versions
    mkdir -p $PROJECT_DIR/diffs
    mkdir -p $PROJECT_DIR/logs
    
    # Set ownership
    chown -R $UPDATE_USER:$UPDATE_GROUP $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    echo -e "${GREEN}Project directory set up successfully${NC}"
}

# Function to set up auto-update script
setup_auto_update() {
    echo -e "${YELLOW}Setting up auto-update script...${NC}"
    
    # Copy auto-update script
    cp $PROJECT_DIR/auto_update.sh /usr/local/bin/auto_update.sh
    chmod +x /usr/local/bin/auto_update.sh
    
    # Copy environment configuration script
    cp $PROJECT_DIR/set_environment.sh /usr/local/bin/set_environment.sh
    chmod +x /usr/local/bin/set_environment.sh
    
    # Create systemd service
    cat > /etc/systemd/system/webtracker-update.service << EOF
[Unit]
Description=Webpage Tracker Auto Update Service
After=network.target

[Service]
Type=oneshot
User=$UPDATE_USER
Group=$UPDATE_GROUP
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/auto_update.sh
StandardOutput=journal
StandardError=journal
EOF

    # Create systemd timer
    cat > /etc/systemd/system/webtracker-update.timer << EOF
[Unit]
Description=Run Webpage Tracker Auto Update every 5 minutes
Requires=webtracker-update.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Enable and start timer
    systemctl daemon-reload
    systemctl enable webtracker-update.timer
    systemctl start webtracker-update.timer
    
    echo -e "${GREEN}Auto-update service set up successfully${NC}"
}

# Function to set up cron alternative (if systemd timer doesn't work)
setup_cron() {
    echo -e "${YELLOW}Setting up cron job as backup...${NC}"
    
    # Add cron job for the user
    (crontab -u $UPDATE_USER -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/auto_update.sh") | crontab -u $UPDATE_USER -
    
    echo -e "${GREEN}Cron job set up successfully${NC}"
}

# Function to set up log rotation
setup_log_rotation() {
    echo -e "${YELLOW}Setting up log rotation...${NC}"
    
    cat > /etc/logrotate.d/webtracker << EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $UPDATE_USER $UPDATE_GROUP
    postrotate
        systemctl reload webtracker-update.service > /dev/null 2>&1 || true
    endscript
}
EOF

    echo -e "${GREEN}Log rotation set up successfully${NC}"
}

# Function to test the setup
test_setup() {
    echo -e "${YELLOW}Testing setup...${NC}"
    
    # Test Docker
    if docker --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker is working${NC}"
    else
        echo -e "${RED}✗ Docker is not working${NC}"
        return 1
    fi
    
    # Test Docker Compose
    if docker-compose --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker Compose is working${NC}"
    else
        echo -e "${RED}✗ Docker Compose is not working${NC}"
        return 1
    fi
    
    # Test Git repository
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo -e "${GREEN}✓ Git repository is set up${NC}"
    else
        echo -e "${RED}✗ Git repository is not set up${NC}"
        return 1
    fi
    
    # Test auto-update script
    if [ -x "/usr/local/bin/auto_update.sh" ]; then
        echo -e "${GREEN}✓ Auto-update script is executable${NC}"
    else
        echo -e "${RED}✗ Auto-update script is not executable${NC}"
        return 1
    fi
    
    echo -e "${GREEN}All tests passed!${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}=== Setup Status ===${NC}"
    echo -e "Project Directory: $PROJECT_DIR"
    echo -e "User: $UPDATE_USER"
    echo -e "Group: $UPDATE_GROUP"
    echo -e "Git Repository: $GIT_REPO"
    echo -e "Git Branch: $GIT_BRANCH"
    echo ""
    echo -e "${YELLOW}Service Status:${NC}"
    systemctl status webtracker-update.timer --no-pager -l
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. Update the Excel file: $PROJECT_DIR/webpages.xlsx"
    echo -e "2. Check logs: tail -f $PROJECT_DIR/logs/auto_update.log"
    echo -e "3. Test manual run: sudo -u $UPDATE_USER /usr/local/bin/auto_update.sh"
    echo -e "4. Monitor containers: docker-compose -f $PROJECT_DIR/docker-compose.yml ps"
    echo -e "5. Set environment: sudo /usr/local/bin/set_environment.sh [production|development]"
}

# Main execution
main() {
    check_root
    
    echo -e "${YELLOW}Starting remote server setup...${NC}"
    
    update_system
    install_packages
    install_docker
    install_docker_compose
    create_user
    setup_project
    setup_auto_update
    setup_cron
    setup_log_rotation
    test_setup
    
    echo -e "${GREEN}=== Setup completed successfully! ===${NC}"
    show_status
}

# Run main function
main "$@" 