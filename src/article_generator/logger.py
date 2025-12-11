# ============================================================================
# src/article_generator/logger.py
# ============================================================================
"""Advanced logging system."""
import json
import logging
import sys
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from logging.handlers import TimedRotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Colored console formatter."""
    
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
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        if record.exc_info:
            log_obj['traceback'] = ''.join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_obj)


class Logger:
    """Advanced logger with multi-level support."""
    
    _instances = {}
    
    def __new__(cls, name: str, log_file: Optional[str] = None):
        """Singleton per logger name."""
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
        """
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with JSON
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
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
    
    def error(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log error message with traceback."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)


def log_execution(logger: Logger) -> Callable:
    """
    Decorator to log function execution with timing.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = datetime.now()
            logger.debug(
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(
                    f"{func.__name__} completed in {duration:.2f}s"
                )
                return result
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator
