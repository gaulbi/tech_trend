"""
Core processing logic for wiki search.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from .config import Config
from .exceptions import ValidationError
from .models import (
    ScrapedContent,
    TrendAnalysis,
    TrendInput,
    TrendOutput,
)
from .wikipedia_searcher import WikipediaSearcher

logger = logging.getLogger("wiki_search")


class WikiSearchProcessor:
    """Processes trend analysis and generates scraped content."""

    def __init__(self, config: Config) -> None:
        """
        Initialize processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.searcher = WikipediaSearcher(config.max_search_results)

    def process_category(
        self,
        category_file: Path,
        feed_date: str
    ) -> None:
        """
        Process a single category file.

        Args:
            category_file: Path to input category JSON file
            feed_date: Feed date for processing
        """
        category = category_file.stem
        output_file = self._get_output_path(feed_date, category)

        # Check idempotency
        if output_file.exists():
            logger.info(
                f"Skipping {category} (already processed for {feed_date})"
            )
            print(
                f"Skipping {category} (already processed for {feed_date})"
            )
            return

        # Load input data
        try:
            trend_analysis = self._load_input(category_file)
        except ValidationError as e:
            logger.error(
                f"Validation error for category '{category}': {e}"
            )
            print(f"Error processing {category}: {e}")
            return

        # Validate feed_date matches
        if trend_analysis.feed_date != feed_date:
            logger.warning(
                f"Feed date mismatch in {category}: "
                f"expected '{feed_date}', got '{trend_analysis.feed_date}'"
            )

        # Validate category matches
        if trend_analysis.category != category:
            logger.warning(
                f"Category mismatch in file {category_file}: "
                f"expected '{category}', got '{trend_analysis.category}'"
            )

        # Process trends
        logger.info(
            f"Processing {len(trend_analysis.trends)} trends "
            f"for category '{category}'"
        )
        output_trends = self._process_trends(trend_analysis)

        # Save output
        self._save_output(output_file, feed_date, category, output_trends)

        logger.info(
            f"Completed category '{category}': "
            f"generated {len(output_trends)} result entries"
        )
        print(
            f"Completed {category}: {len(output_trends)} results saved"
        )

    def _load_input(self, input_file: Path) -> TrendAnalysis:
        """
        Load and validate input JSON file.

        Args:
            input_file: Path to input file

        Returns:
            TrendAnalysis object

        Raises:
            ValidationError: If JSON is invalid
        """
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {input_file}: {e}")
        except Exception as e:
            raise ValidationError(f"Error reading {input_file}: {e}")

        # Validate required top-level fields
        required_fields = ["feed_date", "category", "trends"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(
                    f"Missing required field '{field}' in {input_file}"
                )

        try:
            trends = []
            for idx, t in enumerate(data.get("trends", [])):
                # Validate required trend fields
                trend_required = [
                    "topic", "reason", "score", "links", "search_keywords"
                ]
                for field in trend_required:
                    if field not in t:
                        raise ValidationError(
                            f"Trend {idx} missing required field '{field}'"
                        )

                trends.append(
                    TrendInput(
                        topic=t["topic"],
                        reason=t["reason"],
                        score=t["score"],
                        links=t["links"],
                        search_keywords=t["search_keywords"],
                    )
                )

            return TrendAnalysis(
                feed_date=data["feed_date"],
                category=data["category"],
                trends=trends,
            )
        except (KeyError, TypeError) as e:
            raise ValidationError(
                f"Invalid data structure in {input_file}: {e}"
            )

    def _process_trends(
        self,
        trend_analysis: TrendAnalysis
    ) -> List[TrendOutput]:
        """
        Process all trends and generate output.

        Args:
            trend_analysis: Input trend analysis data

        Returns:
            List of processed trend outputs
        """
        output_trends = []
        total_trends = len(trend_analysis.trends)

        for trend_idx, trend in enumerate(trend_analysis.trends, 1):
            logger.info(
                f"Processing trend {trend_idx}/{total_trends}: "
                f"'{trend.topic}' with {len(trend.search_keywords)} keywords"
            )
            
            trend_results = 0
            for keyword in trend.search_keywords:
                results = self.searcher.search_and_fetch(
                    keyword,
                    trend.topic
                )

                for query_used, page_url, content in results:
                    output_trends.append(
                        TrendOutput(
                            topic=trend.topic,
                            query_used=query_used,
                            search_link=page_url,
                            content=content,
                        )
                    )
                    trend_results += 1

            if trend_results > 0:
                logger.info(
                    f"Trend '{trend.topic}': "
                    f"collected {trend_results} Wikipedia pages"
                )
            else:
                logger.warning(
                    f"Trend '{trend.topic}': no Wikipedia pages found"
                )

        return output_trends

    def _save_output(
        self,
        output_file: Path,
        feed_date: str,
        category: str,
        trends: List[TrendOutput]
    ) -> None:
        """
        Save output to JSON file.

        Args:
            output_file: Path to output file
            feed_date: Feed date
            category: Category name
            trends: List of processed trends
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "feed_date": feed_date,
            "category": category,
            "trends": [
                {
                    "topic": t.topic,
                    "query_used": t.query_used,
                    "search_link": t.search_link,
                    "content": t.content,
                }
                for t in trends
            ],
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved output to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving output to {output_file}: {e}")
            raise

    def _get_output_path(self, feed_date: str, category: str) -> Path:
        """
        Get output file path for category.

        Args:
            feed_date: Feed date
            category: Category name

        Returns:
            Path to output file
        """
        base = Path(self.config.scraped_content_base)
        return base / feed_date / category / "wiki-search.json"