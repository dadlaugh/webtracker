# 🔄 Hybrid Approach: Historical Data Preservation

This branch implements a hybrid approach that preserves historical data while implementing the new Excel-based structure.

## 📋 Overview

The hybrid approach provides the best of both worlds:
- ✅ **Preserves historical data** for reference and analysis
- ✅ **Implements new structure** for future tracking
- ✅ **Clean separation** between old and new systems
- ✅ **Easy migration** path for existing deployments

## 🏗️ Architecture

### **File Structure**
```
webtracker/
├── 📁 Current System (New Structure)
│   ├── webpage_versions/
│   │   ├── 01/en_reference/
│   │   ├── 01/zh_preview/
│   │   ├── 02/en_reference/
│   │   └── ...
│   ├── diffs/
│   └── logs/
│
├── 📦 Historical Archives
│   ├── historical_archive_20250730_140000/
│   │   ├── webpage_versions/ (old domain-based structure)
│   │   ├── diffs/ (historical diffs)
│   │   └── archive_info.txt
│   └── ...
│
└── 📄 Configuration
    ├── webpagesv2.xlsx (new Excel format)
    └── web_server.py (updated with archive support)
```

## 🚀 Deployment

### **Local Development**
```bash
# Switch to hybrid approach branch
git checkout hybrid-approach

# Archive existing data (if any)
python scripts/archive_historical_data.py

# Run the tracker with new structure
python webpage_tracker.py

# Start web server
python web_server.py
```

### **Remote Deployment**
```bash
# Run the hybrid deployment script
./scripts/deploy_hybrid.sh
```

## 📊 Web Interface

The web interface now includes:

### **Dashboard** (`/`)
- Overview of current system
- Statistics for new structure
- Recent files

### **Versions** (`/versions`)
- Current webpage versions in new structure
- Number-based organization (01, 02, 03, etc.)
- Language-based folders (en_reference, zh_preview)

### **Diffs** (`/diffs`)
- Current diff files
- Generated from new structure

### **Archive** (`/archive`) ⭐ **NEW**
- Historical data from old structure
- Preserved domain-based organization
- Accessible for reference and analysis
- Multiple archive versions supported

### **Logs** (`/logs`)
- Application logs
- System monitoring

## 🔧 Key Features

### **1. Automatic Archiving**
- Creates timestamped archives before implementing new structure
- Preserves all historical data
- Maintains original file organization

### **2. Dual System Support**
- Current system uses new Excel-based structure
- Archive system preserves old domain-based structure
- Both accessible through web interface

### **3. Migration Path**
- Seamless transition from old to new structure
- No data loss
- Easy rollback if needed

### **4. Storage Management**
- Historical data stored in separate archives
- Current data uses optimized structure
- Easy to clean up old archives if needed

## 📈 Benefits

### **For Development**
- ✅ Safe migration path
- ✅ No data loss during transition
- ✅ Easy testing of new structure
- ✅ Rollback capability

### **For Production**
- ✅ Preserves historical tracking
- ✅ Maintains data integrity
- ✅ Improved organization
- ✅ Better scalability

### **For Users**
- ✅ Access to both old and new data
- ✅ Familiar interface
- ✅ Enhanced functionality
- ✅ Better file organization

## 🛠️ Scripts

### **Archive Script** (`scripts/archive_historical_data.py`)
- Automatically archives existing data
- Creates timestamped archive directories
- Preserves file structure and metadata
- Generates archive information files

### **Deployment Script** (`scripts/deploy_hybrid.sh`)
- Complete deployment automation
- Archives historical data
- Implements new structure
- Sets up web interface
- Provides deployment summary

## 🔄 Migration Process

1. **Archive Existing Data**
   ```bash
   python scripts/archive_historical_data.py
   ```

2. **Implement New Structure**
   ```bash
   python webpage_tracker.py
   ```

3. **Verify Both Systems**
   - Check current data at `/versions`
   - Check archived data at `/archive`

4. **Monitor and Maintain**
   - Regular tracking with new structure
   - Archive cleanup as needed
   - Performance monitoring

## 📝 Notes

- Historical archives are read-only
- Current system uses new Excel format (`webpagesv2.xlsx`)
- Archive data is preserved for reference only
- New tracking starts fresh with optimized structure
- Both systems are accessible through web interface

## 🎯 Next Steps

1. **Deploy to remote server** using hybrid deployment script
2. **Verify data preservation** in archive section
3. **Test new structure** with current tracking
4. **Monitor performance** and storage usage
5. **Clean up old archives** as needed 