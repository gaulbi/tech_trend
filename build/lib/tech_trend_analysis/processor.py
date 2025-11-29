"""RSS feed processing and trend analysis."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import Config
from .exceptions import ValidationError, LLMProviderError
from .llm import LLMClientFactory, BaseLLMClient
from .models import Article, RSSFeed, Trend, TrendAnalysis

logger = logging.getLogger(__name__)


class TrendAnalysisProcessor:
    """Process RSS feeds and generate trend analysis."""
    
    def __init__(self, config: Config):
        """
        Initialize processor.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.llm_client: BaseLLMClient = LLMClientFactory.create(
            provider=config.llm.server,
            model=config.llm.llm_model,
            timeout=config.llm.timeout,
            max_retries=config.llm.retry
        )
    
    def load_prompt_template(self) -> str:
        """
        Load prompt template from file.
        
        Returns:
            Prompt template text
        """
        prompt_path = self.config.tech_trend_analysis.prompt
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def load_rss_feed(self, feed_path: Path) -> Optional[RSSFeed]:
        """
        Load and validate RSS feed from JSON file.
        
        Args:
            feed_path: Path to RSS feed JSON file
            
        Returns:
            Parsed RSS feed or None if not found
            
        Raises:
            ValidationError: If JSON is malformed
        """
        try:
            with open(feed_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"RSS feed not found: {feed_path}")
            return None
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {feed_path}: {e}")
        
        try:
            articles = [
                Article(title=a['title'], link=a['link'])
                for a in data['articles']
            ]
            
            return RSSFeed(
                category=data['category'],
                fetch_date=data['fetch_date'],
                article_count=data['article_count'],
                articles=articles
            )
        except KeyError as e:
            raise ValidationError(
                f"Missing required field in {feed_path}: {e}"
            )
    
    def build_prompt(self, template: str, rss_feed: RSSFeed) -> str:
        """
        Build LLM prompt from template and RSS feed.
        
        Args:
            template: Prompt template
            rss_feed: RSS feed data
            
        Returns:
            Complete prompt text
        """
        articles_text = "\n".join([
            f"- {article.title} ({article.link})"
            for article in rss_feed.articles
        ])
        
        prompt = template.replace("{category}", rss_feed.category)
        prompt = prompt.replace("{articles}", articles_text)
        prompt = prompt.replace("{date}", rss_feed.fetch_date)
        
        return prompt
    
    def parse_llm_response(self, response: str, 
                          category: str) -> Optional[TrendAnalysis]:
        """
        Parse LLM response into TrendAnalysis object.
        
        Args:
            response: Raw LLM response
            category: Feed category
            
        Returns:
            Parsed TrendAnalysis or None if invalid
        """
        try:
            # Remove potential markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            
            # Handle if LLM returns array directly
            if isinstance(data, list):
                trends_data = data
                analysis_date = datetime.now().strftime("%Y-%m-%d")
            else:
                trends_data = data.get('trends', [])
                analysis_date = data.get(
                    'analysis_date', 
                    datetime.now().strftime("%Y-%m-%d")
                )
            
            trends = [
                Trend(
                    topic=t['topic'],
                    reason=t['reason'],
                    links=t['links'],
                    search_keywords=t['search_keywords']
                )
                for t in trends_data
            ]
            
            return TrendAnalysis(
                analysis_date=analysis_date,
                category=category,
                trends=trends
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response was: {response[:200]}...")
            return None
    
    def save_analysis(self, analysis: TrendAnalysis, 
                     output_path: Path) -> None:
        """
        Save trend analysis to JSON file.
        
        Args:
            analysis: Trend analysis data
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "analysis_date": analysis.analysis_date,
            "category": analysis.category,
            "trends": [
                {
                    "topic": t.topic,
                    "reason": t.reason,
                    "links": t.links,
                    "search_keywords": t.search_keywords
                }
                for t in analysis.trends
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved analysis to {output_path}")
    
    def output_exists(self, date: str, category: str) -> bool:
        """
        Check if output file already exists.
        
        Args:
            date: Analysis date (YYYY-MM-DD)
            category: Feed category
            
        Returns:
            True if output exists
        """
        output_path = self._get_output_path(date, category)
        return output_path.exists()
    
    def _get_output_path(self, date: str, category: str) -> Path:
        """Get output file path."""
        base_path = self.config.tech_trend_analysis.analysis_report
        return base_path / date / f"{category}.json"
    
    def process_category(self, feed_path: Path) -> None:
        """
        Process a single RSS feed category.
        
        Args:
            feed_path: Path to RSS feed JSON file
        """
        try:
            rss_feed = self.load_rss_feed(feed_path)
            if not rss_feed:
                return
            
            if self.output_exists(rss_feed.fetch_date, rss_feed.category):
                logger.info(
                    f"Skipping {rss_feed.category} - already analyzed"
                )
                print(f"Skipping {rss_feed.category} (already analyzed)")
                return
            
            self._process_feed(rss_feed, feed_path)
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            print(f"✗ Failed {feed_path.stem} (validation error)")
        except Exception as e:
            logger.error(f"Unexpected error processing {feed_path}: {e}")
            print(f"✗ Failed {feed_path.stem} (unexpected error)")
    
    def _process_feed(self, rss_feed: RSSFeed, feed_path: Path) -> None:
        """
        Process RSS feed and generate analysis.
        
        Args:
            rss_feed: Parsed RSS feed data
            feed_path: Original feed file path
        """
        logger.info(f"Processing {rss_feed.category}")
        print(f"Processing {rss_feed.category}...")
        
        template = self.load_prompt_template()
        prompt = self.build_prompt(template, rss_feed)
        
        try:
            response = self.llm_client.generate(prompt)
            analysis = self.parse_llm_response(response, rss_feed.category)
            
            if analysis:
                output_path = self._get_output_path(
                    rss_feed.fetch_date, 
                    rss_feed.category
                )
                self.save_analysis(analysis, output_path)
                print(f"✓ Completed {rss_feed.category}")
            else:
                logger.error(
                    f"Invalid LLM response for {rss_feed.category}"
                )
                print(f"✗ Failed {rss_feed.category} (invalid response)")
        
        except LLMProviderError as e:
            logger.error(f"LLM error for {rss_feed.category}: {e}")
            print(f"✗ Failed {rss_feed.category} (LLM error)")
    
    def process_all_feeds(self, date: str) -> None:
        """
        Process all RSS feeds for a given date.
        
        Args:
            date: Date to process (YYYY-MM-DD)
        """
        feed_dir = self.config.rss.rss_feed / date
        
        if not feed_dir.exists():
            logger.warning(f"No RSS feeds found for date: {date}")
            print(f"No RSS feeds found for {date}")
            return
        
        feed_files = list(feed_dir.glob("*.json"))
        
        if not feed_files:
            logger.warning(f"No JSON files in {feed_dir}")
            print(f"No feed files found in {feed_dir}")
            return
        
        logger.info(f"Found {len(feed_files)} feeds to process")
        print(f"\nProcessing {len(feed_files)} feed(s) for {date}\n")
        
        for feed_file in feed_files:
            self.process_category(feed_file)