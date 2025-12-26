"""
Advanced logging module with JSON formatting and function tracing.
"""
import functools
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Optional


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for different log levels."""
    
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
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
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
        
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(config: Any, feed_date: str) -> logging.Logger:
    """
    Set up logger with file and console handlers.
    
    Args:
        config: Configuration manager instance
        feed_date: Feed date string for log file naming
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('image_generator')
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    log_dir = config.log_path
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"image-generator-{feed_date}.log"
    
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='D',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_function_call(func: Callable) -> Callable:
    """
    Decorator to automatically log function calls with timing.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('image_generator')
        func_name = func.__name__
        
        logger.debug(f"Entering {func_name}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(
                f"Exiting {func_name}",
                extra={'extra_data': {'elapsed_seconds': elapsed}}
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Error in {func_name}: {str(e)}",
                exc_info=True,
                extra={'extra_data': {'elapsed_seconds': elapsed}}
            )
            raise
    
    return wrapper


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    context: Optional[dict] = None
) -> None:
    """
    Log error with additional context.
    
    Args:
        logger: Logger instance
        message: Error message
        context: Additional context dictionary
    """
    logger.error(
        message,
        exc_info=True,
        extra={'extra_data': context or {}}
    )
