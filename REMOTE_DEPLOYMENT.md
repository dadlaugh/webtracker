# Remote Server Deployment Guide

This guide will help you set up automated deployment on your remote server that checks for Git updates every 5 minutes.

## 🚀 **Quick Start (5 minutes)**

### 1. **Prepare Your Local Repository**
```bash
# Push your code to GitHub/GitLab
git remote add origin https://github.com/your-username/webtracker.git
git push -u origin main
```

### 2. **Set Up Remote Server**
```bash
# SSH to your remote server
ssh user@your-server-ip

# Download and run the setup script
wget https://raw.githubusercontent.com/your-username/webtracker/main/remote_server_setup.sh
chmod +x remote_server_setup.sh
sudo ./remote_server_setup.sh
```

### 3. **Configure Git Repository**
Edit the setup script to point to your repository:
```bash
# Edit the GIT_REPO variable in remote_server_setup.sh
GIT_REPO="https://github.com/your-username/webtracker.git"
```

## 📋 **Detailed Setup Steps**

### **Step 1: Server Requirements**
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 10GB+ free space
- **Network**: Internet access for Git and Docker

### **Step 2: Update Configuration**

#### **Edit remote_server_setup.sh**
```bash
# Update these variables in remote_server_setup.sh
GIT_REPO="https://github.com/your-username/webtracker.git"
GIT_BRANCH="main"  # or "master"
UPDATE_USER="webtracker"  # can be changed
PROJECT_DIR="/opt/webtracker"  # can be changed
```

#### **For Private Repositories**
```bash
# Option 1: Use SSH keys
GIT_REPO="git@github.com:your-username/webtracker.git"

# Option 2: Use personal access token
GIT_REPO="https://your-token@github.com/your-username/webtracker.git"
```

### **Step 3: Run Setup Script**
```bash
# Make script executable
chmod +x remote_server_setup.sh

# Run as root
sudo ./remote_server_setup.sh
```

### **Step 4: Configure Environment**
```bash
# Set environment (production = auto-updates enabled, development = disabled)
sudo /usr/local/bin/set_environment.sh production

# Check current environment
sudo /usr/local/bin/set_environment.sh
```

### **Step 5: Verify Installation**
```bash
# Check service status
sudo systemctl status webtracker-update.timer

# Check logs
tail -f /opt/webtracker/logs/auto_update.log

# Test manual run
sudo -u webtracker /usr/local/bin/auto_update.sh
```

## 🔧 **Configuration Options**

### **Environment Configuration**
```bash
# Enable auto-updates (production)
sudo /usr/local/bin/set_environment.sh production

# Disable auto-updates (development)
sudo /usr/local/bin/set_environment.sh development

# Check current environment
sudo /usr/local/bin/set_environment.sh
```

**Environment Behavior:**
- **production**: Auto-updates enabled (default)
- **development/dev**: Auto-updates disabled, script will skip updates

### **Update Frequency**
Edit the systemd timer or cron job:

#### **Systemd Timer (Recommended)**
```bash
# Edit the timer file
sudo nano /etc/systemd/system/webtracker-update.timer

# Change OnCalendar value:
OnCalendar=*:0/5    # Every 5 minutes
OnCalendar=*:0/10   # Every 10 minutes
OnCalendar=hourly   # Every hour
OnCalendar=daily    # Daily at midnight
```

#### **Cron Job (Alternative)**
```bash
# Edit cron for the user
sudo crontab -u webtracker -e

# Examples:
*/5 * * * * /usr/local/bin/auto_update.sh    # Every 5 minutes
*/10 * * * * /usr/local/bin/auto_update.sh   # Every 10 minutes
0 * * * * /usr/local/bin/auto_update.sh      # Every hour
0 9 * * * /usr/local/bin/auto_update.sh      # Daily at 9 AM
```

### **Project Directory**
```bash
# Change project directory
PROJECT_DIR="/home/webtracker/project"  # or any path you prefer

# Update ownership
sudo chown -R webtracker:webtracker $PROJECT_DIR
```

## 📊 **Monitoring and Management**

### **Check Service Status**
```bash
# Systemd timer status
sudo systemctl status webtracker-update.timer

# Service logs
sudo journalctl -u webtracker-update.service -f

# Manual service run
sudo systemctl start webtracker-update.service
```

