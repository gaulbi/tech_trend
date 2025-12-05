# ============================================================================
# FILE: src/tech_trend_analysis/logger.py
# ============================================================================
"""Advanced logging configuration with JSON support and decorators."""

import json
import logging
import sys
import traceback
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Optional
import time


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
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
        # Save original level name
        original_levelname = record.levelname
        
        # Apply color
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname}{reset}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original level name (don't pollute other handlers)
        record.levelname = original_levelname
        
        return result


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs in JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        if record.exc_info:
            log_data['traceback'] = ''.join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_data)


def setup_logger(
    name: str,
    log_dir: Path,
    date_str: str,
    level: str = "INFO",
    use_json: bool = True
) -> logging.Logger:
    """
    Set up logger with console and file handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        date_str: Date string for log filename
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Use JSON formatting for file output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []  # Clear existing handlers
    
    # Console handler with colors (for terminal display only)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = '%(asctime)s - %(levelname)s - %(message)s'
    console_handler.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_handler)
    
    # File handler with rotation (NO colors in files)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"tech-trend-analysis-{date_str}.log"
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    if use_json:
        # Use plain JSON formatter without colors
        file_handler.setFormatter(JSONFormatter())
    else:
        # Use plain text formatter without colors
        file_format = (
            '%(asctime)s - %(levelname)s - %(module)s:'
            '%(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(logging.Formatter(file_format))
    
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
            start_time = time.time()
            logger.debug(f"Entering {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(
                    f"Exiting {func.__name__} (took {elapsed:.2f}s)"
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Error in {func.__name__} after {elapsed:.2f}s: {e}",
                    exc_info=True
                )
                raise
                
        return wrapper
    return decorator


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    context: Optional[dict] = None
) -> None:
    """
    Log error with additional context information.
    
    Args:
        logger: Logger instance
        message: Error message
        context: Additional context data
    """
    if context:
        context_str = json.dumps(context, indent=2)
        full_message = f"{message}\nContext: {context_str}"
    else:
        full_message = message
    
    logger.error(full_message, exc_info=True)