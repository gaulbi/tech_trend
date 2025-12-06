"""Utility functions for RSS fetcher."""

import re
from pathlib import Path


def sanitize_category(category: str) -> str:
    """Sanitize category name for use as filename.
    
    Args:
        category: Raw category name
        
    Returns:
        Sanitized category name (lowercase, underscores)
        
    Examples:
        >>> sanitize_category("AI & Hardware!")
        'ai_hardware'
        >>> sanitize_category("Software Engineering")
        'software_engineering'
    """
    # Convert to lowercase
    sanitized = category.lower()
    
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^a-z0-9]+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized


def get_output_path(
    base_dir: str, 
    feed_date: str, 
    category: str
) -> Path:
    """Get output file path for a category.
    
    Args:
        base_dir: Base output directory
        feed_date: Feed date in YYYY-MM-DD format
        category: Category name (will be sanitized)
        
    Returns:
        Path object for output file
        
    Examples:
        >>> get_output_path("data/rss", "2025-02-26", "AI & Hardware")
        PosixPath('data/rss/2025-02-26/ai_hardware.json')
    """
    sanitized = sanitize_category(category)
    return Path(base_dir) / feed_date / f"{sanitized}.json"


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if needed.
    
    Args:
        path: Path to file or directory (creates parent if file path)
    """
    # If path has a file extension, it's a file path - use parent
    if path.suffix:
        path = path.parent
    path.mkdir(parents=True, exist_ok=True)