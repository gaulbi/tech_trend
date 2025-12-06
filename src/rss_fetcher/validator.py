"""Validation utilities for RSS fetcher."""

import json
from pathlib import Path
from typing import Dict


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def load_rss_list(file_path: str) -> Dict[str, Dict[str, str]]:
    """Load and validate RSS list from JSON file.
    
    Args:
        file_path: Path to RSS list JSON file
        
    Returns:
        Dictionary mapping categories to feed sources
        
    Raises:
        ValidationError: If file missing or invalid JSON format
        
    Examples:
        >>> load_rss_list("rss/feeds.json")
        {'AI Hardware': {'MIT': 'https://...'}}
    """
    path = Path(file_path)
    
    if not path.exists():
        raise ValidationError(f"RSS list file not found: {file_path}")
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON in RSS list file: {e}"
        )
    
    # Validate structure
    if not isinstance(data, dict):
        raise ValidationError(
            "RSS list must be a JSON object/dictionary"
        )
    
    for category, feeds in data.items():
        if not isinstance(feeds, dict):
            raise ValidationError(
                f"Category '{category}' must contain a dictionary of feeds"
            )
        
        for source, url in feeds.items():
            if not isinstance(url, str):
                raise ValidationError(
                    f"Feed URL for '{source}' in '{category}' must be string"
                )
    
    return data


def validate_article(article: Dict) -> bool:
    """Validate article has required fields.
    
    Args:
        article: Article dictionary from feed
        
    Returns:
        True if article has title and link, False otherwise
    """
    return 'title' in article and 'link' in article