"""Article and image mapping loaders."""

import json
import re
from pathlib import Path
from typing import List, Optional

from .models import Article, ImageMapping
from .exceptions import ArticleNotFoundError, ImageMappingError
from .logger import get_logger

logger = get_logger(__name__)


def load_article(
    article_path: Path,
    category: str
) -> Article:
    """
    Load article from markdown file.
    
    Args:
        article_path: Path to article file
        category: Article category
        
    Returns:
        Article object
        
    Raises:
        ArticleNotFoundError: If article file not found
    """
    if not article_path.exists():
        raise ArticleNotFoundError(f"Article not found: {article_path}")
    
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise ArticleNotFoundError(
            f"Failed to read article {article_path}: {e}"
        )
    
    # Extract title
    title = extract_title(content)
    
    return Article(
        title=title,
        content=content,
        category=category,
        file_name=article_path.name,
        file_path=str(article_path)
    )


def extract_title(content: str) -> str:
    """
    Extract title from article content.
    
    The title is located between "## Title" and "**Date/Time**:"
    
    Args:
        content: Article markdown content
        
    Returns:
        Extracted title
        
    Raises:
        ArticleNotFoundError: If title cannot be extracted
    """
    # Pattern to match title between ## Title and **Date/Time**:
    pattern = r'## Title\s*\n\s*(.+?)\s*\n\s*\*\*Date/Time\*\*:'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise ArticleNotFoundError(
            "Could not extract title from article content"
        )
    
    title = match.group(1).strip()
    
    # Remove any markdown formatting from title
    title = re.sub(r'[*_~`]', '', title)
    
    return title


def load_image_mapping(mapping_path: Path) -> ImageMapping:
    """
    Load image URL mapping from JSON file.
    
    Args:
        mapping_path: Path to mapping file
        
    Returns:
        ImageMapping object
        
    Raises:
        ImageMappingError: If mapping file not found or invalid
    """
    if not mapping_path.exists():
        raise ImageMappingError(
            f"Image mapping not found: {mapping_path}"
        )
    
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ImageMappingError(
            f"Invalid JSON in mapping file {mapping_path}: {e}"
        )
    except Exception as e:
        raise ImageMappingError(
            f"Failed to read mapping file {mapping_path}: {e}"
        )
    
    # Validate required fields
    required_fields = [
        "article_file",
        "category",
        "feed_date",
        "local_path",
        "imgbb_url",
        "uploaded_at",
        "status"
    ]
    
    for field in required_fields:
        if field not in data:
            raise ImageMappingError(
                f"Missing required field '{field}' in {mapping_path}"
            )
    
    return ImageMapping(**data)


def find_articles(
    base_path: str,
    feed_date: str,
    category: Optional[str] = None
) -> List[tuple[str, Path]]:
    """
    Find all article files for given feed date and optional category.
    
    Args:
        base_path: Base directory for articles
        feed_date: Feed date in YYYY-MM-DD format
        category: Optional category filter
        
    Returns:
        List of (category, article_path) tuples
    """
    articles = []
    base = Path(base_path) / feed_date
    
    if not base.exists():
        logger.warning(
            f"Feed date directory not found: {base}",
            extra={"feed_date": feed_date}
        )
        return articles
    
    if category:
        # Search specific category
        category_path = base / category
        if category_path.exists() and category_path.is_dir():
            for article_file in category_path.glob("*.md"):
                articles.append((category, article_file))
    else:
        # Search all categories
        for category_path in base.iterdir():
            if category_path.is_dir():
                cat = category_path.name
                for article_file in category_path.glob("*.md"):
                    articles.append((cat, article_file))
    
    return articles
