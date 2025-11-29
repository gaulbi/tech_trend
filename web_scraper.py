#!/usr/bin/env python3
"""
Web Scraper - Main Entry Point

This module orchestrates the web scraping process for tech trend analysis.
It processes today's trend data, scrapes URLs, and stores cleaned content.
"""

import sys
import logging
from pathlib import Path

from src.web_scraper.orchestrator import ScraperOrchestrator
from src.web_scraper.exceptions import ConfigurationError


def setup_logging() -> None:
    """
    Configure production-grade logging with handlers and rotation.
    Logs to stdout (container-friendly) and rotating file.
    """
    from logging.handlers import RotatingFileHandler
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout for containers)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler with rotation (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        'web_scraper.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def main() -> int:
    """
    Main entry point for the web scraper application.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting web scraper application")
        orchestrator = ScraperOrchestrator()
        orchestrator.run()
        logger.info("Web scraper completed successfully")
        return 0
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())