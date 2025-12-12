"""
Advanced logging module with JSON formatting and function tracing.
"""
import json
import logging
import traceback
import functools
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable
from logging.handlers import TimedRotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""
    
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
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON objects."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        if record.exc_info:
            log_obj["traceback"] = ''.join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_obj)


class Logger:
    """Advanced logger with multiple handlers and utilities."""
    
    def __init__(
        self,
        name: str,
        log_file: Optional[Path] = None,
        level: str = "INFO",
        use_json: bool = True,
        retention_days: int = 30
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Path to log file
            level: Logging level
            use_json: Use JSON formatting for file output
            retention_days: Days to retain log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                pass  # Another process created it
            
            file_handler = TimedRotatingFileHandler(
                str(log_file),
                when='midnight',
                interval=1,
                backupCount=retention_days
            )
            file_handler.setLevel(logging.DEBUG)
            
            if use_json:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(
        self,
        message: str,
        exc_info: bool = False,
        **kwargs: Any
    ) -> None:
        """Log error message with optional traceback."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)


def log_execution(logger: Logger) -> Callable:
    """
    Decorator to log function execution with timing.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            func_name = func.__qualname__
            
            logger.debug(f"Calling {func_name}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(
                    f"{func_name} completed in {elapsed:.2f}s"
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"{func_name} failed after {elapsed:.2f}s: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator
