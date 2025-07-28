# Webpage Change Tracker

A complete system for tracking changes in webpages over time. This tool reads URLs from an Excel file, fetches webpage content daily, saves prettified HTML versions, and generates diffs between consecutive versions.

## Features

- **Excel Integration**: Reads URLs from `webpages.xlsx` file
- **Daily Tracking**: Fetches and saves webpage content with date-based naming
- **Diff Generation**: Creates HTML diffs between consecutive versions using `difflib.HtmlDiff`
- **Docker Support**: Containerized deployment with persistent data
- **Cron Scheduling**: Automated daily execution
- **Comprehensive Logging**: Detailed logs with timestamps and error handling
- **Git Integration**: Version control ready with proper `.gitignore`

## Project Structure

```
webtracker/
├── webpage_tracker.py      # Main Python script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── .gitignore            # Git ignore rules
├── create_sample_excel.py # Helper script to create sample Excel file
├── README.md             # This file
├── webpages.xlsx         # Excel file with URLs (create this)
├── webpage_versions/     # Saved webpage versions (auto-created)
├── diffs/               # Generated diffs (auto-created)
└── logs/                # Log files (auto-created)
```

## Quick Start

### 1. Create Sample Excel File

```bash
python create_sample_excel.py
```

This creates a `webpages.xlsx` file with sample URLs. Edit this file to add your own URLs.

### 2. Run with Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run with Docker directly
docker build -t webpage-tracker .
docker run -v $(pwd)/webpages.xlsx:/app/webpages.xlsx:ro \
           -v $(pwd)/webpage_versions:/app/webpage_versions \
           -v $(pwd)/diffs:/app/diffs \
           webpage-tracker
```

### 3. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tracker
python webpage_tracker.py
```

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

## Cron Scheduling

Add this to your crontab for daily execution at 9 AM:

```bash
# Edit crontab
crontab -e

# Add this line
0 9 * * * cd /path/to/webtracker && git pull && docker-compose build && docker-compose up >> log.txt 2>&1
```

Or use the provided script:

```bash
# Make script executable
chmod +x run_daily.sh

# Add to crontab
0 9 * * * /path/to/webtracker/run_daily.sh
```

## Configuration

### Environment Variables

- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered in Docker

### Customization

You can modify the script to:
- Add custom headers for specific websites
- Implement change notification (email, Slack, etc.)
- Filter out trivial changes (ads, timestamps)
- Use custom folder naming based on Excel columns

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