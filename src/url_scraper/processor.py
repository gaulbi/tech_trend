"""
Main processing module for URL scraping.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from .config import Config
from .logger import get_logger
from .models import TrendAnalysis, ScrapedContent, TrendItem, ScrapedTrendItem
from .scraper import URLScraper
from .validator import ValidationError


class URLScraperProcessor:
    """Processes tech trend analysis and scrapes URLs."""
    
    def __init__(self, config: Config, feed_date: str):
        """
        Initialize processor.
        
        Args:
            config: Configuration instance.
            feed_date: Feed date in YYYY-MM-DD format.
        """
        self.config = config
        self.feed_date = feed_date
        self.logger = get_logger(__name__)
        self.scraper = URLScraper(config.timeout)
    
    def process(self, category: Optional[str] = None) -> None:
        """
        Process categories for the feed date.
        
        Args:
            category: Specific category to process, or None for all.
        """
        input_dir = Path(self.config.analysis_report_dir) / self.feed_date
        
        if not input_dir.exists():
            self.logger.warning(
                f"No input directory found for {self.feed_date}"
            )
            return
        
        if category:
            categories = [category]
        else:
            categories = self._discover_categories(input_dir)
        
        if not categories:
            self.logger.warning(
                f"No categories found for {self.feed_date}"
            )
            return
        
        for cat in categories:
            self._process_category(cat, input_dir)
    
    def _discover_categories(self, input_dir: Path) -> List[str]:
        """
        Discover all category JSON files in input directory.
        
        Args:
            input_dir: Input directory path.
            
        Returns:
            List of category names (without .json extension).
        """
        json_files = input_dir.glob("*.json")
        return [f.stem for f in json_files]
    
    def _process_category(
        self, 
        category: str, 
        input_dir: Path
    ) -> None:
        """
        Process a single category.
        
        Args:
            category: Category name.
            input_dir: Input directory path.
        """
        self.logger.info(f"Processing category: {category}")
        
        # Check idempotency
        output_dir = (
            Path(self.config.scraped_content_dir) 
            / self.feed_date 
            / category
        )
        output_file = output_dir / "url-scrape.json"
        
        if output_file.exists():
            self.logger.info(
                f"Skipping {category} "
                f"(already processed for {self.feed_date})"
            )
            print(
                f"Skipping {category} "
                f"(already processed for {self.feed_date})"
            )
            return
        
        # Load input file
        input_file = input_dir / f"{category}.json"
        if not input_file.exists():
            self.logger.warning(
                f"Input file not found: {input_file}"
            )
            return
        
        try:
            trend_analysis = self._load_trend_analysis(input_file)
        except ValidationError as e:
            self.logger.error(
                f"Validation error for {category}: {e}"
            )
            return
        
        # Scrape URLs
        scraped_content = self._scrape_trends(trend_analysis)
        
        # Save output
        self._save_output(scraped_content, output_dir)
        
        self.logger.info(
            f"Category {category} completed: "
            f"{len(scraped_content.trends)} items scraped"
        )
    
    def _load_trend_analysis(self, file_path: Path) -> TrendAnalysis:
        """
        Load and validate trend analysis from JSON file.
        
        Args:
            file_path: Path to input JSON file.
            
        Returns:
            TrendAnalysis instance.
            
        Raises:
            ValidationError: If JSON is invalid.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TrendAnalysis.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValidationError(f"Error loading file: {e}")
    
    def _scrape_trends(
        self, 
        trend_analysis: TrendAnalysis
    ) -> ScrapedContent:
        """
        Scrape all URLs from trend analysis.
        
        Args:
            trend_analysis: Trend analysis data.
            
        Returns:
            ScrapedContent with all scraped items.
        """
        scraped_trends: List[ScrapedTrendItem] = []
        
        for trend in trend_analysis.trends:
            scraped_trends.extend(self._scrape_trend_links(trend))
        
        return ScrapedContent(
            feed_date=trend_analysis.feed_date,
            category=trend_analysis.category,
            trends=scraped_trends
        )
    
    def _scrape_trend_links(
        self, 
        trend: TrendItem
    ) -> List[ScrapedTrendItem]:
        """
        Scrape all links for a single trend.
        
        Args:
            trend: Trend item with links to scrape.
            
        Returns:
            List of scraped trend items (one per link).
        """
        scraped_items: List[ScrapedTrendItem] = []
        
        for link in trend.links:
            content = self.scraper.scrape(link)
            
            if content:
                scraped_items.append(
                    ScrapedTrendItem(
                        topic=trend.topic,
                        query_used="na",
                        search_link=link,
                        content=content
                    )
                )
            else:
                self.logger.debug(f"Skipped link: {link}")
        
        return scraped_items
    
    def _save_output(
        self, 
        scraped_content: ScrapedContent, 
        output_dir: Path
    ) -> None:
        """
        Save scraped content to output file.
        
        Args:
            scraped_content: Scraped content to save.
            output_dir: Output directory path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "url-scrape.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                scraped_content.to_dict(), 
                f, 
                indent=2, 
                ensure_ascii=False
            )
        
        self.logger.info(f"Output saved to: {output_file}")
