# src/web_scraper/file_handler.py
"""File handling utilities for input/output operations."""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import date

from .models import TrendAnalysis, ScrapedOutput
from .exceptions import ValidationError


logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file I/O operations for trend analysis."""
    
    @staticmethod
    def get_today_date() -> str:
        """
        Get today's date in YYYY-MM-DD format.
        
        Returns:
            str: Today's date
        """
        return date.today().strftime('%Y-%m-%d')
    
    @staticmethod
    def get_input_files(
        base_dir: str, 
        today_date: str
    ) -> List[Path]:
        """
        Get all input JSON files for today's date.
        
        Args:
            base_dir: Base directory for analysis reports
            today_date: Today's date string (YYYY-MM-DD)
            
        Returns:
            List[Path]: List of input file paths
        """
        input_dir = Path(base_dir) / today_date
        
        if not input_dir.exists():
            logger.warning(
                f"No input directory found for {today_date}"
            )
            return []
        
        json_files = list(input_dir.glob("*.json"))
        logger.info(
            f"Found {len(json_files)} category files for {today_date}"
        )
        return json_files
    
    @staticmethod
    def load_trend_analysis(file_path: Path) -> Optional[TrendAnalysis]:
        """
        Load and parse trend analysis from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Optional[TrendAnalysis]: Parsed trend analysis or None
            
        Raises:
            ValidationError: If JSON is malformed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TrendAnalysis.from_dict(data)
            
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON in {file_path}: {e}"
            )
        except KeyError as e:
            raise ValidationError(
                f"Missing required field in {file_path}: {e}"
            )
        except Exception as e:
            raise ValidationError(
                f"Error loading {file_path}: {e}"
            )
    
    @staticmethod
    def output_exists(
        base_dir: str, 
        today_date: str, 
        category: str
    ) -> bool:
        """
        Check if output file already exists for category.
        
        Args:
            base_dir: Base directory for scrapped content
            today_date: Today's date string (YYYY-MM-DD)
            category: Category name
            
        Returns:
            bool: True if output exists
        """
        output_path = (
            Path(base_dir) / today_date / category / "web-scrap.json"
        )
        return output_path.exists()
    
    @staticmethod
    def save_output(
        base_dir: str,
        today_date: str,
        output: ScrapedOutput
    ) -> None:
        """
        Save scraped output to JSON file.
        
        Args:
            base_dir: Base directory for scrapped content
            today_date: Today's date string (YYYY-MM-DD)
            output: Scraped output data
        """
        output_dir = Path(base_dir) / today_date / output.category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "web-scrap.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved output to {output_file}")