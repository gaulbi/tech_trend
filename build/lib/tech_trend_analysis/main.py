"""Main application entry point."""

import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import load_config
from .exceptions import ConfigurationError
from .processor import TrendAnalysisProcessor


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tech_trend_analysis.log'),
            logging.StreamHandler()
        ]
    )


def get_target_date() -> str:
    """
    Get target date for processing.
    
    Returns:
        Date string in YYYY-MM-DD format (today's date)
    """
    return datetime.now().strftime("%Y-%m-%d")


def main() -> None:
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting tech trend analysis")
        print("=" * 60)
        print("Tech Trend Analysis")
        print("=" * 60)
        
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        processor = TrendAnalysisProcessor(config)
        target_date = get_target_date()
        
        processor.process_all_feeds(target_date)
        
        print("\n" + "=" * 60)
        print("Analysis complete")
        print("=" * 60)
        logger.info("Tech trend analysis completed successfully")
    
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n\nProcess interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()