# src/web_scraper/content_cleaner.py
"""Content cleaning utilities."""

import re
import logging
from typing import Optional

from readability import Document
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class ContentCleaner:
    """Cleans and extracts readable text from HTML content."""
    
    MIN_CONTENT_LENGTH = 50
    
    @staticmethod
    def clean(html_content: str) -> Optional[str]:
        """
        Extract and clean readable text from HTML.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Optional[str]: Cleaned text content or None
        """
        if not html_content or not html_content.strip():
            logger.warning("Empty HTML content provided")
            return None
        
        try:
            # Extract main content using readability
            doc = Document(html_content)
            readable_html = doc.summary()
            
            # Parse with BeautifulSoup for robust text extraction
            soup = BeautifulSoup(readable_html, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Validate minimum length
            if len(text) < ContentCleaner.MIN_CONTENT_LENGTH:
                logger.warning(
                    f"Content too short: {len(text)} chars"
                )
                return None
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to clean content: {e}", exc_info=True)
            return None