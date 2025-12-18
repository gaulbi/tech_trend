"""
Logging configuration and utilities.
"""
import json
import logging
import sys
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Callable, Optional

from .config import Config


# ANSI color codes
COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[35m",   # Magenta
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = (
                f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created
            ).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["traceback"] = "".join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_data)


def setup_logging(config: Config) -> None:
    """
    Setup logging with console and file handlers.
    
    Args:
        config: Configuration object
    """
    log_path = config.log_path
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    log_file = log_path / "deduplication.log"
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_execution(func: Callable) -> Callable:
    """
    Decorator to log function execution with timing.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        logger.debug(f"Entering {func_name}")
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(
                f"Completed {func_name} in {elapsed:.2f}s"
            )
            return result
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Error in {func_name} after {elapsed:.2f}s: {e}",
                exc_info=True,
            )
            raise
    
    return wrapper


def log_error(
    logger: logging.Logger,
    message: str,
    exc: Optional[Exception] = None,
) -> None:
    """
    Log error with stack trace.
    
    Args:
        logger: Logger instance
        message: Error message
        exc: Exception instance (optional)
    """
    if exc:
        logger.error(f"{message}: {exc}", exc_info=True)
    else:
        logger.error(message, exc_info=True)
