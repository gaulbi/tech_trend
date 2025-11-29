"""Utility functions for RSS fetcher."""

import re
from pathlib import Path
from datetime import datetime


def sanitize_category_name(category: str) -> str:
    """
    Sanitize category name for use as filename.
    
    Converts to lowercase and replaces spaces and special characters
    with underscores.
    
    Args:
        category: Original category name
        
    Returns:
        Sanitized category name
        
    Raises:
        ValueError: If sanitized name is empty
        
    Example:
        >>> sanitize_category_name("AI & Hardware!")
        'ai_hardware'
    """
    sanitized = category.lower()
    sanitized = re.sub(r'[^a-z0-9]+', '_', sanitized)
    sanitized = sanitized.strip('_')
    
    if not sanitized:
        raise ValueError(f"Category name '{category}' produces empty filename")
    
    return sanitized


def is_today_file_exists(base_path: str, category: str) -> bool:
    """
    Check if category JSON file already exists for today.
    
    Args:
        base_path: Base output directory path
        category: Sanitized category name
        
    Returns:
        True if file exists, False otherwise
    """
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = Path(base_path) / today / f"{category}.json"
    return file_path.exists()


def get_output_path(base_path: str, category: str) -> Path:
    """
    Get output file path for a category.
    
    Args:
        base_path: Base output directory path
        category: Sanitized category name
        
    Returns:
        Complete Path object for output file
    """
    today = datetime.now().strftime("%Y-%m-%d")
    dir_path = Path(base_path) / today
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / f"{category}.json"