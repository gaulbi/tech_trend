"""
Logging utilities for wiki_search module.
"""

import functools
import json
import logging
import sys
import time
import traceback
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class ColoredFormatter(logging.Formatter):
    """Format log records with colors for console output."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with color.

        Args:
            record: Log record to format

        Returns:
            Colored string representation of log record
        """
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON string representation of log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["traceback"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(log_file: Path, debug: bool = False) -> logging.Logger:
    """
    Set up logger with JSON formatting and rotation.

    Args:
        log_file: Path to log file
        debug: Enable DEBUG level logging

    Returns:
        Configured logger instance
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("wiki_search")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    # File handler with JSON formatter and daily rotation (keep 30 days)
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # Console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        "%(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_execution(func: Callable) -> Callable:
    """
    Decorator to log function execution with timing.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function with logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("wiki_search")
        func_name = func.__name__
        
        logger.debug(
            f"Calling {func_name} with args={args}, kwargs={kwargs}"
        )
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(
                f"Completed {func_name} in {elapsed:.2f}s"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Failed {func_name} after {elapsed:.2f}s: {e}",
                exc_info=True
            )
            raise
    
    return wrapper


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: bool = True
) -> None:
    """
    Log error with additional context information.

    Args:
        logger: Logger instance
        message: Error message
        context: Additional context dictionary
        exc_info: Include exception traceback
    """
    if context:
        context_str = ", ".join(f"{k}='{v}'" for k, v in context.items())
        full_message = f"{message} | Context: {context_str}"
    else:
        full_message = message
    
    logger.error(full_message, exc_info=exc_info)