"""
Input/Output handling for trend analysis files.
"""
import json
import shutil
from pathlib import Path
from typing import List, Optional

from .exceptions import ValidationError
from .logger import get_logger
from .models import TrendAnalysis


logger = get_logger(__name__)


class IOHandler:
    """Handles reading and writing trend analysis files."""
    
    def __init__(
        self,
        analysis_base_path: Path,
        dedup_base_path: Path,
        org_base_path: Path,
    ):
        """
        Initialize IO handler.
        
        Args:
            analysis_base_path: Base path for input files
            dedup_base_path: Base path for output files
            org_base_path: Base path for original backup files
        """
        self.analysis_base_path = analysis_base_path
        self.dedup_base_path = dedup_base_path
        self.org_base_path = org_base_path
    
    def _get_input_path(
        self,
        feed_date: str,
        category: str,
    ) -> Path:
        """
        Get input file path.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            Path to input file
        """
        return (
            self.analysis_base_path / feed_date / f"{category}.json"
        )
    
    def _get_output_path(
        self,
        feed_date: str,
        category: str,
    ) -> Path:
        """
        Get output file path.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            Path to output file
        """
        return (
            self.dedup_base_path / feed_date / f"{category}.json"
        )
    
    def _get_org_path(
        self,
        feed_date: str,
        category: str,
    ) -> Path:
        """
        Get original backup file path.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            Path to original backup file
        """
        return (
            self.org_base_path / feed_date / f"{category}.json"
        )
    
    def output_exists(
        self,
        feed_date: str,
        category: str,
    ) -> bool:
        """
        Check if output file already exists (idempotency).
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            True if output exists, False otherwise
        """
        output_path = self._get_output_path(feed_date, category)
        return output_path.exists()
    
    def get_available_categories(
        self,
        feed_date: str,
    ) -> List[str]:
        """
        Get list of available categories for a feed date.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            
        Returns:
            List of category names
        """
        date_dir = self.analysis_base_path / feed_date
        
        if not date_dir.exists():
            logger.warning(
                f"No analysis directory found for {feed_date}"
            )
            return []
        
        categories = [
            p.stem for p in date_dir.glob("*.json")
        ]
        
        logger.info(
            f"Found {len(categories)} categories for {feed_date}"
        )
        return sorted(categories)
    
    def read_analysis(
        self,
        feed_date: str,
        category: str,
    ) -> Optional[TrendAnalysis]:
        """
        Read trend analysis from file.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            TrendAnalysis object or None if file not found
            
        Raises:
            ValidationError: If JSON is invalid
        """
        input_path = self._get_input_path(feed_date, category)
        
        if not input_path.exists():
            logger.warning(
                f"Input file not found: {input_path}"
            )
            return None
        
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            analysis = TrendAnalysis.from_dict(data)
            logger.info(
                f"Read {len(analysis.trends)} trends from "
                f"{category} ({feed_date})"
            )
            return analysis
            
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON in {input_path}: {e}"
            )
        except KeyError as e:
            raise ValidationError(
                f"Missing required field in {input_path}: {e}"
            )
        except Exception as e:
            raise ValidationError(
                f"Error reading {input_path}: {e}"
            )
    
    def write_analysis(
        self,
        analysis: TrendAnalysis,
    ) -> None:
        """
        Write deduplicated analysis to file.
        
        Args:
            analysis: TrendAnalysis with filtered trends
        """
        output_path = self._get_output_path(
            analysis.feed_date,
            analysis.category,
        )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    analysis.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            
            logger.info(
                f"Wrote {len(analysis.trends)} trends to "
                f"{output_path}"
            )
            
        except Exception as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise ValidationError(
                f"Failed to write output file: {e}"
            )
    
    def rotate_files(
        self,
        feed_date: str,
        category: str,
    ) -> None:
        """
        Rotate files after successful processing.
        
        Steps:
        1. Copy original to org-analysis-report
        2. Delete input file from analysis-report
        3. Copy filtered file to analysis-report
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Category name
        """
        input_path = self._get_input_path(feed_date, category)
        output_path = self._get_output_path(feed_date, category)
        org_path = self._get_org_path(feed_date, category)
        
        try:
            # Step 1: Copy original to org location
            org_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(input_path, org_path)
            logger.info(f"Backed up original to {org_path}")
            
            # Step 2: Delete input file
            input_path.unlink()
            logger.info(f"Deleted input file {input_path}")
            
            # Step 3: Copy filtered file to input location
            shutil.copy2(output_path, input_path)
            logger.info(
                f"Copied filtered file to {input_path}"
            )
            
        except Exception as e:
            logger.error(
                f"Error rotating files for {category}: {e}",
                exc_info=True,
            )
            raise ValidationError(
                f"Failed to rotate files: {e}"
            )
