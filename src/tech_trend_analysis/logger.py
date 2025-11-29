"""JSON logging utilities for tech trend analysis."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'category'):
            log_obj['category'] = record.category
        
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logger(log_path: str, today_date: str) -> logging.Logger:
    """Setup JSON logger for tech trend analysis.
    
    Args:
        log_path: Base path for log files
        today_date: Today's date in YYYY-MM-DD format
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('tech_trend_analysis')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    log_file = Path(log_path) / f"tech-trend-analysis-{today_date}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger