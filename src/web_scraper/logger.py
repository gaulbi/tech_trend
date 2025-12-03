# src/web_scraper/logger.py
"""Structured logging for web scraper."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger(log_dir: str, today: date) -> logging.Logger:
    """
    Set up structured JSON logger.
    
    Args:
        log_dir: Directory for log files
        today: Current date for log filename
        
    Returns:
        Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_file = log_path / f"web-scraper-{today.strftime('%Y-%m-%d')}.log"
    
    logger = logging.getLogger('web_scraper')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # File handler with JSON formatting
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler for user feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger