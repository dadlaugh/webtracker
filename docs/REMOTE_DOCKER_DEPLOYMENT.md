# 🚀 Remote Docker Deployment Guide

Complete guide for deploying the Webpage Tracker system on a remote server using Docker.

## 📋 Prerequisites

- **Ubuntu/Debian server** (or similar Linux distribution)
- **Docker** and **Docker Compose** installed
- **Git** access to the repository
- **SSH** access to the server

## 🔧 Server Setup

### **1. Install Docker**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
exit
# SSH back into the server
```

### **2. Create Project Directory**
```bash
# Create project directory
sudo mkdir -p /opt/webtracker
sudo chown $USER:$USER /opt/webtracker
cd /opt/webtracker
```

### **3. Clone Repository**
```bash
# Clone the repository
git clone git@github.com:dadlaugh/webtracker.git .

# Or if you don't have SSH keys set up:
# git clone https://github.com/dadlaugh/webtracker.git .
```

## 🚀 Quick Deployment

### **Option 1: Use Deployment Script**
```bash
# Run the deployment script
./scripts/deploy.sh
```

### **Option 2: Manual Deployment**
```bash
# Pull latest code
git pull origin main

# Start automation container
./scripts/start_automation.sh
```

## 📦 Docker Services

### **Available Services**

#### **1. Webpage Tracker (One-time execution)**
```bash
# Run tracker once
docker-compose --profile tracker up

# Or manually
docker run --rm \
    -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
    -v $(pwd)/webpage_versions:/app/webpage_versions \
    -v $(pwd)/diffs:/app/diffs \
    webpage-tracker
```

#### **2. Web Server (Team Access)**
```bash
# Start web server
./scripts/start_web_server.sh

# Or use Docker Compose
./scripts/start_web_server_compose.sh

# Or manually
docker-compose --profile web up -d
```

#### **3. Automation (Scheduled Runs)**
```bash
# Start automation (morning runs + Git detection)
./scripts/start_automation.sh

# Or manually
docker-compose --profile automation up -d --build
```

#### **4. Full Stack (Tracker + Web Server)**
```bash
# Start both tracker and web server
docker-compose --profile webtracker-full up -d
```

## ⚙️ Configuration

### **Environment Setup**
```bash
# Set environment (production/development)
./scripts/set_environment.sh production

# Check current environment
./scripts/set_environment.sh
```

### **URL Configuration**
Edit `webpages.xlsx` to add/remove URLs:
```bash
# Edit the Excel file
nano webpages.xlsx

# Or copy from your local machine
scp webpages.xlsx user@your-server-ip:/opt/webtracker/
```

## 📊 Monitoring

### **Check Service Status**
```bash
# Check all containers
docker ps -a

# Check automation status
docker-compose --profile automation ps

# Check web server status
docker-compose --profile web ps
```

### **View Logs**
```bash
# Automation logs
docker-compose --profile automation logs -f

# Web server logs
docker-compose --profile web logs -f

# Or individual containers
docker logs webtracker-automation
docker logs webpage-web-server
```

### **Health Checks**
```bash
# Check automation health
curl http://localhost:8080/health

# Check web server
curl http://localhost:8080
```

## 🔄 Automation Features

### **What the Automation Does**

#### **Morning Runs (9:00 AM Daily)**
- Automatically runs `webpage_tracker` every morning
- Records diffs if any webpage changes are detected
- Logs all activities to `/opt/webtracker/logs/`

#### **Git Change Detection (Every 5 Minutes)**
- Checks for new Git commits every 5 minutes
- If changes detected: Pulls latest code, rebuilds Docker image, runs tracker
- If no changes: Does nothing
- Environment protection: Won't run in development environments

#### **Health Monitoring**
- Built-in health checks at `http://localhost:8080/health`
- Process monitoring and auto-restart
- Comprehensive logging with timestamps

