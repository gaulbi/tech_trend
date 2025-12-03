"""
Logging configuration for wiki_search module.
"""

import json
import logging
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Custom formatter for JSON log output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_obj = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, 'category'):
            log_obj['category'] = record.category
            
        return json.dumps(log_obj)


def setup_logging(log_dir: Path, today: str) -> logging.Logger:
    """
    Configure JSON logging to file.
    
    Args:
        log_dir: Directory for log files
        today: Today's date string (YYYY-MM-DD)
        
    Returns:
        Configured logger instance
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"wiki-search-{today}.log"
    
    logger = logging.getLogger("wiki_search")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    return logger