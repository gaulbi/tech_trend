#!/usr/bin/env python3
"""
URL Content Scraper - Main Entry Point

This module orchestrates the scraping of URLs from tech trend analysis files,
cleans the content, and saves structured output.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from src.url_scrapper.config_manager import ConfigManager
from src.url_scrapper.file_processor import FileProcessor
from src.url_scrapper.scraper import URLScraper
from src.url_scrapper.models import ProcessingReport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('url_scrapper.log')
    ]
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main execution function for URL content scraping.
    
    Orchestrates the complete workflow:
    1. Load configuration
    2. Discover today's trend analysis files
    3. Process each file sequentially
    4. Generate summary report
    """
    try:
        logger.info("Starting URL Content Scraper")
        
        # Initialize configuration
        config = ConfigManager('config.yaml')
        logger.info("Configuration loaded successfully")
        
        # Initialize components
        scraper = URLScraper(timeout=config.scrap_timeout)
        processor = FileProcessor(config, scraper)
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Processing files for date: {today}")
        
        # Process all trend analysis files for today
        report = processor.process_all_files(today)
        
        # Display summary
        display_summary(report)
        
        logger.info("URL Content Scraper completed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration or input file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}", exc_info=True)
        sys.exit(1)


def display_summary(report: ProcessingReport) -> None:
    """
    Display a formatted summary of the processing results.
    
    Args:
        report: ProcessingReport containing execution statistics
    """
    print("\n" + "="*60)
    print("URL CONTENT SCRAPER - EXECUTION SUMMARY")
    print("="*60)
    print(f"Execution Date: {report.execution_date}")
    print(f"Total Categories Processed: {report.total_categories}")
    print(f"Total Trends Found: {report.total_trends}")
    print(f"Total URLs Scraped: {report.total_urls_scraped}")
    print(f"Successful Scrapes: {report.successful_scrapes}")
    print(f"Failed Scrapes: {report.failed_scrapes}")
    print(f"Output Directory: {report.output_directory}")
    
    if report.errors:
        print(f"\nErrors Encountered ({len(report.errors)}):")
        for error in report.errors:
            print(f"  - {error}")
    else:
        print("\n✓ No errors encountered")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()