# ==============================================================================
# FILE: src/article_publisher/logger.py
# ==============================================================================
"""Logging configuration and utilities."""

import json
import logging
import sys
import traceback
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .timezone_utils import get_timezone


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = (
            f"{color}{record.levelname}{self.COLORS['RESET']}"
        )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
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
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName',
                'relativeCreated', 'thread', 'threadName', 'exc_info',
                'exc_text', 'stack_info'
            ]:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    Setup logger with console and file handlers.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('article_publisher')
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    log_dir = Path(config['article-publisher']['log'])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Use configured timezone for log filename
    timezone_str = config['article-publisher']['timezone']
    tz = get_timezone(timezone_str)
    today = datetime.now(tz).strftime('%Y-%m-%d')
    log_file = log_dir / f"article-publisher-{today}.log"
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger


def log_execution_time(logger: logging.Logger) -> Callable:
    """
    Decorator to log function calls with timing.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.debug(
                f"Calling {func.__name__}",
                extra={'args': str(args), 'kwargs': str(kwargs)}
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(
                    f"{func.__name__} completed in {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"{func.__name__} failed after {duration:.3f}s: {e}"
                )
                raise
        
        return wrapper
    return decorator


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str = ""
) -> None:
    """
    Log error with full context and traceback.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context string
    """
    logger.error(
        f"{context}: {error}" if context else str(error),
        exc_info=True
    )