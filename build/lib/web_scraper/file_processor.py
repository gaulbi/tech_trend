"""
File Processor Module

Handles file discovery, loading, and saving operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FileProcessorError(Exception):
    """Raised when file processing fails."""
    pass


class FileProcessor:
    """
    Handles file operations for trend analysis and scraping results.
    
    Manages file discovery, JSON parsing, and result persistence.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize file processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.trend_base_path = Path(
            config.get('tech-trend-analysis', {}).get('analysis-report', 'data/tech-trend-analysis/report')
        )
        self.output_base_path = Path(
            config.get('scrap', {}).get('url-scrapped-content', 'data/scrapped-content')
        )
        
        logger.info(f"Initialized FileProcessor with trend_base: {self.trend_base_path}, "
                   f"output_base: {self.output_base_path}")
    
    def discover_trend_files(self, date: str) -> List[Path]:
        """
        Discover trend analysis files for a given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of Path objects for discovered JSON files
        """
        date_path = self.trend_base_path / date
        
        if not date_path.exists():
            logger.warning(f"Trend directory does not exist: {date_path}")
            return []
        
        # Find all JSON files in the date directory
        json_files = list(date_path.glob("*.json"))
        
        logger.info(f"Discovered {len(json_files)} trend files in {date_path}")
        return sorted(json_files)
    
    def load_trend_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a trend analysis JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileProcessorError: If file cannot be loaded or parsed
        """
        logger.info(f"Loading trend file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            if 'category' not in data:
                logger.warning(f"Missing 'category' field in {file_path}")
                data['category'] = file_path.stem.replace('-', ' ').title()
            
            if 'trends' not in data:
                logger.warning(f"Missing 'trends' field in {file_path}")
                data['trends'] = []
            
            logger.info(f"Loaded {len(data.get('trends', []))} trends from {file_path.name}")
            return data
            
        except json.JSONDecodeError as e:
            raise FileProcessorError(f"Invalid JSON in {file_path}: {str(e)}")
        except Exception as e:
            raise FileProcessorError(f"Error loading {file_path}: {str(e)}")
    
    def save_scraping_results(
        self,
        data: Dict[str, Any],
        date: str,
        category: str
    ) -> Path:
        """
        Save scraping results to JSON file.
        
        Args:
            data: Scraping results data
            date: Date string (YYYY-MM-DD)
            category: Category name
            
        Returns:
            Path to saved file
            
        Raises:
            FileProcessorError: If file cannot be saved
        """
        # Create output directory structure
        category_slug = self._slugify_category(category)
        output_dir = self.output_base_path / date / category_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "web-scrap.json"
        
        logger.info(f"Saving scraping results to: {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved results to {output_file}")
            return output_file
            
        except Exception as e:
            raise FileProcessorError(f"Error saving results to {output_file}: {str(e)}")
    
    def _slugify_category(self, category: str) -> str:
        """
        Convert category name to filesystem-safe slug.
        
        Args:
            category: Category name
            
        Returns:
            Slugified category name
        """
        import re
        
        # Convert to lowercase and replace special chars with hyphens
        slug = category.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        return slug
    
    def ensure_directory_exists(self, path: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path
        """
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")