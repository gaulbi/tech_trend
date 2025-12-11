"""
Logging module with JSON formatting and rotation support.
"""

import functools
import json
import logging
import logging.handlers
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Custom formatter for JSON output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Add traceback for errors
        if record.exc_info:
            log_data['traceback'] = ''.join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_data)


def setup_logger(
    name: str,
    log_dir: str = "log/embedding",
    level: str = "INFO",
    json_format: bool = True
) -> logging.Logger:
    """
    Set up logger with console and file handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level
        json_format: Use JSON formatting for file logs
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Rotating file handler
    log_file = Path(log_dir) / "embedder.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    if json_format:
        file_formatter = JsonFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - '
            '%(funcName)s:%(lineno)d - %(message)s'
        )
    
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_dir = os.getenv('LOG_DIR', 'log/embedding')
    json_format = os.getenv('LOG_JSON', 'true').lower() == 'true'
    
    return setup_logger(name, log_dir, log_level, json_format)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        logger.debug(
            f"Starting {func.__name__}",
            extra={'extra_data': {'function': func.__name__}}
        )
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            logger.debug(
                f"Completed {func.__name__} in {elapsed:.2f}s",
                extra={
                    'extra_data': {
                        'function': func.__name__,
                        'elapsed_seconds': elapsed
                    }
                }
            )
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Failed {func.__name__} after {elapsed:.2f}s: {e}",
                exc_info=True,
                extra={
                    'extra_data': {
                        'function': func.__name__,
                        'elapsed_seconds': elapsed,
                        'error': str(e)
                    }
                }
            )
            raise
    
    return wrapper