# Logging and Summary Reports

This document describes the logging and reporting features implemented for the PhilGEPS Scraper.

## Features

### 📝 File-Based Logging

The scraper now includes comprehensive file-based logging with automatic rotation.

#### Log Files Location
```
scraper-service/logs/
├── scraper.log     # Scraper operations and progress
├── api.log         # API requests and responses
├── scheduler.log   # Scheduled job execution
└── errors.log      # Dedicated error log with stack traces
```

#### Log Configuration
- **Log Rotation**: Logs automatically rotate when they reach 10MB
- **Backup Count**: Keeps 5 backup files (50MB total per log file)
- **Format**: `[timestamp] - [logger_name] - [level] - [message]`
- **Levels**: INFO, WARNING, ERROR
- **Console Output**: Logs are written to both files and console

#### Using Loggers
```python
from logging_config import get_scraper_logger, get_api_logger, log_exception

# Get a logger
logger = get_scraper_logger()

# Log messages
logger.info("Operation started")
logger.warning("Warning message")
logger.error("Error occurred")

# Log exceptions with full traceback
try:
    # ... code ...
except Exception as e:
    log_exception(logger, "Operation failed", e)
```

### 📊 Daily Summary Reports

The scraper automatically generates comprehensive summary reports after each scraping session.

#### Report Formats
1. **JSON** - Machine-readable format for processing
2. **HTML** - Beautiful, human-readable dashboard
3. **CSV** - Spreadsheet-compatible format

#### Report Location
```
scraper-service/reports/
├── json/
│   └── scrape_report_20251112_193718.json
├── html/
│   └── scrape_report_20251112_193718.html
└── csv/
    └── scrape_report_20251112_193718.csv
```

#### Report Contents

**Statistics Section**
- Start and end time
- Duration
- Total pages scraped
- Total bids found
- New bids added
- Existing bids updated
- Error count and success rate
- Applied filters

**Bids Section**
- Reference numbers
- Titles and classifications
- Approved budgets
- Closing dates
- Agency names
- Status (new/updated/skipped)

**Errors Section**
- Error types and messages
- Error counts
- First and last occurrence timestamps

#### Viewing Reports

**HTML Reports** - Open in any web browser for a beautiful dashboard:
```bash
open reports/html/scrape_report_20251112_193718.html
```

**JSON Reports** - Process with scripts or view with jq:
```bash
cat reports/json/scrape_report_20251112_193718.json | jq
```

**CSV Reports** - Open in Excel, Google Sheets, or any spreadsheet app

### 🔧 Integration with Scraper

The scraper automatically tracks statistics during operation:
- Pages scraped
- Bids processed (new vs updated)
- Errors encountered
- Processing time

Reports are generated automatically at the end of each scraping session.

#### Example Usage

```python
from scraper.philgeps_scraper import PhilGEPSScraper

scraper = PhilGEPSScraper()

# Run scraper with reports enabled (default)
result = await scraper.run_daily_scrape(
    max_pages=None,  # All pages
    fetch_details=True,  # Fetch full details
    filters={'classification': 'Goods'},  # Optional filters
    generate_report=True  # Generate reports (default)
)

# Access report file paths
if result['success']:
    print(f"HTML Report: {result['report_files']['html']}")
    print(f"JSON Report: {result['report_files']['json']}")
    print(f"CSV Report: {result['report_files']['csv']}")
```

### 📅 Scheduled Reports

When using the scheduler, reports are automatically generated for each daily scraping job:

```python
from scheduler import daily_scrape_job

# This automatically generates reports
result = await daily_scrape_job()
```

The scheduler logs the report file paths to the scheduler log file.

## Configuration

### Log Rotation Settings

Modify `logging_config.py` to change rotation settings:

```python
# Maximum log file size before rotation
max_bytes=10 * 1024 * 1024  # 10MB (default)

# Number of backup files to keep
backup_count=5  # Keep 5 backups (default)
```

### Report Cleanup

Old reports can be cleaned up automatically:

```python
from report_generator import ReportGenerator

generator = ReportGenerator()

# Remove reports older than 30 days
generator.cleanup_old_reports(days_to_keep=30)
```

## Testing

### Test Logging
```bash
cd scraper-service
python logging_config.py
```

### Test Report Generation
```bash
cd scraper-service
python report_generator.py
```

Both tests will create sample outputs in `logs/` and `reports/` directories.

## Monitoring

### View Latest Logs
```bash
# View scraper log in real-time
tail -f logs/scraper.log

# View only errors
tail -f logs/errors.log

# View scheduler log
tail -f logs/scheduler.log
```

### Get Latest Report
```python
from report_generator import ReportGenerator

generator = ReportGenerator()
latest_html = generator.get_latest_report('html')
print(f"Latest report: {latest_html}")
```

## Best Practices

1. **Review Reports Daily** - Check HTML reports after scheduled runs to monitor scraper health

2. **Monitor Error Logs** - Set up alerts when errors.log grows rapidly

3. **Archive Old Reports** - Reports are timestamped and can be archived for historical analysis

4. **Log Rotation** - Logs automatically rotate, but monitor disk space in production

5. **Report Retention** - Use `cleanup_old_reports()` to manage disk space

## Troubleshooting

### Logs Not Being Created
- Check that the `scraper-service/logs/` directory has write permissions
- Verify `logging_config.py` is in the same directory as the scraper

### Reports Not Being Generated
- Ensure `LOGGING_AVAILABLE = True` in `philgeps_scraper.py`
- Check that `report_generator.py` is importable
- Verify the `scraper-service/reports/` directory has write permissions

### Missing Report Data
- Check that statistics tracking is enabled in the scraper
- Verify that `_reset_stats()` is called at the start of scraping
- Ensure bids are being added to `self.stats['processed_bids']`

## File Structure
```
scraper-service/
├── logging_config.py           # Logging configuration
├── report_generator.py         # Report generation
├── scraper/
│   └── philgeps_scraper.py    # Updated with logging & reporting
├── scheduler.py                # Updated with logging
├── logs/                       # Log files (gitignored)
│   ├── scraper.log
│   ├── api.log
│   ├── scheduler.log
│   └── errors.log
└── reports/                    # Report files (gitignored)
    ├── json/
    ├── html/
    └── csv/
```

## Support

For issues or questions about logging and reporting:
1. Check the error logs: `logs/errors.log`
2. Review test output: Run `python logging_config.py` and `python report_generator.py`
3. Check file permissions on `logs/` and `reports/` directories
