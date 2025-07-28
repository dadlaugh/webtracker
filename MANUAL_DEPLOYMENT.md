# Manual Deployment Guide - Step by Step

This guide will walk you through manually setting up the webpage tracker on your remote server, step by step, without using automated scripts.

## 🎯 **Prerequisites**

- Remote server with Ubuntu 20.04+ or CentOS 8+
- SSH access to the server
- Root or sudo privileges
- Internet connection on the server

## 📋 **Step 1: Connect to Your Remote Server**

```bash
# SSH to your remote server
ssh user@your-server-ip

# Verify you have sudo access
sudo whoami
# Should return: root
```

## 📋 **Step 2: Update System Packages**

```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release
```

## 📋 **Step 3: Install Docker**

```bash
# Remove old Docker versions (if any)
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker installation
docker --version
docker-compose --version
```

## 📋 **Step 4: Create User and Group**

```bash
# Create webtracker group
sudo groupadd webtracker

# Create webtracker user
sudo useradd -m -s /bin/bash -g webtracker webtracker

# Add user to docker group
sudo usermod -aG docker webtracker

# Verify user creation
id webtracker
```

## 📋 **Step 5: Set Up SSH Keys for Git**

```bash
# Switch to webtracker user
sudo -u webtracker bash

# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate SSH key (if you haven't already)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Display public key
cat ~/.ssh/id_rsa.pub

# Exit webtracker user shell
exit
```

**Important**: Copy the public key output and add it to your GitHub SSH keys at: https://github.com/settings/keys

## 📋 **Step 6: Test Git Access**

```bash
# Test SSH connection to GitHub
sudo -u webtracker ssh -T git@github.com

# You should see: "Hi dadlaugh! You've successfully authenticated..."
```

## 📋 **Step 7: Create Project Directory**

```bash
# Create project directory
sudo mkdir -p /opt/webtracker

# Set ownership
sudo chown webtracker:webtracker /opt/webtracker

# Create necessary subdirectories
sudo -u webtracker mkdir -p /opt/webtracker/webpage_versions
sudo -u webtracker mkdir -p /opt/webtracker/diffs
sudo -u webtracker mkdir -p /opt/webtracker/logs
```

## 📋 **Step 8: Clone Your Repository**

```bash
# Clone the repository
sudo -u webtracker git clone git@github.com:dadlaugh/webtracker.git /opt/webtracker

# Verify the clone
sudo -u webtracker ls -la /opt/webtracker
```

## 📋 **Step 9: Set Up Environment Configuration**

```bash
# Create environment file (production by default)
sudo -u webtracker echo "production" > /opt/webtracker/.environment

# Verify environment
sudo -u webtracker cat /opt/webtracker/.environment
```

## 📋 **Step 10: Create Sample Excel File**

```bash
# Navigate to project directory
cd /opt/webtracker

# Create sample Excel file (if not exists)
sudo -u webtracker python3 create_sample_excel_simple.py

# Verify Excel file
sudo -u webtracker ls -la webpages.xlsx
```

## 📋 **Step 11: Test Docker Build**

```bash
# Build Docker image
sudo -u webtracker docker-compose build

# Verify build
sudo -u webtracker docker images | grep webpage-tracker
```

## 📋 **Step 12: Test First Run**

```bash
# Run the webpage tracker manually
sudo -u webtracker docker-compose up

# Check if it worked
sudo -u webtracker ls -la webpage_versions/
sudo -u webtracker ls -la diffs/
```

## 📋 **Step 13: Set Up Auto-Update Script**

```bash
# Copy auto-update script to system location
sudo cp /opt/webtracker/auto_update.sh /usr/local/bin/auto_update.sh

# Make it executable
sudo chmod +x /usr/local/bin/auto_update.sh

# Test the script manually
sudo -u webtracker /usr/local/bin/auto_update.sh
```

## 📋 **Step 14: Create Systemd Service**

