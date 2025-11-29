#!/usr/bin/env python3
"""
Tech Trend Article Generator - Main Entry Point

This module orchestrates the generation of technology trend articles using LLMs.
It reads analysis files, performs similarity searches, and generates articles.
"""

import logging
import sys
from pathlib import Path

from src.article_generator.config_loader import ConfigLoader
from src.article_generator.article_service import ArticleService
from src.article_generator.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('article_generator.log')
    ]
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main entry point for the article generator.
    
    Process:
    1. Load configuration
    2. Initialize services
    3. Process all analysis files
    4. Generate summary report
    """
    try:
        logger.info("=" * 80)
        logger.info("Tech Trend Article Generator Started")
        logger.info("=" * 80)
        
        # Load configuration
        config = ConfigLoader.load_config('config.yaml')
        logger.info("Configuration loaded successfully")
        
        # Initialize article service
        article_service = ArticleService(config)
        
        # Process all analysis files
        results = article_service.process_all_analyses()
        
        # Generate summary report
        report_generator = ReportGenerator()
        report = report_generator.generate_report(results)
        
        # Display report
        print("\n" + "=" * 80)
        print(report)
        print("=" * 80)
        
        logger.info("Article generation completed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()