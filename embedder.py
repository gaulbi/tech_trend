"""
Main entry point for the embedder module.
Processes scraped articles, chunks them, generates embeddings, and stores in ChromaDB.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from src.embedder.config import load_config
from src.embedder.exceptions import ConfigurationError, EmbedderError
from src.embedder.logger import get_logger, log_execution_time
from src.embedder.processor import EmbeddingProcessor


logger = get_logger(__name__)


@log_execution_time
def main() -> int:
    """
    Main entry point for the embedder.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Embed scraped articles into ChromaDB"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to process (optional)",
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)",
    )
    
    args = parser.parse_args()
    
    # Determine feed date
    feed_date = args.feed_date or date.today().strftime('%Y-%m-%d')
    
    logger.info(
        f"Starting embedder",
        extra={
            "feed_date": feed_date,
            "category": args.category or "all",
        }
    )
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize processor
        processor = EmbeddingProcessor(config, feed_date)
        
        # Process categories
        if args.category:
            processor.process_category(args.category)
        else:
            processor.process_all_categories()
        
        logger.info("Embedder completed successfully")
        return 0
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except EmbedderError as e:
        logger.error(f"Embedder error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())