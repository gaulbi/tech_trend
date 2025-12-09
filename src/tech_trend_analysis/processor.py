# ============================================================================
# src/tech_trend_analysis/processor.py
# ============================================================================

"""Core processing logic for tech trend analysis."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import List, Optional

from .config import Config
from .exceptions import ValidationError, LLMError
from .llm.base import BaseLLMClient
from .models import RSSFeed, Article, AnalysisReport, Trend
from .utils.file_ops import (
    read_json_file,
    write_json_file,
    read_text_file,
    list_json_files
)


class TechTrendProcessor:
    """Processes RSS feeds and generates trend analysis reports."""

    def __init__(
        self,
        config: Config,
        llm_client: BaseLLMClient,
        logger: logging.Logger
    ):
        """
        Initialize processor.

        Args:
            config: Application configuration
            llm_client: LLM client instance
            logger: Logger instance
        """
        self.config = config
        self.llm_client = llm_client
        self.logger = logger

    def process_category(
        self,
        category_file: Path,
        feed_date: str,
        prompt_template: str
    ) -> bool:
        """
        Process a single category RSS feed.

        Args:
            category_file: Path to category JSON file
            feed_date: Feed date string (YYYY-MM-DD)
            prompt_template: LLM prompt template

        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            # Load RSS feed
            feed_data = read_json_file(category_file)
            rss_feed = self._parse_rss_feed(feed_data)

            # Check if output already exists (idempotency)
            output_path = self._get_output_path(
                rss_feed.category,
                feed_date
            )
            if output_path.exists():
                self.logger.info(
                    f"Skipping {rss_feed.category}: "
                    f"Output already exists at {output_path}"
                )
                return True

            # Generate prompt
            prompt = self._create_prompt(rss_feed, prompt_template)

            # Call LLM
            self.logger.info(
                f"Analyzing {rss_feed.category} "
                f"with {len(rss_feed.articles)} articles"
            )
            response = self.llm_client.generate(prompt)

            print(f"\n{'='*60}\nRAW LLM RESPONSE:\n{'='*60}\n{response}\n{'='*60}\n")

            # Parse and save response
            report = self._parse_llm_response(
                response,
                rss_feed.category,
                feed_date
            )
            self._save_report(report, output_path)

            self.logger.info(
                f"Successfully processed {rss_feed.category}: "
                f"{len(report.trends)} trends identified"
            )
            return True

        except ValidationError as e:
            self.logger.error(
                f"Validation error processing {category_file}: {e}",
                exc_info=True
            )
            return False

        except LLMError as e:
            self.logger.error(
                f"LLM error processing {category_file}: {e}",
                exc_info=True
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {category_file}: {e}",
                exc_info=True
            )
            return False

    def _parse_rss_feed(self, data: dict) -> RSSFeed:
        """Parse RSS feed JSON data into RSSFeed model."""
        try:
            articles = [
                Article(
                    title=art['title'],
                    link=art['link']
                )
                for art in data.get('articles', [])
            ]

            return RSSFeed(
                category=data['category'],
                feed_date=data['feed_date'],
                article_count=data['article_count'],
                articles=articles
            )
        except KeyError as e:
            raise ValidationError(f"Missing required field in RSS feed: {e}")

    def _create_prompt(
        self,
        rss_feed: RSSFeed,
        template: str
    ) -> str:
        """
        Create LLM prompt from RSS feed and template.

        Args:
            rss_feed: RSS feed data
            template: Prompt template

        Returns:
            Formatted prompt string
        """
        articles_text = "\n\n".join(
            f"Title: {art.title}\nLink: {art.link}"
            for art in rss_feed.articles
        )

        prompt = template.replace(
            "{category}",
            rss_feed.category
        ).replace(
            "{articles}",
            articles_text
        ).replace(
            "{article_count}",
            str(rss_feed.article_count)
        ).replace(
            "{feed_date}",
            rss_feed.feed_date
        )

        return prompt

    def _parse_llm_response(
        self,
        response: str,
        category: str,
        feed_date: str
    ) -> AnalysisReport:
        """
        Parse LLM response into AnalysisReport model.

        Args:
            response: Raw LLM response
            category: Category name
            feed_date: Feed date

        Returns:
            AnalysisReport instance

        Raises:
            ValidationError: If response parsing fails
        """
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Handle markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            data = json.loads(response)

            trends = [
                Trend(
                    topic=t['topic'],
                    reason=t['reason'],
                    score=t['score'],
                    links=t['links'],
                    search_keywords=t['search_keywords']
                )
                for t in data.get('trends', [])
            ]

            return AnalysisReport(
                feed_date=feed_date,
                category=category,
                trends=trends
            )

        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in LLM response: {e}")
        except KeyError as e:
            raise ValidationError(f"Missing field in LLM response: {e}")

    def _get_output_path(self, category: str, feed_date: str) -> Path:
        """Get output file path for a category."""
        base_path = Path(self.config.analysis_report_path)
        return base_path / feed_date / f"{category}.json"

    def _save_report(
        self,
        report: AnalysisReport,
        output_path: Path
    ) -> None:
        """Save analysis report to file."""
        data = {
            'feed_date': report.feed_date,
            'category': report.category,
            'trends': [
                {
                    'topic': t.topic,
                    'reason': t.reason,
                    'score': t.score,
                    'links': t.links,
                    'search_keywords': t.search_keywords
                }
                for t in report.trends
            ]
        }
        write_json_file(output_path, data)