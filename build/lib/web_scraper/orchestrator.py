# src/web_scraper/orchestrator.py
"""Main orchestration logic for web scraper."""

import logging
from typing import List

from .config import Config
from .file_handler import FileHandler
from .scraper_factory import ScraperFactory
from .content_cleaner import ContentCleaner
from .models import TrendAnalysis, ScrapedTrend, ScrapedOutput
from .exceptions import ValidationError, ConfigurationError
from typing import Optional


logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """Orchestrates the web scraping process."""
    
    def __init__(self) -> None:
        """Initialize orchestrator with configuration."""
        self.config = Config()
        self.file_handler = FileHandler()
        self.scraper = ScraperFactory.create_scraper(self.config)
        self.cleaner = ContentCleaner()
        
        if not self.scraper:
            raise ConfigurationError(
                "No valid scraper API key found in environment. "
                "Please add SCRAPERAPI_KEY, SCRAPINGBEE_KEY, "
                "or ZENROWS_KEY to your .env file."
            )
    
    def run(self) -> None:
        """Execute the main scraping workflow."""
        today_date = self.file_handler.get_today_date()
        logger.info(f"Processing data for {today_date}")
        
        input_files = self.file_handler.get_input_files(
            self.config.analysis_report_dir,
            today_date
        )
        
        if not input_files:
            logger.warning(
                f"No input files found for {today_date}. Exiting."
            )
            return
        
        for file_path in input_files:
            self._process_category(file_path, today_date)
    
    def _process_category(self, file_path, today_date: str) -> None:
        """
        Process a single category file.
        
        Args:
            file_path: Path to category JSON file
            today_date: Today's date string (YYYY-MM-DD)
        """
        try:
            analysis = self.file_handler.load_trend_analysis(file_path)
            category = analysis.category
            
            # Check idempotency
            if self.file_handler.output_exists(
                self.config.scrapped_content_dir,
                today_date,
                category
            ):
                message = (
                    f"Skipping {category} "
                    f"(already processed for {today_date})"
                )
                logger.info(message)
                print(message)
                return
            
            logger.info(f"Processing category: {category}")
            scraped_trends = self._scrape_trends(analysis.trends)
            
            if not scraped_trends:
                logger.warning(
                    f"No trends successfully scraped for {category}"
                )
            
            output = ScrapedOutput(
                analysis_date=today_date,
                category=category,
                trends=scraped_trends
            )
            
            self.file_handler.save_output(
                self.config.scrapped_content_dir,
                today_date,
                output
            )
            
        except ValidationError as e:
            logger.error(f"Validation error in {file_path}: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error processing {file_path}: {e}",
                exc_info=True
            )
    
    def _scrape_trends(self, trends: List) -> List[ScrapedTrend]:
        """
        Scrape content for all trends.
        
        Args:
            trends: List of Trend objects
            
        Returns:
            List[ScrapedTrend]: List of successfully scraped trends
        """
        scraped_trends = []
        
        for trend in trends:
            scraped_trend = self._scrape_trend_urls(trend)
            if scraped_trend:
                scraped_trends.append(scraped_trend)
        
        return scraped_trends
    
    def _scrape_trend_urls(self, trend) -> Optional[ScrapedTrend]:
        """
        Attempt to scrape content from trend URLs.
        Tries each URL until one succeeds.
        
        Args:
            trend: Trend object containing URLs
            
        Returns:
            Optional[ScrapedTrend]: First successful scrape or None
        """
        for link in trend.links:
            scraped_trend = self._scrape_single_url(trend, link)
            if scraped_trend:
                return scraped_trend
        
        logger.warning(
            f"Failed to scrape any URL for topic: {trend.topic}"
        )
        return None
    
    def _scrape_single_url(self, trend, link: str):
        """
        Scrape and clean content for a single URL.
        
        Args:
            trend: Trend object
            link: URL to scrape
            
        Returns:
            Optional[ScrapedTrend]: Scraped trend or None
        """
        logger.info(f"Scraping: {link}")
        
        html_content = self.scraper.scrape(link)
        if not html_content:
            logger.error(f"Failed to scrape {link}")
            return None
        
        cleaned_content = self.cleaner.clean(html_content)
        if not cleaned_content:
            logger.error(f"Failed to clean content from {link}")
            return None
        
        return ScrapedTrend(
            topic=trend.topic,
            link=link,
            content=cleaned_content,
            search_keywords=trend.search_keywords
        )