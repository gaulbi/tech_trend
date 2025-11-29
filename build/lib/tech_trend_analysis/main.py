"""Main orchestration logic for tech trend analysis."""

import sys
from datetime import date
from pathlib import Path
from typing import List

from .config import Config
from .logger import setup_logger
from .llm.factory import LLMFactory
from .processor import TrendProcessor
from .exceptions import (
    ConfigurationError,
    ValidationError,
    LLMError,
    NetworkError
)


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format.
    
    Returns:
        Today's date string
    """
    return date.today().strftime('%Y-%m-%d')


def load_prompt_template(prompt_path: str) -> str:
    """Load prompt template from file.
    
    Args:
        prompt_path: Path to prompt template file
        
    Returns:
        Prompt template string
        
    Raises:
        ConfigurationError: If template file not found
    """
    template_file = Path(prompt_path)
    if not template_file.exists():
        raise ConfigurationError(
            f"Prompt template not found: {prompt_path}"
        )
    
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def get_category_files(
    rss_feed_path: str, 
    today_date: str
) -> List[Path]:
    """Get list of category JSON files for today.
    
    Args:
        rss_feed_path: Base RSS feed directory path
        today_date: Today's date in YYYY-MM-DD format
        
    Returns:
        List of category JSON file paths
    """
    feed_dir = Path(rss_feed_path) / today_date
    
    if not feed_dir.exists():
        return []
    
    return list(feed_dir.glob("*.json"))


def process_category(
    processor: TrendProcessor,
    category_file: Path,
    output_dir: Path,
    today_date: str,
    logger
) -> bool:
    """Process a single category file.
    
    Args:
        processor: Trend processor instance
        category_file: Path to category JSON file
        output_dir: Output directory for results
        today_date: Today's date in YYYY-MM-DD format
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    category_name = category_file.stem
    output_file = output_dir / today_date / f"{category_name}.json"
    
    if output_file.exists():
        logger.info(
            f"Skipping category '{category_name}' - already analyzed",
            extra={'category': category_name}
        )
        print(f"Skipping {category_name} (already analyzed)")
        return True
    
    try:
        logger.info(
            f"Processing category: {category_name}",
            extra={'category': category_name}
        )
        print(f"Processing {category_name}...")
        
        feed = processor.load_rss_feed(category_file)
        if feed is None:
            return False
        
        report = processor.analyze_feed(feed, today_date)
        processor.save_report(report, output_file)
        
        logger.info(
            f"Successfully analyzed category: {category_name}",
            extra={'category': category_name}
        )
        print(f"✓ Completed {category_name}")
        return True
        
    except ValidationError as e:
        logger.error(
            f"Validation error for {category_name}: {str(e)}",
            extra={'category': category_name}
        )
        print(f"✗ Validation error in {category_name}: {str(e)}")
        return False
        
    except (NetworkError, LLMError) as e:
        logger.error(
            f"LLM/Network error for {category_name}: {str(e)}",
            extra={'category': category_name}
        )
        print(f"✗ Error processing {category_name}: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(
            f"Unexpected error for {category_name}: {str(e)}",
            extra={'category': category_name},
            exc_info=True
        )
        print(f"✗ Unexpected error in {category_name}: {str(e)}")
        return False


def initialize_components(config: Config, today_date: str):
    """Initialize logger, LLM client, and processor.
    
    Args:
        config: Configuration instance
        today_date: Today's date string
        
    Returns:
        Tuple of (logger, processor)
    """
    logger = setup_logger(config.log_path, today_date)
    prompt_template = load_prompt_template(config.prompt_path)
    
    api_key = config.get_api_key(config.llm_server)
    llm_client = LLMFactory.create_client(
        provider=config.llm_server,
        api_key=api_key,
        model=config.llm_model,
        timeout=config.llm_timeout,
        retry_count=config.llm_retry
    )
    
    processor = TrendProcessor(llm_client, prompt_template, logger)
    return logger, processor


def process_all_categories(
    processor: TrendProcessor,
    category_files: List[Path],
    output_dir: Path,
    today_date: str,
    logger
) -> int:
    """Process all category files.
    
    Args:
        processor: Trend processor instance
        category_files: List of category file paths
        output_dir: Output directory
        today_date: Today's date string
        logger: Logger instance
        
    Returns:
        Number of successfully processed categories
    """
    success_count = 0
    for category_file in category_files:
        if process_category(
            processor, 
            category_file, 
            output_dir, 
            today_date, 
            logger
        ):
            success_count += 1
    return success_count


def main() -> int:
    """Main entry point for tech trend analysis.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        config = Config()
        today_date = get_today_date()
        
        logger, processor = initialize_components(config, today_date)
        
        logger.info(f"Starting tech trend analysis for {today_date}")
        print(f"\n=== Tech Trend Analysis - {today_date} ===\n")
        
        category_files = get_category_files(
            config.rss_feed_path, 
            today_date
        )
        
        if not category_files:
            logger.warning(
                f"No RSS feed files found for {today_date}"
            )
            print(f"No RSS feed files found for {today_date}")
            return 0
        
        logger.info(f"Found {len(category_files)} categories to process")
        print(f"Found {len(category_files)} categories\n")
        
        output_dir = Path(config.analysis_report_path)
        success_count = process_all_categories(
            processor,
            category_files,
            output_dir,
            today_date,
            logger
        )
        
        logger.info(
            f"Analysis complete: {success_count}/{len(category_files)} "
            f"categories processed successfully"
        )
        print(
            f"\n=== Analysis Complete ===\n"
            f"Successfully processed: {success_count}/{len(category_files)}"
        )
        
        return 0
        
    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())