# ============================================================================
# FILE: src/tech_trend_analysis/processor.py
# ============================================================================
"""Core processing logic for trend analysis."""

import json
from datetime import date
from pathlib import Path
from typing import List, Optional
import logging

from .config import Config
from .exceptions import ValidationError
from .llm_client import BaseLLMClient, LLMClientFactory
from .models import Article, RSSFeed, Trend, TrendAnalysis


class TrendAnalysisProcessor:
    """Processes RSS feeds and generates trend analysis."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize processor.
        
        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.today = date.today().strftime('%Y-%m-%d')
        
        self.llm_client = LLMClientFactory.create(
            server=config.llm_server,
            model=config.llm_model,
            timeout=config.llm_timeout,
            retry=config.llm_retry
        )
        
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file."""
        prompt_path = Path(self.config.prompt_path)
        
        if not prompt_path.exists():
            self.logger.warning(
                f"Prompt template not found: {prompt_path}. "
                "Using default prompt."
            )
            return self._get_default_prompt()
        
        try:
            with open(prompt_path, 'r') as f:
                template = f.read()
            
            return template
        except Exception as e:
            self.logger.warning(
                f"Error reading prompt template: {e}. "
                "Using default prompt."
            )
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Get default prompt template."""
        return """Analyze the following technology articles and identify key trends.

Articles:
{{context}}

Provide your analysis in JSON format:
{
  "trends": [
    {
      "topic": "Brief trend topic",
      "reason": "Why this is trending",
      "links": ["relevant article URLs"],
      "search_keywords": ["keywords for further research"]
    }
  ]
}"""
    
    def get_category_files(self) -> List[Path]:
        """Get all category JSON files for today."""
        input_dir = Path(self.config.rss_feed_path) / self.today
        
        if not input_dir.exists():
            self.logger.warning(
                f"No RSS feed directory for today: {input_dir}"
            )
            return []
        
        return list(input_dir.glob('*.json'))
    
    def should_process_category(self, category: str) -> bool:
        """Check if category should be processed (idempotency)."""
        output_file = self._get_output_path(category)
        
        if output_file.exists():
            self.logger.info(
                f"Skipping {category}: Analysis already exists"
            )
            return False
        
        return True
    
    def _get_output_path(self, category: str) -> Path:
        """Get output file path for category."""
        output_dir = Path(self.config.analysis_report_path) / self.today
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{category}.json"
    
    def load_rss_feed(self, file_path: Path) -> Optional[RSSFeed]:
        """
        Load RSS feed from JSON file.
        
        Args:
            file_path: Path to RSS feed JSON
            
        Returns:
            RSSFeed object or None if validation fails
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            articles = [
                Article(title=a['title'], link=a['link'])
                for a in data.get('articles', [])
            ]
            
            return RSSFeed(
                category=data['category'],
                fetch_date=data['fetch_date'],
                article_count=data['article_count'],
                articles=articles
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValidationError(
                f"Invalid RSS feed format in {file_path}: {e}"
            )
    
    def create_prompt(self, rss_feed: RSSFeed) -> str:
        """Create LLM prompt from RSS feed."""
        articles_text = '\n\n'.join([
            f"Title: {article.title}\nLink: {article.link}"
            for article in rss_feed.articles
        ])
        
        # Check which placeholder format the template uses
        if '{articles}' in self.prompt_template:
            return self.prompt_template.replace('{articles}', articles_text)
        elif '{{context}}' in self.prompt_template:
            return self.prompt_template.replace('{{context}}', articles_text)
        else:
            # Template doesn't have expected placeholder
            # Append articles at the end
            self.logger.warning(
                f"Prompt template missing placeholder. "
                f"Appending articles at the end."
            )
            return f"{self.prompt_template}\n\n{articles_text}"
    
    def parse_llm_response(self, response: str) -> List[Trend]:
        """
        Parse LLM response into Trend objects.
        
        Args:
            response: LLM response text
            
        Returns:
            List of Trend objects
            
        Raises:
            ValidationError: If response format is invalid
        """
        try:
            # Extract JSON from markdown code blocks if present
            if '```json' in response:
                start_marker = '```json'
                start = response.find(start_marker) + len(start_marker)
                end = response.find('```', start)
                if end > start:
                    response = response[start:end].strip()
            elif '```' in response:
                # Handle generic code blocks
                parts = response.split('```')
                if len(parts) >= 3:
                    # Take the content between first pair of ```
                    response = parts[1].strip()
                    # Remove language identifier if present
                    if response.startswith(('json', 'JSON')):
                        response = response[4:].strip()
            
            data = json.loads(response)
            
            trends = []
            for trend_data in data.get('trends', []):
                trend = Trend(
                    topic=trend_data['topic'],
                    reason=trend_data['reason'],
                    links=trend_data['links'],
                    search_keywords=trend_data['search_keywords']
                )
                trends.append(trend)
            
            return trends
        except (json.JSONDecodeError, KeyError) as e:
            raise ValidationError(f"Invalid LLM response format: {e}")
    
    def save_analysis(
        self,
        category: str,
        trends: List[Trend]
    ) -> None:
        """Save trend analysis to JSON file."""
        output_path = self._get_output_path(category)
        
        analysis = TrendAnalysis(
            analysis_date=self.today,
            category=category,
            trends=trends
        )
        
        output_data = {
            'analysis_date': analysis.analysis_date,
            'category': analysis.category,
            'trends': [
                {
                    'topic': t.topic,
                    'reason': t.reason,
                    'links': t.links,
                    'search_keywords': t.search_keywords
                }
                for t in analysis.trends
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        self.logger.info(f"Saved analysis for {category} to {output_path}")
    
    def process_category(self, file_path: Path) -> bool:
        """
        Process a single category.
        
        Args:
            file_path: Path to RSS feed JSON
            
        Returns:
            True if successful, False otherwise
        """
        category = file_path.stem
        
        try:
            # Check idempotency
            if not self.should_process_category(category):
                return True
            
            # Load RSS feed
            self.logger.info(f"Processing category: {category}")
            rss_feed = self.load_rss_feed(file_path)
            
            if not rss_feed or not rss_feed.articles:
                self.logger.warning(
                    f"No articles found for {category}, skipping analysis"
                )
                return True
            
            # Generate prompt and call LLM
            prompt = self.create_prompt(rss_feed)
            self.logger.debug(f"Sending prompt to LLM for {category}")
            
            response = self.llm_client.generate(prompt)
            
            # Parse and save results
            trends = self.parse_llm_response(response)
            self.save_analysis(category, trends)
            
            self.logger.info(
                f"Successfully analyzed {category}: "
                f"{len(trends)} trends identified"
            )
            return True
            
        except ValidationError as e:
            self.logger.error(f"Validation error for {category}: {e}")
            return False
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {category}: {e}",
                exc_info=True
            )
            return False
    
    def process_all(self) -> dict:
        """
        Process all categories for today.
        
        Returns:
            Summary dictionary with processing results
        """
        category_files = self.get_category_files()
        
        if not category_files:
            self.logger.warning(
                f"No category files found for {self.today}"
            )
            return {
                'date': self.today,
                'total': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0
            }
        
        self.logger.info(
            f"Found {len(category_files)} categories to process"
        )
        
        successful = 0
        failed = 0
        skipped = 0
        
        for file_path in category_files:
            category = file_path.stem
            
            if not self.should_process_category(category):
                skipped += 1
                continue
            
            if self.process_category(file_path):
                successful += 1
            else:
                failed += 1
        
        return {
            'date': self.today,
            'total': len(category_files),
            'successful': successful,
            'failed': failed,
            'skipped': skipped
        }