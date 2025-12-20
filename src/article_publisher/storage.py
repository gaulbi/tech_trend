"""Storage utilities for publish results and status tracking."""

import json
from pathlib import Path
from typing import Optional

from .models import PublishResult
from .logger import get_logger

logger = get_logger(__name__)


def check_already_published(
    base_path: str,
    feed_date: str,
    category: str,
    file_name: str
) -> bool:
    """
    Check if article has already been published.
    
    Args:
        base_path: Base path for published articles
        feed_date: Feed date
        category: Article category
        file_name: Article file name (with .md extension)
        
    Returns:
        True if already published, False otherwise
    """
    result_path = get_result_path(
        base_path,
        feed_date,
        category,
        file_name
    )
    
    return result_path.exists()


def save_publish_result(
    base_path: str,
    feed_date: str,
    category: str,
    file_name: str,
    result: PublishResult
) -> None:
    """
    Save publish result to JSON file.
    
    Args:
        base_path: Base path for published articles
        feed_date: Feed date
        category: Article category
        file_name: Article file name (with .md extension)
        result: PublishResult object
    """
    result_path = get_result_path(
        base_path,
        feed_date,
        category,
        file_name
    )
    
    # Create directory if it doesn't exist
    result_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save result as JSON
    try:
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        logger.info(
            f"Saved publish result: {result_path}",
            extra={
                "category": category,
                "file_name": file_name,
                "status": result.status
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to save publish result: {e}",
            exc_info=True,
            extra={"result_path": str(result_path)}
        )


def get_result_path(
    base_path: str,
    feed_date: str,
    category: str,
    file_name: str
) -> Path:
    """
    Get path for publish result file.
    
    Args:
        base_path: Base path for published articles
        feed_date: Feed date
        category: Article category
        file_name: Article file name (with .md extension)
        
    Returns:
        Path to result file
    """
    # Remove .md extension and add .json
    json_file_name = file_name.replace('.md', '.json')
    
    return Path(base_path) / feed_date / category / json_file_name


def load_publish_result(
    base_path: str,
    feed_date: str,
    category: str,
    file_name: str
) -> Optional[PublishResult]:
    """
    Load publish result from JSON file.
    
    Args:
        base_path: Base path for published articles
        feed_date: Feed date
        category: Article category
        file_name: Article file name (with .md extension)
        
    Returns:
        PublishResult object or None if not found
    """
    result_path = get_result_path(
        base_path,
        feed_date,
        category,
        file_name
    )
    
    if not result_path.exists():
        return None
    
    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return PublishResult(**data)
    except Exception as e:
        logger.error(
            f"Failed to load publish result: {e}",
            exc_info=True,
            extra={"result_path": str(result_path)}
        )
        return None
