"""Utility functions for article generator."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format.
    
    Returns:
        Date string
    """
    return date.today().strftime('%Y-%m-%d')


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.
    
    Args:
        text: Input text to slugify
        
    Returns:
        Slugified string
        
    Raises:
        ValueError: If text is empty or becomes empty after processing
        
    Examples:
        >>> slugify("Agentic AI Patterns!")
        'agentic-ai-patterns'
        >>> slugify("What's New in Python 3.12?")
        'whats-new-in-python-312'
    """
    import re
    
    # Validate input
    if not text or not isinstance(text, str):
        raise ValueError(f"Cannot slugify empty or non-string value: {text}")
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Strip leading/trailing hyphens
    text = text.strip('-')
    
    # Validate output
    if not text:
        raise ValueError(
            "Slugification resulted in empty string. "
            "Original text contained no alphanumeric characters."
        )
    
    return text


def setup_logger(log_path: str, today_date: str) -> logging.Logger:
    """Setup JSON logger for article generator.
    
    Args:
        log_path: Base log directory path
        today_date: Today's date string (YYYY-MM-DD)
        
    Returns:
        Configured logger instance
    """
    # Create log directory
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file path
    log_file = log_dir / f"article-generator-{today_date}.log"
    
    # Configure logger
    logger = logging.getLogger("article_generator")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create file handler with JSON formatting
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    handler.setLevel(logging.INFO)
    
    # Use custom formatter for JSON output
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Also add console handler for visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation of log record
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record.__dict__ if present
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName',
                'relativeCreated', 'thread', 'threadName', 'exc_info',
                'exc_text', 'stack_info', 'taskName'
            ]:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


def load_prompt_template(template_path: str) -> str:
    """Load prompt template from file.
    
    Args:
        template_path: Path to prompt template file
        
    Returns:
        Template content as string
        
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    path = Path(template_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def inject_prompt_variables(
    template: str,
    variables: Dict[str, str]
) -> str:
    """Inject variables into prompt template.
    
    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary of variable names to values
        
    Returns:
        Template with variables replaced
        
    Examples:
        >>> template = "Hello {{name}}!"
        >>> inject_prompt_variables(template, {"name": "World"})
        'Hello World!'
    """
    result = template
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    
    return result


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path to ensure
    """
    path.mkdir(parents=True, exist_ok=True)