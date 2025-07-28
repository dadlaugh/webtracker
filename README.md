# Webpage Change Tracker

A complete system for tracking changes in webpages over time. This tool reads URLs from an Excel file, fetches webpage content daily, saves prettified HTML versions, and generates diffs between consecutive versions.

## Features

- **Excel Integration**: Reads URLs from `webpages.xlsx` file
- **Daily Tracking**: Fetches and saves webpage content with date-based naming
- **Diff Generation**: Creates HTML diffs between consecutive versions using `difflib.HtmlDiff`
- **Docker Support**: Containerized deployment with persistent data
- **Auto-Updates**: Automated daily execution via systemd timer
- **Comprehensive Logging**: Detailed logs with timestamps and error handling
- **Git Integration**: Version control ready with proper `.gitignore`

## Project Structure

```
webtracker/
├── webpage_tracker.py              # Main Python script
├── requirements.txt                # Python dependencies
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── .gitignore                    # Git ignore rules
├── create_sample_excel_simple.py # Helper script to create sample Excel file
├── auto_update.sh                # Auto-update script for remote server
├── set_environment.sh            # Environment configuration script
├── README.md                     # This file
├── REMOTE_DOCKER_DEPLOYMENT.md   # Remote deployment guide
├── webpages.xlsx                 # Excel file with URLs (create this)
├── webpage_versions/             # Saved webpage versions (auto-created)
├── diffs/                       # Generated diffs (auto-created)
└── logs/                        # Log files (auto-created)
```

## Quick Start

### 1. Create Sample Excel File

```bash
python3 create_sample_excel_simple.py
```

This creates a `webpages.xlsx` file with sample URLs. Edit this file to add your own URLs.

### 2. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tracker
python webpage_tracker.py
```

### 3. Run with Docker

```bash
# Build and run with Docker
docker build -t webpage-tracker .
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker

# Or use Docker Compose
docker-compose up --build
```

## Remote Server Deployment

For production deployment on a remote server, see the comprehensive guide:

**[📖 REMOTE_DOCKER_DEPLOYMENT.md](REMOTE_DOCKER_DEPLOYMENT.md)**

This guide covers:
- Building Docker image on remote server
- Setting up auto-updates every 5 minutes
- Monitoring and troubleshooting
- Environment configuration

## Excel File Format

The `webpages.xlsx` file must contain a column named `URL`. Additional columns are optional:

| URL | Name | Description |
|-----|------|-------------|
| https://example.com | Example Site | Basic example site |
| https://google.com | Google | Search engine |

## Output Structure

### Webpage Versions
```
webpage_versions/
├── example_com/
│   ├── 2024-01-15.html
│   ├── 2024-01-16.html
│   └── 2024-01-17.html
└── google_com/
    ├── 2024-01-15.html
    └── 2024-01-16.html
```

### Diffs
```
diffs/
├── example_com/
│   ├── diff_2024-01-15_to_2024-01-16.html
│   └── diff_2024-01-16_to_2024-01-17.html
└── google_com/
    └── diff_2024-01-15_to_2024-01-16.html
```

## Environment Configuration

The system supports environment-based configuration:

```bash
# Set environment (production = auto-updates enabled, development = disabled)
./set_environment.sh production
./set_environment.sh development

# Check current environment
./set_environment.sh
```

## Logging

The system provides comprehensive logging:
- Console output with real-time status
- Log file: `webpage_tracker.log`
- Error handling for failed requests
- Success/failure summaries

## Error Handling

The system handles various error scenarios:
- Missing Excel file
- Invalid URLs
- Network timeouts
- Permission errors
- Missing directories

## Dependencies

- **Python 3.11+**
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing and prettification
- **pandas**: Excel file reading
- **openpyxl**: Excel file support
- **lxml**: XML/HTML parser

## Docker Commands

```bash
# Build image
docker build -t webpage-tracker .

# Run container
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker

# Run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### Common Issues

1. **Excel file not found**: Ensure `webpages.xlsx` exists in the project directory
2. **Permission errors**: Check directory permissions for `webpage_versions/` and `diffs/`
3. **Network timeouts**: Some websites may block automated requests
4. **Docker volume mounts**: Ensure paths are correct for your OS

### Debug Mode

Run with verbose logging:
```bash
python webpage_tracker.py 2>&1 | tee debug.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License. 