```bash
# Create service file
sudo tee /etc/systemd/system/webtracker-update.service > /dev/null << 'EOF'
[Unit]
Description=Webpage Tracker Auto Update Service
After=network.target

[Service]
Type=oneshot
User=webtracker
Group=webtracker
WorkingDirectory=/opt/webtracker
ExecStart=/usr/local/bin/auto_update.sh
StandardOutput=journal
StandardError=journal
EOF

# Create timer file
sudo tee /etc/systemd/system/webtracker-update.timer > /dev/null << 'EOF'
[Unit]
Description=Run Webpage Tracker Auto Update every 5 minutes
Requires=webtracker-update.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

## 📋 **Step 15: Enable and Start Service**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable timer
sudo systemctl enable webtracker-update.timer

# Start timer
sudo systemctl start webtracker-update.timer

# Check status
sudo systemctl status webtracker-update.timer
```

## 📋 **Step 16: Set Up Log Rotation**

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/webtracker > /dev/null << 'EOF'
/opt/webtracker/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 webtracker webtracker
    postrotate
        systemctl reload webtracker-update.service > /dev/null 2>&1 || true
    endscript
}
EOF
```

## 📋 **Step 17: Verify Everything Works**

```bash
# Check service status
sudo systemctl status webtracker-update.timer

# Check logs
sudo -u webtracker tail -f /opt/webtracker/logs/auto_update.log

# Check containers
sudo -u webtracker docker-compose -f /opt/webtracker/docker-compose.yml ps

# Check webpage versions
sudo -u webtracker ls -la /opt/webtracker/webpage_versions/

# Check diffs
sudo -u webtracker ls -la /opt/webtracker/diffs/
```

## 📋 **Step 18: Test Auto-Update**

```bash
# Wait a few minutes for the timer to trigger
# Or manually trigger the service
sudo systemctl start webtracker-update.service

# Check the logs
sudo -u webtracker tail -f /opt/webtracker/logs/auto_update.log
```

## 🔧 **Configuration Options**

### **Change Update Frequency**
```bash
# Edit the timer file
sudo nano /etc/systemd/system/webtracker-update.timer

# Change OnCalendar value:
# OnCalendar=*:0/5    # Every 5 minutes
# OnCalendar=*:0/10   # Every 10 minutes
# OnCalendar=hourly   # Every hour

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart webtracker-update.timer
```

### **Set Environment**
```bash
# For production (auto-updates enabled)
sudo -u webtracker echo "production" > /opt/webtracker/.environment

# For development (auto-updates disabled)
sudo -u webtracker echo "development" > /opt/webtracker/.environment
```

## 📊 **Monitoring Commands**

```bash
# Check service status
sudo systemctl status webtracker-update.timer

# View service logs
sudo journalctl -u webtracker-update.service -f

# View application logs
sudo -u webtracker tail -f /opt/webtracker/logs/auto_update.log

# Check container status
sudo -u webtracker docker-compose -f /opt/webtracker/docker-compose.yml ps

# View container logs
sudo -u webtracker docker-compose -f /opt/webtracker/docker-compose.yml logs
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **SSH Key Issues**
   ```bash
   # Test SSH connection
   sudo -u webtracker ssh -T git@github.com
   
   # Check key permissions
   sudo -u webtracker chmod 600 ~/.ssh/id_rsa
   sudo -u webtracker chmod 644 ~/.ssh/id_rsa.pub
   ```

2. **Docker Issues**
   ```bash
   # Check Docker status
   sudo systemctl status docker
   
   # Restart Docker
   sudo systemctl restart docker
   
   # Check user permissions
   sudo usermod -aG docker webtracker
   ```

3. **Service Issues**
   ```bash
   # Check service logs
   sudo journalctl -u webtracker-update.service -n 50
   
   # Restart service
   sudo systemctl restart webtracker-update.timer
   ```

## 🛑 **Emergency Stop**

```bash
# Stop auto-updates
sudo systemctl stop webtracker-update.timer

# Stop containers
sudo -u webtracker docker-compose -f /opt/webtracker/docker-compose.yml down
```

This manual approach gives you full control and understanding of each step in the deployment process! 