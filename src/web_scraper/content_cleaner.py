# src/web_scraper/content_cleaner.py
"""Content cleaning utilities."""

import re
from typing import Optional

from readability import Document


class ContentCleaner:
    """Clean and extract readable content from HTML."""
    
    @staticmethod
    def clean(html: str) -> Optional[str]:
        """
        Extract clean, readable text from HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Cleaned text content or None if cleaning failed
        """
        if not html:
            return None
        
        try:
            # Use readability to extract main content
            doc = Document(html)
            content = doc.summary()
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', content)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text if text else None
            
        except Exception:
            return None