# src/web_scraper/orchestrator.py
"""Main orchestration logic for web scraper."""

import logging
from datetime import date
from pathlib import Path
from typing import List

from .config import Config
from .logger import setup_logger
from .scraper_factory import ScraperFactory
from .file_processor import FileProcessor
from .scraper import WebScraper
from .models import OutputData
from .exceptions import ValidationError


class ScraperOrchestrator:
    """Orchestrates the web scraping process."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize orchestrator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.today = date.today()
        self.logger = setup_logger(
            self.config.get('scrape.log'),
            self.today
        )
        
        # Initialize scraper
        factory = ScraperFactory()
        client = factory.create_client(
            timeout=self.config.get('scrape.timeout')
        )
        
        self.scraper = WebScraper(
            client=client,
            max_results=self.config.get('scrape.max-search-results'),
            logger=self.logger
        )
        
        self.file_processor = FileProcessor()
    
    def run(self) -> None:
        """Execute the web scraping process."""
        self.logger.info(f"Starting web scraper for {self.today}")
        
        # Get input directory for today
        input_dir = self._get_input_dir()
        
        if not input_dir.exists():
            self.logger.warning(
                f"No input directory found for {self.today}. Exiting."
            )
            print(f"No data to process for {self.today}")
            return
        
        # Get input files
        input_files = self.file_processor.get_input_files(input_dir)
        
        if not input_files:
            self.logger.warning(
                f"No input files found for {self.today}. Exiting."
            )
            print(f"No input files to process for {self.today}")
            return
        
        self.logger.info(f"Found {len(input_files)} categories to process")
        
        # Process each category
        for input_file in input_files:
            self._process_category(input_file)
        
        self.logger.info("Web scraping completed")
    
    def _get_input_dir(self) -> Path:
        """Get input directory for today's date."""
        base_dir = Path(self.config.get('tech-trend-analysis.analysis-report'))
        return base_dir / self.today.strftime('%Y-%m-%d')
    
    def _get_output_path(self, category: str) -> Path:
        """Get output file path for category."""
        base_dir = Path(self.config.get('scrape.url-scraped-content'))
        date_dir = base_dir / self.today.strftime('%Y-%m-%d')
        return date_dir / category / 'web-scrape.json'
    
    def _process_category(self, input_file: Path) -> None:
        """Process a single category file."""
        category = input_file.stem
        
        try:
            # Check idempotency
            output_path = self._get_output_path(category)
            
            if self.file_processor.output_exists(output_path):
                self.logger.info(
                    f"Skipping {category} (already processed for {self.today})"
                )
                print(
                    f"Skipping {category} (already processed for {self.today})"
                )
                return
            
            # Read input
            self.logger.info(f"Processing category: {category}")
            input_data = self.file_processor.read_input_file(input_file)
            
            if not input_data:
                return
            
            # Scrape content
            all_scraped = []
            
            for trend in input_data.trends:
                self.logger.info(f"Processing trend: {trend.topic}")
                
                try:
                    scraped = self.scraper.scrape_trend(trend)
                    all_scraped.extend(scraped)
                except Exception as e:
                    self.logger.error(
                        f"Error scraping trend {trend.topic}: {e}"
                    )
                    continue
            
            # Write output
            output_data = OutputData(
                analysis_date=input_data.analysis_date,
                category=category,
                trends=all_scraped
            )
            
            self.file_processor.write_output_file(output_path, output_data)
            
            self.logger.info(
                f"Completed {category}: scraped {len(all_scraped)} articles"
            )
            print(
                f"Completed {category}: scraped {len(all_scraped)} articles"
            )
            
        except ValidationError as e:
            self.logger.error(f"Validation error for {category}: {e}")
            print(f"Error processing {category}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error for {category}: {e}")
            print(f"Error processing {category}: {e}")