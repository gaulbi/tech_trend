"""JSON structured logging for RSS fetcher."""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation of log
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, 'category'):
            log_data['category'] = record.category
        if hasattr(record, 'feed_url'):
            log_data['feed_url'] = record.feed_url
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message
            
        return json.dumps(log_data)


def setup_logger(log_dir: str) -> logging.Logger:
    """
    Setup JSON logger with daily file naming.
    
    Creates logs in format: rss-fetcher-{YYYY-MM-DD}.log
    Note: Rotation is handled by creating new files daily.
    Old logs (>30 days) should be cleaned up by external log rotation tool.
    
    Args:
        log_dir: Directory path for log files
        
    Returns:
        Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"rss-fetcher-{today}.log"
    
    logger = logging.getLogger("rss_fetcher")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    return logger