### **View Logs**
```bash
# Auto-update logs
tail -f /opt/webtracker/logs/auto_update.log

# Application logs
tail -f /opt/webtracker/logs/webpage_tracker.log

# Docker logs
docker-compose -f /opt/webtracker/docker-compose.yml logs -f
```

### **Container Management**
```bash
# Check container status
docker-compose -f /opt/webtracker/docker-compose.yml ps

# View container logs
docker-compose -f /opt/webtracker/docker-compose.yml logs webpage-tracker

# Restart containers
docker-compose -f /opt/webtracker/docker-compose.yml restart
```

## 🔒 **Security Considerations**

### **User Permissions**
```bash
# The setup creates a dedicated user with minimal permissions
# Only has access to the project directory and Docker

# Check user permissions
sudo -u webtracker whoami
sudo -u webtracker docker ps
```

### **SSH Key Authentication (for private repos)**
```bash
# Generate SSH key for the webtracker user
sudo -u webtracker ssh-keygen -t rsa -b 4096

# Add public key to GitHub/GitLab
sudo -u webtracker cat ~/.ssh/id_rsa.pub
# Copy this to your Git provider's SSH keys
```

### **Firewall Configuration**
```bash
# Allow SSH (if not already allowed)
sudo ufw allow ssh

# Allow specific ports if needed
sudo ufw allow 8080  # if running web interface
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Git Repository Access**
```bash
# Test Git access
sudo -u webtracker git ls-remote https://github.com/your-username/webtracker.git

# For SSH keys
sudo -u webtracker ssh -T git@github.com
```

#### **2. Docker Issues**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check Docker permissions
sudo usermod -aG docker webtracker
```

#### **3. Service Not Running**
```bash
# Check timer status
sudo systemctl status webtracker-update.timer

# Enable and start timer
sudo systemctl enable webtracker-update.timer
sudo systemctl start webtracker-update.timer

# Check service logs
sudo journalctl -u webtracker-update.service -n 50
```

#### **4. Permission Issues**
```bash
# Fix ownership
sudo chown -R webtracker:webtracker /opt/webtracker

# Fix permissions
sudo chmod -R 755 /opt/webtracker
sudo chmod +x /usr/local/bin/auto_update.sh
```

### **Debug Mode**
```bash
# Run auto-update script manually with verbose output
sudo -u webtracker bash -x /usr/local/bin/auto_update.sh

# Check all logs
sudo journalctl -u webtracker-update.service --since "1 hour ago"
```

## 📈 **Performance Optimization**

### **Disk Space Management**
```bash
# Clean up old Docker images
docker image prune -f

# Clean up old logs
sudo logrotate -f /etc/logrotate.d/webtracker

# Monitor disk usage
df -h /opt/webtracker
```

### **Resource Monitoring**
```bash
# Monitor system resources
htop

# Monitor Docker resources
docker stats

# Monitor disk I/O
iotop
```

## 🔄 **Update Process**

### **How It Works**
1. **Every 5 minutes**: Systemd timer triggers the service
2. **Check for changes**: Script fetches latest Git changes
3. **If changes found**: Pull code and redeploy containers
4. **Health check**: Verify containers are running
5. **Log results**: Record success/failure in logs

### **Manual Updates**
```bash
# Force manual update
sudo -u webtracker /usr/local/bin/auto_update.sh

# Force update even if no changes
sudo -u webtracker bash -c "cd /opt/webtracker && git pull && docker-compose up -d --build"
```

## 📞 **Support**

### **Useful Commands**
```bash
# Service management
sudo systemctl {start|stop|restart|status} webtracker-update.timer
sudo systemctl {enable|disable} webtracker-update.timer

# Log viewing
sudo journalctl -u webtracker-update.service -f
tail -f /opt/webtracker/logs/auto_update.log

# Container management
docker-compose -f /opt/webtracker/docker-compose.yml {up|down|restart|logs}
```

### **Emergency Stop**
```bash
# Stop auto-updates
sudo systemctl stop webtracker-update.timer

# Stop containers
docker-compose -f /opt/webtracker/docker-compose.yml down
```

This setup provides a robust, automated deployment system that will keep your webpage tracker up-to-date with minimal manual intervention! 