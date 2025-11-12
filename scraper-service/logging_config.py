"""
Logging configuration for PhilGEPS Scraper
Provides file-based logging with rotation and structured format
"""
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime


# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
SCRAPER_LOG_FILE = LOGS_DIR / "scraper.log"
API_LOG_FILE = LOGS_DIR / "api.log"
SCHEDULER_LOG_FILE = LOGS_DIR / "scheduler.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str,
    log_file: Path,
    level=logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    also_console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and optional console handlers

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        also_console: Whether to also log to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if also_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def setup_error_logger(
    name: str = "errors",
    level=logging.ERROR
) -> logging.Logger:
    """
    Set up a dedicated error logger that only logs errors and above

    Args:
        name: Logger name
        level: Minimum logging level (default ERROR)

    Returns:
        Configured error logger instance
    """
    error_logger = logging.getLogger(name)
    error_logger.setLevel(level)

    # Remove existing handlers
    error_logger.handlers.clear()

    # File handler for errors only
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(level)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        DATE_FORMAT
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)

    # Don't propagate to avoid duplicate logs
    error_logger.propagate = False

    return error_logger


def setup_daily_logger(
    name: str,
    log_prefix: str = "daily",
    level=logging.INFO
) -> logging.Logger:
    """
    Set up a logger that creates a new log file each day

    Args:
        name: Logger name
        log_prefix: Prefix for daily log files
        level: Logging level

    Returns:
        Configured daily logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Timed rotating handler (daily)
    daily_handler = TimedRotatingFileHandler(
        LOGS_DIR / f"{log_prefix}.log",
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    daily_handler.setLevel(level)
    daily_handler.suffix = "%Y-%m-%d"
    daily_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    daily_handler.setFormatter(daily_formatter)
    logger.addHandler(daily_handler)

    # Also add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


# Pre-configured loggers for different components
def get_scraper_logger() -> logging.Logger:
    """Get logger for scraper operations"""
    return setup_logger("scraper", SCRAPER_LOG_FILE, logging.INFO)


def get_api_logger() -> logging.Logger:
    """Get logger for API operations"""
    return setup_logger("api", API_LOG_FILE, logging.INFO)


def get_scheduler_logger() -> logging.Logger:
    """Get logger for scheduler operations"""
    return setup_logger("scheduler", SCHEDULER_LOG_FILE, logging.INFO)


def get_error_logger() -> logging.Logger:
    """Get dedicated error logger"""
    return setup_error_logger()


# Utility function to log exceptions with full traceback
def log_exception(logger: logging.Logger, message: str, exc: Exception):
    """
    Log an exception with full traceback

    Args:
        logger: Logger instance
        message: Custom message to prepend
        exc: Exception instance
    """
    logger.error(f"{message}: {str(exc)}", exc_info=True)

    # Also log to dedicated error logger
    error_logger = get_error_logger()
    error_logger.error(f"{message}: {str(exc)}", exc_info=True)


if __name__ == "__main__":
    # Test logging configuration
    print("Testing logging configuration...")

    # Test scraper logger
    scraper_log = get_scraper_logger()
    scraper_log.info("Scraper logger test - INFO")
    scraper_log.warning("Scraper logger test - WARNING")
    scraper_log.error("Scraper logger test - ERROR")

    # Test API logger
    api_log = get_api_logger()
    api_log.info("API logger test - INFO")

    # Test scheduler logger
    scheduler_log = get_scheduler_logger()
    scheduler_log.info("Scheduler logger test - INFO")

    # Test error logger
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(scraper_log, "Test exception handling", e)

    print(f"\n✅ Log files created in: {LOGS_DIR}")
    print(f"   - {SCRAPER_LOG_FILE.name}")
    print(f"   - {API_LOG_FILE.name}")
    print(f"   - {SCHEDULER_LOG_FILE.name}")
    print(f"   - {ERROR_LOG_FILE.name}")
