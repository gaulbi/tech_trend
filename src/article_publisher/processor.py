"""Article content processing utilities."""

import re
from datetime import datetime
from typing import Optional

from .models import Article, ImageMapping
from .logger import get_logger

logger = get_logger(__name__)


def inject_published_datetime(content: str) -> str:
    """
    Replace {YYYY-MM-DD HH:mm:ss} with current datetime.
    
    Args:
        content: Article content
        
    Returns:
        Content with injected datetime
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Replace the placeholder
    pattern = r'\{YYYY-MM-DD HH:mm:ss\}'
    updated_content = re.sub(pattern, current_time, content)
    
    return updated_content


def inject_image_url(content: str, image_url: str) -> str:
    """
    Replace image_url_tag_here with image markdown syntax.
    
    Args:
        content: Article content
        image_url: Image URL from mapping
        
    Returns:
        Content with injected image URL
    """
    # Create markdown image syntax
    image_markdown = f"![Alt Text]({image_url})"
    
    # Replace the placeholder
    updated_content = content.replace("image_url_tag_here", image_markdown)
    
    return updated_content


def process_article_content(
    article: Article,
    image_mapping: Optional[ImageMapping]
) -> str:
    """
    Process article content with all injections.
    
    Args:
        article: Article object
        image_mapping: Image mapping object (optional)
        
    Returns:
        Processed article content
    """
    content = article.content
    
    # Inject published datetime
    content = inject_published_datetime(content)
    
    # Inject image URL if mapping exists
    if image_mapping:
        content = inject_image_url(content, image_mapping.imgbb_url)
        logger.debug(
            f"Injected image URL: {image_mapping.imgbb_url}",
            extra={"article": article.file_name}
        )
    else:
        logger.warning(
            f"No image mapping found for {article.file_name}",
            extra={"article": article.file_name}
        )
    
    return content


def validate_processed_content(content: str) -> bool:
    """
    Validate that content has been fully processed.
    
    Args:
        content: Processed content
        
    Returns:
        True if valid, False otherwise
    """
    # Check for remaining placeholders
    if "{YYYY-MM-DD HH:mm:ss}" in content:
        logger.error("Datetime placeholder not replaced")
        return False
    
    if "image_url_tag_here" in content:
        logger.warning("Image URL placeholder not replaced")
        # This is a warning, not an error - continue anyway
    
    return True


def remove_first_line(content: str) -> str:
    """
    Remove the first line from the content string.
    
    Args:
        content: The input string from which the first line will be removed.
    
    Returns:
        The content string without the first line.
    """
    return '\n'.join(content.splitlines()[1:])

