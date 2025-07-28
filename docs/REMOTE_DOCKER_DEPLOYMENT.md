# Remote Docker Deployment Guide

Simple guide to deploy your webpage tracker with comprehensive asset archiving and web server for team access.

## 🎯 **Prerequisites**

- Remote server with Docker installed
- SSH access to the server
- Git repository access (SSH key configured)

## 🌟 **Enhanced Features**

### **Comprehensive Webpage Archiving**
- **CSS Embedding**: All stylesheets downloaded and embedded inline
- **JavaScript Embedding**: All JS files downloaded and embedded inline  
- **Image Embedding**: Images converted to base64 and embedded
- **Complete Visual Preservation**: Pages saved exactly as they appear live
- **Self-Contained Files**: No broken links or missing assets

### **Team Access Web Interface**
- **Beautiful Dashboard**: Professional interface for browsing files
- **File Statistics**: Shows counts of versions, diffs, and domains
- **Easy Navigation**: Browse versions, diffs, and logs
- **Direct File Access**: Click to view any saved webpage
- **Responsive Design**: Works on desktop and mobile devices

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

### **Step 6: Start Web Server (Optional)**

#### **Option A: Docker Web Server (Recommended)**
```bash
# Start web server in Docker
./start_web_server.sh

# Or manually with Docker
docker run -d \
    --name webpage-web-server \
    -p 8080:8080 \
    -v "$(pwd)/webpage_versions:/app/webpage_versions:ro" \
    -v "$(pwd)/diffs:/app/diffs:ro" \
    -v "$(pwd)/logs:/app/logs:ro" \
    -v "$(pwd)/web_server.py:/app/web_server.py:ro" \
    webpage-tracker \
    python web_server.py
```

#### **Option B: Docker Compose**
```bash
# Start web server only
docker-compose --profile web up -d

# Start both tracker and web server
docker-compose --profile webtracker-full up -d
```

#### **Option C: Direct Python (Alternative)**
```bash
# Install Flask if not already installed
pip3 install flask

# Start web server for team access
python3 web_server.py &

# Access the web interface
echo "Web server running at: http://$(hostname -I | awk '{print $1}'):8080"
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

# Check web server
ps aux | grep web_server.py
curl -s http://localhost:8080 | head -5
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

# Start web server manually
python3 web_server.py &
```

## 🔧 **Configuration**

### **Update Excel File**
```bash
# Edit the Excel file
nano /opt/webtracker/webpages.xlsx

# Or copy from your local machine
scp webpages.xlsx user@your-server-ip:/opt/webtracker/
```

### **Web Server Configuration**

#### **Option A: Docker Web Server Service (Recommended)**
```bash
# Create systemd service for Docker web server
sudo tee /etc/systemd/system/webtracker-web.service > /dev/null << 'EOF'
[Unit]
Description=Webpage Tracker Web Server (Docker)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=webtracker
Group=webtracker
WorkingDirectory=/opt/webtracker
ExecStart=/opt/webtracker/start_web_server.sh
ExecStop=/usr/bin/docker stop webpage-web-server
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
EOF

# Enable and start web server
sudo systemctl daemon-reload
sudo systemctl enable webtracker-web.service
sudo systemctl start webtracker-web.service
```

#### **Option B: Docker Compose Service**
```bash
# Create systemd service for Docker Compose
sudo tee /etc/systemd/system/webtracker-web.service > /dev/null << 'EOF'
[Unit]
Description=Webpage Tracker Web Server (Docker Compose)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=webtracker
Group=webtracker
WorkingDirectory=/opt/webtracker
ExecStart=/usr/local/bin/docker-compose --profile web up -d
ExecStop=/usr/local/bin/docker-compose --profile web down
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
EOF

# Enable and start web server
sudo systemctl daemon-reload
sudo systemctl enable webtracker-web.service
sudo systemctl start webtracker-web.service
```

#### **Option C: Direct Python Service (Alternative)**
```bash
# Start web server on boot (optional)
sudo tee /etc/systemd/system/webtracker-web.service > /dev/null << 'EOF'
[Unit]
Description=Webpage Tracker Web Server
After=network.target

[Service]
Type=simple
User=webtracker
Group=webtracker
WorkingDirectory=/opt/webtracker
ExecStart=/usr/bin/python3 web_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start web server
sudo systemctl daemon-reload
sudo systemctl enable webtracker-web.service
sudo systemctl start webtracker-web.service
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

### **Web Server Issues**
```bash
# Check web server status
sudo systemctl status webtracker-web.service

# Check web server logs
sudo journalctl -u webtracker-web.service -f

# Check Docker container status
docker ps | grep webpage-web-server

# Check Docker container logs
docker logs webpage-web-server

# Test web server manually
cd /opt/webtracker
./start_web_server.sh

# Check if port 8080 is in use
sudo netstat -tlnp | grep :8080

# Restart web server container
docker restart webpage-web-server
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

# Stop web server
sudo systemctl stop webtracker-web.service

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
           webpage-tracker && \
./start_web_server.sh
```

## 🚀 **Quick Start Commands**

### **Run Tracker Only**
```bash
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker
```

### **Start Web Server Only**
```bash
./start_web_server.sh
```

### **Run Both (Docker Compose)**
```bash
docker-compose --profile webtracker-full up -d
```

### **Access Web Interface**
```bash
echo "Web interface: http://$(hostname -I | awk '{print $1}'):8080"
```

This approach is simple, reliable, and gives you full control over the deployment process! 