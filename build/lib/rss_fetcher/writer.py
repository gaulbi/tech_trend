"""Output file writer for RSS feeds."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OutputWriter:
    """Writes RSS feed data to JSON files."""
    
    def __init__(self, base_dir: Path):
        """
        Initialize output writer.
        
        Args:
            base_dir: Base directory for output files
        """
        self.base_dir = base_dir
    
    def write_category(
        self,
        category_data: Dict[str, Any],
        category_filename: str
    ) -> Path:
        """
        Write category data to JSON file.
        
        Args:
            category_data: Category data with articles
            category_filename: Safe filename for category
            
        Returns:
            Path to written file
            
        Raises:
            IOError: If file writing fails
        """
        # Create date-based directory
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_dir = self.base_dir / date_str
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output file path
        output_file = output_dir / f"{category_filename}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Wrote {category_data['article_count']} articles to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to write file {output_file}: {e}")
            raise IOError(f"Failed to write category data: {e}")
    
    def get_output_path(self, category_filename: str) -> Path:
        """
        Get the output path for a category file without writing.
        
        Args:
            category_filename: Safe filename for category
            
        Returns:
            Path where file would be written
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        return self.base_dir / date_str / f"{category_filename}.json"