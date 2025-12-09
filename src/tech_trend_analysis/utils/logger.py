# ============================================================================
# src/tech_trend_analysis/utils/logger.py
# ============================================================================

"""Advanced logging utilities with JSON support and decorators."""

import json
import logging
import sys
import traceback
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import time
from typing import Any, Callable, Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(
                record.created
            ).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }

        if record.exc_info:
            log_data['traceback'] = ''.join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(log_data)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level
        json_format: Use JSON formatting if True
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with JSON or text format
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)

        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - '
                '%(module)s:%(funcName)s:%(lineno)d - %(message)s'
            )

        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def log_execution(logger: logging.Logger) -> Callable:
    """
    Decorator to log function execution with timing.

    Args:
        logger: Logger instance to use

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time()
            logger.debug(
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            try:
                result = func(*args, **kwargs)
                elapsed = time() - start
                logger.debug(
                    f"{func.__name__} completed in {elapsed:.2f}s"
                )
                return result
            except Exception as e:
                elapsed = time() - start
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}s: {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


def log_error(
    logger: logging.Logger,
    message: str,
    exc_info: bool = True
) -> None:
    """
    Log an error with full context and traceback.

    Args:
        logger: Logger instance
        message: Error message
        exc_info: Include exception info if True
    """
    logger.error(message, exc_info=exc_info)