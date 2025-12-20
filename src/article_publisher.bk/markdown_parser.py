# ==============================================================================
# FILE: src/article_publisher/markdown_parser.py
# ==============================================================================
"""Markdown file parsing utilities."""

import re
from pathlib import Path
from typing import Optional, Tuple

from .logger import log_error


class MarkdownParser:
    """Parser for markdown article files."""
    
    TITLE_PATTERN = re.compile(r'^##\s*Title\s*\n(.+)$', re.MULTILINE)
    MAX_TITLE_LENGTH = 250  # Hashnode typical limit
    
    @staticmethod
    def parse_article(
        file_path: Path,
        logger
    ) -> Optional[Tuple[str, str]]:
        """
        Parse markdown file to extract title and content.
        
        Args:
            file_path: Path to markdown file
            logger: Logger instance
            
        Returns:
            Tuple of (title, content) or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip empty files
            if not content.strip():
                logger.warning(f"Empty file skipped: {file_path}")
                return None
            
            # Extract title
            match = MarkdownParser.TITLE_PATTERN.search(content)
            if not match:
                logger.warning(
                    f"No title found in format '**[EN] Title**: ...' "
                    f"in {file_path}"
                )
                return None
            
            title = match.group(1).strip()
            
            if not title:
                logger.warning(f"Empty title extracted from {file_path}")
                return None
            
            # Validate title length
            if len(title) > MarkdownParser.MAX_TITLE_LENGTH:
                logger.warning(
                    f"Title exceeds {MarkdownParser.MAX_TITLE_LENGTH} "
                    f"characters ({len(title)} chars) in {file_path}: "
                    f"{title[:50]}..."
                )
                # Truncate title
                title = title[:MarkdownParser.MAX_TITLE_LENGTH]
            
            logger.debug(f"Parsed article: {title} from {file_path}")
            return title, content
            
        except Exception as e:
            log_error(logger, e, f"Failed to parse {file_path}")
            return None