"""
Main orchestrator for wiki_search module.
"""

import sys
from datetime import date
from pathlib import Path

from .config import load_config
from .exceptions import ConfigurationError, ValidationError
from .file_handler import get_input_files, load_category_data, output_exists
from .logger import setup_logging
from .processor import CategoryProcessor
from .wikipedia_client import WikipediaClient


class WikiSearchOrchestrator:
    """Orchestrates the entire Wikipedia search workflow."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.config = None
        self.logger = None
        self.today = None
    
    def run(self) -> int:
        """
        Execute the Wikipedia search workflow.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            self._initialize()
            self._process_categories()
            
            self.logger.info("Wikipedia search completed successfully")
            return 0
            
        except ConfigurationError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    def _initialize(self) -> None:
        """Initialize configuration, logging, and Wikipedia client."""
        # Load configuration
        self.config = load_config()
        
        # Get today's date
        self.today = date.today().strftime('%Y-%m-%d')
        
        # Setup logging
        log_dir = Path(self.config['scrape']['log'])
        self.logger = setup_logging(log_dir, self.today)
        
        self.logger.info(f"Starting Wikipedia search for date: {self.today}")
    
    def _process_categories(self) -> None:
        """Process all categories for today's date."""
        # Get input files
        base_dir = Path(self.config['tech-trend-analysis']['analysis-report'])
        input_files = get_input_files(base_dir, self.today)
        
        if not input_files:
            self.logger.warning(f"No input files found for {self.today}")
            print(f"No input files found for {self.today}")
            return
        
        self.logger.info(f"Found {len(input_files)} categories to process")
        
        # Initialize Wikipedia client and processor
        timeout = self.config['scrape'].get('timeout', 60)
        max_results = self.config['scrape'].get('max-search-results', 5)
        
        wikipedia_client = WikipediaClient(timeout=timeout)
        processor = CategoryProcessor(
            wikipedia_client, max_results, self.logger
        )
        
        # Process each category
        output_base = Path(self.config['scrape']['url-scraped-content'])
        
        for input_file in input_files:
            self._process_single_category(
                input_file, output_base, processor
            )
    
    def _process_single_category(
        self,
        input_file: Path,
        output_base: Path,
        processor: CategoryProcessor
    ) -> None:
        """
        Process a single category file.
        
        Args:
            input_file: Path to input category JSON
            output_base: Base directory for output
            processor: Category processor instance
        """
        try:
            # Load category data
            category_data = load_category_data(input_file)
            category = category_data['category']
            
            # Check if already processed
            output_path = output_base / self.today / category / "wiki-search.json"
            if output_exists(output_path):
                print(f"Skipping {category} (already processed for {self.today})")
                self.logger.info(
                    f"Skipped (already processed)",
                    extra={'category': category}
                )
                return
            
            # Process category
            self.logger.info(
                f"Processing category", extra={'category': category}
            )
            processor.process(category_data, output_path)
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing {input_file}: {e}")