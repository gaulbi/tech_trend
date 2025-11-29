"""Main URL scraper implementation."""

import json
from datetime import date
from pathlib import Path
from typing import List, Optional
import logging

from .config import Config
from .logger import setup_logger
from .url_fetcher import URLFetcher
from .content_extractor import ContentExtractor
from .models import (
    AnalysisInput, AnalysisOutput, TrendInput, TrendOutput
)
from .exceptions import ValidationError


class URLScraper:
    """Main URL scraper orchestrator."""
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        """
        Initialize URL scraper.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.today = date.today()
        self.logger = setup_logger(self.config.log_dir, self.today)
        self.fetcher = URLFetcher(self.config.timeout, self.logger)
        self.extractor = ContentExtractor()
        
        self.logger.info(f"URL Scraper initialized for {self.today}")
    
    def run(self) -> None:
        """Run the scraper for today's date."""
        input_dir = self._get_input_directory()
        
        if not input_dir.exists():
            self.logger.warning(
                f"No input directory for today: {input_dir}"
            )
            print(f"No data found for {self.today}. Exiting gracefully.")
            return
        
        category_files = list(input_dir.glob("*.json"))
        
        if not category_files:
            self.logger.warning(
                f"No category files found in {input_dir}"
            )
            print(f"No category files for {self.today}. Exiting gracefully.")
            return
        
        self.logger.info(
            f"Found {len(category_files)} categories to process"
        )
        
        for category_file in category_files:
            self._process_category(category_file)
        
        self.fetcher.close()
        self.logger.info("URL scraping completed")
    
    def _get_input_directory(self) -> Path:
        """Get today's input directory."""
        date_str = self.today.strftime('%Y-%m-%d')
        return self.config.analysis_report_dir / date_str
    
    def _get_output_path(self, category: str) -> Path:
        """
        Get output file path for a category.
        
        Args:
            category: Category name
            
        Returns:
            Path: Output file path
        """
        date_str = self.today.strftime('%Y-%m-%d')
        output_dir = self.config.scrapped_content_dir / date_str / category
        return output_dir / "url-scrape.json"
    
    def _process_category(self, category_file: Path) -> None:
        """
        Process a single category file.
        
        Args:
            category_file: Path to category JSON file
        """
        category = category_file.stem
        output_path = self._get_output_path(category)
        
        # Check idempotency
        if output_path.exists():
            message = (
                f"Skipping {category} "
                f"(already processed for {self.today})"
            )
            self.logger.info(message)
            print(message)
            return
        
        try:
            analysis_input = self._load_analysis_input(category_file)
            analysis_output = self._scrape_trends(analysis_input)
            self._save_output(output_path, analysis_output)
            
            self.logger.info(f"Successfully processed category: {category}")
            
        except ValidationError as e:
            self.logger.error(
                f"Validation error for {category}: {e}"
            )
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {category}: {e}", 
                exc_info=True
            )
    
    def _load_analysis_input(self, file_path: Path) -> AnalysisInput:
        """
        Load and validate analysis input file.
        
        Args:
            file_path: Path to input JSON file
            
        Returns:
            AnalysisInput: Validated input data
            
        Raises:
            ValidationError: If JSON is invalid or malformed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            trends = [
                TrendInput(
                    topic=t['topic'],
                    reason=t['reason'],
                    links=t['links'],
                    search_keywords=t['search_keywords']
                )
                for t in data['trends']
            ]
            
            return AnalysisInput(
                analysis_date=data['analysis_date'],
                category=data['category'],
                trends=trends
            )
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {file_path}: {e}")
        except KeyError as e:
            raise ValidationError(f"Missing required field in {file_path}: {e}")
    
    def _scrape_trends(self, analysis: AnalysisInput) -> AnalysisOutput:
        """
        Scrape all URLs from trends.
        
        Args:
            analysis: Input analysis data
            
        Returns:
            AnalysisOutput: Output with scraped content
        """
        output_trends: List[TrendOutput] = []
        
        for trend in analysis.trends:
            for link in trend.links:
                content = self._scrape_url(link)
                
                if content:
                    output_trends.append(
                        TrendOutput(
                            topic=trend.topic,
                            link=link,
                            content=content,
                            search_keywords=trend.search_keywords
                        )
                    )
                else:
                    self.logger.warning(
                        f"Skipping trend '{trend.topic}' "
                        f"link {link} (fetch failed)"
                    )
        
        return AnalysisOutput(
            analysis_date=analysis.analysis_date,
            category=analysis.category,
            trends=output_trends
        )
    
    def _scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape and clean content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Optional[str]: Cleaned content or None if failed
        """
        html = self.fetcher.fetch(url)
        
        if html is None:
            return None
        
        try:
            content = self.extractor.extract_clean_content(html)
            return content
        except Exception as e:
            self.logger.error(
                f"Error extracting content from {url}: {e}"
            )
            return None
    
    def _save_output(
        self, 
        output_path: Path, 
        analysis: AnalysisOutput
    ) -> None:
        """
        Save output to JSON file.
        
        Args:
            output_path: Path to save output
            analysis: Analysis output data
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "analysis_date": analysis.analysis_date,
            "category": analysis.category,
            "trends": [
                {
                    "topic": t.topic,
                    "link": t.link,
                    "content": t.content,
                    "search_keywords": t.search_keywords
                }
                for t in analysis.trends
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved output to {output_path}")