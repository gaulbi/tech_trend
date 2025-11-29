"""Utility functions for the embedder module."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .config import Config
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


def setup_logging(config: Config) -> logging.Logger:
    """
    Configure logging for the embedder.

    Args:
        config: Configuration object.

    Returns:
        Configured logger instance.
    """
    log_dir = Path(config.log_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"embedder_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


def hash_url(url: str) -> str:
    """
    Generate a hash for a URL.

    Args:
        url: URL to hash.

    Returns:
        Hexadecimal hash string (first 16 characters).
    """
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and validate JSON file.

    Args:
        file_path: Path to JSON file.

    Returns:
        Parsed JSON dictionary.

    Raises:
        ValidationError: If file is invalid or missing required fields.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON in {file_path}: {e}"
        ) from e
    except Exception as e:
        raise ValidationError(f"Error reading {file_path}: {e}") from e

    # Validate required fields
    required_fields = ["analysis_date", "category", "trends"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(
                f"Missing required field '{field}' in {file_path}"
            )

    if not isinstance(data["trends"], list):
        raise ValidationError(
            f"'trends' must be a list in {file_path}"
        )

    return data


def validate_trend_item(
    trend: Dict[str, Any], file_path: Path
) -> bool:
    """
    Validate a single trend item.

    Args:
        trend: Trend dictionary to validate.
        file_path: Source file path for error messages.

    Returns:
        True if valid, False otherwise.
    """
    required_fields = ["topic", "link", "content"]
    for field in required_fields:
        if field not in trend or not trend[field]:
            logger.warning(
                f"Trend missing '{field}' in {file_path}, skipping"
            )
            return False

    if not isinstance(trend["content"], str):
        logger.warning(
            f"Invalid content type in {file_path}, skipping"
        )
        return False

    return True


def find_category_directories(
    base_path: Path, target_date: str
) -> List[Path]:
    """
    Find all category directories for a given date.

    Args:
        base_path: Base scraped content directory.
        target_date: Date in YYYY-MM-DD format.

    Returns:
        List of category directory paths.
    """
    date_path = base_path / target_date
    if not date_path.exists():
        return []

    categories = []
    for item in date_path.iterdir():
        if item.is_dir():
            categories.append(item)

    return sorted(categories)


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split a list into batches.

    Args:
        items: List to split.
        batch_size: Maximum size per batch.

    Returns:
        List of batches.
    """
    return [
        items[i : i + batch_size]
        for i in range(0, len(items), batch_size)
    ]