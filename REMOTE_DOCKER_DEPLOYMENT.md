# Remote Docker Deployment Guide

Simple guide to deploy your webpage tracker by building the Docker image directly on the remote server.

## 🎯 **Prerequisites**

- Remote server with Docker installed
- SSH access to the server
- Git repository access (SSH key configured)

## 🚀 **Quick Deployment (5 minutes)**

### **Step 1: SSH to Remote Server**
```bash
ssh user@your-server-ip
```

### **Step 2: Clone Repository**
```bash
# Create project directory
mkdir -p /opt/webtracker
cd /opt/webtracker

# Clone your repository
git clone git@github.com:dadlaugh/webtracker.git .

# Verify files
ls -la
```

### **Step 3: Build Docker Image**
```bash
# Build the image
docker build -t webpage-tracker .

# Verify image was created
docker images | grep webpage-tracker
```

### **Step 4: Create Sample Excel File**
```bash
# Create sample Excel file
python3 create_sample_excel_simple.py

# Verify Excel file
ls -la webpages.xlsx
```

### **Step 5: Run Container**
```bash
# Run the container
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker
```

## 🔄 **For Auto-Updates**

### **Set Up Auto-Update Script**
```bash
# Copy auto-update script
sudo cp auto_update.sh /usr/local/bin/auto_update.sh
sudo chmod +x /usr/local/bin/auto_update.sh

# Test the script
sudo -u webtracker /usr/local/bin/auto_update.sh
```

### **Create Systemd Service**
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

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable webtracker-update.timer
sudo systemctl start webtracker-update.timer
```

## 📊 **Monitoring**

### **Check Status**
```bash
# Check service status
sudo systemctl status webtracker-update.timer

# Check logs
tail -f /opt/webtracker/logs/auto_update.log

# Check containers
docker ps -a

# Check webpage versions
ls -la /opt/webtracker/webpage_versions/

# Check diffs
ls -la /opt/webtracker/diffs/
```

### **Manual Run**
```bash
# Run manually
sudo -u webtracker /usr/local/bin/auto_update.sh

# Or run container directly
cd /opt/webtracker
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker
```

## 🔧 **Configuration**

### **Update Excel File**
```bash
# Edit the Excel file
nano /opt/webtracker/webpages.xlsx

# Or copy from your local machine
scp webpages.xlsx user@your-server-ip:/opt/webtracker/
```

### **Change Update Frequency**
```bash
# Edit timer file
sudo nano /etc/systemd/system/webtracker-update.timer

# Change OnCalendar value:
# OnCalendar=*:0/5    # Every 5 minutes
# OnCalendar=*:0/10   # Every 10 minutes
# OnCalendar=hourly   # Every hour

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart webtracker-update.timer
```

## 🚨 **Troubleshooting**

### **Docker Issues**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check Docker images
docker images

# Remove old images
docker image prune -f
```

### **Git Issues**
```bash
# Test Git access
ssh -T git@github.com

# Check repository
cd /opt/webtracker
git status
git pull origin main
```

### **Permission Issues**
```bash
# Fix ownership
sudo chown -R webtracker:webtracker /opt/webtracker

# Fix permissions
sudo chmod -R 755 /opt/webtracker
```

## 🛑 **Emergency Stop**

```bash
# Stop auto-updates
sudo systemctl stop webtracker-update.timer

# Stop all containers
docker stop $(docker ps -q)

# Remove containers
docker rm $(docker ps -aq)
```

## 📋 **Complete One-Line Deployment**

```bash
# Run this on your remote server
mkdir -p /opt/webtracker && cd /opt/webtracker && \
git clone git@github.com:dadlaugh/webtracker.git . && \
docker build -t webpage-tracker . && \
python3 create_sample_excel_simple.py && \
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker
```

This approach is simple, reliable, and gives you full control over the deployment process! 