### **Manual Runs**
```bash
# Run tracker manually
docker run --rm \
    -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
    -v $(pwd)/webpage_versions:/app/webpage_versions \
    -v $(pwd)/diffs:/app/diffs \
    webpage-tracker

# Check cron jobs
docker exec webtracker-automation crontab -l

# View automation logs
tail -f logs/auto_update.log
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Docker Permission Errors**
```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

#### **2. Port Conflicts**
```bash
# Check what's using port 8080
sudo netstat -tlnp | grep :8080

# Change port in docker-compose.yml if needed
# Edit the ports section: "8081:8080"
```

#### **3. Container Won't Start**
```bash
# Check container logs
docker logs webtracker-automation

# Check Docker daemon
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

#### **4. Git Access Issues**
```bash
# Set up SSH keys for Git
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
# Add public key to GitHub repository
```

### **Debug Commands**
```bash
# Check automation container
docker exec -it webtracker-automation /bin/sh

# Check cron jobs
docker exec webtracker-automation crontab -l

# Check file permissions
ls -la /opt/webtracker/

# Check disk space
df -h
```

## 📁 File Structure

After deployment, your server will have this structure:
```
/opt/webtracker/
├── 📄 Core Files
│   ├── webpage_tracker.py      # Main tracking script
│   ├── web_server.py           # Flask web server
│   ├── webpages.xlsx           # URL configuration
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Main application container
│
├── 📦 Docker & Deployment
│   ├── docker-compose.yml      # Multi-service orchestration
│   └── automation/
│       ├── Dockerfile.automation    # Automation container
│       └── automation_entrypoint.sh # Automation startup script
│
├── 🔧 Scripts
│   ├── start_automation.sh     # Start automation container
│   ├── start_web_server.sh     # Start web server
│   ├── start_web_server_compose.sh # Start web server (Docker Compose)
│   ├── deploy.sh               # Quick deployment
│   ├── set_environment.sh      # Environment configuration
│   ├── auto_update.sh          # Git change detection
│   └── morning_tracker.sh      # Daily morning runs
│
├── 📚 Documentation
│   └── REMOTE_DOCKER_DEPLOYMENT.md  # This guide
│
├── 🎯 Examples
│   ├── create_example_diff.py      # Create sample diffs
│   ├── create_more_examples.py     # Create additional examples
│   └── create_sample_excel_simple.py # Create sample Excel file
│
├── 📊 Data Directories
│   ├── webpage_versions/       # Saved webpage versions
│   ├── diffs/                  # Generated diff files
│   └── logs/                   # Application logs
│
└── 📋 Configuration
    ├── .gitignore              # Git ignore rules
    └── README.md               # Project documentation
```

## 🎯 Quick Commands Reference

### **Start Services**
```bash
# Start automation (recommended)
./scripts/start_automation.sh

# Start web server only
./scripts/start_web_server.sh

# Start web server (Docker Compose)
./scripts/start_web_server_compose.sh

# Start full stack
docker-compose --profile webtracker-full up -d
```

### **Stop Services**
```bash
# Stop automation
docker-compose --profile automation down

# Stop web server
docker-compose --profile web down

# Stop all services
docker-compose down
```

### **Update System**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart automation
./scripts/start_automation.sh

# Or rebuild all services
docker-compose --profile automation up -d --build
```

### **Monitoring**
```bash
# View all logs
docker-compose logs -f

# Check automation status
docker-compose --profile automation ps

# Health check
curl http://localhost:8080/health
```

## 🚀 Next Steps

1. **Configure URLs**: Edit `webpages.xlsx` with your target URLs
2. **Set Environment**: Run `./scripts/set_environment.sh production`
3. **Start Automation**: Run `./scripts/start_automation.sh`
4. **Access Web Interface**: Visit `http://your-server-ip:8080`
5. **Monitor**: Check logs and health status regularly

Your webpage tracker is now fully automated and ready to monitor your websites! 🎉 