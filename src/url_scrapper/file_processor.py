"""
File Processor Module

Handles reading trend analysis files and coordinating scraping operations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config_manager import ConfigManager
from .models import (
    ProcessingReport, 
    ScrapedContent, 
    ScrapedOutput, 
    Trend, 
    TrendAnalysis
)
from .scraper import URLScraper

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Processes trend analysis files and coordinates URL scraping.
    
    Attributes:
        config: Configuration manager instance
        scraper: URL scraper instance
    """
    
    def __init__(self, config: ConfigManager, scraper: URLScraper):
        """
        Initialize file processor.
        
        Args:
            config: Configuration manager
            scraper: URL scraper instance
        """
        self.config = config
        self.scraper = scraper
        logger.info("FileProcessor initialized")
    
    def process_all_files(self, date: str) -> ProcessingReport:
        """
        Process all trend analysis files for a given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            ProcessingReport with execution statistics
        """
        report = ProcessingReport(
            execution_date=date,
            output_directory=str(self.config.url_scrapped_content_base_path / date)
        )
        
        # Get input directory for the date
        input_dir = self.config.analysis_report_base_path / date
        
        if not input_dir.exists():
            error_msg = f"Input directory does not exist: {input_dir}"
            logger.error(error_msg)
            report.add_error(error_msg)
            return report
        
        # Find all JSON files
        json_files = list(input_dir.glob("*.json"))
        
        if not json_files:
            error_msg = f"No JSON files found in {input_dir}"
            logger.warning(error_msg)
            report.add_error(error_msg)
            return report
        
        logger.info(f"Found {len(json_files)} files to process")
        report.total_categories = len(json_files)
        
        # Process each file sequentially
        for json_file in json_files:
            try:
                self._process_file(json_file, date, report)
            except Exception as e:
                error_msg = f"Error processing file {json_file.name}: {e}"
                logger.error(error_msg, exc_info=True)
                report.add_error(error_msg)
                # Continue with next file (error isolation)
                continue
        
        return report
    
    def _process_file(self, file_path: Path, date: str, report: ProcessingReport) -> None:
        """
        Process a single trend analysis file.
        
        Args:
            file_path: Path to the JSON file
            date: Date string in YYYY-MM-DD format
            report: Processing report to update
        """
        logger.info(f"Processing file: {file_path.name}")
        
        # Load and parse the file
        trend_analysis = self._load_trend_analysis(file_path)
        if not trend_analysis:
            report.add_error(f"Failed to load {file_path.name}")
            return
        
        # Count trends
        report.total_trends += len(trend_analysis.trends)
        
        # Scrape URLs from all trends
        scraped_contents = self._scrape_trends(trend_analysis.trends, report)
        
        # Save output
        self._save_output(trend_analysis, scraped_contents, date)
        
        logger.info(f"Completed processing {file_path.name}")
    
    def _load_trend_analysis(self, file_path: Path) -> Optional[TrendAnalysis]:
        """
        Load and parse a trend analysis JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            TrendAnalysis object or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse trends
            trends = []
            for trend_data in data.get('trends', []):
                trend = Trend(
                    topic=trend_data.get('topic', ''),
                    reason=trend_data.get('reason', ''),
                    category=trend_data.get('category', ''),
                    links=trend_data.get('links', []),
                    search_keywords=trend_data.get('search_keywords', [])
                )
                trends.append(trend)
            
            analysis = TrendAnalysis(
                analysis_timestamp=data.get('analysis_timestamp', ''),
                source_file=data.get('source_file', file_path.name),
                category=data.get('category', ''),
                trends=trends
            )
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {file_path.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}", exc_info=True)
            return None
    
    def _scrape_trends(self, trends: List[Trend], report: ProcessingReport) -> List[ScrapedContent]:
        """
        Scrape URLs from all trends.
        
        Args:
            trends: List of trends to process
            report: Processing report to update
            
        Returns:
            List of scraped content objects
        """
        scraped_contents = []
        
        for trend in trends:
            for link in trend.links:
                report.total_urls_scraped += 1
                
                # Scrape the URL
                content = self.scraper.scrape_url(link)
                
                # Create scraped content object
                scraped = ScrapedContent(
                    topic=trend.topic,
                    link=link,
                    scrape_timestamp=datetime.now().isoformat()
                )
                
                if content:
                    scraped.content = content
                    report.increment_success()
                    logger.info(f"Successfully scraped: {link}")
                else:
                    scraped.error = "Failed to scrape content"
                    report.increment_failure()
                    logger.warning(f"Failed to scrape: {link}")
                
                scraped_contents.append(scraped)
        
        return scraped_contents
    
    def _save_output(
        self, 
        analysis: TrendAnalysis, 
        scraped_contents: List[ScrapedContent], 
        date: str
    ) -> None:
        """
        Save scraped content to output file.
        
        Args:
            analysis: Original trend analysis
            scraped_contents: List of scraped content
            date: Date string in YYYY-MM-DD format
        """
        # Create output directory structure
        # Convert category to safe filename
        category_safe = self._sanitize_filename(analysis.category)
        output_dir = self.config.url_scrapped_content_base_path / date / category_safe
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output object
        output = ScrapedOutput(
            analysis_timestamp=analysis.analysis_timestamp,
            source_file=analysis.source_file,
            category=analysis.category,
            trends=scraped_contents
        )
        
        # Save to JSON
        output_file = output_dir / "url-scrap.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self._to_dict(output), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved output to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving output to {output_file}: {e}", exc_info=True)
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Convert a string to a safe filename.
        
        Args:
            filename: Original filename/category
            
        Returns:
            Sanitized filename
        """
        # Replace spaces and slashes with hyphens
        safe = filename.replace(' ', '-').replace('/', '-')
        # Convert to lowercase
        safe = safe.lower()
        # Remove any other problematic characters
        safe = ''.join(c for c in safe if c.isalnum() or c == '-')
        # Remove consecutive hyphens
        safe = '-'.join(filter(None, safe.split('-')))
        return safe
    
    def _to_dict(self, obj) -> dict:
        """
        Convert dataclass to dictionary recursively.
        
        Args:
            obj: Object to convert
            
        Returns:
            Dictionary representation
        """
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, list):
                    result[key] = [self._to_dict(item) for item in value]
                elif hasattr(value, '__dict__'):
                    result[key] = self._to_dict(value)
                else:
                    result[key] = value
            return result
        return obj