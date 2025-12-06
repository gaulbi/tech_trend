#!/usr/bin/env python3
"""
Article Publisher - Main Entry Point
Publishes today's technology articles to Hashnode using GraphQL API.
"""

import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from article_publisher.publisher import ArticlePublisher
from article_publisher.config import load_config
from article_publisher.logger import setup_logger, log_error
from article_publisher.exceptions import ConfigurationError


def main() -> int:
    """
    Main entry point for article publisher.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = None
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        logger = setup_logger(config)
        logger.info("Article Publisher started")
        
        # Initialize and run publisher
        publisher = ArticlePublisher(config, logger)
        success_count, fail_count = publisher.publish_today_articles()
        
        logger.info(
            f"Publishing completed: {success_count} succeeded, "
            f"{fail_count} failed"
        )
        
        return 0 if fail_count == 0 else 1
        
    except ConfigurationError as e:
        if logger:
            log_error(logger, e, "Configuration error")
        else:
            print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        if logger:
            log_error(logger, e, "Unexpected error")
        else:
            print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())