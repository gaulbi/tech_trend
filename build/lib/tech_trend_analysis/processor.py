"""RSS feed processor and trend analyzer."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from .models import RSSFeed, AnalysisReport, Trend
from .llm.base import BaseLLMClient
from .exceptions import ValidationError, LLMError


class TrendProcessor:
    """Processes RSS feeds and generates trend analysis."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        prompt_template: str,
        logger: logging.Logger
    ):
        """Initialize trend processor.
        
        Args:
            llm_client: LLM client for generating analysis
            prompt_template: Prompt template string
            logger: Logger instance
        """
        self.llm_client = llm_client
        self.prompt_template = prompt_template
        self.logger = logger

    def load_rss_feed(self, file_path: Path) -> Optional[RSSFeed]:
        """Load RSS feed from JSON file.
        
        Args:
            file_path: Path to RSS feed JSON file
            
        Returns:
            RSSFeed instance or None if validation fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            feed = RSSFeed.from_dict(data)
            return feed
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON in {file_path}: {str(e)}"
            )
        except (KeyError, TypeError) as e:
            raise ValidationError(
                f"Invalid RSS feed structure in {file_path}: {str(e)}"
            )

    def analyze_feed(
        self, 
        feed: RSSFeed, 
        analysis_date: str
    ) -> AnalysisReport:
        """Analyze RSS feed and generate trend report.
        
        Args:
            feed: RSS feed to analyze
            analysis_date: Date of analysis
            
        Returns:
            Analysis report
            
        Raises:
            LLMError: If LLM generation fails
        """
        context = feed.to_dict()
        prompt = self.llm_client._prepare_prompt(
            self.prompt_template, 
            {"context": context}
        )
        
        response = self.llm_client.generate(prompt)
        trends = self._parse_llm_response(response)
        
        return AnalysisReport(
            analysis_date=analysis_date,
            category=feed.category,
            trends=trends
        )

    def _parse_llm_response(self, response: str) -> List[Trend]:
        """Parse LLM response into Trend objects.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            List of Trend objects
            
        Raises:
            ValidationError: If response format is invalid
        """
        cleaned_response = self._clean_json_response(response)
        
        try:
            data = json.loads(cleaned_response)
            
            if not isinstance(data, list):
                raise ValidationError("Expected JSON array")
            
            trends = []
            for item in data:
                trend = Trend(
                    topic=item["topic"],
                    reason=item["reason"],
                    category=item["category"],
                    links=item["links"],
                    search_keywords=item["search_keywords"]
                )
                trends.append(trend)
            
            return trends
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValidationError(
                f"Invalid LLM response format: {str(e)}"
            )

    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown formatting.
        
        Args:
            response: Raw response text
            
        Returns:
            Cleaned JSON string
        """
        response = response.strip()
        
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()

    def save_report(self, report: AnalysisReport, file_path: Path) -> None:
        """Save analysis report to JSON file.
        
        Args:
            report: Analysis report to save
            file_path: Destination file path
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)