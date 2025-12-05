# ============================================================================
# FILE: src/tech_trend_analysis/main.py
# ============================================================================
"""Main entry point for tech trend analysis."""

from datetime import date
from pathlib import Path
import sys

from .config import Config
from .exceptions import ConfigurationError, LLMError
from .logger import setup_logger
from .processor import TrendAnalysisProcessor


def main() -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    today = date.today().strftime('%Y-%m-%d')
    
    # Determine config path relative to script location
    script_dir = Path(__file__).resolve().parent.parent.parent
    config_path = script_dir / 'config.yaml'
    
    # Load configuration
    try:
        config = Config(config_path)
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    
    # Setup logger
    log_dir = Path(config.log_path)
    logger = setup_logger(
        name='tech_trend_analysis',
        log_dir=log_dir,
        date_str=today,
        level='INFO',
        use_json=True
    )
    
    logger.info("=" * 70)
    logger.info(f"Starting Tech Trend Analysis for {today}")
    logger.info("=" * 70)
    
    try:
        # Create processor and run
        processor = TrendAnalysisProcessor(config, logger)
        summary = processor.process_all()
        
        # Log summary
        logger.info("=" * 70)
        logger.info("Processing Summary:")
        logger.info(f"  Date: {summary['date']}")
        logger.info(f"  Total categories: {summary['total']}")
        logger.info(f"  Successful: {summary['successful']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Skipped: {summary['skipped']}")
        logger.info("=" * 70)
        
        if summary['failed'] > 0:
            logger.warning(
                f"{summary['failed']} categories failed processing"
            )
        
        logger.info("Tech Trend Analysis completed")
        return 0
        
    except LLMError as e:
        logger.critical(
            f"LLM configuration error: {e}",
            exc_info=True
        )
        return 1
    except Exception as e:
        logger.critical(
            f"Fatal error during execution: {e}",
            exc_info=True
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())