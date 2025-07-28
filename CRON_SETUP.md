# Cron Setup Guide for Webpage Tracker

This guide explains how to set up automated daily execution of the webpage tracker using cron.

## Prerequisites

1. **Docker and Docker Compose installed**
2. **Git repository set up** (for pulling latest code)
3. **Proper permissions** to run the script

## Method 1: Using the Provided Script (Recommended)

### 1. Make the script executable
```bash
chmod +x run_daily.sh
```

### 2. Test the script manually
```bash
./run_daily.sh
```

### 3. Add to crontab
```bash
# Edit crontab
crontab -e

# Add this line for daily execution at 9 AM
0 9 * * * /full/path/to/webtracker/run_daily.sh
```

## Method 2: Direct Cron Command

### 1. Edit crontab
```bash
crontab -e
```

### 2. Add cron entry
```bash
# Daily at 9 AM
0 9 * * * cd /full/path/to/webtracker && git pull && docker-compose build && docker-compose up >> log.txt 2>&1

# Or multiple times per day (e.g., 9 AM and 6 PM)
0 9,18 * * * cd /full/path/to/webtracker && git pull && docker-compose build && docker-compose up >> log.txt 2>&1

# Or every 6 hours
0 */6 * * * cd /full/path/to/webtracker && git pull && docker-compose build && docker-compose up >> log.txt 2>&1
```

## Cron Schedule Examples

| Schedule | Description |
|----------|-------------|
| `0 9 * * *` | Daily at 9:00 AM |
| `0 9,18 * * *` | Daily at 9:00 AM and 6:00 PM |
| `0 */6 * * *` | Every 6 hours |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 9 1 * *` | First day of each month at 9:00 AM |

## Monitoring and Logs

### 1. Check cron logs
```bash
# View system cron logs
sudo tail -f /var/log/cron

# View application logs
tail -f /path/to/webtracker/log.txt
```

### 2. Check if cron is running
```bash
# Check cron service status
sudo systemctl status cron

# List current crontab
crontab -l
```

### 3. Test cron execution
```bash
# Run the script manually to test
cd /path/to/webtracker
./run_daily.sh
```

## Troubleshooting

### Common Issues

1. **Path Issues**: Always use absolute paths in cron
   ```bash
   # Wrong
   0 9 * * * cd webtracker && ./run_daily.sh
   
   # Correct
   0 9 * * * cd /full/path/to/webtracker && ./run_daily.sh
   ```

2. **Permission Issues**: Ensure the script is executable
   ```bash
   chmod +x run_daily.sh
   ```

3. **Docker Issues**: Ensure Docker daemon is running
   ```bash
   sudo systemctl start docker
   ```

4. **Git Issues**: Ensure proper Git credentials
   ```bash
   # Test Git access
   cd /path/to/webtracker
   git pull
   ```

### Debug Mode

To debug cron issues, add verbose logging:

```bash
# Edit crontab
crontab -e

# Add with verbose output
0 9 * * * cd /path/to/webtracker && ./run_daily.sh >> /path/to/webtracker/debug.log 2>&1
```

### Environment Variables

If your script needs specific environment variables, add them to crontab:

```bash
# Add environment variables
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/home/username

# Then your cron job
0 9 * * * cd /path/to/webtracker && ./run_daily.sh
```

## Security Considerations

1. **File Permissions**: Ensure sensitive files have proper permissions
   ```bash
   chmod 600 webpages.xlsx
   chmod 755 run_daily.sh
   ```

2. **Log Rotation**: Implement log rotation to prevent disk space issues
   ```bash
   # Add to /etc/logrotate.d/webtracker
   /path/to/webtracker/log.txt {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

3. **Backup**: Regularly backup your data
   ```bash
   # Add backup cron job
   0 2 * * 0 tar -czf /backup/webtracker-$(date +\%Y\%m\%d).tar.gz /path/to/webtracker/webpage_versions /path/to/webtracker/diffs
   ```

## Production Deployment

For production environments, consider:

1. **Systemd Service**: Create a systemd service instead of cron
2. **Monitoring**: Set up monitoring for the cron job
3. **Alerting**: Configure alerts for failures
4. **Load Balancing**: Distribute load across multiple servers

### Systemd Service Example

Create `/etc/systemd/system/webtracker.service`:

```ini
[Unit]
Description=Webpage Tracker Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/webtracker
ExecStart=/path/to/webtracker/run_daily.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then create a timer:

```ini
[Unit]
Description=Run Webpage Tracker daily
Requires=webtracker.service

[Timer]
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable webtracker.timer
sudo systemctl start webtracker.timer
``` 