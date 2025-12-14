"""
Markdown article parser module.
"""
import re
from pathlib import Path
from typing import Optional

from .exceptions import ValidationError


class ArticleParser:
    """Parser for extracting summary from markdown articles."""
    
    SUMMARY_PATTERN = re.compile(
        r'##\s+Summary\s*\n(.*?)\n##\s+Full Article',
        re.DOTALL | re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize article parser."""
        pass
    
    def parse(self, file_path: Path) -> str:
        """
        Parse markdown file and extract summary content.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Extracted summary text
            
        Raises:
            ValidationError: If file structure is invalid
        """
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            raise ValidationError(f"Failed to read file {file_path}: {e}")
        
        summary = self._extract_summary(content)
        
        if not summary:
            raise ValidationError(
                f"No summary section found in {file_path.name}"
            )
        
        return summary.strip()
    
    def _extract_summary(self, content: str) -> Optional[str]:
        """
        Extract summary section from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            Summary text or None if not found
        """
        match = self.SUMMARY_PATTERN.search(content)
        if match:
            return match.group(1).strip()
        return None
