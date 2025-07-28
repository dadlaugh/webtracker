# 🌐 Webpage Tracker

A comprehensive system for tracking webpage changes, generating diffs, and providing team access through a web interface.

## 📁 Project Structure

```
webtracker/
├── 📄 Core Files
│   ├── webpage_tracker.py      # Main tracking script
│   ├── web_server.py           # Flask web server for team access
│   ├── webpages.xlsx           # URL configuration file
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
│   ├── deploy.sh               # Quick deployment
│   ├── set_environment.sh      # Environment configuration
│   ├── auto_update.sh          # Git change detection
│   └── morning_tracker.sh      # Daily morning runs
│
├── 📚 Documentation
│   └── REMOTE_DOCKER_DEPLOYMENT.md  # Deployment guide
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
    └── README.md               # This file
```

## 🚀 Quick Start

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run tracker
python webpage_tracker.py

# Start web server
python web_server.py
```

### **Docker Development**
```bash
# Run tracker only
docker-compose --profile tracker up

# Start web server
./scripts/start_web_server.sh

# Start automation (morning runs + Git detection)
./scripts/start_automation.sh
```

### **Full Stack (Tracker + Web Server)**
```bash
docker-compose --profile webtracker-full up -d
```

## 🎯 Features

### **Core Functionality**
- **Webpage Tracking**: Fetches and saves webpage versions
- **Diff Generation**: Creates HTML diffs showing changes
- **Comprehensive Archiving**: Embeds CSS, JS, and images inline
- **Hierarchical Storage**: Organizes files by domain/path structure

### **Automation**
- **Morning Runs**: Daily execution at 9:00 AM
- **Git Integration**: Automatic runs on code changes
- **Environment Protection**: Won't run in development
- **Health Monitoring**: Built-in health checks

### **Team Access**
- **Web Interface**: Browse versions and diffs
- **Tree Navigation**: Hierarchical file display
- **Search & Filter**: Easy file discovery
- **Responsive Design**: Works on all devices

## 🔧 Configuration

### **URL Configuration**
Edit `webpages.xlsx` to add/remove URLs to track:
- **URL**: Full webpage URL
- **Name**: Optional display name
- **Active**: Enable/disable tracking

### **Environment Setup**
```bash
# Set environment (production/development)
./scripts/set_environment.sh production
```

### **Docker Services**
- **`webpage-tracker`**: One-time tracking execution
- **`web-server`**: Flask web interface
- **`automation`**: Scheduled runs and Git detection
- **`webtracker-full`**: Combined tracker + web server

## 📊 Monitoring

### **Logs**
```bash
# View application logs
tail -f logs/webpage_tracker.log

# View automation logs
docker-compose --profile automation logs -f

# View web server logs
docker logs webpage-web-server
```

### **Health Checks**
```bash
# Check automation health
curl http://localhost:8080/health

# Check web server
curl http://localhost:8080
```

## 🚀 Deployment

### **Remote Server Deployment**
See `docs/REMOTE_DOCKER_DEPLOYMENT.md` for detailed instructions.

### **Quick Deployment**
```bash
# Deploy to remote server
./scripts/deploy.sh

# Or manual deployment
git pull origin main
docker-compose --profile automation up -d --build
```

## 🎯 Use Cases

- **Website Monitoring**: Track changes to important websites
- **Content Verification**: Ensure content hasn't been modified
- **Team Collaboration**: Share webpage versions with team
- **Change Detection**: Get notified of webpage changes
- **Archive Management**: Maintain historical webpage versions

## 🔍 Troubleshooting

### **Common Issues**
1. **Docker not running**: Ensure Docker daemon is started
2. **Permission errors**: Check file permissions and Docker socket access
3. **Port conflicts**: Change ports in docker-compose.yml
4. **Environment issues**: Verify .environment file configuration

### **Log Analysis**
```bash
# Check automation status
docker-compose --profile automation ps

# View recent logs
docker-compose --profile automation logs --tail=50

# Check cron jobs
docker exec webtracker-automation crontab -l
```

## 📝 License

This project is open source and available under the MIT License. 